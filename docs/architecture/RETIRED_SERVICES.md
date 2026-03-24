# Retired Services Registry

> Decommission records for services removed from the InsightPulseAI active plane.
> These systems are **not part of the active reference architecture**.
> The Microsoft reference patterns (AI-led SDLC, Databricks+Fabric, Foundry) apply to the reduced active stack only.
> Cross-referenced by: `ACTIVE_PLATFORM_BOUNDARIES.md`, `AZURE_NATIVE_TARGET_STATE.md`
> Updated: 2026-03-25

---

## Retirement Protocol

1. Service is flagged in `ACTIVE_PLATFORM_BOUNDARIES.md` as "Sunset in progress"
2. Data migration plan created (if applicable)
3. DNS records removed or redirected
4. ACA container app scaled to 0, then deleted
5. Azure resources (RG, storage, secrets) cleaned up
6. Entry added to this document with evidence

---

## Retired Services

### Supabase (Self-Hosted on Azure VM)

| Field | Value |
|-------|-------|
| **Resource** | `vm-ipai-supabase-dev` in `rg-ipai-agents-dev` |
| **Project ID** | `spdtwktxdalcfigzeqrz` |
| **Role** | Auth, Edge Functions, Vault, Realtime, pgvector, n8n bridge |
| **Retirement reason** | Non-Azure-native; operational burden of self-hosted VM; capabilities replaced by Entra (auth), Databricks (data), ACA (serverless functions) |
| **Data migration** | Edge Functions → ACA or Foundry agents; Auth → Entra ID; pgvector → Databricks ML; Vault → Azure Key Vault |
| **Status** | Sunset in progress — target Q2 2026 |
| **DNS** | `supabase.insightpulseai.com` → to be removed |
| **Previously deprecated instances** | `xkxyvboeubffxxbebsll`, `ublqmilcjtpnflofprkr` (already decommissioned) |

### n8n

| Field | Value |
|-------|-------|
| **Endpoint** | `n8n.insightpulseai.com` (via Azure Front Door) |
| **Role** | Workflow automation, Slack/GitHub integrations, task bus |
| **Retirement reason** | Workflow automation consolidated into Foundry agents + Azure DevOps pipelines; reduces operational surface |
| **Data migration** | Critical workflows → Foundry agent skills; GitHub integrations → DevOps pipelines; Slack integrations → direct Slack MCP |
| **Status** | Sunset in progress — target Q2 2026 |
| **DNS** | `n8n.insightpulseai.com` → to be removed |

### Plane

| Field | Value |
|-------|-------|
| **Resource** | `ipai-plane-dev` in `rg-ipai-dev-odoo-runtime` |
| **Endpoint** | `plane.insightpulseai.com` |
| **Role** | Project management, task tracking |
| **Retirement reason** | Consolidate to Azure DevOps Boards; eliminates separate identity silo |
| **Data migration** | Active projects → DevOps Boards; archived data → export + docs |
| **Status** | Sunset in progress — target Q2 2026 |
| **DNS** | `plane.insightpulseai.com` → to be removed |

### Shelf

| Field | Value |
|-------|-------|
| **Resource** | `ipai-shelf-dev` in `rg-ipai-dev-odoo-runtime` |
| **Endpoint** | `shelf.insightpulseai.com` |
| **Role** | Knowledge base service |
| **Retirement reason** | Consolidate to Odoo Knowledge module + Databricks for search/embeddings |
| **Data migration** | Articles → Odoo Knowledge; embeddings → Databricks/pgvector |
| **Status** | Sunset in progress — target Q2 2026 |
| **DNS** | `shelf.insightpulseai.com` → to be removed |

### Standalone CRM Service

| Field | Value |
|-------|-------|
| **Resource** | `ipai-crm-dev` in `rg-ipai-dev-odoo-runtime` |
| **Endpoint** | `crm.insightpulseai.com` |
| **Role** | CRM service (separate from Odoo) |
| **Retirement reason** | Redundant — Odoo CRM module is the canonical CRM surface |
| **Data migration** | Merge any unique data into Odoo CRM |
| **Status** | Sunset in progress — target Q2 2026 |
| **DNS** | `crm.insightpulseai.com` → to be removed |

### Keycloak

| Field | Value |
|-------|-------|
| **Resource** | `ipai-auth-dev` in `rg-ipai-dev-odoo-runtime` |
| **Endpoint** | `auth.insightpulseai.com` |
| **Role** | SSO / Identity Provider |
| **Retirement reason** | Never operationalized — no apps authenticate through it; Entra ID is the target IdP |
| **Data migration** | None (no production users) |
| **Status** | Decommission candidate — delete when Entra is active |
| **DNS** | `auth.insightpulseai.com` → to be repurposed or removed |

---

## Previously Retired (Completed)

| Service | Replacement | Retired Date | Evidence |
|---------|-------------|-------------|----------|
| DigitalOcean (all) | Azure (ACA + VM + managed PG) | 2026-03-15 | Infra migration complete |
| Public nginx edge | Azure Front Door | 2026-03-15 | Front Door routes active |
| Mailgun (`mg.insightpulseai.com`) | Zoho SMTP | 2026-03-11 | DNS MX updated |
| Vercel deployment | Azure Container Apps | 2026-03-11 | All deployments on ACA |
| Self-hosted runners | GitHub-hosted / Azure DevOps pool | 2026-03-15 | Runners decommissioned |
| Mattermost | Slack | 2026-01-28 | `ipai_slack_connector` active |
| Appfine (all) | Removed | 2026-02 | No replacement needed |
| `insightpulseai.net` | `insightpulseai.com` | 2026-02 | Domain deprecated |

---

*When a service completes retirement, move its entry from "Retired Services" to "Previously Retired" with evidence.*
