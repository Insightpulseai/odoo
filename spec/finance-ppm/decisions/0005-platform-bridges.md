# ADR-0005: Platform Bridges

| Field | Value |
|-------|-------|
| **Capability** | Recurrent alerts, BIR form generation, e-filing, AI journal posting, compliance dashboard |
| **Parity target** | Bridge (platform/service substitutes) |
| **Date** | 2026-02-16 |
| **Status** | Accepted |

## Context

Five capabilities in Finance PPM require platform-level services that are
inherently NOT Odoo modules. These are service-based gaps, not module-based gaps.

## Why These Are Bridges, Not Modules

| Capability | Why not a module |
|-----------|-----------------|
| Recurrent alerts | Requires external Slack API integration + cron orchestration outside Odoo |
| BIR form generation | Requires .dat file generation per eBIRForms spec + delivery packaging |
| e-Filing automation | Requires integration with government eFPS/eBIRForms/eAFS portals |
| AI journal posting | Requires external AI API (Claude) — Odoo IAP is EE-only |
| Compliance dashboard | Requires external BI tool (Superset) for SQL-driven KPI views |

Each of these bridges:
1. Runs **outside** the Odoo process
2. Cannot be installed via `ir.module.module`
3. Substitutes a platform-level EE/SAP service, not an installable add-on

## Implementation

All bridges use **n8n workflow orchestration** or **Superset SQL views**:

| Bridge | Implementation | Trigger |
|--------|---------------|---------|
| Recurrent alerts | n8n workflow | Cron 9AM/5PM PHT |
| BIR form generation | n8n workflow | Weekly + Webhook |
| e-Filing automation | n8n workflow | Webhook |
| AI journal posting | n8n workflow + Claude API | Weekday 6AM + Webhook |
| Compliance dashboard | Superset + 11 SQL views | On-demand |

## Bridge Directory

Each bridge has a dedicated folder under `platform/bridges/`:

```
platform/bridges/
├── recurrent-alerts/
├── bir-form-generation/
├── efiling-automation/
├── ai-journal-posting/
└── compliance-dashboard/
```

## Consequences

- Bridges depend on external services (n8n, Superset, Claude API, Slack)
- Failure of a bridge does not crash Odoo — graceful degradation
- Each bridge must document inputs/outputs/failure modes in its README
- Secrets are managed via n8n credentials, never hardcoded
