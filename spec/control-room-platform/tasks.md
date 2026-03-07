# Control Room Platform -- Tasks

> **Version**: 1.0.0
> **Last Updated**: 2026-03-07
> **Total Tasks**: 48
> **Completed**: 6 (W1)
> **Pending**: 42

---

## W1: Spec & Governance (Phase 0)

- [x] W1.1 -- Write `spec/control-room-platform/constitution.md` with 9 non-negotiable rules
- [x] W1.2 -- Write `spec/control-room-platform/prd.md` with 5 use cases and data model
- [x] W1.3 -- Write `spec/control-room-platform/plan.md` with 4-phase rollout and 9 workstreams
- [x] W1.4 -- Write `spec/control-room-platform/tasks.md` (this file) with 48 tasks
- [x] W1.5 -- Write `docs/architecture/CONTROL_ROOM_RUNTIME_STATE.md` with honest activation status
- [x] W1.6 -- Write `docs/governance/repository_taxonomy.yaml` and `repository_taxonomy.schema.json`

---

## W2: KPI Contracts (Phase 0)

- [x] W2.1 -- Define 17 KPIs in `platform/data/contracts/control_room_kpis.yaml`
- [ ] W2.2 -- Validate each KPI has `source`, `target`, `threshold_warn`, `threshold_critical`
- [ ] W2.3 -- Cross-reference KPIs with bounded context ownership in `CANONICAL_ENTITY_MAP.yaml`
- [ ] W2.4 -- Add SQL/API evidence queries for each KPI (document in `evidence` field)
- [ ] W2.5 -- Write KPI contract validation script (`scripts/ci/validate_kpi_contracts.sh`)

---

## W3: Event Contracts (Phase 0)

- [x] W3.1 -- Define 11 events in `platform/data/contracts/control_room_events.yaml`
- [ ] W3.2 -- Validate each event has JSON Schema and `kpi_linkage`
- [ ] W3.3 -- Cross-reference events with existing `ctrl.integration_events` schema
- [ ] W3.4 -- Verify event names follow dot-notation convention (`<domain>.<action>`)
- [ ] W3.5 -- Write event contract validation script (`scripts/ci/validate_event_contracts.sh`)

---

## W4: CI Validators (Phase 0)

- [ ] W4.1 -- Create `scripts/ci/validate_kpi_contracts.sh` -- YAML lint + required fields check
- [ ] W4.2 -- Create `scripts/ci/validate_event_contracts.sh` -- YAML lint + JSON Schema validation
- [ ] W4.3 -- Create `scripts/ci/validate_runtime_state.sh` -- check no overclaiming vs evidence files
- [ ] W4.4 -- Create `scripts/ci/validate_repository_taxonomy.sh` -- YAML against JSON Schema
- [ ] W4.5 -- Add GitHub Actions workflow `.github/workflows/control-room-governance.yml`
- [ ] W4.6 -- Add pre-commit hook for governance YAML linting

---

## W5: Environment Setup (Phase 1)

- [ ] W5.1 -- Create environment variable manifest: list all required env vars per bounded context
- [ ] W5.2 -- Provision Supabase `ctrl.*` schema in staging (extend `spec/integration-control-plane/`)
- [ ] W5.3 -- Provision Odoo `odoo_dev` database with KPI extraction views
- [ ] W5.4 -- Configure Databricks workspace with Unity Catalog schemas (bronze/silver/gold)
- [ ] W5.5 -- Create Azure/Foundry project and register copilot tool definitions
- [ ] W5.6 -- Configure Plane workspace with Control Room project and issue types
- [ ] W5.7 -- Write connection verification script per context (`scripts/verify_connections.sh`)

---

## W6: Odoo Integration (Phase 2)

- [ ] W6.1 -- Create Odoo SQL views for KPI extraction (approval turnaround, expense processing, etc.)
- [ ] W6.2 -- Create `ipai_control_room_kpi` module with cron job for KPI collection
- [ ] W6.3 -- Implement Odoo --> Supabase KPI push via n8n webhook
- [ ] W6.4 -- Create Odoo health check endpoint at `/api/v1/health/control-room`
- [ ] W6.5 -- Write integration test: Odoo KPI push --> Supabase `ctrl.integration_events`

---

## W7: Supabase Integration (Phase 2)

- [ ] W7.1 -- Deploy `ctrl.integration_events` table with RLS and indexes
- [ ] W7.2 -- Deploy `ctrl.kpi_snapshots` table for KPI history storage
- [ ] W7.3 -- Create Edge Function `control-room-event-ingest` for event validation
- [ ] W7.4 -- Create Edge Function `control-room-kpi-query` for KPI retrieval
- [ ] W7.5 -- Write integration test: event ingest --> validation --> storage --> query

---

## W8: Databricks Integration (Phase 2)

- [ ] W8.1 -- Create DLT pipeline: Supabase `ctrl.integration_events` --> bronze table
- [ ] W8.2 -- Create silver table: cleaned and normalized events with entity resolution
- [ ] W8.3 -- Create gold table: KPI aggregations (daily/weekly/monthly)
- [ ] W8.4 -- Create Databricks SQL dashboard for KPI trend visualization

---

## W9: Dashboard & Observability (Phase 2-3)

- [ ] W9.1 -- Design Control Room dashboard wireframe (bounded context inventory view)
- [ ] W9.2 -- Implement dashboard data layer (reads from Supabase `ctrl.*` tables)
- [ ] W9.3 -- Implement KPI threshold alerting (n8n workflow --> Slack notification)
- [ ] W9.4 -- Implement weekly governance report generator (CI job or n8n schedule)
- [ ] W9.5 -- Create runbook for each bounded context (incident response, rollback, escalation)

---

## Summary

| Workstream | Total | Done | Pending | Phase |
|-----------|-------|------|---------|-------|
| W1: Spec & Governance | 6 | 6 | 0 | 0 |
| W2: KPI Contracts | 5 | 1 | 4 | 0 |
| W3: Event Contracts | 5 | 1 | 4 | 0 |
| W4: CI Validators | 6 | 0 | 6 | 0 |
| W5: Environment Setup | 7 | 0 | 7 | 1 |
| W6: Odoo Integration | 5 | 0 | 5 | 2 |
| W7: Supabase Integration | 5 | 0 | 5 | 2 |
| W8: Databricks Integration | 4 | 0 | 4 | 2 |
| W9: Dashboard & Observability | 5 | 0 | 5 | 2-3 |
| **Total** | **48** | **8** | **40** | |
