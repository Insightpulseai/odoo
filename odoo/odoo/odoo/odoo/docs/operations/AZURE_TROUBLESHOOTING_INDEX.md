# Azure Troubleshooting Index

> Ops knowledge layer for IPAI Odoo ERP SaaS on Azure.
> Only services actively used in our stack are listed.
> Reference: [Azure Troubleshooting Hub](https://learn.microsoft.com/en-us/troubleshoot/azure/)

## Core Runtime

| Service | Troubleshoot Link | Our Usage |
|---------|------------------|-----------|
| Container Apps | [Docs](https://learn.microsoft.com/en-us/troubleshoot/azure/azure-container-apps/) | Odoo web/worker runtime |
| Container Registry | [Docs](https://learn.microsoft.com/en-us/troubleshoot/azure/azure-container-registry/) | Image storage (ACR) |
| PostgreSQL Flexible Server | [Docs](https://learn.microsoft.com/en-us/troubleshoot/azure/azure-database-postgresql/) | Odoo database |

## Networking and Ingress

| Service | Troubleshoot Link | Our Usage |
|---------|------------------|-----------|
| Front Door | [Docs](https://learn.microsoft.com/en-us/troubleshoot/azure/azure-front-door/) | Global ingress + CDN + WAF |
| Virtual Network | [Docs](https://learn.microsoft.com/en-us/troubleshoot/azure/virtual-network/) | Private networking |

## Identity and Secrets

| Service | Troubleshoot Link | Our Usage |
|---------|------------------|-----------|
| Entra ID | [Docs](https://learn.microsoft.com/en-us/troubleshoot/azure/entra/entra-id/) | OIDC + managed identity |
| Key Vault | [Docs](https://learn.microsoft.com/en-us/troubleshoot/azure/key-vault/) | Runtime secrets |

## Observability

| Service | Troubleshoot Link | Our Usage |
|---------|------------------|-----------|
| Azure Monitor | [Docs](https://learn.microsoft.com/en-us/troubleshoot/azure/azure-monitor/) | Metrics + alerts |
| Application Insights | [Docs](https://learn.microsoft.com/en-us/troubleshoot/azure/app-insights/) | APM for Odoo |
| Log Analytics | [Docs](https://learn.microsoft.com/en-us/troubleshoot/azure/log-analytics/) | Centralized logging |

## Optional (If Adopted)

| Service | Troubleshoot Link | Our Usage |
|---------|------------------|-----------|
| Service Bus | [Docs](https://learn.microsoft.com/en-us/troubleshoot/azure/service-bus/) | Async decoupling |
| Function App | [Docs](https://learn.microsoft.com/en-us/troubleshoot/azure/azure-functions/) | Event-driven handlers |
| Databricks | [Docs](https://learn.microsoft.com/en-us/troubleshoot/azure/databricks/) | Analytics/AI plane |

## Common Scenarios

### Image Pull Failures (ACR)
- Verify managed identity has `AcrPull` role on registry
- Check ACR firewall rules if using VNet integration
- Validate image tag exists: `az acr repository show-tags --name <acr> --repository odoo`

### Container App Not Starting
- Check revision logs: `az containerapp logs show --name <app> --resource-group <rg>`
- Verify health probe path `/web/health` is accessible
- Check env vars and secrets are properly configured

### PostgreSQL Connection Issues
- Verify firewall allows Azure services (0.0.0.0 rule)
- Check connection string format: `postgresql://<user>:<pass>@<fqdn>:5432/odoo?sslmode=require`
- Validate max_connections not exhausted

### OIDC Authentication (CI/CD)
- Verify federated credential subject matches: `repo:Insightpulseai/odoo:ref:refs/heads/main`
- Check `id-token: write` permission in workflow
- Validate AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_SUBSCRIPTION_ID secrets

---

*This index covers only services in our stack. For the full Azure troubleshooting catalog, see [Microsoft Learn](https://learn.microsoft.com/en-us/troubleshoot/azure/).*
