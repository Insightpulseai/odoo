# Marketing Agency Stack Architecture

> **Date:** 2026-03-25
> **Status:** Target state — implementation not started
> **Relates to:** `spec/marketing-agency-stack/`, `docs/architecture/COPILOT_AGENT_GAP_ANALYSIS.md`

---

## Architecture Principles

This solution has two distinct layers:

1. **Business capability layer (Odoo CE + OCA)**
   - CRM
   - Project delivery
   - Timesheets
   - Recurring contracts / retainers
   - Mass mailing / automation
   - Billing and profitability inputs

2. **AI and orchestration layer (Microsoft stack)**
   - Azure AI Foundry Agent Service for pro-code agent runtime
   - Entra ID for identity, access, and governance
   - Copilot Studio only for low-code departmental agents where speed matters more than deep custom runtime control
   - M365 channel delivery (Teams / Outlook) as the preferred enterprise interaction surface when required
   - Security Copilot deferred unless Defender/Sentinel is adopted

**Rule:** OCA modules provide operational system capability; Foundry/Copilot provide assistance, orchestration, and channel delivery. Do not model Foundry/Copilot as substitutes for core Odoo agency operations.

---

## Target-State Layer Mapping

| Concern | Primary Stack | Notes |
|---|---|---|
| Lead / opportunity / client record | Odoo CE + OCA CRM | System of record |
| Campaign lists / nurture | Odoo CE + OCA mass-mailing + automation | Operational marketing layer |
| Project execution / task delivery | Odoo CE + OCA project | Agency delivery core |
| Timesheets / approvals / billable utilization | Odoo CE + OCA timesheet | Billing-control core |
| Retainers / recurring billing | Odoo CE + OCA contract | Subscription/retainer equivalent |
| Client brand / creative brief / assets | Odoo CE + `ipai_marketing_agency_pack` (port to 19.0) | Custom delta — archived v18.0 exists |
| Content calendar / performance metrics | Odoo CE + `ipai_marketing_agency_pack` (port to 19.0) | Custom delta — archived v18.0 exists |
| Marketing analytics pipeline | Azure Databricks (medallion DLT) | `infra/databricks/pipelines/marketing_pipeline.sql` |
| AI work assistant | Azure AI Foundry Agent Service | Pro-code assistant runtime |
| Low-code departmental agent | Copilot Studio | Optional complement, not primary runtime |
| Identity / governance | Entra ID | P0 dependency for enterprise delivery surface |
| Enterprise chat/email surface | Teams / Outlook / M365 Copilot surfaces | Secondary delivery channel |
| Security operations assistant | Security Copilot | Deferred unless security stack requires it |

---

## OCA Agency Baseline — CE + OCA Module Shortlist

| Capability | OCA Module(s) | Repo | 19.0 Status |
|---|---|---|---|
| CRM pipeline | `crm` (core) | odoo/odoo | Built-in |
| Lead scoring / dedup | `crm_lead_scoring`, `crm_deduplicate` | OCA/crm | Verify 19.0 |
| Project management | `project` (core) | odoo/odoo | Built-in |
| Project templates | `project_template` | OCA/project | Verify 19.0 |
| Timesheets | `hr_timesheet` (core) | odoo/odoo | Built-in |
| Timesheet approval | `hr_timesheet_sheet` | OCA/timesheet | Verify 19.0 |
| Contracts / retainers | `contract` | OCA/contract | Verify 19.0 |
| Mass mailing | `mass_mailing` (core) | odoo/odoo | Built-in |
| Marketing automation | `marketing_automation` (core) | odoo/odoo | Built-in (CE subset) |
| Social publishing | None (CE gap) | — | **Gap** |
| WIP / profitability | None packaged | — | **Gap** (reporting work) |

---

## Known Gaps and Non-Goals

### Known Gaps

- **Social publishing parity** is not fully covered by current CE + OCA stack. Enterprise `social` module has no CE equivalent. Evaluate `ipai_social_bridge` or external API integration.
- **Packaged WIP/profitability parity** should be treated as reporting/modeling work (Databricks Gold/Platinum layer), not assumed from a single addon.
- **M365-native delivery** is not automatic; it depends on Entra setup and explicit channel integration.
- **`ipai_marketing_agency_pack`** exists as v18.0 archive — requires port to 19.0 via `oca-port` workflow.

### Non-Goals

- Do not use Copilot Studio to replace Odoo transactional flows.
- Do not use Foundry agents as the system of record.
- Do not collapse OCA parity planning and Copilot/Foundry planning into a single workstream; they should be tracked separately but integrated at the architecture level.
- Do not invent a single monolithic "marketing agency" module — the v18.0 archive is the delta layer on top of OCA, not a replacement for it.

---

## Workstreams

| WS | Name | Scope | Dependency |
|---|---|---|---|
| WS1 | OCA agency baseline | Verify/port CRM, project, timesheet, contract, mailing modules for 19.0 | None |
| WS2 | Foundry agent overlay | Define Pulser tools for agency workflows (brief generation, campaign summary, utilization alerts) | Foundry Agent Service operational |
| WS3 | Entra + M365 channel readiness | Entra bootstrap (P0), Teams channel for Pulser, Copilot Studio eval | Entra Phase 0 complete |
| WS4 | Reporting / profitability gap closure | Databricks Gold layer for WIP, utilization, profitability dashboards | Databricks SQL Warehouse |
| WS5 | Agency pack port | Port `ipai_marketing_agency_pack` from 18.0 to 19.0 | WS1 baseline stable |

---

## References

- Archived module: `archive/addons/ipai_marketing_agency_pack/`
- Databricks pipeline: `infra/databricks/pipelines/marketing_pipeline.sql`
- Marketing analytics: `docs/architecture/marketing_analytics_reference_model.md`
- Copilot gap analysis: `docs/architecture/COPILOT_AGENT_GAP_ANALYSIS.md`
- Entra spec: `spec/entra-identity-migration/`
- Integration doctrine: memory `project_azure_integration_doctrine.md`

---

*Generated 2026-03-25. OCA parity and Microsoft AI concerns are separate workstreams integrated at this architecture level.*
