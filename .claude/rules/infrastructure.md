---
paths:
  - "infra/**"
  - "deploy/**"
---

# Infrastructure Rules

> Canonical Azure resource inventory for agent decision-making.
> Last updated: 2026-04-18.

---

## Subscription

| Field | Value |
|---|---|
| Name | Microsoft Azure Sponsorship |
| ID | `eba824fb-332d-4623-9dfb-2c9f7ee83f4e` |

---

## Resource Groups

| RG | Purpose |
|---|---|
| `rg-ipai-dev-odoo-sea` | Odoo runtime: ACA, ACR, PG |
| `rg-ipai-dev-security-sea` | Key Vault, Purview, Managed Identities, Backup Vault |
| `rg-ipai-dev-ai-sea` | AI/ML services |
| `rg-ipai-dev-net-sea` | VNet, Private Endpoints, DNS zones |
| `rg-ipai-dev-data-sea` | Storage accounts, ADLS |
| `rg-ipai-dev-mon-sea` | Log Analytics, App Insights |
| `rg-ipai-dev-realtime` | SignalR, Communication Services, Redis |
| `rg-ipai-dev-agent-runtime` | Agent ACA apps, MCP servers |
| `rg-ipai-dev-dbw-managed` | Databricks managed RG |
| `rg-ipai-shared` | Shared cross-environment resources |
| `rg-ipai-data-sea` | Data platform resources |

---

## Container Registry

| Field | Value |
|---|---|
| Name | `acripaiodoo` |
| RG | `rg-ipai-dev-odoo-sea` |

---

## PostgreSQL

| Field | Value |
|---|---|
| Server | `pg-ipai-odoo` |
| RG | `rg-ipai-dev-odoo-sea` |
| SKU | General Purpose D2s_v3 |
| Databases | `odoo` (prod), `odoo_staging`, `odoo_dev` |

`ipai-odoo-dev-pg` is DEPRECATED — never reference it.

---

## Key Vault

| Field | Value |
|---|---|
| Name | `kv-ipai-dev-sea` |
| RG | `rg-ipai-dev-security-sea` |

All runtime secrets (SMTP credentials, API keys, connection strings) resolve from this vault via Managed Identity. No plaintext credentials in any committed file.

---

## Azure Container Apps

ACA environment is in `rg-ipai-dev-odoo-sea`.

| App | Role |
|---|---|
| `ca-ipai-odoo-web-dev` | Odoo web server |
| `ca-ipai-odoo-worker-dev` | Odoo async worker |
| `ca-ipai-odoo-cron-dev` | Odoo cron runner |
| `ipai-prismalab-web` | Prisma Lab web app |
| `ipai-website-dev` | Public website |
| `ipai-w9studio-dev` | W9 Studio app |

ACA is the canonical hosting surface. Azure Front Door exists as legacy infrastructure — it is NOT the canonical ingress path.

---

## AI / ML Resources (`rg-ipai-dev-ai-sea`)

| Resource | Type |
|---|---|
| `ipai-copilot-resource` | Azure AI Services (AIServices kind), subdomain: `ipai-foundry-sea` |
| `docai-ipai-dev` | Form Recognizer (Document Intelligence) |

---

## Databricks

| Field | Value |
|---|---|
| Workspace | `dbw-ipai-dev` |
| Governance | Unity Catalog (mandatory) |

Databricks + Unity Catalog is the mandatory governed transformation, engineering, and serving plane.

---

## Realtime Resources (`rg-ipai-dev-realtime`)

| Resource | Type |
|---|---|
| `sigr-ipai-dev-sea` | Azure SignalR Service |
| `acs-ipai-dev-sea` | Azure Communication Services |
| `redis-ipai-dev-sea` | Azure Cache for Redis |

---

## DNS

| Zone | Authority |
|---|---|
| `insightpulseai.com` | Azure DNS (delegated from Squarespace) |
| `w9studio.net` | Azure DNS (delegated from Squarespace) |

`insightpulseai.net` is DEPRECATED. Always use `insightpulseai.com`.

---

## Mail

| Field | Value |
|---|---|
| Provider | Zoho SMTP |
| Host | `smtp.zoho.com` |
| Port | `587` (STARTTLS) |
| Domain | `insightpulseai.com` |
| Credentials | `kv-ipai-dev-sea` → `zoho-smtp-user` / `zoho-smtp-password` |

---

## CI/CD Authority

| System | Role |
|---|---|
| **Azure Pipelines** | Sole deploy authority for ALL lanes |
| **GitHub Actions** | Pre-merge validation only (scoped exception — see CLAUDE.md) |

Never add deploy steps, image builds, infra provisioning, or secret-bearing steps to GitHub Actions workflows.

---

## Deprecated — Never Reference as Active

| Service | Status |
|---|---|
| Supabase (all instances) | Removed 2026-03-26 |
| Cloudflare (DNS, Workers, Pages, R2) | Removed 2026-04-07 |
| n8n (all) | Removed 2026-04-07 |
| Vercel (all) | Removed 2026-04-07 |
| DigitalOcean (all) | Removed 2026-03-15 |
| Mailgun / `mg.insightpulseai.com` | Removed 2026-03-11 |
| Mattermost (all) | Removed 2026-01-28 |
| Wix (all) | Removed 2026-04-02 |
| Keycloak / `ipai_auth_oidc` | Removed — use Entra ID (OIDC/SAML native) |
| `ipai-odoo-dev-pg` (Burstable PG) | Replaced by `pg-ipai-odoo` |
| Public nginx edge | Replaced by Azure Front Door → ACA |
| Self-hosted runners | Replaced by GitHub-hosted / Azure DevOps pool |

---

## Invariants

1. All infra changes require a repo commit (Bicep / YAML / IaC). No console-only changes.
2. All service-to-service auth uses Managed Identities + Key Vault. No hardcoded credentials.
3. ACA is the only compute surface. No DigitalOcean, no Vercel, no self-hosted VMs outside the defined stack.
4. Secrets resolve at runtime from `kv-ipai-dev-sea`. Never in `.env` files committed to git.
