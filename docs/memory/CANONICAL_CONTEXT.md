# CANONICAL_CONTEXT.md — jgtolentino/odoo-ce

> Generated: 2026-01-21 | HEAD: 76c23e3b822fbe5e9ed9854ba8107f24af2bca11 | Branch: claude/memory-bundle-dual-repos-Jj5W5

---

## Identity

| Property | Value |
|----------|-------|
| **Repo URL** | https://github.com/jgtolentino/odoo-ce |
| **Wiki URL** | https://github.com/jgtolentino/odoo-ce/wiki |
| **Default Branch** | main |
| **HEAD Commit** | 76c23e3b822fbe5e9ed9854ba8107f24af2bca11 (provenance only) |

---

## Purpose / Scope

Self-hosted **Odoo 18 Community Edition** + **OCA** stack with InsightPulse AI (IPAI) custom modules for:

- **PH Expense & Travel** — Concur replacement
- **Equipment Booking** — Cheqroom parity
- **Finance Month-End Close** — PH tax filing automation (BIR compliance)
- **Canonical Data Model** — Versioned DBML/ERD/ORM maps with CI drift gates

**Production URL**: https://erp.insightpulseai.com

### Key Constraints (Non-negotiable)

- CE + OCA only (no Enterprise modules, no IAP dependencies)
- No odoo.com upsells (branding/links rewired)
- Self-hosted via Docker/Kubernetes (DigitalOcean supported)
- Deterministic docs + seeds (generated artifacts are versioned + drift-checked)

---

## Runtime & Environments

### Local Dev Runtime

```bash
# Canonical local dev (sandbox)
cd sandbox/dev && docker compose up -d

# Production-connection sandbox (DO Managed Postgres)
cd sandbox/dev && docker compose -f docker-compose.production.yml --env-file .env.production up -d
```

### Production Runtime

- **Platform**: DigitalOcean Droplet (Ubuntu 22.04/24.04)
- **Container Image**: `ghcr.io/jgtolentino/odoo-ce:latest`
- **Database**: PostgreSQL 16 (local container or DO Managed)
- **Reverse Proxy**: Nginx (SSL termination)

```bash
# Production deploy
cd deploy && docker compose -f docker-compose.prod.yml --env-file ../.env up -d
```

### Runtime Requirements

| Component | Version |
|-----------|---------|
| **Python** | 3.10+ (Odoo 18 requirement) |
| **Node.js** | >= 18.0.0 (pnpm workspaces) |
| **PostgreSQL** | 16 (production), 15+ (dev) |
| **Docker** | Latest stable |

---

## Architecture

### Major Components

```
┌─────────────────────────────────────────────────────────────────────┐
│                         InsightPulse AI Stack                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   Mattermost ◄──► n8n ◄──► Odoo CE 18 ◄──► PostgreSQL 16            │
│       │           │            │                                     │
│       │           │            ├── Core (8069)                       │
│       │           │            ├── Marketing (8070)                  │
│       │           │            └── Accounting (8071)                 │
│       │           │                                                  │
│       │           └──────────► Supabase (external integrations)      │
│       │                                                              │
│       └─────────────────────► AI Agents (Pulser, Claude, Codex)     │
│                                                                      │
├─────────────────────────────────────────────────────────────────────┤
│  Superset (BI)  │  Keycloak (SSO)  │  DigitalOcean (Hosting)        │
└─────────────────────────────────────────────────────────────────────┘
```

### Key Directories

| Directory | Role |
|-----------|------|
| `addons/ipai/` | IPAI custom Odoo modules (96 modules) |
| `addons/oca/` | OCA community modules (submodules, not tracked) |
| `apps/` | Node.js applications (pulser-runner, control-room, etc.) |
| `packages/` | Shared Node.js packages (agent-core, github-app, design-tokens) |
| `spec/` | Spec bundles (constitution, PRD, plan, tasks per feature) |
| `scripts/` | Automation scripts (160+ scripts) |
| `deploy/` | Production deployment configs |
| `sandbox/dev/` | Local development compose files |
| `docs/data-model/` | Canonical DBML/ERD/ORM artifacts |
| `.github/workflows/` | CI/CD pipelines (77 workflows) |
| `.claude/` | Claude Code configuration + commands |
| `mcp/servers/` | MCP server implementations |

