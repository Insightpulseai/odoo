# Documentation Placement Matrix (SSOT)

This file is the single source of truth for which documentation files belong in which repository across the Insightpulseai org (9 active repos). Machine-readable companion: `doc-placement-matrix.yaml`.

---

## Root-Level Files (Required in Every Repo)

| File | Purpose | Required |
|------|---------|----------|
| `README.md` | Repo overview, quick start, badges | Yes |
| `CLAUDE.md` | AI agent instructions, project context | Yes |
| `CONTRIBUTING.md` | Dev workflow, PR conventions, code style | Yes |
| `SECURITY.md` | Vulnerability reporting, disclosure policy | Yes |

---

## Per-Repo Canonical Docs

### `.github` --- Governance (org-wide policies)

**Domain**: `governance`

**Root files**: `README.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `SECURITY.md`

**Architecture docs** (`docs/architecture/`):

| File | Purpose |
|------|---------|
| `ORG_GOVERNANCE.md` | Org-wide governance policies, team structure |
| `WORKFLOW_TAXONOMY.md` | GitHub Actions workflow classification |
| `REPO_ROLES.md` | Which repo owns which domain |
| `CI_CD_POLICY_MATRIX.md` | CI/CD policies and gating rules |
| `GITHUB_ENTERPRISE_CONTRACT.md` | GitHub plan features, limits |
| `GOVERNANCE_BRANCH_PROTECTION.md` | Branch protection rules |

---

### `infra` --- Infrastructure

**Domain**: `infrastructure`

**Architecture docs** (`docs/architecture/`):

| File | Purpose |
|------|---------|
| `INFRA_TOPOLOGY.md` | DigitalOcean droplets, networking, DNS |
| `DNS_ARCHITECTURE.md` | Cloudflare DNS, subdomain registry |
| `DOCKER_STACK.md` | Docker compose, container layout |
| `BACKUP_DR.md` | Backup strategy, disaster recovery runbook |
| `ENVIRONMENTS.md` | Dev/staging/prod environment definitions |
| `DEPLOY_TARGET_MATRIX.md` | Where each service deploys to |
| `CONNECTION_MATRIX.md` | Service-to-service connectivity |

---

### `ops-platform` --- Control Plane

**Domain**: `control-plane`

**Architecture docs** (`docs/architecture/`):

| File | Purpose |
|------|---------|
| `OPS_PLATFORM_ARCH.md` | Ops console architecture |
| `MONITORING.md` | Monitoring stack (Prometheus, Grafana) |
| `ALERTING.md` | Alert rules and notification channels |
| `OPS_ADVISOR_CONTRACT.md` | Ops advisor system contract |
| `PLATFORM_RUNTIME_STATE.md` | Runtime state tracking |

---

### `odoo` --- ERP (monorepo, retains most docs)

**Domain**: `erp`

**Architecture docs** (`docs/architecture/`):

| File | Purpose |
|------|---------|
| `ODOO_MODULE_HIERARCHY.md` | Module dependency tree |
| `EE_PARITY_MATRIX.md` | Enterprise parity tracking |
| `EE_PARITY_POLICY.md` | Parity development policy |
| `OCA_WORKFLOW.md` | OCA module management |
| `OCA_HYDRATION.md` | OCA git-aggregator workflow |
| `OCA_REPO_INTAKE_MATRIX.md` | OCA repo selection criteria |
| `ODOO_EDITIONS_SSOT.md` | CE vs EE edition rules |
| `ODOO_TEST_STRATEGY.md` | Testing conventions |
| `ODOO_SEMANTIC_LINT.md` | Semantic linting rules |
| `ODOO_SH_EQUIVALENT.md` | Self-hosted Odoo.sh replacement |
| `MODULE_DECISION_RUBRIC.md` | Build vs OCA vs config rubric |
| `ADDONS_PATH_INVARIANTS.md` | Addons path rules |
| `ADDONS_STRUCTURE_BOUNDARY.md` | Addons directory layout |
| `CANONICAL_RUNTIME_IMAGE.md` | Docker image specification |
| `DATABASES_AND_ROLES.md` | PostgreSQL databases and roles |
| `N8N_AUTOMATION_CONTRACT.md` | n8n workflow contracts |
| `AUTOMATION_AUDIT_TRAIL.md` | Automation audit logging |
| `SECRETS_POLICY.md` | Secrets management policy |
| `SSOT_BOUNDARIES.md` | SSOT domain boundaries |
| `MONOREPO_CONTRACT.md` | Monorepo rules and structure |
| `PLATFORM_REPO_TREE.md` | Platform file tree (SSOT map) |
| `CANONICAL_ENTITY_MAP.md` | Entity naming canonical map |
| `CANONICAL_MONOREPO_LAYOUT.md` | Directory layout rules |
| `CANONICAL_URLS.md` | URL naming conventions |
| `ROOT_ALLOWLIST.md` | Allowed root-level files |
| `REPO_LAYOUT.md` | Detailed repo structure |
| `REPO_MAP.md` | Repo navigation map |
| `ORG_REPO_SSOT_MAP.md` | Org repo SSOT assignments |
| `INTEGRATION_BOUNDARY_MODEL.md` | Integration boundaries |
| `INTEGRATIONS_SURFACE.md` | Integration surface area |
| `SOW_BOUNDARY.md` | Scope of work boundaries |
| `VENDOR_SUBTREE_ISOLATION.md` | Vendor code isolation |

---

### `web` --- Web/CMS

**Domain**: `web`

**Architecture docs** (`docs/architecture/`):

| File | Purpose |
|------|---------|
| `WEB_CMS_STRATEGY.md` | Web presence strategy (Next.js + Odoo) |
| `VERCEL_DEPLOYMENT.md` | Vercel deployment patterns |
| `VERCEL_MONOREPO_CONTRACT.md` | Vercel monorepo rules |

---

### `lakehouse` --- Data Platform

**Domain**: `data-platform`

**Architecture docs** (`docs/architecture/`):

| File | Purpose |
|------|---------|
| `MEDALLION_ARCH.md` | Bronze/Silver/Gold/Platinum architecture |
| `ETL_PIPELINES.md` | ETL pipeline inventory |
| `DATABRICKS_ARCHITECTURE.md` | Databricks workspace design |
| `SUPERSET.md` | Apache Superset BI configuration |

---

### `design-system` --- Design System

**Domain**: `design-system`

**Architecture docs** (`docs/architecture/`):

| File | Purpose |
|------|---------|
| `TOKEN_PIPELINE.md` | Figma to tokens to code pipeline |
| `COMPONENT_CATALOG.md` | Component inventory and usage |
| `FIGMA_INTEGRATION_SURFACE.md` | Figma MCP and dev mode |

---

### `agents` --- AI Agents

**Domain**: `agents`

**Architecture docs** (`docs/architecture/`):

| File | Purpose |
|------|---------|
| `AGENT_TAXONOMY.md` | Agent classification and capabilities |
| `MCP_ARCHITECTURE.md` | MCP server registry and protocol |
| `PULSER_SYSTEM.md` | Pulser orchestration design |
| `AI_PROVIDER_BRIDGE.md` | AI provider abstraction layer |
| `AGENT_RUNTIMES.md` | Agent runtime environments |
| `AGENTIC_CODING_CONTRACT.md` | Agentic coding rules |
| `SLACK_AGENT_CONTRACT.md` | Slack agent integration |
| `GRAPHRAG_CONTRACT.md` | GraphRAG implementation |
| `CONTROL_ROOM_RUNTIME_STATE.md` | Control room state |

---

### `templates` --- Templates

**Domain**: `templates`

**Architecture docs** (`docs/architecture/`):

| File | Purpose |
|------|---------|
| `TEMPLATE_CATALOG.md` | Available templates and usage |

---

## Placement Rules

### Directory Conventions

| Path | Purpose | Format |
|------|---------|--------|
| Repo root | Essential project files | `README.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `SECURITY.md` |
| `docs/architecture/` | Architecture decision records and system design | `UPPER_SNAKE_CASE.md` |
| `docs/ai/` | AI agent reference docs (odoo repo only) | `UPPER_SNAKE_CASE.md` |
| `spec/<slug>/` | Feature spec bundles | `constitution.md`, `prd.md`, `plan.md`, `tasks.md` |
| `.claude/rules/` | Agent behavior overrides | `kebab-case.md` |
| `ssot/` | SSOT data files | YAML/JSON only, never `.md` |
| `docs/evidence/20YY*/` | Timestamped evidence bundles | Never SSOT |
| `docs/contracts/` | Cross-domain contracts | `<NAME>_CONTRACT.md` |

