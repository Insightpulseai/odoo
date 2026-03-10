# Enterprise Operating Model

## Purpose

Consolidated anchor document for the InsightPulse AI enterprise operating model.
Links strategic objectives to operational KPIs, repo taxonomy, and system boundaries.

## 5-Layer Org Model

| Layer | Name | Repos / Systems | Purpose |
|-------|------|----------------|---------|
| 1 | Control Plane | `.github`, `ops-platform`, `infra` | Governance, CI/CD, org-wide workflows |
| 2 | Core Runtime | `odoo`, `web`, `lakehouse` | ERP, product surfaces, data/analytics |
| 3 | Shared Systems | `design-system`, `templates`, `agents` | Tokens, scaffolds, agent framework |
| 4 | Planning & Governance | GitHub Projects, ADRs, contracts | Cross-cutting governance surfaces |
| 5 | Archived | (13 archived repos) | No canonical logic; content migrated |

**SSOT**: `ssot/github/desired-end-state.yaml` (`org_layers` section)

## Strategic OKR Framework

| ID | Objective | Key Results Summary |
|----|-----------|-------------------|
| O1 | Governed Engineering Control Plane | Repo taxonomy, GitHub Projects, CI green rate |
| O2 | Odoo as Governed Runtime | EE parity >= 80%, BIR 100%, close < 10 days |
| O3 | Azure-Native AI/Data Maturity | Databricks Phase 1, agent reliability, medallion coverage |

Strategic objectives (A-E) map to operational KPIs (kpi_001 through kpi_017).

**SSOT**: `ssot/governance/enterprise_okrs.yaml`

## System-of-Record Matrix

| Data Domain | System of Record | Read Replicas | Sync Direction | Notes |
|-------------|-----------------|---------------|----------------|-------|
| Finance records | Odoo CE 19 | Databricks (gold) | Odoo -> Databricks | Transactional truth |
| Approvals | Odoo CE 19 | Supabase (events) | Odoo -> Supabase | State machine in Odoo |
| Identity map | Supabase | -- | Supabase <-> all | IdP for cross-system identity |
| Analytics | Databricks | -- | Databricks -> dashboards | Medallion architecture |
| Documents | Plane | -- | Plane -> agents (read) | SoW only, not SoR |
| Workflows | n8n | -- | n8n <-> Odoo/Supabase | Event routing |
| Slack | (interaction surface) | -- | Slack -> n8n -> Odoo | Not a system of record |

**Slack boundary**: Slack is an interaction surface for notifications, approvals, and ChatOps. It is NOT a system of record. All state transitions flow through the integration backbone (n8n -> Odoo/Supabase).

## Roadmap Linking Model

| Surface | Role | Owns |
|---------|------|------|
| Figma | Design & alignment | Visual roadmap, design specs, strategic alignment |
| GitHub Projects | Execution tracking | Sprints, issues, PR linkage, CI status |
| Plane | Statement of Work | Initiatives, epics, work items, SoW contracts |

**Rule**: Plane is SoW-only (never SoR). GitHub is execution truth. Figma is alignment visualization.

## Azure Maturity Benchmark

"SAP-grade operational maturity" means achieving SAP-like operational posture on Azure, not SAP feature parity:

- IaC-defined landing zone (Bicep/Terraform)
- Governed runtime with Unity Catalog and RBAC
- Enterprise identity via Entra ID
- Release evidence and formal contracts
- Integration backbone with audit trail
- Cost governance and FinOps controls

See: `docs/governance/ERP_POSITIONING.md` (SAP maturity framing section)

## Databricks Maturity Progression

| Phase | Name | Status | Trigger |
|-------|------|--------|---------|
| 1 | Shared sandbox | **Active** | -- |
| 2 | Dev/Prod split | Planned | Production data boundaries harden |
| 3 | Full dev/stage/prod | Future | Release promotion model required |

**SSOT**: `ssot/databricks/workspace.yaml` (`maturity_phases` section)

## Bounded Contexts

| Context | System | Source of Truth | Status |
|---------|--------|----------------|--------|
| ERP | Odoo CE 19 | Transactional records | repo-only |
| Control Plane | Supabase | Identity map, sync state | repo-only |
| Intelligence | Databricks | Analytics, forecasts | repo-only |
| Workspace | Plane | Docs, projects | repo-only |
| Automation | n8n | Workflows, events | repo-only |
| Agent Platform | Azure Foundry | Copilot, tools | repo-only |
| Source Control | GitHub | Code, CI/CD | active |

## Canonical References

| Domain | SSOT | Format |
|--------|------|--------|
| Strategic OKRs | `ssot/governance/enterprise_okrs.yaml` | YAML |
| Repo taxonomy (5-layer) | `ssot/github/desired-end-state.yaml` | YAML |
| Plane project taxonomy | `ssot/plane/config.yaml` | YAML |
| Databricks maturity | `ssot/databricks/workspace.yaml` | YAML |
| KPI contracts | `platform/data/contracts/control_room_kpis.yaml` | YAML |
| Event contracts | `platform/data/contracts/control_room_events.yaml` | YAML |
| Entity ownership | `docs/architecture/CANONICAL_ENTITY_MAP.yaml` | YAML |
| Integration boundaries | `docs/architecture/INTEGRATION_BOUNDARY_MODEL.md` | Markdown |
| Operating model spec | `spec/control-room-platform/constitution.md` | Spec Kit |
| Enterprise target state | `spec/enterprise-target-state/` | Spec Kit |
| ERP positioning | `docs/governance/ERP_POSITIONING.md` | Markdown |
