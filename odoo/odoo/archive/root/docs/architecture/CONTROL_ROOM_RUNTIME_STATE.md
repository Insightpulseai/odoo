# Control Room -- Runtime Activation State

> **Last Updated**: 2026-03-07
> **Governance**: `spec/control-room-platform/constitution.md`
> **Rule**: No overclaiming. Every state claim must be backed by evidence.

---

## Summary

All 7 bounded contexts are at **repo-only** activation state. Specs and contracts exist in the repository. No runtime services are deployed. No production traffic is flowing.

| Bounded Context | State | Health | Last Verified |
|----------------|-------|--------|--------------|
| Odoo ERP | `repo-only` | unknown | 2026-03-07 |
| Supabase | `repo-only` | unknown | 2026-03-07 |
| Databricks | `repo-only` | unknown | 2026-03-07 |
| Plane | `repo-only` | unknown | 2026-03-07 |
| n8n | `repo-only` | unknown | 2026-03-07 |
| Azure/Foundry | `repo-only` | unknown | 2026-03-07 |
| GitHub | `repo-only` | unknown | 2026-03-07 |

---

## Per-Context Detail

### 1. Odoo ERP

**State**: `repo-only`

**What exists**:
- Spec bundles: `spec/odoo-approval-inbox/`, `spec/odoo-bir-filing-control/`, `spec/odoo-ap-invoice-control/`, `spec/odoo-tne-control/`
- Custom modules: 43 `ipai_*` modules in `addons/ipai/`
- KPI contracts: 6 KPIs defined (kpi_001 through kpi_006) in `platform/data/contracts/control_room_kpis.yaml`
- Event contracts: 4 events (approval, expense, close task, BIR filing) in `platform/data/contracts/control_room_events.yaml`
- Entity ownership: defined in `docs/architecture/CANONICAL_ENTITY_MAP.yaml`

**What is missing**:
- Runtime KPI extraction SQL views
- `ipai_control_room_kpi` module (not yet scaffolded)
- Health check endpoint for Control Room specifically
- Cron job for KPI collection
- Connection to Supabase `ctrl.*` for event push
- Evidence of any deployed service

**Promotion criteria to `configured`**:
- Odoo `odoo_dev` database accessible with KPI extraction views
- Environment variables for Supabase connection provisioned
- Connection verification script passes

---

### 2. Supabase

**State**: `repo-only`

**What exists**:
- Spec bundle: `spec/integration-control-plane/` (constitution, prd, plan, tasks)
- Schema design: `ctrl.identity_map`, `ctrl.entity_links`, `ctrl.sync_state`, `ctrl.integration_events`
- Entity map: `docs/architecture/CANONICAL_ENTITY_MAP.yaml` defines Supabase as integration hub
- Architecture: `docs/architecture/SUPABASE_CONTROL_PLANE.md`
- KPI contracts: 2 KPIs defined (kpi_012, kpi_013)
- Event contract: `evt_008` (sync.completed)

**What is missing**:
- `ctrl.*` schema deployed to Supabase instance (`spdtwktxdalcfigzeqrz`)
- RLS policies applied
- Edge Functions for event ingest and KPI query
- `ctrl.kpi_snapshots` table (not yet designed)
- Migration files in `supabase/migrations/`
- Evidence of schema deployment

**Promotion criteria to `configured`**:
- `ctrl.*` schema created in staging
- RLS policies applied
- Service role key verified (by name, not value)
- Connection verification script passes

---

### 3. Databricks

**State**: `repo-only`

**What exists**:
- Spec bundle: `spec/databricks-apps-control-room/` (constitution, prd, plan, tasks)
- Architecture: Connector Control Room for 5 data sources
- Entity map: Databricks defined as read-only consumer in `CANONICAL_ENTITY_MAP.yaml`
- KPI contracts: 2 KPIs defined (kpi_016, kpi_017)
- Anti-pattern rule: "Never write back to Databricks source systems"

**What is missing**:
- Databricks workspace provisioned for IPAI
- Unity Catalog schemas (bronze, silver, gold)
- DLT pipelines for event/KPI ingestion
- Streamlit Control Room app
- SQL dashboards for KPI trends
- Evidence of workspace access

**Promotion criteria to `configured`**:
- Databricks workspace accessible
- Unity Catalog schema created
- Service principal configured
- Connection verification script passes

