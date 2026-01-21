# InsightPulse AI Platform - Makefile
# Multi-tenant Odoo + Supabase + Superset orchestration
# Dev server orchestration for cloud IDEs (Claude Code Web, Codex, Figma Make)

.PHONY: help provision-tbwa provision-tenant test-connection
.PHONY: dev dev-minimal dev-full dev-frontend dev-backend dev-stop dev-status dev-health

# Default target
help:
	@echo "InsightPulse AI Platform - Make Targets"
	@echo "========================================"
	@echo ""
	@echo "Dev Server (Cloud IDE):"
	@echo "  make dev                    Start default dev server (Odoo Core)"
	@echo "  make dev-minimal            Start minimal stack (Postgres + Odoo Core)"
	@echo "  make dev-full               Start full stack (all services)"
	@echo "  make dev-frontend           Start Control Room frontend (port 3000)"
	@echo "  make dev-backend            Start Control Room API (port 8789)"
	@echo "  make dev-stop               Stop all dev services"
	@echo "  make dev-status             Show running services"
	@echo "  make dev-health             Run health checks on all services"
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

# =============================================================================
# Odoo Schema Mirror Pipeline
# =============================================================================
.PHONY: odoo-schema-export odoo-supabase-sync odoo-dbml-generate odoo-erd-generate
.PHONY: odoo-schema-pipeline odoo-schema-validate test-odoo-schema-pipeline

# Export Odoo schema to JSON artifact
odoo-schema-export:
	@echo "📤 Exporting Odoo schema..."
	@if [ -z "$$ODOO_DB_HOST" ]; then \
		echo "❌ ODOO_DB_HOST not set. See odoo-schema-mirror/.env.example"; \
		exit 1; \
	fi
	@python3 odoo-schema-mirror/export_odoo_schema.py
	@echo "✅ Schema exported to odoo-schema-mirror/artifacts/odoo_schema.json"

# Generate Supabase migration from Odoo schema
odoo-supabase-sync:
	@echo "🔄 Syncing schema to Supabase..."
	@if [ -z "$$SUPABASE_DB_URL" ]; then \
		echo "❌ SUPABASE_DB_URL not set. See odoo-schema-mirror/.env.example"; \
		exit 1; \
	fi
	@if [ ! -f "odoo-schema-mirror/artifacts/odoo_schema.json" ]; then \
		echo "❌ No schema artifact found. Run 'make odoo-schema-export' first"; \
		exit 1; \
	fi
	@python3 odoo-schema-mirror/sync_to_supabase.py
	@echo "✅ Migration generated in supabase/migrations/odoo_mirror/"
	@echo ""
	@echo "To apply migration:"
	@echo "  supabase db push"
	@echo "  OR: psql \$$SUPABASE_DB_URL -f <migration_file>"

