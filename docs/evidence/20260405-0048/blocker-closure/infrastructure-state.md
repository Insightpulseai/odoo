# Infrastructure State Discovery

> Evidence: Azure resource inventory at 2026-04-05T00:48Z

## Subscription

- Name: Azure subscription 1
- ID: 536d8cf6-89e1-4815-aef3-d5f2c5f4d070
- Tenant: insightpulseai.com (402de71a-87ec-4302-a609-fb76098d1da7)

## Resource Groups

| Name | Location |
|---|---|
| rg-ipai-dev-odoo-data | southeastasia |
| rg-ipai-dev-platform | southeastasia |
| rg-ipai-dev-odoo-runtime | southeastasia |
| ai_ipai-appinsights (managed) | southeastasia |
| ME_ipai-odoo-ha-env (managed) | southeastasia |

## Total Resources: 1

| Resource | Type | Resource Group |
|---|---|---|
| ag-ipai-platform | Microsoft.Insights/actiongroups | rg-ipai-dev-odoo-runtime |

## Missing Infrastructure

The following resources documented in `docs/architecture/ODOO_ON_AZURE_REFERENCE_ARCHITECTURE.md` and `.claude/rules/infrastructure.md` are **not present** in this subscription:

- Azure Database for PostgreSQL (`ipai-odoo-dev-pg`, `pg-ipai-odoo`) — not found
- Key Vaults (`kv-ipai-dev`, `ipai-odoo-dev-kv`) — not found
- Container Apps (all 12 documented apps) — not found
- Container Registries (`cripaidev`, `ipaiodoodevacr`) — not found
- Front Door (`ipai-fd-dev`) — not found
- All AI services — not found

## Impact on Blockers

| Blocker | Status | Reason |
|---|---|---|
| 1. Alert routing verification | **CLOSED** | ag-ipai-platform test succeeded |
| 2. PG PITR restore test | **BLOCKED** | No PostgreSQL server exists in subscription |
| 3. KV private endpoint | **BLOCKED** | No Key Vault exists in subscription |
| 4. IaC drift measurement | **BLOCKED** | No resources to measure drift against |
| 5. Entra OIDC activation | Requires Entra config only | May proceed independently |
