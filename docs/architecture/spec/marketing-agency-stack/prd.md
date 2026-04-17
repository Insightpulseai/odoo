# PRD — Marketing Agency Stack

> **Status:** Draft
> **Date:** 2026-03-25

---

## Problem

Marketing agencies running on Odoo CE need:
- Operational workflow parity with enterprise agency tools (CRM, project delivery, timesheets, retainers, creative production)
- AI-assisted workflows (brief generation, campaign summarization, utilization alerts) without replacing the transactional core
- Enterprise delivery surfaces (Teams, Outlook) for agent interactions

Current state: an archived v18.0 custom module (`ipai_marketing_agency_pack`) with brand, campaign, brief, asset, approval, and calendar models — not yet ported to 19.0. OCA baseline modules not verified for 19.0.

---

## Goals

1. **Agency workflow parity on CE + OCA** — CRM, project, timesheet, contract, mailing verified and operational on Odoo 18.0
2. **Agency-specific delta ported** — `ipai_marketing_agency_pack` ported from 18.0 to 19.0 (brand, brief, asset, approval, calendar, metrics)
3. **Foundry agent overlay** — Pulser tools for agency workflows (brief generation, campaign summary, utilization alerts) via Foundry Agent Service
4. **Entra + M365 readiness** — Identity foundation enabling Teams/Outlook delivery when needed
5. **Reporting gap closure** — WIP, utilization, profitability dashboards via Databricks Gold layer + Power BI

---

## Non-Goals

- No single monolithic "marketing agency module" — use OCA + targeted delta
- No Copilot/Foundry replacement of Odoo transactional flows
- No M365 delivery without Entra operational
- No social publishing parity in first iteration (tracked as known gap)
- No Security Copilot integration (deferred)

---

## User Personas

| Persona | Primary tools | AI assistance |
|---|---|---|
| Account Manager | CRM, project, client brand records | Lead scoring suggestions, campaign summaries |
| Creative Lead | Briefs, assets, approval cycles | Brief generation from strategy docs |
| Project Manager | Project tasks, timesheets, utilization | Utilization alerts, delivery risk flags |
| Finance / Billing | Contracts, invoices, profitability | WIP reports, retainer burn-rate alerts |

---

## Success Criteria

- [ ] OCA baseline modules install and pass tests on Odoo 18.0
- [ ] `ipai_marketing_agency_pack` ported to 19.0, installs clean
- [ ] At least 3 Pulser agency tools defined in `tool_contracts.yaml`
- [ ] Entra Phase 0 complete (prerequisite, tracked in separate spec)
- [ ] Databricks Gold marketing tables queryable via Power BI

---

*Created 2026-03-25.*
