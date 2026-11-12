.DEFAULT_GOAL := help
COMPOSE := docker compose
BACKEND := $(COMPOSE) exec api

.PHONY: help env up down logs ps test test-unit lint fmt migrate migration shell psql clean

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

env: ## Create .env from template (if missing)
	@test -f .env || cp .env.example .env

up: env ## Start the full stack (api, worker, frontend, postgres, redis)
	$(COMPOSE) up -d --build
	@echo "Frontend: http://localhost:5173   API docs: http://localhost:8000/docs"

down: ## Stop the stack
	$(COMPOSE) down

logs: ## Tail logs
	$(COMPOSE) logs -f --tail=100

ps: ## Show service status
	$(COMPOSE) ps

test: ## Run all backend tests (incl. integration) inside the api container
	$(BACKEND) pytest -v

test-unit: ## Run backend unit tests only
	$(BACKEND) pytest -v -m "not integration"

lint: ## Lint backend + frontend
	$(BACKEND) ruff check .
	$(BACKEND) ruff format --check .
	$(COMPOSE) exec frontend npm run lint

fmt: ## Auto-format backend
	$(BACKEND) ruff check --fix .
	$(BACKEND) ruff format .

migrate: ## Apply DB migrations
	$(BACKEND) alembic upgrade head

migration: ## Create a migration: make migration m="add users table"
	$(BACKEND) alembic revision --autogenerate -m "$(m)"

shell: ## Shell inside the api container
	$(BACKEND) bash

psql: ## psql into the local database
	$(COMPOSE) exec postgres psql -U text2chess -d text2chess

clean: ## Stop and DELETE local volumes (database data!)
	$(COMPOSE) down -v