### Canonical Module Architecture

```
ipai_enterprise_bridge     # Base layer: config, approvals, AI/infra glue
    ├── ipai_scout_bundle  # Retail vertical (POS, inventory, sales)
    └── ipai_ces_bundle    # Creative services vertical (projects, timesheets)
```

**Policy**: Only canonical modules define the platform surface area. Feature modules must be explicitly referenced by a bundle dependency.

---

## CI/CD

### Core Workflows (77 total)

| Workflow | Purpose |
|----------|---------|
| `ci-odoo-ce.yml` | Main guardrails + data-model drift |
| `ci.yml` | General CI checks |
| `all-green-gates.yml` | All gates must pass |
| `spec-kit-enforce.yml` | Spec bundle 4-file structure validation |
| `repo-structure.yml` | Repo tree consistency |
| `infra-validate.yml` | Infrastructure template validation |
| `build-unified-image.yml` | Build unified Docker image |
| `build-seeded-image.yml` | Build pre-seeded image |
| `deploy-odoo-prod.yml` | Odoo production deployment |
| `deploy-production.yml` | General production deployment |
| `auto-sitemap-tree.yml` | Auto-update SITEMAP.md/TREE.md |

### CI Gates (Must Stay Green)

- **Odoo 18 CE / OCA CI** — Lint, static checks, unit tests
- **guardrails** — Block Enterprise modules and odoo.com links
- **repo-structure** — Repo tree in spec.md must match generator
- **data-model-drift** — `docs/data-model/` must match generator output
- **seed-finance-close-drift** — Seed data must match generator output
- **spec-kit-enforce** — Spec bundles must have complete 4-file structure
- **infra-validate** — Infrastructure template validation

---

## Configuration

### Required Environment Variables (from .env.example)

**Database**:
- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- `POSTGRES_MAX_CONNECTIONS`

**Odoo**:
- `ODOO_RC` — Path to odoo.conf
- `ADMIN_PASSWD` — Odoo supermaster password
- `WORKERS`, `MAX_CRON_THREADS`, `DB_MAXCONN`
- `LIMIT_MEMORY_HARD`, `LIMIT_MEMORY_SOFT`
- `LIMIT_TIME_CPU`, `LIMIT_TIME_REAL`
- `LOG_LEVEL`, `DEV_MODE`, `PROXY_MODE`

**Docker**:
- `APP_IMAGE` — Container image (default: `ghcr.io/jgtolentino/odoo-ce`)
- `APP_IMAGE_VERSION` — Image tag (default: `latest`)
- `ODOO_PORT` — Port binding (default: 8069)

**External Integrations** (Supabase, n8n, Mattermost, Mailgun):
- `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`
- `N8N_HOST`, `N8N_PORT`, `N8N_WEBHOOK_URL`
- `MATTERMOST_URL`, `MATTERMOST_WEBHOOK_URL`, `MATTERMOST_BOT_TOKEN`
- `MAILGUN_API_KEY`, `MAILGUN_DOMAIN`, etc.

### Config Files

| File | Purpose |
|------|---------|
| `deploy/odoo.conf` | Production Odoo configuration |
| `deploy/odoo.canonical.conf` | Canonical Odoo config template |
| `.env.example` | Environment variable template |
| `sandbox/dev/.env.example` | Dev environment template |

---

## Data & Storage

### Databases

- **Odoo PostgreSQL** — Local PostgreSQL 16 container (production) or DO Managed
- **Supabase** — External integrations only (n8n workflows, task bus)

**Important**: Odoo uses local PostgreSQL, NOT Supabase for core ERP data.

### Volumes (Docker)

- `odoo-db-data` — PostgreSQL data
- `odoo-filestore` — Odoo attachments/images (persistent)
- `odoo-logs` — Application logs

### Migration Approach