### Naming Rules

- Architecture docs: `UPPER_SNAKE_CASE.md` (e.g., `DNS_ARCHITECTURE.md`)
- Spec directories: `kebab-case` (e.g., `spec/close-orchestration/`)
- SSOT data: `snake_case.yaml` or `snake_case.json`

### What Stays in `odoo` (Monorepo)

The `odoo` repo is the monorepo SSOT and retains:

- All Odoo-specific docs (modules, OCA, parity, testing)
- Cross-cutting architecture docs (SSOT boundaries, monorepo contract)
- Integration boundary docs (how services connect)
- All `docs/ai/` reference docs
- All `spec/` bundles
- All `ssot/` data files

### What Moves to Domain Repos

Each domain repo owns docs about its primary concern:

- `infra` owns infrastructure, DNS, Docker, backups
- `agents` owns agent taxonomy, MCP, Pulser
- `.github` owns governance, CI/CD policy, branch protection
- `ops-platform` owns monitoring, alerting, ops console
- `web` owns web/CMS strategy, Vercel deployment
- `lakehouse` owns medallion architecture, ETL, Superset
- `design-system` owns tokens, components, Figma integration
- `templates` owns template catalog

Actual file moves are tracked in `PLACEMENT_AUDIT.yaml` and executed in separate PRs.

---

## Machine-Readable Companion

See `doc-placement-matrix.yaml` for CI-parseable version of this matrix.
