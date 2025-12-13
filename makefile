.PHONY: all install build run test clean format lint type-check help evolutionary local_search

# Default target
.DEFAULT_GOAL := build

# Python interpreter
PYTHON := python3

# Subdirectories
EVOLUTIONARY_DIR := src/evolutionary
LOCAL_SEARCH_DIR := src/local_search

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install all dependencies
	$(PYTHON) -m pip install -r requirements.txt

install-dev:  ## Install development dependencies
	$(PYTHON) -m pip install -r requirements-dev.txt

build: build-evolutionary build-local_search  ## Build all modules (default)
	@echo "All modules built successfully"

build-evolutionary:  ## Build evolutionary module
	@echo "Building evolutionary module..."
	$(MAKE) -C $(EVOLUTIONARY_DIR) build

build-local_search:  ## Build local_search module
	@echo "Building local_search module..."
	$(MAKE) -C $(LOCAL_SEARCH_DIR) build

run-evolutionary:  ## Run evolutionary algorithm example
	$(MAKE) -C $(EVOLUTIONARY_DIR) run

run-local_search:  ## Run local search examples
	$(MAKE) -C $(LOCAL_SEARCH_DIR) run

run: run-local_search  ## Run default example (local_search)

test:  ## Run all tests
	$(MAKE) -C $(EVOLUTIONARY_DIR) test
	$(MAKE) -C $(LOCAL_SEARCH_DIR) test

clean:  ## Clean all build artifacts
	$(MAKE) -C $(EVOLUTIONARY_DIR) clean
	$(MAKE) -C $(LOCAL_SEARCH_DIR) clean
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .mypy_cache

format:  ## Format all code
	$(MAKE) -C $(EVOLUTIONARY_DIR) format
	$(MAKE) -C $(LOCAL_SEARCH_DIR) format

lint:  ## Lint all code
	$(MAKE) -C $(EVOLUTIONARY_DIR) lint
	$(MAKE) -C $(LOCAL_SEARCH_DIR) lint

type-check:  ## Type check all code
	$(MAKE) -C $(EVOLUTIONARY_DIR) type-check
	$(MAKE) -C $(LOCAL_SEARCH_DIR) type-check
