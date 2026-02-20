# =============================================================================
# Makefile — Odoo CE 19 Monorepo (Single Command Surface)
# =============================================================================
# Usage: make help
#
# Compose SSOT: docker-compose.yml (root)
# Production:   infra/deploy/docker-compose.prod.yml
# OCA stack:    infra/do-oca-stack/
# =============================================================================

SHELL := /bin/bash
.DEFAULT_GOAL := help
.PHONY: help up down ps logs health init update restart config \
        db-shell db-health redis-health odoo-shell \
        tools ipai-guard parity-seed parity-seed-check \
        oca-aggregate oca-aggregate-single gen-addons-path render-odoo-conf addons-path-check \
        chore lint

# ---------------------------------------------------------------------------
# Stack lifecycle
# ---------------------------------------------------------------------------

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'

up: ## Start Odoo + PG + Redis
	docker compose up -d

down: ## Stop stack
	docker compose down

ps: ## Show running services
	docker compose ps

logs: ## Tail Odoo logs
	docker compose logs -f --tail=200 odoo

restart: ## Restart Odoo (keep PG + Redis)
	docker compose restart odoo

config: ## Validate compose syntax
	@docker compose config >/dev/null && echo "OK: compose config valid"

# ---------------------------------------------------------------------------
# Health checks
# ---------------------------------------------------------------------------

health: ## HTTP health check (Odoo /web/health)
	@curl -fsS -I http://localhost:$${ODOO_PORT:-8069}/web/health | head -5

db-health: ## PostgreSQL readiness check
	@docker exec odoo-db pg_isready -U $${POSTGRES_USER:-odoo} -d $${POSTGRES_DB:-odoo}

redis-health: ## Redis PING check
	@docker exec odoo-redis redis-cli ping

# ---------------------------------------------------------------------------
# Shells
# ---------------------------------------------------------------------------

db-shell: ## Open psql shell in PG container
	docker exec -it odoo-db psql -U $${POSTGRES_USER:-odoo} -d $${POSTGRES_DB:-odoo}

odoo-shell: ## Open Odoo shell (Python REPL with ORM)
	docker compose exec odoo odoo shell --db_host=db --db_user=$${POSTGRES_USER:-odoo} --db_password=$${POSTGRES_PASSWORD:-odoo} -d $${ODOO_DB:-odoo_dev}

# ---------------------------------------------------------------------------
# Module operations (one-shot profiles)
# ---------------------------------------------------------------------------

init: ## Initialize database + install base (one-shot)
	docker compose --profile init up odoo-init

update: ## Update modules (set UPDATE_MODULES=mod1,mod2; default: all)
	UPDATE_MODULES=$${UPDATE_MODULES:-all} docker compose --profile update up odoo-update

# ---------------------------------------------------------------------------
# Tools (optional profile)
# ---------------------------------------------------------------------------

tools: ## Start pgAdmin + Mailpit
	docker compose --profile tools up -d pgadmin mailpit

# ---------------------------------------------------------------------------
# Quality gates
# ---------------------------------------------------------------------------

ipai-guard: ## Validate ipai_* modules against allowlist
	python3 scripts/ci/validate_ipai_custom_modules.py

parity-seed: ## Generate Odoo Editions parity seed (deterministic)
	PARITY_SEED_DETERMINISTIC=1 python3 scripts/gen_odoo_editions_parity_seed.py

parity-seed-check: ## Generate parity seed and check for drift
	PARITY_SEED_DETERMINISTIC=1 python3 scripts/gen_odoo_editions_parity_seed.py
	git diff --exit-code -- spec/parity/odoo_editions_parity_seed.yaml

# ---------------------------------------------------------------------------
# OCA dependencies (git-aggregator)
# ---------------------------------------------------------------------------

oca-aggregate: ## Clone/update all OCA repos (gitaggregate)
	gitaggregate -c oca-aggregate.yml -j 4

oca-aggregate-single: ## Clone/update one OCA repo (OCA_REPO=web)
	gitaggregate -c oca-aggregate.yml -d ./addons/oca/$${OCA_REPO}

# ---------------------------------------------------------------------------
# Addons path (OCA-canonical deterministic enumeration)
# ---------------------------------------------------------------------------

gen-addons-path: ## Regenerate addons-path from addons/oca/<repo>
	./scripts/gen_addons_path.sh

render-odoo-conf: ## Render odoo.conf from template + generated addons-path
	@source infra/odoo/addons-path.env && export ODOO_ADDONS_PATH && \
		envsubst < infra/odoo/odoo.conf.template > infra/odoo/odoo.conf && \
		echo "OK: infra/odoo/odoo.conf rendered"

addons-path-check: ## CI gate: fail if addons-path is stale
	./scripts/gen_addons_path.sh
	git diff --exit-code -- infra/odoo/addons-path.txt infra/odoo/addons-path.env

# ---------------------------------------------------------------------------
# Repo chores (hygiene + drift gates)
# ---------------------------------------------------------------------------

chore: ## Run all repo chores (regen + lint + deprecated check)
	./scripts/chore_repo.sh

lint: ## Run unified lint (python + yaml + markdown)
	./scripts/lint_all.sh
