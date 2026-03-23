# InsightPulseAI Odoo Monorepo

[![odoo-ci](https://github.com/Insightpulseai/odoo/actions/workflows/ci-odoo.yml/badge.svg)](https://github.com/Insightpulseai/odoo/actions/workflows/ci-odoo.yml)

## Repo Metadata

- **Status:** Active
- **Class:** Transitional Odoo-led platform monorepo
- **Tier:** Tier 0 / production-critical
- **Primary Role:** Canonical repository for the Odoo ERP runtime layer, while still temporarily hosting cross-domain platform artifacts pending decomposition
- **Primary Owner Team:** erp + platform-core
- **Lifecycle:** Production / Canonical
- **Current Constraint:** Repository still contains shared platform, infra, automation, agent, and web artifacts that are planned to move to their owning repositories over time

---

## Canonical unified baseline

The canonical operating model is:

- **Azure** = cloud/runtime/control access
- **Azure DevOps** = planning/governance spine (one project: `ipai-platform`)
- **GitHub** = current engineering truth until deliberate Azure Repos cutover
- **Repo SSOT files** = intended-state truth
- **IaC / migrations / pipelines / tests** = executable truth

Canonical naming (retire aliases):

| Canonical | Retire |
|---|---|
| `platform` | `ops-platform` |
| `design` | `design-system` |
| `data-intelligence` | `lakehouse` |

Canonical local runtime:

- Docker context: `colima-odoo`
- Runtime source: repo-root `docker-compose.yml`
- Devcontainer is tooling-only, never runtime authority
- Databases: `odoo_dev`, `odoo_staging`, `odoo`

Any competing name, runtime lane, or ownership surface is considered transitional or deprecated and must not gain new authority.

## Canonical product target

The canonical desired end state is defined in [`docs/architecture/INSIGHTPULSEAI_ODOO_ON_AZURE_TARGET_STATE.md`](./docs/architecture/INSIGHTPULSEAI_ODOO_ON_AZURE_TARGET_STATE.md):

- Odoo 19 as the transactional system of record
- Odoo Copilot as the user-facing ERP copilot
- Foundry Agent Applications as the governed AI runtime
- Document Intelligence as the OCR and structured extraction layer
- Azure landing zones, Entra, and Azure DevOps/GitHub as the operating backbone

---

## Canonical Required End State (Hard Rules)

The platform architecture is built on five mandatory execution lanes and a formal SaaS operating model:

1.  **Azure SaaS Workload Documentation**: The **canonical top-level design framework** for the platform. All design areas (IAM, Networking, Data, DevOps, etc.) must map to this authority.
2.  **Odoo Integration Lane (n8n)**: n8n is the **required** integration and workflow orchestration layer. Not for CDC.
3.  **Odoo Analytics Lane (Fabric Mirroring)**: Fabric mirroring is the **required** native landing path for Azure PostgreSQL/Odoo analytics.
4.  **Databricks Lane (Unity Catalog)**: Databricks + Unity Catalog is the **required** mandatory data-engineering and governed lakehouse plane.
5.  **Power BI Lane**: Power BI is the **required** primary business-consumption surface, connected live to Unity Catalog.
6.  **Supabase Lane (supabase/etl)**: Self-hosted `supabase/etl` is the **required** CDC path for Supabase data.

> [!IMPORTANT]
> **Databricks is the engineering authority.** Fabric is a complementary mirroring and semantic-consumption layer. The `data-intelligence` directory is the single code authority for all Databricks and lakehouse artifacts.
>
> Refer to the [Go-Live Checklist](file:///Users/tbwa/Documents/GitHub/Insightpulseai/docs/architecture/GO_LIVE_CHECKLIST.md) for mandatory release gates.

---

## Agent platform architecture

The agent platform follows two mandatory design lenses:

1. **Component model**
   - Frontend/app surface
   - Agent runtime/framework
   - Tool layer
   - Memory/state layer
   - Model/runtime layer
   - Coordination layer

2. **Execution model**
   - Sequential orchestration for deterministic multi-step enterprise workflows
   - Concurrent orchestration for parallel specialist analysis
   - Maker-checker/group-chat orchestration for review and quality gates
   - Handoff orchestration for dynamic specialist routing
   - Magentic orchestration only for open-ended adaptive planning

### Hard rules

- MCP is the required interoperability contract for reusable tools across agents.
- Production agents must externalize durable state; critical process state must not live only in agent memory.
- Do not use agentic workflows for simple deterministic tasks that are better served by fixed workflows or single calls.

---

## Actual Current State

This repository currently contains:

- Odoo CE/OCA/IPAI runtime artifacts
- ERP deployment/config/runtime contracts
- shared infra and deployment assets
- Supabase/platform artifacts
- agent/runbook/registry assets
- automation assets
- platform app artifacts
- web/public surface artifacts
- design assets

This means the repository is **currently broader than a pure ERP runtime repo**.

> **This is intentionally NOT structured like upstream `odoo/odoo`.**
> Upstream places CE addons directly under `/addons/`. We separate three addon stacks
> to enforce OCA-first parity, restrict `ipai_*` to integration bridges, and maintain
> deterministic deploy + CI governance. See [REPO_LAYOUT.md](docs/architecture/REPO_LAYOUT.md).

### What counts as an "integration bridge"?

If it talks to something **outside Odoo** (daemon, cloud API, hardware, queue) → it is a bridge (`addons/ipai/`).
If it extends **Odoo business logic** or replaces EE features → it must be CE or OCA (`addons/oca/`).

**Production URL:** https://erp.insightpulseai.com
**Documentation:** https://insightpulseai.github.io/odoo/

---

## Target State

The intended end state is:

- `odoo` repo owns ERP runtime, addons, Odoo config, ERP deployment contracts, ERP SSOT
- `platform` repo owns OdooOps console and platform admin apps
- `infra` repo owns cloud/network/edge/IaC
- `web` repo owns apex/public marketing surfaces
- `agents` repo owns shared agent/skill/runbook assets
- `automations` repo owns shared workflow assets
- `design` repo owns shared design assets/tokens
- `data-intelligence` repo owns Databricks/lakehouse analytics
- `docs` repo owns cross-platform documentation

Until decomposition is completed, this repository remains the authoritative source of truth for the ERP runtime layer.

---

## Canonical runtime contract

### Local runtime
- **Compose file:** `docker-compose.yml`
- **Docker context:** `colima-odoo`
- **Database:** `odoo_dev`
- **Config:** `config/dev/odoo.conf`

### Staging runtime
- **Runtime surface:** Azure Container Apps
- **Database:** `odoo_staging`
- **Config:** `config/staging/odoo.conf`

### Production runtime
- **Runtime surface:** Azure Container Apps
- **Database:** `odoo`
- **Config:** `config/prod/odoo.conf`

### Runtime image

| Property | Value |
|----------|-------|
| Image | `ipai-odoo-runtime` |
| Base | `odoo:19` (Odoo Community Edition) |
| Dockerfile | [`docker/Dockerfile.unified`](docker/Dockerfile.unified) |
| GHCR | `ghcr.io/insightpulseai/ipai-odoo-runtime` |

The runtime contract is:

- **CE 19 base** — official Odoo Community Edition Docker image
- **OCA for parity** — EE-equivalent functionality via OCA modules (`addons/oca/`)
- **`ipai_*` only where required** — integration bridges, external connectors, approved meta-bundles (`addons/ipai/`)
- **Deterministic builds** — images tied to Git commit provenance, Cosign-signed, SBOM-tracked

### Canonical addon layers
- `addons/oca/`
- `addons/ipai/`
- `addons/local/` (minimal only where truly needed)

Historical references such as `odoo_core`, `odoo_stage`, or `odoo_prod` are non-canonical and should be treated as legacy references only. The canonical names are `odoo_dev`, `odoo_staging`, and `odoo` (production).

Full specification: [`docs/architecture/CANONICAL_RUNTIME_IMAGE.md`](docs/architecture/CANONICAL_RUNTIME_IMAGE.md)

---

## Canonical service surfaces

### Current production-critical ERP surface

| Service  | URL                                 | Edge | Success Criteria |
|----------|-------------------------------------|------|------------------|
| ERP      | https://erp.insightpulseai.com      | Azure Front Door | HTTP 200, Odoo login visible |

### Current platform/public surfaces (transitional)

These are hosted in this repo temporarily. They may move to owning repos during decomposition.

| Service  | URL                                 | Edge | Notes |
|----------|-------------------------------------|------|-------|
| Apex     | https://insightpulseai.com          | Azure Front Door | Standalone site, NOT a redirect to ERP |
| Web      | https://www.insightpulseai.com      | Azure Front Door | Redirect to apex or same site |
| n8n      | https://n8n.insightpulseai.com      | Azure Front Door | Automation |
| MCP      | https://mcp.insightpulseai.com      | Azure Front Door | MCP coordination |
| Superset | https://superset.insightpulseai.com | Azure Front Door | BI dashboards |
| OCR      | https://ocr.insightpulseai.com      | Azure Front Door | Document processing |
| Auth     | https://auth.insightpulseai.com     | Azure Front Door | Keycloak (transitional); target: Entra ID |
| Ops      | https://ops.insightpulseai.com      | Azure Front Door | Operations console |
| Plane    | https://plane.insightpulseai.com    | Azure Front Door | Project management |
| Shelf    | https://shelf.insightpulseai.com    | Azure Front Door | Asset management |
| CRM      | https://crm.insightpulseai.com      | Azure Front Door | CRM |

### Environment-specific hostnames (target)

| Service  | Staging | Dev |
|----------|---------|-----|
| ERP      | `erp-staging.insightpulseai.com` | `erp-dev.insightpulseai.com` |
| Auth     | `auth-staging.insightpulseai.com` | `auth-dev.insightpulseai.com` |

### Local development

| Service  | URL |
|----------|-----|
| Odoo     | http://localhost:8069 |
| n8n      | http://localhost:5678 |
| MCP      | http://localhost:8766 |
| Supabase | http://localhost:54321 |

### Edge model

- **Cloudflare** = authoritative DNS only (DNS-only mode for Front Door-backed records)
- **Azure Front Door** = public application edge for all app surfaces
- No direct VM/Container IP A-records in final DNS — all traffic via Azure Front Door
- **Microsoft 365 Agents SDK** is a channel layer, not a replacement for `agent-platform`.
- Mail DNS (`MX`, `SPF`, `DKIM`, `DMARC`, `zoho._domainkey`) always DNS-only, never proxied
- **Zoho** = mail (MX, SPF, DKIM, DMARC)

### Rules

- Do not assume that every listed hostname is owned by the Odoo runtime layer. Only ERP-specific runtime surfaces are canonical to this repository.
- **Do not hardcode URLs** — use `infra/dns/subdomain-registry.yaml` as SSOT
- `.net` domains are deprecated — `.com` only
- Any new subdomain **must be added to SSOT first**

See also:
- `infra/dns/subdomain-registry.yaml` — authoritative DNS SSOT
- `reports/url_inventory.json` — machine-readable inventory

---

## Quick Start

## Local development

### Canonical local runtime

- **File:** `docker-compose.yml`
- **Docker context:** `colima-odoo`
- **Database:** `odoo_dev`

```bash
docker compose up -d
docker compose logs -f odoo
```

### Canonical devcontainer

- **File:** `.devcontainer/docker-compose.devcontainer.yml`
- **Purpose:** editor/tooling shell only
- **Not the runtime contract**

To use: Open in VS Code → Command Palette → "Dev Containers: Reopen in Container"

### Canonical persistent runtime volumes

- `ipai-pgdata`
- `ipai-redisdata`
- `ipai-web-data`

### Canonical bind-mounted runtime inputs

- `config/dev/odoo.conf`
- `addons/oca`
- `addons/ipai`
- `addons/local`

**📖 Full Guide**: See [docs/development/DEV_CONTAINER_GUIDE.md](./docs/development/DEV_CONTAINER_GUIDE.md) for features, troubleshooting, and advanced usage.

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

### SSOT Boundary

This repository is the canonical source of truth for the Odoo ERP runtime layer. It currently also contains cross-domain artifacts from earlier platform consolidation phases — see [Actual Current State](#actual-current-state) and [Target State](#target-state) above.

Target ownership boundaries (decomposition in progress):

- ERP runtime, Odoo config, addon stacks, ERP deployment contracts: `odoo`
- Platform SSOT and admin apps: `platform`
- Databricks/lakehouse analytics and intelligence: `data-intelligence`
- Shared infrastructure and edge: `infra`
- Shared web surfaces and docs sites outside ERP: `web`
- Shared agent/skills/orchestration assets: `agents`
- Shared automation/runbooks: `automations`
- Shared design tokens/components/assets: `design`

### Tranche 1 decomposition lock

The following top-level domains are under active extraction and must not gain new cross-domain ownership inside this repository except for temporary compatibility shims explicitly tracked for removal:

- `infra/` → target repo `infra`
- `platform/` + `ops-platform/` + non-ERP `supabase/` → target repo `platform`
- `agents/` + shared reusable `skills/` → target repo `agents`
- `automations/` → target repo `automations`
- `web/` + `web-site/` + published `docs-site/` → target repo `web`

`odoo` remains authoritative only for ERP runtime concerns: addon stacks, config, docker/runtime, ERP-specific scripts/tests/docs/spec/ssot, and runtime contracts.

See [`ssot/repo/tranche_1_move_plan.yaml`](./ssot/repo/tranche_1_move_plan.yaml) for the full move map, cutover gates, and completion criteria.

---

## Repo Map

**Actual vs target state:** [`docs/architecture/REPO_ACTUAL_VS_TARGET_STATE.md`](./docs/architecture/REPO_ACTUAL_VS_TARGET_STATE.md)
**Ownership boundaries:** [`ssot/repo/ownership-boundaries.yaml`](./ssot/repo/ownership-boundaries.yaml)

### Top-level directories: actual vs target ownership

| Directory | Actual current state | Target owning repo |
|---|---|---|
| `addons/` | Canonical Odoo addon stacks | `odoo` |
| `config/` | Canonical Odoo runtime config | `odoo` |
| `docker/` | Canonical Odoo image/runtime assets | `odoo` |
| `docs/` | Mixed ERP + platform docs | split over time; ERP docs stay in `odoo` |
| `scripts/` | Mixed ERP + platform scripts | split over time; ERP scripts stay in `odoo` |
| `ssot/` | Mixed ERP + platform SSOT | split over time; ERP SSOT stays in `odoo` |
| `spec/` | Spec Kit bundles (mixed ERP + platform) | split over time; ERP specs stay in `odoo` |
| `infra/` | Present here temporarily | `infra` |
| `platform/` | Present here temporarily | `platform` |
| `web/` | Present here temporarily | `web` |
| `agents/` | Primary home for agent personas/skills | `agents` |
| `agent-platform/` | Primary home for agent runtime/orchestration | `agent-platform` |
| `automations/` | Present here temporarily | `automations` |
| `design/` | Present here temporarily | `design` |
| `data-intelligence/` | Primary lakehouse code authority | `data-intelligence` |
| `ops-platform/` | Retired legacy platform surface | `platform` |
| `lakehouse/` | Retired legacy lakehouse surface | `data-intelligence` |
| `odoo/` | Runtime-specific sub-tree | `odoo` |

### OCA Addons (Hydrated)

`addons/oca/` is **generated** by hydrating [`oca-aggregate.yml`](oca-aggregate.yml) (Odoo 19.0 SSOT).
The directory is intentionally empty in git (only a `.gitkeep`) and is populated at
dev/build time via [git-aggregator](https://github.com/acsone/git-aggregator).
Docker Compose mounts it into the container at `/mnt/oca`.

See: [`docs/architecture/OCA_HYDRATION.md`](docs/architecture/OCA_HYDRATION.md)

### Canonical `addons_path` (all environments)

All environments must load addon stacks in this priority order:

1. Odoo CE core (vendor-managed runtime path or `vendor/odoo/addons/`)
2. `addons/oca` — OCA EE-parity modules
3. `addons/ipai` — Integration bridges only
4. `addons/local` — Minimal local overrides (only where truly needed)

> Odoo core/vendor code exists under vendor-managed runtime paths.
> The canonical **extension/governance layers** are `addons/oca`, `addons/ipai`, `addons/local`.
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
- ✅ **Self-hosted** via Docker/Azure Container Apps (Azure-native target)
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
  oca/           # OCA addons (vendored via gitaggregate, see oca-aggregate.yml)
  ipai/          # Integration-bridge connectors only (thin adapters)
  local/         # Minimal local overrides (only where truly needed)
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

## Decomposition Policy

Non-ERP platform artifacts discovered in this repository should be evaluated against the following rule:

- **keep here** if required to build, run, govern, test, or deploy the ERP runtime
- **move out** if the artifact primarily belongs to shared infra, shared agents, shared analytics, or non-ERP product surfaces

Decomposition must be incremental and must not break production runtime, CI contracts, or existing SSOT references.

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

Canonical package classification is maintained in:

- `ssot/odoo/package-classification.yaml`

This file defines:
- canonical install targets
- optional domain packages
- deprecation review policy for unclassified `ipai_*` modules

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

## Quick Start (Production)

Production runtime targets Azure Container Apps behind Azure Front Door.

- **Production URL:** https://erp.insightpulseai.com/web
- **Runtime:** Azure Container Apps (`ca-ipai-dev`)
- **Database:** `odoo`
- **Edge:** Azure Front Door

---

## Quick Start (Local Dev)

```bash
git clone https://github.com/Insightpulseai/odoo.git
cd odoo
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

SMTP credentials are managed via Azure Key Vault (`kv-ipai-dev`). Runtime binding uses managed identity to inject `ZOHO_SMTP_USER` / `ZOHO_SMTP_PASSWORD` as environment variables. See `config/odoo/mail_settings.yaml` for the canonical mail transport contract.

```bash
# Apply settings to database (Azure runtime)
python3 scripts/odoo/apply_settings_as_code.py

# Verify
docker compose exec -T db psql -U odoo -d odoo -c "
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
- **API**: https://plane.insightpulseai.com (Azure Front Door)
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
