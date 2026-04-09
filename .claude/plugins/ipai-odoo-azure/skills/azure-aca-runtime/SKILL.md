---
name: azure-aca-runtime
description: Manage Azure Container Apps runtime for Odoo 18 on ACA
triggers:
  - keywords: ["container app", "ACA", "revision", "scale", "ingress", "health probe"]
layer: B-platform
---

# Azure Container Apps Runtime Skill

When working with ACA for Odoo:

1. Environment: `ipai-odoo-dev-env` in `rg-ipai-dev-odoo-runtime` (southeastasia)
2. Static IP: `57.155.216.101` (Front Door origin)
3. Container apps: `ipai-odoo-dev-web` (8069), `ipai-odoo-dev-worker`, `ipai-odoo-dev-cron`
4. Registry: `ipaiodoodevacr.azurecr.io`
5. Health probe: `/web/health` (HTTP, port 8069)
6. Min replicas: web=1, worker=1, cron=1 (never scale to zero for stateful Odoo)
7. Secrets via Key Vault: `ipai-odoo-dev-kv` (managed identity binding)
8. Never expose Odoo longpolling port (8072) externally — internal gevent only
9. Revision mode: single (blue-green via ACA revision management)
10. Logs: `az containerapp logs show --name ipai-odoo-dev-web --resource-group rg-ipai-dev-odoo-runtime`
