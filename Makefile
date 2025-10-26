.PHONY: help install test test-all lint format clean coverage docs

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install the package in development mode with dev dependencies
	uv pip install -e ".[dev]"

test: ## Run unit tests
	uv run pytest tests/ -v --tb=short

test-all: ## Run all tests with coverage
	uv run pytest tests/ --cov=bluepyll --cov-report=term-missing --cov-report=html --cov-fail-under=80

test-controller: ## Run only controller tests
	uv run pytest tests/test_controller.py -v

test-ui: ## Run only UI tests
	uv run pytest tests/test_ui.py -v

test-utils: ## Run only utils tests
	uv run pytest tests/test_utils.py -v

lint: ## Check code formatting and style
	uv run black --check src/ tests/
	uv run isort --check-only src/ tests/

format: ## Format code with black and isort
	uv run black src/ tests/
	uv run isort src/ tests/

coverage: ## Show coverage report
	uv run pytest tests/ --cov=bluepyll --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

clean: ## Remove build artifacts and cache files
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

docs: ## Generate documentation (if sphinx is configured)
	@echo "Documentation generation not configured yet"

run-tests: ## Run the comprehensive test runner
	uv run python run_tests.py