---

### 4. Plane

**State**: `repo-only`

**What exists**:
- Spec bundle: `spec/odoo-workspace-os/` (constitution, prd, plan, tasks)
- Entity map: Plane owns projects, issues, cycles in `CANONICAL_ENTITY_MAP.yaml`
- Sync rules: `plane_to_odoo` defined in entity map

**What is missing**:
- Plane workspace provisioned for Control Room project
- API key configured
- n8n webhook for Plane --> Supabase sync
- Issue types and labels for Control Room governance
- Evidence of workspace access

**Promotion criteria to `configured`**:
- Plane workspace accessible with API key
- Control Room project created
- Connection verification script passes

---

### 5. n8n

**State**: `repo-only`

**What exists**:
- Workflow templates in `n8n/` directory
- Architecture: n8n is self-hosted at `n8n.insightpulseai.com` (for other use cases)
- KPI contracts: 2 KPIs defined (kpi_010, kpi_011)
- Event contracts: `evt_006` (workflow.executed)

**What is missing**:
- Control Room-specific workflows (KPI push, event routing, alerting)
- n8n credentials for Supabase `ctrl.*` access
- Workflow execution history specific to Control Room
- Evidence of Control Room workflows deployed

**Promotion criteria to `configured`**:
- n8n instance accessible at `n8n.insightpulseai.com`
- Supabase credentials provisioned in n8n
- Control Room workflow templates imported (not yet activated)

---

### 6. Azure/Foundry

**State**: `repo-only`

**What exists**:
- Spec bundle: `spec/odoo-copilot-azure/` (constitution, prd, plan, tasks)
- KPI contracts: 2 KPIs defined (kpi_014, kpi_015)
- Event contract: `evt_007` (agent.tool.invoked)

**What is missing**:
- Azure AI Foundry project provisioned
- Copilot tool registrations
- MCP tool definitions for Control Room queries
- Agent action definitions for remediation workflows
- Evidence of project access

**Promotion criteria to `configured`**:
- Azure AI Foundry project created
- Service principal configured
- Tool definitions registered
- Connection verification script passes

---

### 7. GitHub

**State**: `repo-only`

**What exists**:
- Repository: `Insightpulseai/odoo` (active, 153 workflows)
- Repository: `Insightpulseai/ipai-odoo-refactor` (this repo, spec planning)
- CI workflows in `.github/workflows/`
- KPI contract: `kpi_013` (deployment frequency)
- Event contracts: `evt_009` (escalation.triggered), `evt_011` (deployment.completed)

**What is missing**:
- CI workflow for Control Room governance validation (`control-room-governance.yml`)
- Pre-commit hooks for governance YAML linting
- Automated weekly governance report
- Evidence of governance CI running

**Promotion criteria to `configured`**:
- Governance CI workflow committed and passing
- Pre-commit hooks installed
- Repository taxonomy validated by CI

---

## State Transition Log

| Date | Context | From | To | Evidence | Actor |
|------|---------|------|----|----------|-------|
| 2026-03-07 | all | (none) | repo-only | Spec bundle committed | Platform team |

---

## Honest Assessment

As of 2026-03-07:

1. **No runtime services exist** for the Control Room Platform. All artifacts are specifications and contracts.
2. **Odoo ERP is running** at `erp.insightpulseai.com` for other workloads, but no Control Room-specific KPI extraction or event push is configured.
3. **Supabase instance exists** at `spdtwktxdalcfigzeqrz` for other use cases, but the `ctrl.*` schema has not been deployed.
4. **n8n is running** at `n8n.insightpulseai.com` for other workflows, but no Control Room workflows are deployed.
5. **GitHub Actions run** on the repositories, but no governance-specific validators exist yet.
6. **Databricks, Plane, and Azure/Foundry** have no provisioned resources for Control Room.

The next milestone is completing Phase 0 (CI validators) to ensure governance enforcement before any runtime deployment begins.

---

## Cross-References

- `spec/control-room-platform/constitution.md` -- Promotion state machine rules
- `spec/control-room-platform/plan.md` -- Phase definitions and exit criteria
- `platform/data/contracts/control_room_kpis.yaml` -- KPI definitions
- `platform/data/contracts/control_room_events.yaml` -- Event definitions
- `docs/governance/repository_taxonomy.yaml` -- Repository inventory
