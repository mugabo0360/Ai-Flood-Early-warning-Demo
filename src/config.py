"""Load and validate the catchment configuration (YAML) and runtime settings (.env).

Placeholders such as ``TODO`` or ``[choose catchment]`` are allowed when *loading* a
config so the repo works before a study area is chosen. Pipeline commands must call
:meth:`CatchmentConfig.require_complete`, which fails with a clear message listing every
field that is still a placeholder.

CLI::

    python -m src.config --config configs/catchment.yaml [--strict]
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import date
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

DEFAULT_CONFIG_PATH = Path("configs/catchment.yaml")


class ConfigError(ValueError):
    """Raised when a configuration file is missing, malformed or invalid."""


class ConfigIncompleteError(ConfigError):
    """Raised when a pipeline command runs while required fields are still placeholders."""


def is_placeholder(value: Any) -> bool:
    """Return True if ``value`` is unset or a placeholder (``TODO...`` or ``[...]``)."""
    if value is None:
        return True
    if isinstance(value, str):
        text = value.strip()
        return not text or text.upper().startswith("TODO") or (
            text.startswith("[") and text.endswith("]")
        )
    return False


class GeometryConfig(BaseModel):
    """Study-area geometry: a WGS84 bounding box and/or a GeoJSON file path."""

    model_config = ConfigDict(extra="forbid")

    bbox: list[float] | str | None = None
    geojson: str | None = None

    @field_validator("bbox")
    @classmethod
    def _check_bbox(cls, v: list[float] | str | None) -> list[float] | str | None:
        if v is None or isinstance(v, str):
            if isinstance(v, str) and not is_placeholder(v):
                raise ValueError("bbox must be [min_lon, min_lat, max_lon, max_lat] or TODO")
            return v
        if len(v) != 4:
            raise ValueError("bbox must have 4 values: [min_lon, min_lat, max_lon, max_lat]")
        min_lon, min_lat, max_lon, max_lat = v
        if not (-180 <= min_lon < max_lon <= 180):
            raise ValueError("bbox longitudes must satisfy -180 <= min_lon < max_lon <= 180")
        if not (-90 <= min_lat < max_lat <= 90):
            raise ValueError("bbox latitudes must satisfy -90 <= min_lat < max_lat <= 90")
        return v

    def is_set(self) -> bool:
        """Return True if at least one usable geometry source is configured."""
        return not is_placeholder(self.bbox) or not is_placeholder(self.geojson)


class CatchmentConfig(BaseModel):
    """Validated contents of ``configs/catchment.yaml``."""

    model_config = ConfigDict(extra="forbid")

    name: str
    geometry: GeometryConfig = Field(default_factory=GeometryConfig)
    start_date: date | str | None = None
    end_date: date | str | None = None
    target_variable: str | None = None
    horizons: list[int] = Field(default_factory=lambda: list(range(1, 8)))

    @field_validator("start_date", "end_date", mode="before")
    @classmethod
    def _parse_date(cls, v: Any) -> Any:
        if isinstance(v, str) and not is_placeholder(v):
            try:
                return date.fromisoformat(v.strip())
            except ValueError as exc:
                raise ValueError(f"invalid ISO date {v!r} (expected YYYY-MM-DD or TODO)") from exc
        return v

    @field_validator("horizons")
    @classmethod
    def _check_horizons(cls, v: list[int]) -> list[int]:
        if not v:
            raise ValueError("horizons must not be empty")
        if any(h < 1 for h in v):
            raise ValueError("horizons must be positive integers (days ahead)")
        if len(set(v)) != len(v):
            raise ValueError("horizons must not contain duplicates")
        return sorted(v)

    @model_validator(mode="after")
    def _check_date_order(self) -> CatchmentConfig:
        if (
            isinstance(self.start_date, date)
            and isinstance(self.end_date, date)
            and self.start_date >= self.end_date
        ):
            raise ValueError("start_date must be before end_date")
        return self

    def missing_fields(self) -> list[str]:
        """Return the names of required fields that are still placeholders."""
        missing = [
            field
            for field in ("name", "start_date", "end_date", "target_variable")
            if is_placeholder(getattr(self, field))
        ]
        if not self.geometry.is_set():
            missing.append("geometry (bbox or geojson)")
        return missing

    def require_complete(self) -> CatchmentConfig:
        """Raise :class:`ConfigIncompleteError` if any required field is a placeholder."""
        missing = self.missing_fields()
        if missing:
            raise ConfigIncompleteError(
                "Catchment config is incomplete; fill in these fields in "
                f"configs/catchment.yaml before running pipeline commands: {', '.join(missing)}"
            )
        return self


class Settings(BaseModel):
    """Runtime settings read from environment variables / ``.env``."""

    ee_project: str | None = None
    database_url: str | None = None
    log_level: str = "INFO"

    @field_validator("ee_project", "database_url", mode="before")
    @classmethod
    def _empty_to_none(cls, v: Any) -> Any:
        return None if isinstance(v, str) and not v.strip() else v

    @field_validator("log_level")
    @classmethod
    def _check_log_level(cls, v: str) -> str:
        level = v.upper()
        if level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise ValueError(f"invalid LOG_LEVEL {v!r}")
        return level


def load_config(path: str | Path = DEFAULT_CONFIG_PATH) -> CatchmentConfig:
    """Load and validate a catchment YAML file.

    Raises:
        ConfigError: if the file is missing, not valid YAML, or fails validation.
    """
    path = Path(path)
    if not path.is_file():
        raise ConfigError(f"Config file not found: {path}")
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigError(f"Invalid YAML in {path}: {exc}") from exc
    if not isinstance(raw, dict):
        raise ConfigError(f"Config {path} must be a YAML mapping")
    try:
        return CatchmentConfig.model_validate(raw)
    except ValidationError as exc:
        raise ConfigError(f"Invalid config {path}:\n{exc}") from exc


def load_settings(env_file: str | Path | None = ".env") -> Settings:
    """Load settings from ``env_file`` (if it exists) and the process environment."""
    if env_file is not None and Path(env_file).is_file():
        load_dotenv(env_file, override=False)
    return Settings(
        ee_project=os.getenv("EE_PROJECT"),
        database_url=os.getenv("DATABASE_URL"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )


def main(argv: list[str] | None = None) -> int:
    """Validate a config file; with ``--strict`` also require all fields to be filled."""
    parser = argparse.ArgumentParser(description="Validate the catchment configuration.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument(
        "--strict", action="store_true", help="fail if any required field is a placeholder"
    )
    args = parser.parse_args(argv)
    try:
        cfg = load_config(args.config)
        if args.strict:
            cfg.require_complete()
    except ConfigError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    missing = cfg.missing_fields()
    print(f"Config OK: {args.config}")
    if missing:
        print(f"Placeholders remaining: {', '.join(missing)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
