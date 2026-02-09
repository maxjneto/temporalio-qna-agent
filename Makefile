# Makefile to facilitate common project commands

.PHONY: help setup install run-worker run-api run-frontend run-all docker-up docker-down test lint format clean

# Detect operating system
ifeq ($(OS),Windows_NT)
    PYTHON := python
    VENV_ACTIVATE := .venv\Scripts\activate.bat
else
    PYTHON := python3
    VENV_ACTIVATE := source .venv/bin/activate
endif

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Configure environment (install dependencies)
	$(PYTHON) setup.py

install: ## Install dependencies only
	$(PYTHON) -m pip install -r requirements.txt

run-worker: ## Start Temporal Worker
	$(PYTHON) worker.py

run-api: ## Start FastAPI
	$(PYTHON) api/main.py

run-frontend: ## Start Streamlit frontend
	streamlit run frontend/app.py

run-all: ## Start all components (worker, api, frontend)
ifeq ($(OS),Windows_NT)
	@echo "Use: run.bat"
else
	@bash run.sh
endif

docker-up: ## Start Temporal Server via Docker Compose
	docker-compose up -d

docker-down: ## Stop Temporal Server
	docker-compose down

docker-logs: ## Show Temporal Server logs
	docker-compose logs -f temporal

generate-embeddings: ## Generate search index embeddings
	$(PYTHON) database/utils.py

test: ## Run tests (when available)
	pytest tests/ -v

lint: ## Check code with ruff
	ruff check .

format: ## Format code with black
	black .

clean: ## Remove temporary files and cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete

# Shortcuts
w: run-worker ## Shortcut for run-worker
a: run-api ## Shortcut for run-api
f: run-frontend ## Shortcut for run-frontend
