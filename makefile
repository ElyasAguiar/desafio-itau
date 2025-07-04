# Project Metadata
PROJECT_NAME := fastapi_boilerplate
ENV_FILE := ".env"
PORT := $(shell grep ^PORT= $(ENV_FILE) | cut -d '=' -f2)

# Commands
PYTHON := uv run python
UVICORN := $(PYTHON) main.py
ISORT := uv run isort .
BLACK := uv run black .
RUFF := uv run ruff .
MYPY := uv run mypy .
PRECOMMIT := uv run pre-commit

# Default
.DEFAULT_GOAL := help

## ----------- Local Development -----------

.PHONY: run
run: ## Run FastAPI app with reload (Dev)
	$(UVICORN) --reload --env-file $(ENV_FILE)