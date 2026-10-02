from datetime import date
from pathlib import Path

import pytest

from src.config import (
    CatchmentConfig,
    ConfigError,
    ConfigIncompleteError,
    is_placeholder,
    load_config,
    load_settings,
    main,
)

REPO_CONFIG = Path(__file__).resolve().parents[1] / "configs" / "catchment.yaml"

COMPLETE_YAML = """
name: Test catchment
geometry:
  bbox: [32.0, 0.0, 32.5, 0.5]
start_date: 2001-01-01
end_date: 2020-12-31
target_variable: discharge_m3s
horizons: [1, 2, 3, 4, 5, 6, 7]
"""


def write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "catchment.yaml"
    path.write_text(text, encoding="utf-8")
    return path


@pytest.mark.parametrize(
    "value, expected",
    [(None, True), ("TODO", True), ("todo: later", True), ("[choose catchment]", True),
     ("", True), ("Mpanga", False), (3, False), ([1.0], False)],
)
def test_is_placeholder(value, expected):
    assert is_placeholder(value) is expected


def test_repo_config_loads_with_placeholders():
    cfg = load_config(REPO_CONFIG)
    assert cfg.horizons == [1, 2, 3, 4, 5, 6, 7]
    assert set(cfg.missing_fields()) >= {"name", "start_date", "end_date", "target_variable"}


def test_repo_config_fails_strict_with_clear_message():
    cfg = load_config(REPO_CONFIG)
    with pytest.raises(ConfigIncompleteError, match="target_variable"):
        cfg.require_complete()


def test_complete_config(tmp_path):
    cfg = load_config(write(tmp_path, COMPLETE_YAML)).require_complete()
    assert cfg.start_date == date(2001, 1, 1)
    assert cfg.geometry.bbox == [32.0, 0.0, 32.5, 0.5]
    assert cfg.missing_fields() == []


def test_quoted_iso_date_is_parsed(tmp_path):
    cfg = load_config(write(tmp_path, COMPLETE_YAML.replace("2001-01-01", '"2001-01-01"')))
    assert cfg.start_date == date(2001, 1, 1)


@pytest.mark.parametrize(
    "old, new",
    [
        ("[32.0, 0.0, 32.5, 0.5]", "[32.5, 0.0, 32.0, 0.5]"),
        ("[32.0, 0.0, 32.5, 0.5]", "[32.0, 0.0, 32.5]"),
        ("end_date: 2020-12-31", "end_date: 2000-12-31"),
        ("start_date: 2001-01-01", "start_date: 01/01/2001"),
        ("horizons: [1, 2, 3, 4, 5, 6, 7]", "horizons: [0, 1]"),
        ("horizons: [1, 2, 3, 4, 5, 6, 7]", "horizons: [1, 1]"),
        ("horizons: [1, 2, 3, 4, 5, 6, 7]", "horizons: [1]\nunknown_key: 1"),
    ],
)
def test_invalid_configs_raise(tmp_path, old, new):
    with pytest.raises(ConfigError):
        load_config(write(tmp_path, COMPLETE_YAML.replace(old, new)))


def test_missing_file_raises(tmp_path):
    with pytest.raises(ConfigError, match="not found"):
        load_config(tmp_path / "nope.yaml")


def test_geojson_alone_counts_as_geometry():
    cfg = CatchmentConfig.model_validate(
        {"name": "X", "geometry": {"bbox": "TODO", "geojson": "data/raw/catchment.geojson"},
         "start_date": "2001-01-01", "end_date": "2002-01-01", "target_variable": "q"}
    )
    assert cfg.missing_fields() == []


def test_load_settings_from_env_file(tmp_path, monkeypatch):
    for var in ("EE_PROJECT", "DATABASE_URL", "LOG_LEVEL"):
        monkeypatch.delenv(var, raising=False)
    env = tmp_path / ".env"
    env.write_text("EE_PROJECT=my-project\nDATABASE_URL=\nLOG_LEVEL=debug\n", encoding="utf-8")
    settings = load_settings(env)
    assert settings.ee_project == "my-project"
    assert settings.database_url is None
    assert settings.log_level == "DEBUG"


def test_cli_strict_exit_codes(tmp_path, capsys):
    assert main(["--config", str(REPO_CONFIG)]) == 0
    assert main(["--config", str(REPO_CONFIG), "--strict"]) == 1
    assert "incomplete" in capsys.readouterr().err
    assert main(["--config", str(write(tmp_path, COMPLETE_YAML)), "--strict"]) == 0
