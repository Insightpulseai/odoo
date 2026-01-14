# Odoo 18 CE Local Sandbox - Makefile
# Canonical commands for local development

.PHONY: help
help: ## Show this help message
	@echo "Odoo 18 CE Local Sandbox Commands"
	@echo "=================================="
	@awk 'BEGIN {FS = ":.*##"; printf "\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Sandbox Management

.PHONY: start
start: ## Start Odoo sandbox (docker compose up -d)
	docker compose up -d

.PHONY: stop
stop: ## Stop Odoo sandbox (keep volumes)
	docker compose stop

.PHONY: restart
restart: ## Restart Odoo service only
	docker compose restart odoo

.PHONY: down
down: ## Stop and remove containers (keep volumes)
	docker compose down

.PHONY: logs
logs: ## Show logs (follow mode)
	docker compose logs -f

.PHONY: logs-odoo
logs-odoo: ## Show Odoo logs only
	docker compose logs -f odoo

.PHONY: logs-db
logs-db: ## Show database logs only
	docker compose logs -f db

.PHONY: status
status: ## Show service status
	docker compose ps

##@ Database Management

.PHONY: psql
psql: ## Connect to PostgreSQL via psql
	docker compose exec db psql -U odoo -d odoo

.PHONY: db-check
db-check: ## Check database health
	docker compose exec db pg_isready -U odoo -d odoo

.PHONY: db-version
db-version: ## Show PostgreSQL version
	docker compose exec db psql -U odoo -d odoo -c "SELECT version();"

##@ Module Management (Legacy - Use Hot-Reload Commands Instead)

.PHONY: update-apps-list
update-apps-list: ## Update Odoo apps list
	docker compose exec -T odoo odoo -d odoo -u base --stop-after-init
	docker compose restart odoo

.PHONY: install
install: ## Install module (usage: make install MODULE=ipai_finance_ppm)
	@if [ -z "$(MODULE)" ]; then \
		echo "Error: MODULE not specified"; \
		echo "Usage: make install MODULE=module_name"; \
		exit 1; \
	fi
	docker compose exec -T odoo odoo -d odoo -i $(MODULE) --stop-after-init
	docker compose restart odoo

.PHONY: upgrade
upgrade: ## Upgrade module (usage: make upgrade MODULE=ipai_finance_ppm)
	@if [ -z "$(MODULE)" ]; then \
		echo "Error: MODULE not specified"; \
		echo "Usage: make upgrade MODULE=module_name"; \
		exit 1; \
	fi
	docker compose exec -T odoo odoo -d odoo -u $(MODULE) --stop-after-init
	docker compose restart odoo

.PHONY: check-addons
check-addons: ## Verify addon directories
	@echo "Checking OCA addons:"
	@docker compose exec odoo ls -la /mnt/addons/oca | head -20 || echo "OCA addons not found"
	@echo ""
	@echo "Checking IPAI addons:"
	@docker compose exec odoo ls -la /mnt/addons/ipai | head -20 || echo "IPAI addons not found"

##@ Hot-Reload Development

.PHONY: dev-restart
dev-restart: ## Restart Odoo only (Python changes)
	docker compose restart odoo
	@echo "✓ Odoo restarted. Python changes applied."

.PHONY: dev-upgrade
dev-upgrade: ## Upgrade module (usage: make dev-upgrade MODULE=ipai_finance_ppm)
	@if [ -z "$(MODULE)" ]; then \
		echo "Error: MODULE not specified"; \
		echo "Usage: make dev-upgrade MODULE=module_name"; \
		exit 1; \
	fi
	@echo "Upgrading module $(MODULE)..."
	docker compose exec -T odoo odoo -d odoo -u $(MODULE) --stop-after-init
	docker compose restart odoo
	@echo "✓ Module $(MODULE) upgraded."

.PHONY: dev-install
dev-install: ## Install module (usage: make dev-install MODULE=ipai_finance_ppm)
	@if [ -z "$(MODULE)" ]; then \
		echo "Error: MODULE not specified"; \
		echo "Usage: make dev-install MODULE=module_name"; \
		exit 1; \
	fi
	@echo "Installing module $(MODULE)..."
	docker compose exec -T odoo odoo -d odoo -i $(MODULE) --stop-after-init
	docker compose restart odoo
	@echo "✓ Module $(MODULE) installed."

.PHONY: dev-enable-assets
dev-enable-assets: ## Enable dev mode for automatic asset reloading
	@echo "Enabling dev mode in odoo.conf..."
	@grep -q "^dev_mode = all" odoo.conf || echo "dev_mode = all" >> odoo.conf
	docker compose restart odoo
	@echo "✓ Dev mode enabled. Assets will reload automatically."

.PHONY: dev-disable-assets
dev-disable-assets: ## Disable dev mode
	@sed -i.bak '/^dev_mode = all/d' odoo.conf
	docker compose restart odoo
	@echo "✓ Dev mode disabled."

##@ Reset & Cleanup

.PHONY: reset
reset: ## Hard reset - destroy all data and restart fresh
	@echo "WARNING: This will destroy all data (database + filestore)"
	@echo "Press Ctrl+C to cancel, or wait 5 seconds to continue..."
	@sleep 5
	docker compose down -v
	docker compose up -d

.PHONY: reset-soft
reset-soft: ## Soft reset - restart services (keep data)
	docker compose restart

##@ Development Tools

.PHONY: shell
shell: ## Open bash shell in Odoo container
	docker compose exec odoo bash

.PHONY: odoo-version
odoo-version: ## Show Odoo version
	docker compose exec odoo odoo --version

.PHONY: python-shell
python-shell: ## Open Odoo Python shell
	docker compose exec odoo odoo shell -d odoo

.PHONY: open
open: ## Open Odoo in browser
	@echo "Opening http://localhost:8069"
	@which open > /dev/null && open http://localhost:8069 || echo "Visit http://localhost:8069 in your browser"

##@ CI-Style Checks

.PHONY: verify
verify: status db-check ## Verify sandbox health
	@echo ""
	@echo "Sandbox verification complete"

.PHONY: test-connection
test-connection: ## Test Odoo HTTP connection
	@echo "Testing Odoo connection..."
	@curl -sf http://localhost:8069/web/health > /dev/null && echo "✓ Odoo is responding" || echo "✗ Odoo is not responding"

##@ Quick Workflows

.PHONY: clean-start
clean-start: down start ## Clean start - stop, remove containers, start fresh (keep volumes)
	@echo "Waiting for services to be healthy..."
	@sleep 10
	@make status

.PHONY: full-reset
full-reset: reset ## Full reset - alias for 'reset' (destroy all data)

# Default target
.DEFAULT_GOAL := help
