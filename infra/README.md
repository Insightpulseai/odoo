# Infra

Azure-native infrastructure as code for the InsightPulse AI platform.

## Canonical Scope

This repo owns all Azure IaC and edge configuration:

| Service | Azure Resource | Purpose |
|---------|---------------|---------|
| Front Door | `afd-ipai-prod` | Public ingress, TLS, global routing |
| WAF | `waf-afd-ipai-prod` | OWASP rules, bot mitigation |
| Entra ID | App registrations | OIDC identity for Odoo and platform apps |
| Key Vault | `kv-ipai-prod` | Secrets, certificates, keys |
| Container Registry | `acripaiprod` | OCI image store for all ACA workloads |
| Container Apps Env | `cae-ipai-odoo-prod` | Shared ACA environment |
| Odoo Web | `aca-ipai-odoo-web-prod` | Odoo CE 19 HTTP frontend |
| Odoo Worker | `aca-ipai-odoo-worker-prod` | Background jobs and cron |
| PostgreSQL | `pgflex-ipai-odoo-prod` | Odoo transactional database |
| Azure Files | `stipaiprododoo` | Persistent filestore and backups |
| AI Foundry Hub | `aihub-ipai-prod` | Model management and endpoints |
| AI Foundry Project | `aiproj-pulser-prod` | Pulser agent project |
| Pulser Agent | `agent-pulser-prod` | AI assistant serving endpoint |
| Document Intelligence | `docint-ipai-prod` | OCR for receipts and invoices |
| Databricks | `dbw-ipai-prod` | Governed data engineering and ML |
| Log Analytics | `log-ipai-prod` | Centralized log aggregation |
| Application Insights | `appi-ipai-prod` | APM, tracing, alerting |

Full machine-readable BOM: `platform/ssot/services.yaml`

## Active Platform Doctrine

| Plane | Service | Role |
|-------|---------|------|
| SoR (System of Record) | Odoo CE 19 | ERP — finance, HR, inventory, CRM |
| Assistant | Pulser | AI copilot agent via Foundry |
| Identity | Entra ID | OIDC SSO, managed identities |
| Edge | Azure Front Door + WAF | TLS termination, routing, bot protection |
| AI | Azure AI Foundry | Model hosting, agent deployment |
| OCR | Document Intelligence | Receipt and invoice extraction |
| Data | Databricks + Unity Catalog | Governed lakehouse, analytics, ML serving |
| Observability | Log Analytics + App Insights | Logs, metrics, traces, alerts |
| Secrets | Key Vault | All credentials resolved at runtime |

## External Dependency Exceptions

Only two non-Azure external services are active:

| Service | Role | Notes |
|---------|------|-------|
| Squarespace | Domain registrar | Registration only. DNS delegated to Azure Front Door. |
| Zoho Mail | Production email | SMTP on `insightpulseai.com`. Credentials in Key Vault. |

Full registry: `platform/ssot/external_dependencies.yaml`

## Retired / Decommissioned

| Service | Retired | Replacement |
|---------|---------|-------------|
| Cloudflare | 2026-03-15 | Azure Front Door |
| Supabase | 2026-03-15 | Azure PostgreSQL Flexible Server |
| n8n | 2026-03-21 | Azure DevOps Pipelines + Foundry agents |
| Plane | 2026-03-21 | Azure DevOps Boards |
| Shelf | 2026-03-21 | Odoo Knowledge + agent knowledge layer |

## Resource Group Pattern

| Resource Group | Plane | Contains |
|----------------|-------|----------|
| `rg-ipai-prod-edge` | Edge | Front Door, WAF, DNS zone |
| `rg-ipai-prod-shared` | Shared | Key Vault, ACR, Log Analytics, App Insights, Managed Identities |
| `rg-ipai-prod-odoo` | Odoo | Container Apps Environment, Odoo web + worker |
| `rg-ipai-prod-ai` | AI | Foundry Hub, Foundry Project, Pulser Agent, Doc Intelligence, AI Search |
| `rg-ipai-prod-data` | Data | PostgreSQL, Azure Files, Databricks |

## Boundary Rules

1. All infrastructure changes are IaC — never console-only.
2. Front Door is the sole public ingress — no direct ACA endpoint exposure.
3. Secrets reference Key Vault — never hardcode.
4. Service-to-service auth uses managed identities.
5. DNS records are managed via `infra/dns/subdomain-registry.yaml`.
6. Repo ownership boundaries are defined in `platform/ssot/repo_ownership.yaml`.
