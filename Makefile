.PHONY: help install check-env init-db db-migrate db-upgrade db-seed run run-demo test test-cov lint lint-full format-check format clean reset-admin

help: ## Show this help
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

install: ## Install Python dependencies
	pip install -r requirements.txt

check-env: ## Validate environment configuration
	python check_env.py

init-db: ## Initialize MySQL database and seed data
	python init_db.py

db-migrate: ## Generate new Alembic migration
	flask db migrate

db-upgrade: ## Apply pending Alembic migrations
	flask db upgrade

db-seed: ## Seed demo data
	python scripts/seed_demo_data.py

run: ## Start Flask dev server (MySQL)
	python app.py

run-demo: ## Start Flask in demo mode (SQLite)
	FLASK_ENV=demo python app.py

test: ## Run all Python tests
	pytest

test-cov: ## Run tests with HTML coverage report
	pytest --cov=. --cov-report=html:Test/reports/coverage_html --cov-report=term-missing

test-p0: ## Run P0 smoke tests only
	pytest -m p0

lint: ## Lint - critical errors only
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

lint-full: ## Lint - all rules
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

format-check: ## Check code formatting (dry run)
	black --check .

format: ## Auto-format code with black
	black .

clean: ## Remove Python cache artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; find . -type f -name '*.pyc' -delete

reset-admin: ## Reset admin account password
	python reset_admin_password.py
