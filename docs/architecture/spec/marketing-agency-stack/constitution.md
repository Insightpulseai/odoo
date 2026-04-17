# Constitution — Marketing Agency Stack

> Governance principles for the marketing agency capability build.

---

## Principles

1. **Two-layer separation.** OCA modules provide operational business capability. Microsoft AI stack provides assistance, orchestration, and channel delivery. These are separate workstreams integrated at the architecture level.

2. **OCA-first for operations.** CRM, project, timesheet, contract, mailing — use CE core + OCA before custom `ipai_*` modules. The archived `ipai_marketing_agency_pack` is the delta layer, not a replacement.

3. **Foundry-first for agents.** Azure AI Foundry Agent Service is the primary pro-code agent runtime. Copilot Studio is an optional low-code complement for simple departmental agents.

4. **Entra gates enterprise delivery.** No M365 channel publishing, no Copilot Studio agents, no Agent 365 governance without Entra ID operational. Entra is a P0 prerequisite.

5. **Agents recommend; Odoo commits.** No Foundry agent directly mutates CRM, project, or accounting records. All writes go through Odoo API tools that create draft records.

6. **No monolithic module.** Do not collapse all agency functionality into a single custom module. Use OCA modules for standard capabilities, `ipai_marketing_agency_pack` for agency-specific delta (brand, brief, asset, approval, calendar, metrics).

7. **Reporting via Databricks.** WIP, utilization, and profitability are reporting/modeling concerns handled in the Databricks Gold/Platinum layer, not packaged as Odoo addons.

8. **Port before rewrite.** The v18.0 `ipai_marketing_agency_pack` must be ported to 19.0 via `oca-port` workflow, not rewritten from scratch.

---

## Authority

| Decision | Owner |
|---|---|
| OCA module selection | OCA governance rules (`.claude/rules/oca-governance.md`) |
| Agent tool contracts | `ssot/contracts/tool_contracts.yaml` |
| Identity architecture | `spec/entra-identity-migration/` |
| Marketing analytics | `docs/architecture/marketing_analytics_reference_model.md` |
| This spec bundle | `docs/architecture/marketing-agency-stack.md` |

---

*Created 2026-03-25.*
