.DEFAULT_GOAL := help

.PHONY: build
build: ## Build the Docker containers
	docker compose build

.PHONY: start
start: ## Start the application
	docker compose up -d

.PHONY: stop
stop: ## Stop the application
	docker compose down

.PHONY: logs
logs: ## Tail the logs for the application
	docker compose logs -f

.PHONY: test
test: ## Run tests
	python -m unittest json_fixer.fixer_test

.PHONY: help
help: ## Display this help message
	@echo "Usage: make [target] ...\n"
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
