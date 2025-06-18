.PHONY: help test test-all lint format clean install dev-install

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install the package
	pip install .

dev-install:  ## Install the package in development mode
	pip install -e .
	pip install -r requirements-test.txt

test:  ## Run tests with pytest
	pytest tests/ -v

test-all:  ## Run tests across all supported Python versions with tox
	tox

test-cov:  ## Run tests with coverage report
	pytest tests/ --cov=service_config_foundry --cov-report=term-missing --cov-report=html

lint:  ## Run linting with flake8
	flake8 service_config_foundry tests

format:  ## Format code with black and isort
	black service_config_foundry tests
	isort service_config_foundry tests

format-check:  ## Check code formatting
	black --check service_config_foundry tests
	isort --check-only service_config_foundry tests

clean:  ## Clean up build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .tox/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:  ## Build the package
	python -m build

publish-test:  ## Publish to TestPyPI
	python -m build
	twine upload --repository testpypi dist/*

publish:  ## Publish to PyPI
	python -m build
	twine upload dist/*

pre-commit-install:  ## Install pre-commit hooks
	pre-commit install

pre-commit-run:  ## Run pre-commit on all files
	pre-commit run --all-files

deploy:
	bash deploy.bash

bump-patch:  ## Bump patch version (0.1.0 -> 0.1.1)
	bash release.bash patch

bump-minor:  ## Bump minor version (0.1.0 -> 0.2.0)
	bash release.bash minor

bump-major:  ## Bump major version (0.1.0 -> 1.0.0)
	bash release.bash major

release:  ## Create a new release (defaults to patch)
	bash release.bash

release-patch:  ## Create a patch release
	bash release.bash patch

release-minor:  ## Create a minor release  
	bash release.bash minor

release-major:  ## Create a major release
	bash release.bash major

release-test:  ## Test release to TestPyPI
	python -m build
	twine upload --repository testpypi dist/*