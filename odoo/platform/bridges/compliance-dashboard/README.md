# Bridge: Compliance Dashboard

> **Type**: Platform bridge (Superset + SQL views)
> **Replaces**: SAP FCC Closing Cockpit dashboard
> **Decision record**: `spec/finance-ppm/decisions/0005-platform-bridges.md`

## Contract

| Field | Value |
|-------|-------|
| **Trigger** | On-demand (Superset auto-refresh) |
| **Input** | PostgreSQL direct query against Odoo database |
| **Output** | 11 SQL views with RAG status indicators |
| **Failure mode** | Superset query timeout. Odoo data unaffected. |

## Views (11)

### Operational (6)
1. `v_closing_task_summary` — Task status by project and stage
2. `v_tax_filing_calendar` — BIR deadline calendar (9 form types)
3. `v_stage_funnel` — Stage transition funnel
4. `v_assignee_workload` — Workload distribution per analyst
5. `v_closing_timeline` — Close cycle timeline
6. `v_finance_team` — Team directory with roles

### Logframe KPIs (5)
7. `v_logframe_goal_kpi` — On-time % with RAG status (Goal)
8. `v_logframe_outcome_kpi` — Avg delay per project (Outcome)
9. `v_logframe_im1_kpi` — Monthly close reconciliation (IM1)
10. `v_logframe_im2_kpi` — BIR filing rate by form type (IM2)
11. `v_logframe_outputs_kpi` — Consolidated output counts

## Required Environment Variables

See `env.example` in this directory.

## Setup

Source: `scripts/dashboard_queries_odoo19.sql`

Execute SQL views against the Odoo PostgreSQL database, then configure
Superset datasets to point at these views.
