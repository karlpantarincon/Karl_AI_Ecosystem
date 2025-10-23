.PHONY: help fmt lint test dev clean install

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install poetry
	poetry install

fmt: ## Format code with black and ruff
	poetry run black corehub/ agents/
	poetry run ruff --fix corehub/ agents/

lint: ## Run linting with ruff and mypy
	poetry run ruff corehub/ agents/
	poetry run mypy corehub/ agents/

test: ## Run tests with coverage
	poetry run pytest --cov=corehub --cov=agents --cov-report=term-missing

test-corehub: ## Run only CoreHub tests
	poetry run pytest corehub/tests/ --cov=corehub --cov-report=term-missing

test-devagent: ## Run only DevAgent tests
	poetry run pytest agents/devagent/tests/ --cov=agents --cov-report=term-missing

dev: ## Start CoreHub in development mode
	poetry run uvicorn corehub.api.main:app --reload --port 8000

devagent: ## Run DevAgent once
	poetry run python -m agents.devagent.app.main run_once

devagent-loop: ## Run DevAgent in loop mode
	poetry run python -m agents.devagent.app.main loop --interval 300

db-migrate: ## Run database migrations
	poetry run alembic upgrade head

db-revision: ## Create new database migration
	poetry run alembic revision --autogenerate -m "$(message)"

db-reset: ## Reset database (WARNING: destroys all data)
	poetry run alembic downgrade base
	poetry run alembic upgrade head

clean: ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/

setup: install db-migrate ## Complete setup (install + migrate)
	@echo "Setup complete! Run 'make dev' to start the API"

ci: lint test ## Run CI pipeline (lint + test)

all: fmt lint test ## Run all checks (format + lint + test)