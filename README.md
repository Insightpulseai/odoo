# InsightPulseAI Odoo Runtime (CE + OCA + Bridges)

[![odoo-ci](https://github.com/Insightpulseai/odoo/actions/workflows/ci-odoo.yml/badge.svg)](https://github.com/Insightpulseai/odoo/actions/workflows/ci-odoo.yml)

This repository is a **production runtime wrapper** around:

- **Odoo Community Edition (CE)** — base ERP runtime (official `odoo:19` Docker image)
- **OCA addons** — community EE-parity modules (vendored under `addons/oca/`)
- **IPAI integration bridges** — thin connectors to external services only (under `addons/ipai/`)

> **This is intentionally NOT structured like upstream `odoo/odoo`.**
> Upstream places CE addons directly under `/addons/`. We separate three addon stacks
> to enforce OCA-first parity, restrict `ipai_*` to integration bridges, and maintain
> deterministic deploy + CI governance. See [REPO_LAYOUT.md](docs/architecture/REPO_LAYOUT.md).

### What counts as an "integration bridge"?

If it talks to something **outside Odoo** (daemon, cloud API, hardware, queue) → it is a bridge (`addons/ipai/`).
If it extends **Odoo business logic** or replaces EE features → it must be CE or OCA (`addons/oca/`).

Self-hosted **Odoo 19 CE** + **OCA** stack with InsightPulseAI bridges for:
- PH expense & travel management
- Equipment booking & inventory
- Finance month-end close and PH BIR tax filing task automation (Finance PPM)
- Canonical, versioned data-model artifacts (DBML / ERD / ORM maps) with CI-enforced drift gates

**Production URL:** https://erp.insightpulseai.com
**Documentation:** https://insightpulseai.github.io/odoo/

---

## Canonical URLs (SSOT)

This repository uses a **single source of truth** for all service URLs.

**Authoritative reference:**
[`docs/architecture/CANONICAL_URLS.md`](docs/architecture/CANONICAL_URLS.md)

### Production

| Service  | URL                                 | Success Criteria |
|----------|-------------------------------------|------------------|
| ERP      | https://erp.insightpulseai.com      | HTTP 200, Odoo login visible |
| n8n      | https://n8n.insightpulseai.com      | HTTP 200, n8n UI loads |
| MCP      | https://mcp.insightpulseai.com      | `/health` → `{ "status": "ok" }` |
| Superset | https://superset.insightpulseai.com | HTTP 200, login page |
| OCR      | https://ocr.insightpulseai.com      | `/healthz` returns OK |
| Auth     | https://auth.insightpulseai.com     | Supabase auth reachable |
| Web      | https://www.insightpulseai.com      | HTTP 200, marketing site |
| Apex     | https://insightpulseai.com          | Redirects or serves root |

### Staging

| Service  | URL                                     |
|----------|-----------------------------------------|
| ERP      | https://stage-erp.insightpulseai.com    |
| n8n      | https://stage-n8n.insightpulseai.com    |
| MCP      | https://stage-mcp.insightpulseai.com    |
| Superset | https://stage-superset.insightpulseai.com |
| API      | https://stage-api.insightpulseai.com    |
| Auth     | https://stage-auth.insightpulseai.com   |
| OCR      | https://stage-ocr.insightpulseai.com    |

### Local Development

| Service  | URL |
|----------|-----|
| Odoo     | http://localhost:8069 |
| n8n      | http://localhost:5678 |
| MCP      | http://localhost:8766 |
| Supabase | http://localhost:54321 |

### Rules

- **Do not hardcode URLs** outside `CANONICAL_URLS.md`
- `.net` domains are deprecated — `.com` only
- Any new subdomain **must be added to SSOT first**
- CI and audits rely on this mapping

See also:
- `reports/url_inventory.json` — machine-readable inventory
- `docs/architecture/INTEGRATIONS_SURFACE.md`
- `spec/insightpulseai-com/` — Spec Kit bundle

---

## Quick Start

### Option 1: Dev Container (Recommended for Development)

**Fastest way to get started with a fully configured environment:**

1. **Prerequisites**:
   - [VS Code](https://code.visualstudio.com/) + [Remote - Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
   - [Docker Desktop](https://www.docker.com/products/docker-desktop)

2. **Open in Container**:
   ```bash
   # Open workspace
   code odoo.code-workspace

   # Command Palette (Cmd+Shift+P / Ctrl+Shift+P)
   # Select: "Dev Containers: Reopen in Container"

   # Wait for setup (~3-5 minutes first time)
   ```

3. **Verify**:
   - Odoo: http://localhost:8069
   - PostgreSQL: `psql -U odoo -d odoo_dev`
   - Docker access: `docker ps`

**📖 Full Guide**: See [docs/development/DEV_CONTAINER_GUIDE.md](./docs/development/DEV_CONTAINER_GUIDE.md) for features, troubleshooting, and advanced usage.

**What You Get**:
- ✅ **Python 3.12** + dev tools (black, flake8, pytest, pre-commit)
- ✅ **Node.js LTS** + pnpm
- ✅ **Docker-outside-of-Docker** (manage host containers)
- ✅ **2 databases** pre-created (odoo_dev, odoo) — dev and prod names per CLAUDE.md
- ✅ **VS Code extensions** (Python, Docker, Git, AI tools)
- ✅ **Spec Kit** integration
- ✅ **Auto-reload** on code changes

### Option 2: Local Docker Compose

**Manual setup for direct Docker Compose control:**

```bash
# Local dev sandbox (default)
cd sandbox/dev && docker compose up -d

# Prod-connection sandbox (DO Managed Postgres)
cd sandbox/dev && docker compose -f docker-compose.production.yml --env-file .env.production up -d

# Production deploy (droplet only)
cd deploy && docker compose -f docker-compose.prod.yml up -d
```

**📖 Full Guide**: See [SANDBOX.md](./SANDBOX.md) for complete documentation.

---

## SSOT (Single Source of Truth)

**This repository is the canonical Odoo development root.**

- ✅ **Canonical Odoo source:** All Odoo development happens in this repository
- ❌ **No shadow roots:** `work/` is scratch-only and must NOT contain `odoo-ce*`, `odoo/`, or `odoo19/` directories
- ✅ **CI enforcement:** [`repo-structure-guard.yml`](.github/workflows/repo-structure-guard.yml) prevents duplicate odoo roots
- 📖 **Architecture map:** See [`docs/architecture/REPO_SSOT_MAP.md`](./docs/architecture/REPO_SSOT_MAP.md) for canonical locations

**Repository Relationships:**
- `../` — Parent workspace repository
- `./` (this repo) — **Canonical Odoo SSOT**
- `../work/` — Scratch repository (must NOT contain odoo roots)

---

## Repo Map

**Full governance contract:** [`docs/architecture/MONOREPO_CONTRACT.md`](./docs/architecture/MONOREPO_CONTRACT.md)
**Addons boundary rules:** [`docs/architecture/ADDONS_STRUCTURE_BOUNDARY.md`](./docs/architecture/ADDONS_STRUCTURE_BOUNDARY.md)

**Top-level directory guide:**

| Directory | Purpose | Owner Team |
|-----------|---------|------------|
| `addons/odoo/` | CE core addons (upstream mirror, read-only) | Upstream |
| `addons/oca/` | OCA EE-parity addons (vendored via gitaggregate) | OCA/Backend |
| `addons/ipai/` | Integration bridge connectors only (thin adapters) | IPAI/Backend |
| `supabase/` | Control plane SSOT, ops.* tables | Platform/DB |
| `automations/` | n8n workflows, runbooks, audits | DevOps/Automations |
| `infra/` | Cloudflare/DO/Vercel/IaC + drift detection | DevOps/Infra |
| `config/` | Odoo config per environment (dev/staging/prod) | DevOps |
| `docker/` | Docker images, compose templates, entrypoints | DevOps |
| `design/` | tokens.json SSOT + extracted assets | Design/Frontend |
| `agents/` | Agent registry + skills + runbooks | AI/Platform |
| `docs/` | Architecture + contracts + runbooks | All |
| `scripts/` | Repo-wide tooling | All |
| `spec/` | Spec Kit bundles (constitution, prd, plan, tasks) | Architecture/Product |

### OCA Addons (Hydrated)

`addons/oca/` is **generated** by hydrating [`oca-aggregate.yml`](oca-aggregate.yml) (Odoo 19.0 SSOT).
The directory is intentionally empty in git (only a `.gitkeep`) and is populated at
dev/build time via [git-aggregator](https://github.com/acsone/git-aggregator).
Docker Compose mounts it into the container at `/mnt/oca`.

See: [`docs/architecture/OCA_HYDRATION.md`](docs/architecture/OCA_HYDRATION.md)

### Canonical `addons_path` (all environments)

All environments must load the three addon stacks in this priority order:

1. `addons/odoo` — CE core
2. `addons/oca` — OCA EE-parity modules
3. `addons/ipai` — Integration bridges only

> Any new EE-parity functionality must land in **OCA** (preferred) or CE.
> `addons/ipai/*` is reserved for connectors to external bridges
> (OCR, IoT daemons, payment terminals, queues, email gateways, etc.).

**Key boundaries:**
- ✅ Odoo is the SOR for accounting, inventory, posted documents
- ✅ Supabase is the SSOT for ops/control plane, analytics, AI layers
- ❌ `ipai_*` modules must NOT implement EE parity (use OCA instead)
- ❌ No cross-domain writes without audit trail

See [MONOREPO_CONTRACT.md](./docs/architecture/MONOREPO_CONTRACT.md) for:
- Detailed sub-structure standards
- Data flow rules (what talks to what)
- CI invariants and quality gates

---

## Odoo Execution Patterns

**⚠️ Important**: Use the correct execution pattern to avoid errors.

| Command | Status | Notes |
|---------|--------|-------|
| `./scripts/odoo.sh` | ✅ **Recommended** | Auto-detects environment |
| `./odoo-bin` | ✅ Correct | Repo-provided bash wrapper (not upstream `odoo-bin`) |
| `python -m odoo` | ✅ Correct | If `odoo` package installed |
| `python odoo-bin` | ❌ **WRONG** | Results in `SyntaxError` (bash ≠ Python) |

**📖 Full Guide**: See [docs/ODOO_EXECUTION.md](./docs/ODOO_EXECUTION.md) for examples, troubleshooting, and architecture notes.

---

## Key Constraints (Non-negotiable)

- ✅ **CE + OCA only** (no Enterprise modules, no IAP dependencies)
- ✅ **No odoo.com upsells** (branding/links rewired)
- ✅ **Self-hosted** via Docker/Kubernetes (DigitalOcean supported)
- ✅ **Deterministic docs + seeds** (generated artifacts are versioned + drift-checked)

---

<!-- CURRENT_STATE:BEGIN -->

## Current State (Authoritative)

**Canonical IPAI strategy (single-bridge + vertical bundles):**

| Module | Role | Description |
|--------|------|-------------|
| `ipai_enterprise_bridge` | Bridge | Thin cross-cutting layer: config, approvals, AI/infra integration, shared mixins |
| `ipai_scout_bundle` | Vertical | Meta-bundle for Scout retail ops + analytics (depends-only, no business logic) |
| `ipai_ces_bundle` | Vertical | Meta-bundle for CES creative effectiveness ops (depends-only, no business logic) |

**Detected in repo:**

- Canonical modules present: `ipai_enterprise_bridge`
- Other IPAI modules (feature/legacy): 91
- Non-IPAI modules at addons root: 2

**Policy:**
- Only canonical modules define the platform surface area
- Feature modules must be explicitly referenced by a bundle dependency
- Deprecated modules should be moved to `addons/_deprecated/` and blocked by CI

**Install canonical stack:**
```bash
docker compose exec -T odoo odoo -d odoo_dev -i ipai_enterprise_bridge --stop-after-init
docker compose exec -T odoo odoo -d odoo_dev -i ipai_scout_bundle --stop-after-init
docker compose exec -T odoo odoo -d odoo_dev -i ipai_ces_bundle --stop-after-init
```

<!-- CURRENT_STATE:END -->

## Repository Layout (SSOT)

> This repo is a **deployment + governance wrapper**, not a source distribution.
> See [REPO_LAYOUT.md](docs/architecture/REPO_LAYOUT.md) for rationale.

```
addons/
  odoo/          # CE core addons (vendor mirror, read-only)
  oca/           # OCA addons (vendored via gitaggregate, see oca-aggregate.yml)
  ipai/          # Integration-bridge connectors only (thin adapters)
config/
  dev/           # Dev environment Odoo conf
  staging/       # Staging environment Odoo conf
  prod/          # Production environment Odoo conf
docker/          # Images, compose templates, entrypoints
scripts/         # Idempotent lifecycle + install tooling
docs/            # Architecture + ops SSOT
  architecture/  # Canonical contracts and boundary docs
  data-model/    # DBML / ERD / ORM maps + JSON index
spec/            # Spec Kit bundles (constitution, PRD, plan, tasks)
.github/
  workflows/     # CI/CD guardrails + drift gates
```

---

## Strategic Architecture & Decision Frameworks

**Recent Strategic Work** (February 2026):

| Document | Purpose | Key Outcomes |
|----------|---------|--------------|
| [Supabase Prioritization Framework](docs/arch/SUPABASE_PRIMITIVES.md) | 5-criterion rubric for Supabase feature adoption | ✅ High priority (≥4.0): PostgreSQL, RLS, Auth, Vault, Storage, Edge Functions<br>⚠️ Medium (3.0-4.0): Realtime, PostgREST, Monitoring<br>❌ Low (<3.0): Studio UI → use Superset/Plane |
| [Agent Constitution](spec/agent/constitution.md) | Agent execution constraints + governance | ✅ 8 verified capabilities, hard constraints (container/package ops forbidden) |

**Integration Patterns**:
- **Email Notifications (Zoho SMTP)**: Daily digest (08:00 PH) + urgent alerts (<24h); compatible with Microsoft 365/Outlook recipients
- **Plane OKR Tracking**: Bidirectional sync (Odoo ↔ Plane) for BIR compliance management
- **Supabase Decision Rubric**: SoR fit (35%), security (25%), leverage (20%), portability (10%), latency/cost (10%)

---

## Module Architecture

### Canonical Stack (Install These)

The platform surface is defined by **three canonical modules** only:

```
ipai_enterprise_bridge     # Base layer: config, approvals, AI/infra glue
    ├── ipai_scout_bundle  # Retail vertical (POS, inventory, sales)
    └── ipai_ces_bundle    # Creative services vertical (projects, timesheets)
```

Installing a bundle installs all its dependencies transitively.

### Bridge Module

**`ipai_enterprise_bridge`** — Minimal stubs and redirections for EE model references:
- Configuration policies and settings
- Approval tier validation mixins
- AI/infrastructure connector stubs
- Shared security groups

### Vertical Bundles

| Bundle | Focus | CE Modules Included |
|--------|-------|---------------------|
| `ipai_scout_bundle` | Retail ops | `sale_management`, `purchase`, `stock`, `point_of_sale`, `account` |
| `ipai_ces_bundle` | Creative ops | `project`, `hr`, `hr_timesheet`, `mail`, `portal` |

### Feature Modules (Optional)

Feature modules are **not part of the canonical surface**. They must be:
1. Explicitly depended on by a bundle, OR
2. Installed manually for specific use cases

| Category | Examples | Purpose |
|----------|----------|---------|
| Finance | `ipai_finance_ppm`, `ipai_finance_month_end`, `ipai_bir_compliance` | PH tax, month-end close |
| Expense | `ipai_expense`, `ipai_expense_ocr` | PH expense workflows |
| Equipment | `ipai_equipment` | Cheqroom-style booking |
| AI | `ipai_ai_core`, `ipai_ai_agents` | AI platform integrations |
| Branding | `ipai_ce_cleaner`, `ipai_ce_branding` | Remove Enterprise upsells |
| BIR Notifications | `ipai_bir_notifications` | Email alerts (daily digest + urgent) for BIR filing deadlines |
| Plane Integration | `ipai_bir_plane_sync` | Bidirectional OKR sync for BIR compliance tracking |

### Deprecated Modules

Modules that are no longer maintained should be moved to `addons/_deprecated/` and blocked by CI.

---

## Quick Start (Production - DigitalOcean)

Recommended for fresh Ubuntu 22.04/24.04 droplet.

```bash
curl -fsSL https://raw.githubusercontent.com/Insightpulseai/odoo/main/deploy_m1.sh.template -o deploy_m1.sh
chmod +x deploy_m1.sh
sudo ./deploy_m1.sh
```

Access:
- https://erp.insightpulseai.com/web
- Secrets:

```bash
cat /opt/odoo/deploy/.env
tail -f /var/log/odoo_deploy.log
```

---

## Quick Start (Local Dev)

```bash
git clone https://github.com/Insightpulseai/odoo.git
cd odoo
cd deploy
docker compose up -d
docker compose logs -f odoo
```

---

## Install IPAI Modules

### Install canonical stack (recommended)

```bash
# Install bridge first (required by all bundles)
docker compose exec -T odoo odoo -d odoo_dev -i ipai_enterprise_bridge --stop-after-init

# Install verticals as needed
docker compose exec -T odoo odoo -d odoo_dev -i ipai_scout_bundle --stop-after-init    # Retail
docker compose exec -T odoo odoo -d odoo_dev -i ipai_ces_bundle --stop-after-init      # Creative
```

### Install optional feature modules

```bash
# Finance close seed data
docker compose exec -T odoo odoo -d odoo_dev -i ipai_finance_close_seed --stop-after-init

# Other feature modules as needed
docker compose exec -T odoo odoo -d odoo_dev -i ipai_expense --stop-after-init
docker compose exec -T odoo odoo -d odoo_dev -i ipai_equipment --stop-after-init
```

### Verify installation

```bash
docker compose exec -T db psql -U odoo -d odoo_dev -c "
SELECT name, state FROM ir_module_module
WHERE name IN ('ipai_enterprise_bridge','ipai_scout_bundle','ipai_ces_bundle')
ORDER BY name;"
```

---

## Canonical Data Model (DBML / ERD / ORM maps)

Canonical, machine-readable outputs live in:

- `docs/data-model/`
  - `ODOO_CANONICAL_SCHEMA.dbml` — DBML schema for dbdiagram.io
  - `ODOO_ERD.mmd` — Mermaid ER diagram
  - `ODOO_ERD.puml` — PlantUML ER diagram
  - `ODOO_ORM_MAP.md` — ORM map linking models, tables, fields
  - `ODOO_MODULE_DELTAS.md` — Per-module schema deltas
  - `ODOO_MODEL_INDEX.json` — Machine-readable index

Regenerate deterministically:

```bash
python scripts/generate_odoo_dbml.py
git diff --exit-code docs/data-model/
```

---

## Deterministic Seed Generator (from Excel)

If you update the source Excel or want to refresh seed artifacts:

```bash
python scripts/seed_finance_close_from_xlsx.py
git diff --exit-code addons/ipai_finance_close_seed
```

---

## CI/CD Guardrails (What must stay green)

CI enforces:

- **Odoo 19 CE / OCA CI** — Lint, static checks, and unit tests
- **guardrails** — Block Enterprise modules and odoo.com links
- **repo-structure** — Repo tree in spec.md must match generator
- **data-model-drift** — `docs/data-model/` must match generator output
- **seed-finance-close-drift** — `addons/ipai_finance_close_seed` must match `seed_finance_close_from_xlsx.py` output
- **spec-kit-enforce** — Spec bundles must have complete 4-file structure
- **infra-validate** — Infrastructure template validation

### Key workflows:

| Workflow | Purpose |
|----------|---------|
| `ci-odoo.yml` | Main guardrails + data-model drift |
| `repo-structure.yml` | Repo tree consistency |
| `spec-kit-enforce.yml` | Spec bundle validation |
| `infra-validate.yml` | Infrastructure templates |
| `auto-sitemap-tree.yml` | Auto-update SITEMAP.md/TREE.md |

If CI fails, reproduce locally by running the same generator commands + `git diff --exit-code` checks above.

---

## Email Integration

**Production Architecture** (Zoho Mail SMTP):
```
Odoo 19 CE → Zoho Mail SMTP (smtp.zoho.com:587, STARTTLS) → Email delivery
├─ Outbound: ${SMTP_FROM} (configurable via .env)
├─ BIR Notifications: Daily digest (08:00 PH) + urgent alerts (<24h deadline)
└─ External recipients: Microsoft 365/Outlook compatible (one-way notifications)
```

**DNS Status**: ✅ SPF, DKIM, DMARC verified
**Deployment Status**: ✅ DEPLOYED (2026-02-12)

**BIR Email Notifications** (`ipai_bir_notifications` module):
- **Daily Digest** (08:00 PH): Summary of due/overdue/upcoming filings
- **Urgent Alerts** (<24h): Deadline escalations with 4-hour cooldown (idempotency)
- **Configuration**: System parameters + cron jobs
**Settings-as-Code Deployment:**

```bash
# 1. Create secrets file on production
ssh root@178.128.112.214
sudo mkdir -p /opt/odoo/secrets
sudo bash -c 'cat > /opt/odoo/secrets/zoho-mail.env <<EOF
ZOHO_SMTP_SERVER=smtp.zoho.com
ZOHO_SMTP_PORT=587
ZOHO_SMTP_USER=${SMTP_USER}
ZOHO_SMTP_APP_PASSWORD=__REPLACE_WITH_APP_PASSWORD__
ZOHO_SMTP_FROM=${SMTP_FROM}
EOF'
sudo chmod 600 /opt/odoo/secrets/zoho-mail.env

# 2. Apply settings to database
set -a; source /opt/odoo/secrets/zoho-mail.env; set +a
export ODOO_DB=odoo
export PGHOST="odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com"
export PGPORT="25060"
export PGUSER="doadmin"
export PGPASSWORD="__REPLACE__"
cd /opt/odoo
python3 scripts/odoo/apply_settings_as_code.py

# 3. Verify deployment
psql "host=$PGHOST port=$PGPORT user=$PGUSER dbname=$ODOO_DB sslmode=require" -c "
SELECT id, name, smtp_host, smtp_user, smtp_port
FROM ir_mail_server
WHERE name='Zoho Mail SMTP (insightpulseai.com)';"
```

**Documentation**: [docs/guides/email/EMAIL_SETUP_ZOHO.md](docs/guides/email/EMAIL_SETUP_ZOHO.md)

---

## Plane Project Management

**Production Architecture**:
```
Plane Backend (Django/PostgreSQL) → SMTP Email Delivery
Users → https://plane.insightpulseai.com → Nginx → Plane API (port 8002)
Odoo BIR Module ↔ Supabase Edge Function (plane-sync/) ↔ Plane API
```

**Production Status**: ✅ DEPLOYED (Backend: 2026-01-30, BIR Sync: 2026-02-12)
- **API**: http://178.128.112.214:8002
- **Database**: PostgreSQL 15.7-alpine (88 migrations)
- **Workers**: Background + scheduled tasks running
- **BIR Integration**: Bidirectional sync for OKR tracking (`ipai_bir_plane_sync` module)

**BIR Compliance in Plane** (`ipai_bir_plane_sync` module):
- **Sync Strategy**: Odoo `bir.filing.deadline` ↔ Plane tasks via Edge Function
- **Sync Triggers**: Manual button + batch action + automatic updates
- **Field Mapping**: Status, priority, date, labels (OKR hierarchy)
- **Setup**: Bootstrap script at `scripts/plane_bir_bootstrap.sql`

**Plane Integration**: BIR compliance tracking via `ipai_bir_plane_sync` module. See [implementation docs](docs/evidence/20260212-2045/plane-integration/IMPLEMENTATION.md) for project structure details.

**Documentation**:
- [Deployment](docs/evidence/20260130-2014/PLANE_PRODUCTION_DEPLOYMENT.md)
- [BIR Sync](docs/evidence/20260212-2045/plane-integration/IMPLEMENTATION.md)

---

## Docs

- `spec.md` — Project spec / repo snapshot
- `plan.md` — Implementation plan
- `tasks.md` — Task checklist
- `docs/` — Architecture + deployment docs
- `docs/data-model/` — Canonical schema outputs
- `docs/arch/SUPABASE_PRIMITIVES.md` — **Supabase prioritization framework (5-criterion rubric)**
- `spec/agent/constitution.md` — **Agent execution constraints** (defines what agents running in CI/runner environments can and cannot do; not a repo-wide restriction)
- `docs/arch/IDEAL_ORG_ENTERPRISE_REPO_STRUCTURE.md` — Ideal repository structure guide
- `docs/EMAIL_INTEGRATION.md` — Complete email integration guide

---

## License

- IPAI modules: **AGPL-3**
- OCA modules: See each upstream repo/license

---

## Support

- Issues: [GitHub Issues](https://github.com/Insightpulseai/odoo/issues)
- Docs: https://insightpulseai.github.io/odoo/
