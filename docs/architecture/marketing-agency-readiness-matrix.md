# Marketing Agency Stack + Foundry Readiness Matrix

> **Date:** 2026-03-25
> **Parent:** `docs/architecture/marketing-agency-stack.md`

---

## OCA Capability Readiness

| Capability | Module | Status | Action |
|---|---|---|---|
| CRM pipeline | `crm` (core) | Ready | Built-in CE |
| Lead management | `crm` + OCA extensions | Verify | Check 19.0 OCA CRM repos |
| Project management | `project` (core) | Ready | Built-in CE |
| Project templates | `project_template` (OCA) | Verify | Test install on 19.0 |
| Timesheets | `hr_timesheet` (core) | Ready | Built-in CE |
| Timesheet approval | `hr_timesheet_sheet` (OCA) | Verify | Test install on 19.0 |
| Contracts / retainers | `contract` (OCA) | Verify | Test install on 19.0 |
| Mass mailing | `mass_mailing` (core) | Ready | Built-in CE |
| Marketing automation | `marketing_automation` (core) | Partial | CE subset only |
| Social publishing | None | **Gap** | Bridge module or external API |
| WIP / profitability | None packaged | **Gap** | Databricks reporting layer |
| Client brand mgmt | `ipai_marketing_agency_pack` | Archive (v18.0) | Port to 19.0 |
| Creative briefs | `ipai_marketing_agency_pack` | Archive (v18.0) | Port to 19.0 |
| Asset versioning | `ipai_marketing_agency_pack` | Archive (v18.0) | Port to 19.0 |
| Approval cycles | `ipai_marketing_agency_pack` | Archive (v18.0) | Port to 19.0 |
| Content calendar | `ipai_marketing_agency_pack` | Archive (v18.0) | Port to 19.0 |
| Performance metrics | `ipai_marketing_agency_pack` | Archive (v18.0) | Port to 19.0 |

---

## Microsoft AI / Control-Plane Readiness

| Capability | Platform | Status | Blocker |
|---|---|---|---|
| Pro-code agent runtime | Azure AI Foundry Agent Service | **Aligned** | None — operational |
| LLM inference | Azure OpenAI (`oai-ipai-dev`) | **Aligned** | None — deployed |
| Identity / SSO | Entra ID | **P0 prerequisite** | Phase 0 not started (77 tasks) |
| M365 delivery surface | Teams / Outlook / M365 Copilot | **Planned** | Entra + M365 Agents SDK + licensing |
| Low-code agents | Copilot Studio | **Optional** | Entra + evaluation needed |
| Agent governance | Agent 365 | **Watchlist** | Preview only |
| Security assistant | Security Copilot | **Deferred** | No Defender/Sentinel active |
| Marketing analytics | Databricks (DLT pipeline) | **Active** | SQL Warehouse + Power BI |
| BI / dashboards | Power BI | **Planned** | Not yet deployed |

---

## Readiness Summary

```
OCA Agency Baseline
  Ready:    4 capabilities (CRM, project, timesheet, mailing)
  Verify:   4 capabilities (OCA extensions for 19.0)
  Gap:      2 capabilities (social publishing, WIP/profitability)
  Port:     6 capabilities (ipai_marketing_agency_pack v18.0 → 19.0)

Microsoft AI Stack
  Aligned:  2 capabilities (Foundry, Azure OpenAI)
  Blocked:  1 capability (Entra — P0)
  Planned:  3 capabilities (M365, Power BI, Copilot Studio)
  Deferred: 2 capabilities (Security Copilot, Agent 365)
```

---

## Critical Path

```
Entra Phase 0 (P0 blocker)
    ↓
OCA 19.0 verification (WS1) ←→ Foundry agent tools (WS2) [parallel]
    ↓
Agency pack port (WS5, depends on WS1)
    ↓
M365 channel + Copilot Studio eval (WS3, depends on Entra)
    ↓
Databricks reporting gap closure (WS4)
```

---

*Generated 2026-03-25.*
