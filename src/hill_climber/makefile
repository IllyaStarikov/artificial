.PHONY: all install build run test clean format lint type-check help

# Default target
.DEFAULT_GOAL := build

# Python interpreter
PYTHON := python3

# Source files
SOURCES := $(wildcard *.py)

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	$(PYTHON) -m pip install -r ../../requirements.txt

install-dev:  ## Install development dependencies
	$(PYTHON) -m pip install -r ../../requirements-dev.txt

build: lint type-check  ## Run all checks (default)
	@echo "Build complete - all checks passed"

run:  ## Run local search examples
	$(PYTHON) main.py

test:  ## Run tests
	$(PYTHON) -m pytest tests/ -v

clean:  ## Remove build artifacts
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -f *.pyc
	rm -f .coverage

format:  ## Format code with black
	$(PYTHON) -m black $(SOURCES)

lint:  ## Run linter
	$(PYTHON) -m flake8 $(SOURCES) --max-line-length=100 --ignore=E501

type-check:  ## Run type checker
	$(PYTHON) -m mypy $(SOURCES) --ignore-missing-imports