# Apply generated migrations to Supabase
odoo-supabase-apply:
	@echo "📥 Applying shadow schema migrations to Supabase..."
	@if [ -z "$$SUPABASE_DB_URL" ]; then \
		echo "❌ SUPABASE_DB_URL not set"; \
		exit 1; \
	fi
	@for file in supabase/migrations/odoo_mirror/*.sql; do \
		if [ -f "$$file" ]; then \
			echo "Applying $$file..."; \
			psql "$$SUPABASE_DB_URL" -f "$$file" || exit 1; \
		fi; \
	done
	@echo "✅ Shadow schema migrations applied"

# Generate DBML from Supabase schema
odoo-dbml-generate:
	@echo "📊 Generating DBML..."
	@if [ -z "$$SUPABASE_DB_URL" ]; then \
		echo "❌ SUPABASE_DB_URL not set"; \
		exit 1; \
	fi
	@python3 odoo-schema-mirror/generate_dbml.py
	@echo "✅ DBML generated at docs/dbml/odoo_supabase_schema.dbml"

# Install DBML tools (Node.js required)
odoo-erd-install:
	@echo "📦 Installing DBML/ERD tools..."
	@cd tools/dbml && npm install
	@echo "✅ DBML tools installed"

# Generate ERD from DBML (requires Node.js and installed tools)
odoo-erd-generate:
	@echo "🖼️  Generating ERD diagrams..."
	@if [ ! -f "docs/dbml/odoo_supabase_schema.dbml" ]; then \
		echo "❌ No DBML file found. Run 'make odoo-dbml-generate' first"; \
		exit 1; \
	fi
	@if [ ! -d "tools/dbml/node_modules" ]; then \
		echo "⚠️  DBML tools not installed. Running 'make odoo-erd-install' first..."; \
		$(MAKE) odoo-erd-install; \
	fi
	@cd tools/dbml && npm run erd:all
	@echo "✅ ERD diagrams generated:"
	@echo "   - docs/erd/odoo_supabase_schema.svg"
	@echo "   - docs/erd/odoo_supabase_schema.png"

# Validate DBML syntax
odoo-dbml-validate:
	@echo "✔️  Validating DBML..."
	@if [ ! -f "docs/dbml/odoo_supabase_schema.dbml" ]; then \
		echo "❌ No DBML file found"; \
		exit 1; \
	fi
	@cd tools/dbml && npm run dbml:validate
	@echo "✅ DBML is valid"

# Validate schema parity between Odoo and Supabase
odoo-schema-validate:
	@echo "🔍 Validating schema parity..."
	@python3 odoo-schema-mirror/validate_parity.py

# Full pipeline: export → sync → dbml → erd
odoo-schema-pipeline:
	@echo "🚀 Running full Odoo schema pipeline..."
	@echo ""
	$(MAKE) odoo-schema-export
	@echo ""
	$(MAKE) odoo-supabase-sync
	@echo ""
	$(MAKE) odoo-supabase-apply
	@echo ""
	$(MAKE) odoo-dbml-generate
	@echo ""
	$(MAKE) odoo-erd-generate
	@echo ""
	@echo "🎉 Pipeline complete!"
	@echo ""
	@echo "Artifacts:"
	@echo "  - odoo-schema-mirror/artifacts/odoo_schema.json"
	@echo "  - supabase/migrations/odoo_mirror/*.sql"
	@echo "  - docs/dbml/odoo_supabase_schema.dbml"
	@echo "  - docs/erd/odoo_supabase_schema.svg"
	@echo "  - docs/erd/odoo_supabase_schema.png"

# Run tests for the schema pipeline
test-odoo-schema-pipeline:
	@echo "🧪 Running schema pipeline tests..."
	@python3 -m pytest odoo-schema-mirror/tests/ -v --tb=short
	@echo "✅ All tests passed"

# CI-friendly pipeline (for GitHub Actions)
odoo-schema-pipeline-ci:
	@echo "🤖 Running CI schema pipeline..."
	@if [ "$$ODOO_SCHEMA_PIPELINE_ENABLED" = "false" ]; then \
		echo "⏭️  Pipeline disabled via ODOO_SCHEMA_PIPELINE_ENABLED"; \
		exit 0; \
	fi
	$(MAKE) odoo-schema-pipeline
	$(MAKE) odoo-schema-validate || true

# =============================================================================
# Dev Server Orchestration (Cloud IDE Support)
# =============================================================================
# Unified dev server targets for Claude Code Web, Codex, Figma Make, and CI runners
# Config: devserver.config.json

# Default dev server (Odoo Core + Postgres)
dev:
	@echo "🚀 Starting default dev server (Odoo Core)..."
	@echo ""
	@if [ -f "docker-compose.yml" ]; then \
		docker compose up -d postgres; \
		sleep 3; \
		docker compose up odoo-core; \
	else \
		echo "❌ docker-compose.yml not found"; \
		exit 1; \
	fi

# Minimal stack (Postgres + Odoo Core only)
dev-minimal:
	@echo "🚀 Starting minimal stack..."
	@echo "   Services: postgres, odoo-core"
	@echo "   Ports: 5432, 8069"
	@echo ""
	docker compose up -d postgres
	@sleep 3
	docker compose up -d odoo-core
	@echo ""
	@echo "✅ Minimal stack started"
	@echo "   Odoo:     http://localhost:8069"
	@echo "   Postgres: localhost:5432"

# Full stack (all services)
dev-full:
	@echo "🚀 Starting full stack..."
	@echo "   Services: postgres, odoo-core, odoo-marketing, odoo-accounting, n8n"
	@echo "   Ports: 5432, 8069, 8070, 8071, 5678"
	@echo ""
	docker compose up -d
	@echo ""
	@echo "✅ Full stack started"
	@echo "   Odoo Core:       http://localhost:8069"
	@echo "   Odoo Marketing:  http://localhost:8070"
	@echo "   Odoo Accounting: http://localhost:8071"
	@echo "   n8n:             http://localhost:5678"
	@echo "   Postgres:        localhost:5432"

# Control Room frontend (Next.js)
dev-frontend:
	@echo "🚀 Starting Control Room frontend..."
	@echo "   Port: 3000"
	@echo ""
	@if command -v pnpm &> /dev/null; then \
		pnpm install --filter control-room; \
		pnpm --filter control-room dev; \
	elif command -v npm &> /dev/null; then \
		cd apps/control-room && npm install && npm run dev; \
	else \
		echo "❌ pnpm or npm not found"; \
		exit 1; \
	fi

# Control Room API (FastAPI)
dev-backend:
	@echo "🚀 Starting Control Room API..."
	@echo "   Port: 8789"
	@echo ""
	@if [ -d "apps/control-room-api" ]; then \
		cd apps/control-room-api && \
		pip install -r requirements.txt 2>/dev/null || pip3 install -r requirements.txt 2>/dev/null || true && \
		uvicorn app:app --reload --host 0.0.0.0 --port 8789; \
	else \
		echo "❌ apps/control-room-api not found"; \
		exit 1; \
	fi

# Stop all dev services
dev-stop:
	@echo "🛑 Stopping dev services..."
	@if [ -f "docker-compose.yml" ]; then \
		docker compose down; \
	fi
	@echo "✅ Dev services stopped"

# Show running services status
dev-status:
	@echo "📊 Dev Services Status"
	@echo "======================"
	@echo ""
	@if [ -f "docker-compose.yml" ]; then \
		docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"; \
	else \
		echo "No docker-compose.yml found"; \
	fi
	@echo ""
	@echo "Port Check:"
	@for port in 8069 8070 8071 5678 3000 8789 5432; do \
		if nc -z localhost $$port 2>/dev/null; then \
			echo "  ✅ Port $$port: OPEN"; \
		else \
			echo "  ⚪ Port $$port: closed"; \
		fi; \
	done

# Health checks for all services
dev-health:
	@echo "🏥 Running health checks..."
	@echo ""
	@echo "Odoo Core (8069):"
	@curl -sf http://localhost:8069/web/health && echo "  ✅ Healthy" || echo "  ❌ Unhealthy or not running"
	@echo ""
	@echo "Odoo Marketing (8070):"
	@curl -sf http://localhost:8070/web/health && echo "  ✅ Healthy" || echo "  ❌ Unhealthy or not running"
	@echo ""
	@echo "Odoo Accounting (8071):"
	@curl -sf http://localhost:8071/web/health && echo "  ✅ Healthy" || echo "  ❌ Unhealthy or not running"
	@echo ""
	@echo "n8n (5678):"
	@curl -sf http://localhost:5678/healthz && echo "  ✅ Healthy" || echo "  ❌ Unhealthy or not running"
	@echo ""
	@echo "Control Room (3000):"
	@curl -sf http://localhost:3000/ >/dev/null && echo "  ✅ Healthy" || echo "  ❌ Unhealthy or not running"
	@echo ""
	@echo "Control Room API (8789):"
	@curl -sf http://localhost:8789/health && echo "  ✅ Healthy" || echo "  ❌ Unhealthy or not running"
	@echo ""
	@echo "MCP Coordinator (8766):"
	@curl -sf http://localhost:8766/health && echo "  ✅ Healthy" || echo "  ❌ Unhealthy or not running"
