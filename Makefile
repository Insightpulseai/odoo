# InsightPulse AI Platform - Makefile
# Multi-tenant Odoo + Supabase + Superset orchestration

.PHONY: help provision-tbwa provision-tenant test-connection

# Default target
help:
	@echo "InsightPulse AI Platform - Make Targets"
	@echo "========================================"
	@echo ""
	@echo "Tenant Provisioning:"
	@echo "  make provision-tbwa         Provision TBWA tenant (shortcut)"
	@echo "  make provision-tenant CODE=<code>  Provision arbitrary tenant"
	@echo ""
	@echo "Database:"
	@echo "  make test-connection        Test Supabase connection"
	@echo "  make migrate                Run Supabase migrations"
	@echo ""
	@echo "Odoo:"
	@echo "  make odoo-start             Start Odoo server"
	@echo "  make odoo-stop              Stop Odoo server"
	@echo "  make odoo-logs              View Odoo logs"
	@echo ""
	@echo "Superset:"
	@echo "  make superset-deploy        Deploy Superset to DO App Platform"
	@echo "  make superset-logs          View Superset logs"
	@echo ""
	@echo "CI/CD:"
	@echo "  make ci-notify-superset     Trigger Superset rebuild"
	@echo ""

# Provision TBWA tenant (shortcut)
provision-tbwa:
	@echo "Provisioning TBWA tenant..."
	@./scripts/provision_tenant.sh tbwa

# Provision arbitrary tenant
provision-tenant:
	@if [ -z "$(CODE)" ]; then \
		echo "Usage: make provision-tenant CODE=<tenant_code>"; \
		exit 1; \
	fi
	@echo "Provisioning tenant: $(CODE)"
	@./scripts/provision_tenant.sh $(CODE)

# Test Supabase connection
test-connection:
	@echo "Testing Supabase connection..."
	@if [ -z "$$POSTGRES_URL" ]; then \
		echo "❌ POSTGRES_URL not set"; \
		exit 1; \
	fi
	@psql "$$POSTGRES_URL" -c "SELECT version();" && echo "✅ Connection successful"

# Run Supabase migrations
migrate:
	@echo "Running Supabase migrations..."
	@if [ -d "supabase/migrations" ]; then \
		for file in supabase/migrations/*.sql; do \
			echo "Applying $$file..."; \
			psql "$$POSTGRES_URL" -f "$$file"; \
		done; \
		echo "✅ Migrations complete"; \
	else \
		echo "⚠️  No migrations directory found"; \
	fi

# Odoo operations
odoo-start:
	@echo "Starting Odoo server..."
	@if command -v docker-compose &> /dev/null && [ -f "docker-compose.yml" ]; then \
		docker-compose up -d odoo; \
	elif command -v odoo-bin &> /dev/null; then \
		odoo-bin -c odoo.conf & \
	else \
		echo "❌ No Odoo installation found"; \
		exit 1; \
	fi

odoo-stop:
	@echo "Stopping Odoo server..."
	@if command -v docker-compose &> /dev/null && [ -f "docker-compose.yml" ]; then \
		docker-compose stop odoo; \
	else \
		killall odoo-bin || echo "Odoo not running"; \
	fi

odoo-logs:
	@if command -v docker-compose &> /dev/null && [ -f "docker-compose.yml" ]; then \
		docker-compose logs -f --tail=100 odoo; \
	else \
		tail -f /var/log/odoo/odoo-server.log; \
	fi

# Superset operations
superset-deploy:
	@echo "Deploying Superset to DigitalOcean App Platform..."
	@if [ -z "$$DOCTL_ACCESS_TOKEN" ]; then \
		echo "❌ DOCTL_ACCESS_TOKEN not set"; \
		exit 1; \
	fi
	@cd ../superset && doctl apps update $${SUPERSET_APP_ID} --spec infra/do/superset-app.yaml
	@cd ../superset && doctl apps create-deployment $${SUPERSET_APP_ID} --force-rebuild

superset-logs:
	@echo "Fetching Superset logs..."
	@if [ -z "$$SUPERSET_APP_ID" ]; then \
		echo "❌ SUPERSET_APP_ID not set"; \
		exit 1; \
	fi
	@doctl apps logs $$SUPERSET_APP_ID --follow

# CI/CD operations
ci-notify-superset:
	@echo "Triggering Superset rebuild..."
	@if [ -z "$$GH_PAT_SUPERSET" ]; then \
		echo "❌ GH_PAT_SUPERSET not set"; \
		exit 1; \
	fi
	@curl -X POST \
		-H "Accept: application/vnd.github+json" \
		-H "Authorization: Bearer $$GH_PAT_SUPERSET" \
		https://api.github.com/repos/jgtolentino/superset/dispatches \
		-d '{"event_type":"schema_changed","client_payload":{"manual_trigger":true}}'
	@echo "✅ Superset rebuild triggered"
