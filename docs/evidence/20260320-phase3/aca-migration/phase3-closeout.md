# Phase 3 Closeout — ACA Runtime Migration

Status: **accepted**

## Completed

- Recreated 12 ACA apps in `rg-ipai-dev-odoo-runtime`
- New ACA environment: `ipai-odoo-dev-env` (domain: `salmontree-b7d27e19.southeastasia.azurecontainerapps.io`)
- New static IP: `57.155.216.101`
- Linked `odoofilestore` Azure Files storage (account: `stipaiodoodev`, share: `odoo-filestore`)
- Cut Front Door origins (10/10) to new ACA FQDNs
- Verified direct ACA and public `/web/health` checks return 200

## Apps Deployed

| App | State | Ingress |
|-----|-------|---------|
| ipai-odoo-dev-web | Succeeded | external:8069 |
| ipai-odoo-dev-worker | Succeeded | none |
| ipai-odoo-dev-cron | Succeeded | none |
| ipai-crm-dev | Succeeded | external:3000 |
| ipai-plane-dev | Succeeded | external:3000 |
| ipai-shelf-dev | Succeeded | external:80 |
| ipai-auth-dev | Succeeded | external:80 |
| ipai-mcp-dev | Succeeded | external:8766 |
| ipai-ocr-dev | Succeeded | external:8000 |
| ipai-superset-dev | Succeeded | external:8088 |
| ipai-website-dev | Succeeded | external:3000 |
| ipai-copilot-gateway | Succeeded | internal:8088 |

## Verification

```
erp.insightpulseai.com/web/health: HTTP 200 (0.488s) — {"status": "pass"}
direct ACA: HTTP 200 (0.227s)
```

## Hold Policy

- Legacy apps in `rg-ipai-dev` remain untouched for 72h stabilization (until 2026-03-23)
- Legacy cleanup in `rg-ipai-agents-dev` may proceed only for non-production debug/init resources