- Schema changes via Odoo module upgrades
- Data model artifacts regenerated via `scripts/generate_odoo_dbml.py`
- Drift gates in CI ensure consistency

---

## Operational Runbooks

### Start/Stop

```bash
# Start stack
cd deploy && docker compose -f docker-compose.prod.yml up -d

# Stop stack
docker compose -f docker-compose.prod.yml down

# View logs
docker compose logs -f odoo
```

### Health Checks

```bash
# Odoo health endpoint
curl -s -o /dev/null -w "%{http_code}" http://localhost:8069/web/health

# PostgreSQL check
docker compose exec db pg_isready -U odoo -d odoo
```

### Install Canonical Modules

```bash
# Install bridge first (required by all bundles)
docker compose exec -T odoo odoo -d odoo_dev -i ipai_enterprise_bridge --stop-after-init

# Install verticals as needed
docker compose exec -T odoo odoo -d odoo_dev -i ipai_scout_bundle --stop-after-init    # Retail
docker compose exec -T odoo odoo -d odoo_dev -i ipai_ces_bundle --stop-after-init      # Creative
```

### Verify Installation

```bash
docker compose exec -T db psql -U odoo -d odoo_dev -c "
SELECT name, state FROM ir_module_module
WHERE name IN ('ipai_enterprise_bridge','ipai_scout_bundle','ipai_ces_bundle')
ORDER BY name;"
```

### Regenerate Data Model

```bash
python scripts/generate_odoo_dbml.py
git diff --exit-code docs/data-model/
```

### Local CI

```bash
./scripts/repo_health.sh       # Check repo structure
./scripts/spec_validate.sh     # Validate spec bundles
./scripts/ci_local.sh          # Run full local CI suite
```

---

## Documentation Inventory

### Wiki Pages

| Page | Description |
|------|-------------|
| `Home.md` | Wiki landing page (minimal) |

### In-Repo Documentation

| Path | Description |
|------|-------------|
| `README.md` | Main project readme with quick start |
| `CLAUDE.md` | Claude Code agent instructions |
| `SANDBOX.md` | Complete sandbox documentation |
| `spec.md` | Project specification |
| `plan.md` | Implementation plan |
| `tasks.md` | Task checklist |
| `docs/data-model/` | DBML, ERD, ORM artifacts |
| `deploy/README.md` | Deployment documentation |
| `deploy/PRODUCTION_SETUP.md` | Production setup guide |
| `deploy/DROPLET_DEPLOYMENT.md` | DigitalOcean droplet deployment |

### Spec Bundles (40+)

Key spec bundles in `spec/`:
- `pulser-master-control` — Master control plane
- `close-orchestration` — Month-end close workflows
- `bir-tax-compliance` — BIR tax compliance
- `expense-automation` — Expense automation
- `ipai-ai-platform` — AI platform core
- `ipai-control-center` — Control center UI
- `odoo-mcp-server` — MCP server integration

Each bundle contains: `constitution.md`, `prd.md`, `plan.md`, `tasks.md`

---

## Open TODOs / Unknowns

- **TODO**: Wiki content is minimal (only Home.md with placeholder text)
- **TODO**: Supabase schema details not captured in this bundle
- **TODO**: MCP server configurations require separate documentation
- **TODO**: n8n workflow templates inventory not captured
- **TODO**: Keycloak SSO integration details not in context bundle

---

## Validation Checklist

| Item | Status | Source File |
|------|--------|-------------|
| Repo URL | Verified | repo.meta |
| Wiki URL | Verified | wiki.pages.txt |
| HEAD commit | Verified | repo.meta |
| Odoo version (18 CE) | Verified | README.md, docker-compose.prod.yml |
| PostgreSQL version (16) | Verified | docker-compose.prod.yml |
| Node.js >= 18 | Verified | package.json |
| Python 3.10+ | Verified | CLAUDE.md, pyproject.toml |
| IPAI module count (96) | Verified | addons/ipai directory listing |
| Workflow count (77) | Verified | .github/workflows directory |
| Spec bundle count (40+) | Verified | spec directory listing |
| Production URL | Verified | README.md |
| Canonical modules | Verified | README.md |
