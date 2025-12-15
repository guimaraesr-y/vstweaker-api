# ============================
# CONFIG
# ============================
DEV_COMPOSE = docker-compose.dev.yml
PROD_COMPOSE = docker-compose.prod.yml

PROJECT_NAME = vstweaker

# ============================
# HELP
# ============================
.PHONY: help
help:
	@echo ""
	@echo "Uso:"
	@echo "  make dev-up          Sobe ambiente DEV"
	@echo "  make dev-down        Para ambiente DEV"
	@echo "  make dev-migrate     Roda migrate no DEV"
	@echo "  make dev-makemigrations"
	@echo "  make dev-logs        Logs do DEV"
	@echo ""
	@echo "  make prod-up         Sobe ambiente PROD"
	@echo "  make prod-down       Para ambiente PROD"
	@echo "  make prod-migrate    Roda migrate no PROD"
	@echo "  make prod-logs       Logs do PROD"
	@echo ""

# ============================
# DEV
# ============================

.PHONY: dev-up
dev-up:
	docker compose -f $(DEV_COMPOSE) up --build -d

.PHONY: dev-down
dev-down:
	docker compose -f $(DEV_COMPOSE) down

.PHONY: dev-migrate
dev-migrate:
	docker compose -f $(DEV_COMPOSE) exec web python manage.py migrate

.PHONY: dev-makemigrations
dev-makemigrations:
	docker compose -f $(DEV_COMPOSE) exec web python manage.py makemigrations

.PHONY: dev-logs
dev-logs:
	docker compose -f $(DEV_COMPOSE) logs -f

# ============================
# PROD
# ============================

.PHONY: prod-up
prod-up:
	docker compose -f $(PROD_COMPOSE) up -d --build

.PHONY: prod-down
prod-down:
	docker compose -f $(PROD_COMPOSE) down

.PHONY: prod-migrate
prod-migrate:
	docker compose -f $(PROD_COMPOSE) exec web python manage.py migrate

.PHONY: prod-logs
prod-logs:
	docker compose -f $(PROD_COMPOSE) logs -f
