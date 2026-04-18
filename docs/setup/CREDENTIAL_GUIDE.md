# IPAI Credential & Connection Authority

This document serves as the operational authority for all secrets, service principals, and ingress tokens required for the IPAI Agent Factory V2.

## 1. Secret Inventory Matrix

| Integration | Secret Name | Purpose | Source System | Target Runtime | Owner | Rotation Owner | Storage Authority | Injection Method | Validation Method | Env Scope |
|---|---|---|---|---|---|---|---|---|---|---|
| **Odoo API** | `ODOO_API_KEY` | RPC Execution | Odoo Users | Azure Functions | ERP Admin | Security Team | Odoo External | App Setting | Odoo Auth Test | All |
| **Azure AI** | `AZURE_TENANT_ID` | Auth Context | Azure Portal | Odoo (Foundry) | Cloud Ops | Cloud Ops | Azure Entra | res.config | Foundry Ping | All |
| **Azure AI** | `AZURE_CLIENT_ID` | Identity | App Reg | Odoo (Foundry) | Cloud Ops | Cloud Ops | Azure Entra | res.config | Foundry Ping | All |
| **Azure AI** | `AZURE_CLIENT_SECRET` | Secret Key | App Reg | Odoo (Foundry) | Cloud Ops | Cloud Ops | Azure Entra | res.config (Enc) | Foundry Ping | All |
| **Doc Intel** | `DOC_INTEL_ENDPOINT` | OCR Service | Azure AI | Odoo (Foundry) | Cloud Ops | Cloud Ops | Azure Portal | res.config | OCR Mock Test | All |
| **Zoho SMTP** | `zoho-smtp-user` | Mail sender | Zoho | Odoo | Cloud Ops | Cloud Ops | Key Vault | Env Variable | SMTP connect | All |
| **Zoho SMTP** | `zoho-smtp-password` | Mail auth | Zoho | Odoo | Cloud Ops | Cloud Ops | Key Vault | Env Variable | SMTP connect | All |
| **PostgreSQL**| `PGHOST` | DB Host | Azure Postgres | Odoo / Scripts | DB Admin | DBA | Azure Portal | Env Variable | `pg_isready` | Dev |
| **PostgreSQL**| `PGUSER` | DB Admin User | Azure Postgres | Odoo / Scripts | DB Admin | DBA | Azure Portal | Env Variable | `psql -c 'SELECT 1'`| Dev |
| **PostgreSQL**| `PGPASSWORD` | DB Password | Azure Postgres | Odoo / Scripts | DB Admin | DBA | Azure Portal | Key Vault | `psql` connection | Dev |

## 2. Environment Isolation

- **Isolation Rule**: Separate credentials MUST be used for Production and Staging environments.
- **Key Vault**: All runtime secrets are stored in `kv-ipai-dev-sea`. Access via managed identity only.
- **No plaintext secrets**: Never store credentials in tracked config files, CI logs, or environment templates.

> **Deprecated (2026-04-07):** Telegram bots and n8n webhook routing are no longer used. All automation uses Azure Functions / Logic Apps.

## 3. Runtime Ownership & Security
- **Odoo**: Owns the persistent business state and accounting truth.
- **Azure Functions / Logic Apps**: Own transient orchestration credentials. Access restricted to Platform Ops.
- **Security**: **NO PLAINTEXT SECRETS** are permitted within this repository or any sign-off documentation. All production secrets must be managed via Azure Key Vault (`kv-ipai-dev-sea`).

## 4. Connection Validation
Validation must be performed periodically to ensure no credential drift:
1. **Odoo -> Azure AI**: Through the "Test Connection" button in InsightPulse Settings.
2. **Odoo -> PostgreSQL**: `pg_isready -h pg-ipai-odoo.postgres.database.azure.com`
3. **Odoo -> Zoho SMTP**: Send test email via Odoo Settings → Technical → Outgoing Mail Servers → Test Connection.
4. **Azure CLI**: `az account show` to verify subscription access.
5. **Foundry**: `az cognitiveservices account show -n ipai-copilot-resource -g rg-ipai-dev-ai-sea` to verify Foundry access.
