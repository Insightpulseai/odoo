# `infra/azure/` — Canonical Azure IaC

This directory is the single source of truth for Azure infrastructure deployed
to the InsightPulse AI subscriptions. Every Azure resource in production should
have a Bicep definition here.

Companion docs:
- `docs/runbooks/bicep-authoring-standard.md` — authoring + validation + promotion workflow
- `docs/architecture/azure-naming-convention.md` — CAF-aligned naming
- `ssot/governance/tagging-doctrine.yaml` — required/recommended tags (snake_case)
- `platform/contracts/finops/cost-allocation-model.yaml` — allocation dimensions

---

## Contract

Every Azure resource definition in this repo must have:

1. A `main.bicep` or module-level `.bicep` entrypoint under `infra/azure/`.
2. A `.bicepparam` file where environment values differ (dev/staging/prod).
3. No portal-only drift accepted as canonical. If a resource was created in the
   portal, codify it here within the same sprint.

Author in VS Code with the Bicep extension.
Validate with Azure CLI locally.
Promote with Azure Pipelines (`azure-pipelines/templates/bicep-lint-validate.yml`).
Never promote via GitHub Actions (forbidden — CLAUDE.md rev 2026-04-14).

---

## Layout

```
infra/azure/
├── README.md                       # this file
├── main.bicep                      # subscription-scope composition
├── odoo-runtime.bicep              # composition for Odoo container-apps lane
├── deploy-agent-identities.bicep   # Entra Agent ID + MI creation
├── deploy-agent-routes.bicep       # ACA ingress routes
├── deploy-frontdoor-erp.bicep      # Front Door → ERP backend mapping
├── foundations/                    # tenant-scope policies, hubs, etc.
├── identity/                       # Entra app regs, managed identities
├── ingress/                        # Front Door, APIM
├── modules/                        # reusable resource modules (see list below)
├── networking/                     # VNets, subnets, private endpoints
├── observability/                  # App Insights, Log Analytics, Monitor
├── parameters/                     # per-env .bicepparam files
├── pg-mcp/                         # PG MCP server composition
├── platform/                       # shared platform scaffolding
├── policy/                         # Azure Policy assignments
├── scripts/                        # deployment helpers (bash wrappers)
└── workload/                       # workload-specific compositions
```

## Key modules

| Module | Purpose |
|---|---|
| `modules/data-lake-canonical.bicep` | `stipaidevlake` ADLS Gen2 + containers + UC access-connector RBAC |
| `modules/storage.bicep` | Generic HNS-enabled ADLS Gen2 with medallion containers |
| `modules/databricks.bicep` | Databricks workspace |
| `modules/postgres-flexible.bicep` | Azure Database for PostgreSQL flexible server |
| `modules/container-apps.bicep` | Container Apps environment + apps |
| `modules/aca-odoo-services.bicep` | Odoo web/worker/cron ACA composition |
| `modules/keyvault.bicep` | Key Vault (RBAC mode) |
| `modules/front-door.bicep` | Azure Front Door (standard/premium) |
| `modules/ai-search.bicep` | Azure AI Search service |
| `modules/app-insights.bicep` | Application Insights workspace-based |
| `modules/log-analytics.bicep` | Log Analytics workspace |
| `modules/policy-tag-governance.bicep` | Required-tag policy assignments |

---

## Reference API versions

Always target recent, stable API versions. The Bicep MCP server
(`"Update the API versions to the latest"`) will fetch current stable versions.
Use:
- https://learn.microsoft.com/en-us/rest/api/resources/ for ARM resource schemas
- `az bicep build` to validate API version choices

---

## Deployment scopes

| Scope | Tool | When |
|---|---|---|
| Resource group | `az deployment group create` | Default for workload modules |
| Subscription | `az deployment sub create` | Policy / role assignments / RG creation |
| Management group | `az deployment mg create` | Tenant-wide policy |
| Tenant | `az deployment tenant create` | Rare — reserved for top-level governance |

---

## Local validation quickstart

```bash
# Assumes az login + correct subscription selected
cd infra/azure

# Lint
az bicep build --file modules/data-lake-canonical.bicep

# Validate
az deployment group validate \
  --resource-group rg-ipai-dev-data-sea \
  --template-file modules/data-lake-canonical.bicep \
  --parameters ucAccessConnectorPrincipalId=79fbecac-8341-44d3-8711-12e8a51ddc18

# Preview
az deployment group what-if \
  --resource-group rg-ipai-dev-data-sea \
  --template-file modules/data-lake-canonical.bicep \
  --parameters ucAccessConnectorPrincipalId=79fbecac-8341-44d3-8711-12e8a51ddc18
```

---

## Governance references

- Naming rules: https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/resource-name-rules
- CAF abbreviations: https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/azure-best-practices/resource-abbreviations
- Azure Naming Tool: https://github.com/mspnp/AzureNamingTool
- ARM REST reference: https://learn.microsoft.com/en-us/rest/api/resources/
- ARM monitoring: https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/monitor-resource-manager
