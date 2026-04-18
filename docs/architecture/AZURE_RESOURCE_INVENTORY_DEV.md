# Azure Resource Inventory (Dev)

Canonical source: [`platform/ssot/azure/resource-inventory.dev.yaml`](../../platform/ssot/azure/resource-inventory.dev.yaml)

## Notes

- Primary runtime, network, monitoring, storage, and data resources are concentrated in **Southeast Asia**.
- The primary Foundry resource (`ipai-copilot-resource`) is currently an explicit **East US 2 exception**.
- `rg-ipai-dev-odoo-sea` currently acts as a **shared app runtime** resource group for:
  - Odoo
  - Prismalab
  - W9 Studio
  - Website
  - shared ACA environment
- Mailbox authority remains outside Entra:
  - `insightpulseai.com` → Zoho Mail
  - `w9studio.net` → Google Workspace
- Entra remains the workforce/admin/guest/app identity authority.

## Related

- Architectural analysis + planes + cleanup observations: [`ssot/architecture/azure-resource-inventory.yaml`](../../ssot/architecture/azure-resource-inventory.yaml)
- Architecture map: [`ssot/architecture/azure-architecture-center-map.yaml`](../../ssot/architecture/azure-architecture-center-map.yaml)
- Site portfolio: [`ssot/web/site-template-adoption.yaml`](../../ssot/web/site-template-adoption.yaml)
- Identity target: [`ssot/identity/entra_target_state.yaml`](../../ssot/identity/entra_target_state.yaml)
- Production-foundation adoption: [`ssot/governance/production-ai-foundation-adoption.yaml`](../../ssot/governance/production-ai-foundation-adoption.yaml)
