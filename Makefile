PYTHON ?= python
CONFIG ?= configs/catchment.yaml

.PHONY: setup lint test check-config data baseline train eval api

setup:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e ".[dev]"

lint:
	$(PYTHON) -m ruff check .

test:
	$(PYTHON) -m pytest

# Pipeline targets refuse to run while configs/catchment.yaml still has placeholders.
check-config:
	$(PYTHON) -m src.config --config $(CONFIG) --strict

data: check-config
	@echo "TODO: Earth Engine pull not implemented yet (step 2)." && exit 1

baseline: check-config
	@echo "TODO: SCS-CN baseline not implemented yet (step 3)." && exit 1

train: check-config
	@echo "TODO: XGBoost/LSTM training not implemented yet (steps 4-5)." && exit 1

eval: check-config
	@echo "TODO: evaluation not implemented yet (step 6)." && exit 1

api:
	@echo "TODO: FastAPI backend not implemented yet (step 7)." && exit 1
