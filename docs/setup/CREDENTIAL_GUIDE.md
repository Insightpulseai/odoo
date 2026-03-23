# IPAI Credential & Connection Authority

This document serves as the operational authority for all secrets, service principals, and ingress tokens required for the IPAI Agent Factory V2.

## 1. Secret Inventory Matrix

| Integration | Secret Name | Purpose | Source System | Target Runtime | Owner | Rotation Owner | Storage Authority | Injection Method | Validation Method | Env Scope |
|---|---|---|---|---|---|---|---|---|---|---|
| **Telegram** | `TG_BOT_TOKEN_PROD` | Mobile Ingress | @BotFather | n8n (Prod) | Finance IT | Platform Ops | Azure Key Vault | Env Variable | Check bot /info | Prod |
| **Telegram** | `TG_BOT_TOKEN_STG` | Testing Ingress | @BotFather | n8n (Staging) | Finance IT | Platform Ops | Azure Key Vault | Env Variable | Check bot /info | Staging |
| **Odoo API** | `ODOO_API_KEY` | RPC Execution | Odoo Users | n8n | ERP Admin | Security Team | Odoo External | App Setting | Odoo Auth Test | All |
| **Azure AI** | `AZURE_TENANT_ID` | Auth Context | Azure Portal | Odoo (Foundry) | Cloud Ops | Cloud Ops | Azure Entra | res.config | Foundry Ping | All |
| **Azure AI** | `AZURE_CLIENT_ID` | Identity | App Reg | Odoo (Foundry) | Cloud Ops | Cloud Ops | Azure Entra | res.config | Foundry Ping | All |
| **Azure AI** | `AZURE_CLIENT_SECRET` | Secret Key | App Reg | Odoo (Foundry) | Cloud Ops | Cloud Ops | Azure Entra | res.config (Enc) | Foundry Ping | All |
| **Doc Intel** | `DOC_INTEL_ENDPOINT` | OCR Service | Azure AI | Odoo (Foundry) | Cloud Ops | Cloud Ops | Azure Portal | res.config | OCR Mock Test | All |
| **PostgreSQL**| `PGHOST` | DB Host | Azure Postgres | Odoo / Scripts | DB Admin | DBA | Azure Portal | Env Variable | `pg_isready` | Dev |
| **PostgreSQL**| `PGUSER` | DB Admin User | Azure Postgres | Odoo / Scripts | DB Admin | DBA | Azure Portal | Env Variable | `psql -c 'SELECT 1'`| Dev |
| **PostgreSQL**| `PGPASSWORD` | DB Password | Azure Postgres | Odoo / Scripts | DB Admin | DBA | Azure Portal | Key Vault | `psql` connection | Dev |

## 2. Environment Isolation & Webhook Strategy
> [!WARNING]
> Telegram bots support exactly **one** active Webhook URL. Overwriting this will break all other environments referencing the same token.

- **Isolation Rule**: Separate bots MUST be used for Production (`@IPAI_PROD_BOT`) and Staging (`@IPAI_STG_BOT`).
- **Callback Routing**: n8n environments must use unique path segments (e.g., `/webhooks/prod/...` vs `/webhooks/staging/...`) to avoid accidental prod-triggering from staging tests.
- **Rollback Procedure**: If a webhook is misrouted, deactivate the offending n8n workflow immediately and re-initialize the bot webhook via the `setWebhook` API call.

## 3. Runtime Ownership & Security
- **Odoo**: Owns the persistent business state and accounting truth.
- **n8n**: Owns the transient orchestration credentials only. Access must be restricted to Platform Ops.
- **Telegram**: Owns the ingress token only.
- **Security**: **NO PLAINTEXT SECRETS** are permitted within this repository or any sign-off documentation. All production secrets must be managed via Azure Key Vault or equivalent encrypted stores.

## 4. Connection Validation
Validation must be performed periodically to ensure no credential drift:
1. **Odoo -> Azure**: Through the "Test Connection" button in InsightPulse Settings.
2. **n8n -> Odoo**: Through the `odoo-auth-test` node in the Health Check workflow.
3. **Telegram -> n8n**: Through a manual `/ping` command to the bot.
4. **Scripts -> PostgreSQL**: Through the `pg_isready -h ipai-odoo-dev-pg.postgres.database.azure.com` command.
5. **Azure CLI**: Refer to the **[Azure PostgreSQL CLI Runbook](file:///Users/tbwa/Documents/GitHub/Insightpulseai/docs/runbooks/AZURE_POSTGRES_CLI_OPS.md)** for advanced management.
