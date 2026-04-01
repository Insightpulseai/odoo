# Azure Foundation Resources

Azure foundation resources: resource groups, subscriptions, management groups, and tagging policies.

## Resource Groups (SSOT)

| Resource Group | Purpose |
|---------------|---------|
| `rg-ipai-dev-odoo-runtime` | Odoo + platform container apps |
| `rg-ipai-dev-odoo-data` | PostgreSQL and data stores |
| `rg-ipai-ai-dev` | AI services: OpenAI, Doc Intelligence, Search |
| `rg-ipai-dev-platform` | Shared platform: ACR, Key Vault |
| `rg-ipai-data-dev` | Platform data services |

## Convention

- All resources in `southeastasia` region unless service unavailable
- Naming: `<resource-type>-ipai-<env>-<purpose>`
- Tags: `environment`, `owner`, `cost-center` required on all resources
