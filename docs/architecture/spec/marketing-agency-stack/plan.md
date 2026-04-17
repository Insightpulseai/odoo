# Implementation Plan — Marketing Agency Stack

> **Status:** Draft
> **Date:** 2026-03-25

---

## Workstreams

### WS1: OCA Agency Baseline (no dependencies)

Verify and install core + OCA modules for agency operations on Odoo 18.0.

| Step | Module | Action |
|---|---|---|
| 1.1 | `crm` (core) | Verify installed, test lead/opportunity flow |
| 1.2 | `project` (core) | Verify installed, test task/stage flow |
| 1.3 | `hr_timesheet` (core) | Verify installed, test entry/approval |
| 1.4 | `mass_mailing` (core) | Verify installed, test list/campaign |
| 1.5 | `contract` (OCA) | Check 19.0 branch, test install, verify recurring invoice |
| 1.6 | `hr_timesheet_sheet` (OCA) | Check 19.0 branch, test install |
| 1.7 | `project_template` (OCA) | Check 19.0 branch, test install |
| 1.8 | OCA CRM extensions | Evaluate `crm_lead_scoring`, `crm_deduplicate` for 19.0 |

**Exit criteria:** All modules install clean on `test_agency_baseline` DB.

---

### WS2: Foundry Agent Overlay (depends on Foundry operational)

Define and implement Pulser tools for agency-specific workflows.

| Step | Tool | Description |
|---|---|---|
| 2.1 | `generate_creative_brief` | Generate brief from campaign strategy + client brand profile |
| 2.2 | `summarize_campaign_performance` | Aggregate metrics from performance snapshots |
| 2.3 | `alert_utilization_threshold` | Flag team members approaching billable capacity |
| 2.4 | Tool contract registration | Add to `ssot/contracts/tool_contracts.yaml` |
| 2.5 | Integration test | Verify Foundry → Odoo tool execution round-trip |

**Exit criteria:** Tools registered, callable from Foundry, create draft records in Odoo.

---

### WS3: Entra + M365 Channel Readiness (depends on Entra Phase 0)

| Step | Action |
|---|---|
| 3.1 | Entra Phase 0 complete (tracked in `spec/entra-identity-migration/`) |
| 3.2 | Evaluate Copilot Studio for 2-3 internal agent use cases (HR policy, IT helpdesk, onboarding) |
| 3.3 | Wrap Pulser as custom engine agent via M365 Agents SDK |
| 3.4 | Publish Ask Pulser to Teams channel (requires M365 Copilot licensing) |

**Exit criteria:** Pulser accessible in Teams. Copilot Studio evaluation complete with go/no-go.

---

### WS4: Reporting / Profitability Gap Closure (depends on Databricks SQL Warehouse)

| Step | Action |
|---|---|
| 4.1 | Validate existing DLT pipeline (`marketing_pipeline.sql`) end-to-end |
| 4.2 | Add Gold layer views for WIP, utilization, retainer burn-rate |
| 4.3 | Create Power BI dataset connected to Databricks SQL Warehouse |
| 4.4 | Build profitability dashboard (project margin, team utilization, retainer coverage) |

**Exit criteria:** Power BI dashboard live with Gold layer data.

---

### WS5: Agency Pack Port (depends on WS1 baseline stable)

| Step | Action |
|---|---|
| 5.1 | Dry-run `oca-port origin/18.0 origin/19.0 ipai_marketing_agency_pack` |
| 5.2 | Apply `odoo-bin upgrade_code` (tree→list migration, field renames) |
| 5.3 | Fix Odoo 18 breaking changes (`groups_id` → `group_ids`, Command tuples) |
| 5.4 | Test install on `test_ipai_marketing_agency_pack` |
| 5.5 | Classify test results per testing policy |
| 5.6 | Register in `config/addons.manifest.yaml` |

**Exit criteria:** Module installs and basic CRUD works on 19.0.

---

## Sequencing

```
Phase 0: Entra bootstrap (P0 blocker — separate spec)
    ↓
WS1 (OCA baseline) ←→ WS2 (Foundry tools)     [parallel]
    ↓
WS5 (Agency pack port, depends on WS1)
    ↓
WS3 (M365 channels, depends on Entra)
    ↓
WS4 (Reporting, depends on Databricks)
```

---

*Created 2026-03-25.*
