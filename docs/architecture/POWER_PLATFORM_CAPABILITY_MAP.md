# Power Platform Capability Map

Canonical source: [`ssot/governance/power-platform-adoption.yaml`](../../ssot/governance/power-platform-adoption.yaml)

## Purpose

Map Microsoft Power Platform to IPAI's stack: which products we adopt, which we bound, and where the lines sit against Odoo CE, Databricks, and `agent-platform`.

## Power Platform at a glance

| Layer | Members |
|---|---|
| Products | Copilot Studio · Power Apps · Power Automate · Power BI · Power Pages |
| Shared substrate | AI Builder · Connectors · Copilots + Generative AI · Dataverse · Power Fx |
| Admin / engineering layers | Admin center · ALM guide · Guidance center · Extend and develop · Architecture Center · Well-Architected guidance |
| Adjacent ecosystem | Dynamics 365 · Microsoft Azure |

## IPAI adoption per product

| Product | Role in Microsoft's framing | IPAI adoption |
|---|---|---|
| Copilot Studio | AI agent authoring | Bounded — M365-surface agents only; Pulser agents remain on `agent-platform` |
| Power Apps | Business applications (low-code) | Case by case; Odoo CE is the business app SoR |
| Power Automate | Workflow automation | Permitted for M365-centric flows; Azure Logic Apps / Functions remain primary for Odoo lane |
| Power BI | Reporting / semantic consumption | **Primary BI surface** (per `CLAUDE.md` #12) |
| Power Pages | External sites / portals | Not currently adopted — Odoo website + ACA own public surfaces |

## Shared substrate adoption

| Primitive | IPAI adoption |
|---|---|
| AI Builder | Reference only — IPAI AI runtime is Foundry via `agent-platform` |
| Connectors | Adopt for M365 automation; custom connectors allowed for IPAI APIs |
| Copilots + Generative AI | Bounded to the M365 surface |
| Dataverse | Scoped to Power Platform resources; Odoo Postgres = ERP data SoR, Unity Catalog = analytics data SoR |
| Power Fx | Permitted inside Power Apps / Automate only |

## Boundary rules

- **ERP SoR** stays Odoo CE 18 + OCA + `ipai_*`. Power Apps is not an ERP replacement.
- **Analytics engineering** stays Databricks + Unity Catalog. Dataverse is not a replacement.
- **Agent runtime** stays `agent-platform` (MAF on Foundry). Copilot Studio is M365-surface only.
- **Automation runtime** defaults to Azure Logic Apps / Functions. Power Automate is for M365-centric flows.

> [!IMPORTANT]
> When in doubt, prefer Azure-native over Power Platform for IPAI-internal automation.

## Admin + governance layer

Enabled per [`ssot/governance/power-platform-admin-surface.yaml`](../../ssot/governance/power-platform-admin-surface.yaml):

- Power Platform inventory (GA)
- Admin center notifications (preview)
- Admin center announcements (preview)

Enablement runbook: [`docs/runbooks/power-platform-inventory-enablement.md`](../runbooks/power-platform-inventory-enablement.md).

## Well-Architected alignment

Power Platform publishes its own Well-Architected guidance. IPAI aligns primarily to Azure WAF; Power Platform WAF pillars are treated as a subset for resources that live inside Power Platform.

## Non-goals

- Not replacing Odoo CE with Power Apps.
- Not replacing `agent-platform` with Copilot Studio.
- Not replacing Azure Logic Apps / Functions with Power Automate for IPAI-internal flows.
- Not replacing Databricks with Dataverse.
- Not adopting Power Pages before a clear external-portal need arises.

## Related

- [Power Platform adoption SSOT](../../ssot/governance/power-platform-adoption.yaml)
- [Power Platform admin surface SSOT](../../ssot/governance/power-platform-admin-surface.yaml)
- [Enablement runbook](../runbooks/power-platform-inventory-enablement.md)
- [Agent framework adoption](../../ssot/agent-platform/agent_framework_adoption.yaml)
- [Foundry control plane](../../platform/docs/architecture/FOUNDRY_CONTROL_PLANE.md)
