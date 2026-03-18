# Odoo Runtime & Infrastructure

> Canonical Odoo 19 setup, Docker dev contract, database naming, architecture, hosting.

---

## Architecture Overview

```
Slack (SaaS) <--> n8n <--> Odoo CE 19 <--> PostgreSQL 16
                   |          (8069)
                   +--------> Supabase (external integrations only)
                   +--------> AI Agents (Pulser, Claude, Codex)

Edge: Azure Front Door | BI: Superset | SSO: Keycloak | Hosting: Azure ACA
```

## Azure-First Hosting

- **Edge/TLS**: Azure Front Door + WAF (`ipai-fd-dev`) -- sole public edge
- **DNS**: Cloudflare (authoritative DNS only, no proxy/CDN)
- **Compute**: Azure Container Apps (`cae-ipai-dev`, region: `southeastasia`)
- **Database**: Azure Database for PostgreSQL Flexible Server (`ipai-odoo-dev-pg`)
- **BI**: Apache Superset (Azure Container App)
- **SSO**: Keycloak (Azure Container App, transitional -- Entra ID is target)
- **Automation**: n8n (Azure Container App)
- **Supabase**: Self-hosted on Azure VM (`vm-ipai-supabase-dev`) -- exception to managed
- **Chat**: Slack (SaaS)

## Local Dev

- **Odoo CE 19**: Native Mac runtime (`vendor/odoo/odoo-bin`)
- **PostgreSQL 15**: Homebrew native (`localhost:5432`, user: `tbwa`)
- **DB**: `odoo_dev` (local dev only -- never use `odoo` locally)
- **No Docker required** for inner-loop development

## Database Naming (Strict)

| Name | Environment | Notes |
|------|------------|-------|
| `odoo_dev` | Local dev | Native Postgres on Mac |
| `odoo_staging` | Staging | Azure PostgreSQL Flexible Server |
| `odoo` | Production | Azure PostgreSQL Flexible Server |

Never blur `odoo` and `odoo_dev`. Test DBs: `test_<module>` (disposable).

## Canonical Odoo 19 Setup

**Location**: `odoo19/` directory -- recommended for all AI agent operations.

**Philosophy**: Deterministic, single-database, zero-ambiguity configuration.

| Problem | Old Setup | Canonical Setup |
|---------|-----------|----------------|
| AI Agent Commands | 36 possible combinations | 1 deterministic command |
| Database Targets | 4 databases (all deprecated) | 1 database per env: `odoo_dev`, `odoo_staging`, `odoo` |
| Container Names | Custom (odoo-ce-core, odoo-dev) | Project-prefixed (odoo19-web-1, odoo19-db-1) |
| Configuration | Docker volumes (not tracked) | Version-controlled (./config/odoo.conf) |
| Database Selector | Enabled (UI confusion) | Disabled (list_db = False) |

**Key Features**:
- Single database target per environment (`db_name = odoo_dev` / `odoo_staging` / `odoo`)
- No database selector (`list_db = False`)
- File-based secrets (no hardcoded passwords)
- Health checks (PostgreSQL guards web startup)
- No container_name (allows scaling/isolation)
- Idempotent backup script
- Version-controlled config

**Complete Documentation**: `odoo19/CANONICAL_SETUP.md` and `odoo19/QUICK_REFERENCE.md`

## Docker Dev Contract

- **Runtime**: All Docker Odoo dev runs inside `.devcontainer/`. Never on host.
- **Execution**: `scripts/odoo/*.sh` are authoritative. Skills reference them, never replace.
- **Paths**: workspace=`/workspaces/odoo`, odoo=`/opt/odoo`, config=`/etc/odoo/odoo.conf`, db=`db`
- **Testing**: Disposable DB per test (`test_<module>`).
- **Never**: run Odoo on host via Docker, modify `/opt/odoo`, use `odoo_dev`/`odoo_staging`/`odoo` DBs for tests.

## Docker Commands

### Development

```bash
# Start core services
docker compose up -d postgres odoo-core

# Run init profiles (first-time setup)
docker compose --profile ce-init up    # Install CE modules
docker compose --profile init up       # Install IPAI modules

# View logs
docker compose logs -f odoo-core

# Restart service
docker compose restart odoo
```

### Database Access

```bash
# Connect to PostgreSQL
docker compose exec db psql -U odoo -d odoo_dev

# Backup database
docker compose exec db pg_dump -U odoo odoo_dev > backup.sql
```

### Canonical Quick Start

```bash
cd odoo19
docker compose up -d                              # Start stack
docker compose exec -T web odoo -d odoo_dev -i base   # Install module
./scripts/backup_db.sh                            # Backup database
```

## Common Commands

```bash
# Stack management
docker compose up -d                    # Start full stack
docker compose --profile init up        # Run with init profiles
docker compose logs -f odoo-core        # View logs

# Module deployment
./scripts/deploy-odoo-modules.sh        # Deploy IPAI modules

# Testing
./scripts/ci/run_odoo_tests.sh          # Run Odoo unit tests
./scripts/ci_local.sh                   # Run local CI checks

# Verification (always run before commit)
./scripts/repo_health.sh                # Check repo structure
./scripts/spec_validate.sh              # Validate spec bundles
```

---

*Last updated: 2026-03-16*
