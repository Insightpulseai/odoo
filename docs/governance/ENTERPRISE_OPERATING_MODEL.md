# Enterprise Operating Model

## Purpose

Reference document for the InsightPulse AI enterprise operating model.
Execution model details are defined in `spec/control-room-platform/constitution.md`.

## Canonical References

| Domain | SSOT | Format |
|--------|------|--------|
| Operating model | `spec/control-room-platform/constitution.md` | Spec Kit |
| Repository taxonomy | `docs/governance/repository_taxonomy.yaml` | YAML |
| KPI contracts | `platform/data/contracts/control_room_kpis.yaml` | YAML |
| Event contracts | `platform/data/contracts/control_room_events.yaml` | YAML |
| Entity ownership | `docs/architecture/CANONICAL_ENTITY_MAP.yaml` | YAML |
| Integration boundaries | `docs/architecture/INTEGRATION_BOUNDARY_MODEL.md` | Markdown |
| Runtime state | `docs/architecture/CONTROL_ROOM_RUNTIME_STATE.md` | Markdown |

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

## System-of-Record Matrix

| Data Domain | Owner | Read Replicas | Sync Direction |
|-------------|-------|---------------|----------------|
| Finance records | Odoo | Databricks (gold) | Odoo → Databricks |
| Approvals | Odoo | Supabase (events) | Odoo → Supabase |
| Identity map | Supabase | — | Supabase ↔ all |
| Analytics | Databricks | — | Databricks → dashboards |
| Documents | Plane | — | Plane → agents (read) |
| Workflows | n8n | — | n8n ↔ Odoo/Supabase |

## Cross-References

- Canonical entity map: `docs/architecture/CANONICAL_ENTITY_MAP.yaml`
- Integration boundaries: `docs/architecture/INTEGRATION_BOUNDARY_MODEL.md`
- Control Room spec: `spec/control-room-platform/`
