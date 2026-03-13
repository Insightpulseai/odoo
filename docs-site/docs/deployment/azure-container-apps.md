# Azure Container Apps

Azure Container Apps is the canonical compute runtime for all InsightPulse AI services. Every container app sits behind Azure Front Door for public ingress, TLS termination, and WAF.

## Resource topology

| Property | Value |
|----------|-------|
| **Resource group** | `rg-ipai-dev` |
| **Region** | `southeastasia` |
| **Container Apps environment** | `cae-ipai-dev` |

## Container apps

| Container App | FQDN | Public hostname | Port | Purpose |
|---------------|------|-----------------|------|---------|
| `ipai-odoo-dev-web` | `ipai-odoo-dev-web.thankfulbush-191bdcb0.southeastasia.azurecontainerapps.io` | `erp.insightpulseai.com` | 8069 | Odoo CE 19 ERP |
| `ipai-auth-dev` | `ipai-auth-dev.thankfulbush-191bdcb0.southeastasia.azurecontainerapps.io` | `auth.insightpulseai.com` | -- | Keycloak SSO |
| `ipai-mcp-dev` | `ipai-mcp-dev.thankfulbush-191bdcb0.southeastasia.azurecontainerapps.io` | `mcp.insightpulseai.com` | -- | MCP coordination |
| `ipai-ocr-dev` | `ipai-ocr-dev.thankfulbush-191bdcb0.southeastasia.azurecontainerapps.io` | `ocr.insightpulseai.com` | -- | Document OCR |
| `ipai-superset-dev` | `ipai-superset-dev.thankfulbush-191bdcb0.southeastasia.azurecontainerapps.io` | `superset.insightpulseai.com` | -- | Apache Superset BI |
| `ipai-plane-dev` | `ipai-plane-dev.thankfulbush-191bdcb0.southeastasia.azurecontainerapps.io` | `plane.insightpulseai.com` | -- | Plane project management |

## Azure Front Door

| Property | Value |
|----------|-------|
| **Front Door name** | `ipai-fd-dev` |
| **Endpoint** | `ipai-fd-dev-ep-fnh4e8d6gtdhc8ax.z03.azurefd.net` |
| **Role** | Public ingress, TLS termination, WAF |

Front Door handles:

- Custom domain binding for all `*.insightpulseai.com` subdomains
- Managed TLS certificates with automatic renewal
- WAF policy enforcement
- Origin health probes to each container app

## Scaling

Container Apps use consumption-based scaling. Each app defines min/max replica counts and scaling rules (HTTP concurrency, CPU, or custom metrics). Odoo (`ipai-odoo-dev-web`) scales on HTTP request concurrency.

## Secrets management

All secrets are stored in **Azure Key Vault** (`kv-ipai-dev`). Container apps bind secrets at runtime via managed identity. Never hardcode secrets in container environment variables or image layers.

```
Container App → Managed Identity → Key Vault → env var injection
```

## Deprecated platforms

!!! warning "Deprecated compute platforms"

    | Platform | Status | Date |
    |----------|--------|------|
    | Vercel | Deprecated | 2026-03 |
    | DigitalOcean App Platform | Decommissioned | 2026-03-11 |
    | DigitalOcean Droplet (`178.128.112.214`) | Deleted | 2026-03-11 |

    Azure Container Apps is the only supported compute runtime. Do not deploy to Vercel or DigitalOcean.
