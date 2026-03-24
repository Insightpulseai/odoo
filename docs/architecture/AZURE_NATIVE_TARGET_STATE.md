# Azure-Native Target State

> Canonical architecture for InsightPulseAI after platform reduction.
> Cross-referenced by: `ACTIVE_PLATFORM_REFERENCE_MODEL.md`, `PULSER_MINIMAL_RUNTIME.md`
> Updated: 2026-03-25

---

## Design Principle

**Azure-native by default.** Every service runs on Azure-managed infrastructure. Non-Azure services require explicit justification and appear in the exception list.

---

## Target Architecture

```
                        ┌─────────────────────┐
                        │   Cloudflare DNS     │  (delegated from Spacesquare)
                        └──────────┬──────────┘
                                   │
                        ┌──────────▼──────────┐
                        │  Azure Front Door   │  TLS, WAF, edge routing
                        │  (ipai-fd-dev)      │
                        └──────────┬──────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                     │
    ┌─────────▼─────────┐ ┌───────▼────────┐  ┌────────▼────────┐
    │  Odoo CE 19       │ │  Pulser Agents │  │  Web Surfaces   │
    │  (ACA: web,       │ │  (ACA +        │  │  (ACA: landing, │
    │   worker, cron)   │ │   Foundry)     │  │   SaaS, public) │
    └─────────┬─────────┘ └───────┬────────┘  └─────────────────┘
              │                    │
    ┌─────────▼─────────┐ ┌───────▼────────┐
    │  Azure PostgreSQL │ │  Azure AI      │
    │  (pg-ipai-odoo)   │ │  Foundry       │
    └───────────────────┘ │  + Doc Intel   │
                          │  + OpenAI      │
                          └───────┬────────┘
                                  │
                        ┌─────────▼─────────┐
                        │  Azure Databricks │  Lakehouse, DLT, Unity Catalog
                        │  + Power BI       │  Reporting surface
                        └───────────────────┘

    Identity: Microsoft Entra ID (all services)
    Secrets:  Azure Key Vault (kv-ipai-dev / staging / prod)
    CI/CD:    Azure DevOps Pipelines
    Registry: Azure Container Registry (cripaidev)
```

## Service Matrix

| Layer | Service | Azure Resource | Purpose |
|-------|---------|---------------|---------|
| **Edge** | Front Door | `ipai-fd-dev` | Ingress, TLS, WAF |
| **Compute** | Container Apps | `ipai-odoo-dev-env` | All application hosting |
| **Identity** | Entra ID | Tenant-level | SSO, agent identity, RBAC |
| **Secrets** | Key Vault | `kv-ipai-dev` | Secrets, certificates |
| **Database** | PostgreSQL Flexible | `pg-ipai-odoo` | Odoo operational data |
| **AI** | AI Foundry | `aifoundry-ipai-dev` | Agent runtime, orchestration |
| **AI** | OpenAI | `oai-ipai-dev` | LLM inference (GPT-4.1, eval judges) |
| **AI** | Document Intelligence | `docai-ipai-dev` | OCR, document extraction |
| **AI** | Gemini (direct API) | External | Creative generation (Nano Banana, Imagen, Veo) |
| **Data** | Databricks | `dbw-ipai-dev` | Lakehouse, DLT, ML serving |
| **Data** | Unity Catalog | Via Databricks | Data governance, lineage |
| **Reporting** | Power BI | SaaS | Business dashboards |
| **CI/CD** | Azure DevOps | Organization-level | Pipelines, boards, artifacts |
| **Registry** | Container Registry | `cripaidev` | Docker images |

---

## Doctrinal Split

> **Entra authenticates. Foundry thinks. Document Intelligence reads. Odoo records.**

### Entra ID → Odoo SSO

Odoo 19 has [native Microsoft Azure / Entra sign-in](https://www.odoo.com/documentation/19.0/applications/general/users/azure.html) via OAuth provider flow:

- Register app in Entra ID with redirect URI `/auth_oauth/signin`
- Grant `User.Read` scope minimum
- Configure Odoo OAuth provider with Microsoft authorization + Graph OIDC userinfo endpoints

**Entra provides SSO.** Odoo retains its internal authorization model (groups, record rules, finance permissions). Entra does not replace Odoo's permission system.

### Foundry Agent Service → Pulser Runtime

[Foundry Agent Service](https://learn.microsoft.com/azure/ai-foundry/agents/overview) hosts Pulser agents with:

- File search, function calling, Azure AI Search, code interpreter
- Foundry agents **reason and orchestrate**, then call Odoo APIs/tools to read/write business data
- Business state (invoices, approvals, expenses, tickets) stays in Odoo

| Concern | Owner |
|---------|-------|
| Agent behavior (prompts, skills, judges) | `agents/` repo |
| Agent runtime & hosting | Foundry Agent Service |
| Transactional state | Odoo (always) |
| Agent identity | Entra Agent ID + managed identity |

### Document Intelligence → Odoo Document Intake

[Document Intelligence](https://learn.microsoft.com/azure/ai-services/document-intelligence/overview) handles all document-heavy extraction:

```
File → Odoo attachment/intake →
  Document Intelligence (Read/Layout/Prebuilt model) →
  Structured output (text, tables, key-values) →
  Odoo maps to vendor bill / receipt / expense claim / document record →
  Pulser/Foundry for review, exception handling, guided corrections
```

- **Documents** (PDFs, scans, receipts, invoices, forms): Use Document Intelligence Read/Layout
- **Non-document images** (street signs, labels, posters): Use Azure AI Vision OCR
- Supported add-ons: high-res OCR, barcodes, fonts, formulas, key-value pairs, searchable PDF

---

## AI-Led SDLC Spine

> Reference: [AI-led SDLC with Azure and GitHub](https://techcommunity.microsoft.com/blog/appsonazureblog/an-ai-led-sdlc-building-an-end-to-end-agentic-software-development-lifecycle-wit/4491896)

```
Spec Kit (idea → requirements → plan → tasks)
    ↓
Coding Agent (implement against spec)
    ↓
Quality Agent (eval gates — judges in agents/)
    ↓
GitHub Actions (build, test, deploy preview)
    ↓
ACA Revision URL (review environment)
    ↓
SRE Agent (monitor, open issues)
```

| SDLC Component | Repo Location | Runtime |
|----------------|--------------|---------|
| Spec bundles | `spec/` | Static (repo) |
| Agent evals/judges | `agents/evals/` | Foundry |
| CI/CD orchestration | `.github/workflows/` | GitHub Actions |
| Preview environments | `infra/azure/` | ACA revision URLs |

---

## AI Platform Plane (Foundry)

> Reference: [Microsoft Foundry](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/microsoft-foundry-an-end-to-end-platform-for-building-governing-and-scaling-ai/4496736)

Foundry = **AI build/govern/scale plane**: model choice, agent runtime, evaluation, safety/governance, monitoring.

| Concern | Owner | Not Owner |
|---------|-------|-----------|
| Agent behavior | `agents/` repo | Foundry portal |
| Agent runtime | Foundry | ACA directly |
| Agent identity | Entra Agent ID | Custom auth |
| Foundry IaC | `infra/azure/foundry/` | `platform/` |

---

## Data Plane (Databricks + Fabric/Power BI)

> Reference: [Data Intelligence with Azure Databricks and Microsoft Fabric](https://techcommunity.microsoft.com/blog/azurearchitectureblog/data-intelligence-end-to-end-with-azure-databricks-and-microsoft-fabric/4232621)

```
Odoo PostgreSQL (operational SoR)
    ↓ JDBC extract
Azure Databricks (lakehouse — Bronze → Silver → Gold)
    ↓ Unity Catalog governance
    ├── ML serving (feature store, model registry)
    └── Semantic prep (Gold tables)
            ↓
        Microsoft Fabric / Power BI (consumption layer)
```

- **Databricks is primary** for data engineering. Fabric does not replace it.
- **Power BI / Fabric are consumption/semantic layers only.**
- **Unity Catalog is mandatory** for governance.
- **Entra ID** is the identity authority for both.

---

## Exceptions (Non-Azure)

| Service | Justification | Mitigation |
|---------|--------------|------------|
| **Cloudflare** | DNS delegation from registrar | DNS YAML in repo, CI sync |
| **Zoho SMTP** | Outbound mail | Credentials in Key Vault |
| **Gemini API** (direct) | Creative generation models not on Azure OpenAI | API key in Key Vault; switchable to Vertex AI |
| **fal** | Mixed media generation (Kling, LTX, audio, SFX) | API key in Key Vault; via provider router |
| **GitHub** | Source control | Mirrors to Azure DevOps for CI/CD |

## Container Apps Inventory (Target State)

| App | Public Hostname | Purpose | Keep |
|-----|----------------|---------|------|
| `ipai-odoo-dev-web` | `erp.insightpulseai.com` | Odoo ERP | Yes |
| `ipai-odoo-dev-worker` | (internal) | Odoo background jobs | Yes |
| `ipai-odoo-dev-cron` | (internal) | Odoo scheduled tasks | Yes |
| `ipai-ocr-dev` | `ocr.insightpulseai.com` | Document OCR | Yes |
| `ipai-mcp-dev` | `mcp.insightpulseai.com` | MCP coordination | Yes |
| `ipai-copilot-gateway` | (internal) | Pulser gateway | Yes |
| `ipai-website-dev` | `www.insightpulseai.com` | Public website | Yes |
| `ipai-superset-dev` | `superset.insightpulseai.com` | Superset (supplemental) | Demoted |
| `ipai-auth-dev` | `auth.insightpulseai.com` | Keycloak | **Delete** |
| `ipai-plane-dev` | `plane.insightpulseai.com` | Plane | **Delete** |
| `ipai-shelf-dev` | `shelf.insightpulseai.com` | Shelf | **Delete** |
| `ipai-crm-dev` | `crm.insightpulseai.com` | Standalone CRM | **Delete** |

## Identity Target

| Surface | Current Auth | Target Auth |
|---------|-------------|-------------|
| Odoo ERP | Basic login | Entra OIDC (`/auth_oauth/signin`) |
| Pulser agents | API key | Entra Agent ID + managed identity |
| Web surfaces | None / public | Entra (authenticated pages) |
| Databricks | Workspace login | Entra SSO |
| Power BI | Microsoft account | Entra SSO |
| DevOps | GitHub OAuth | Entra SSO |

## Migration Sequence

1. **Entra ID** — Register apps, configure OIDC for Odoo
2. **Delete retired ACA apps** — Keycloak, Plane, Shelf, standalone CRM
3. **Migrate n8n workflows** — Critical paths to Foundry agents; remainder archived
4. **Supabase sunset** — Edge Functions to ACA; Auth to Entra; pgvector to Databricks
5. **DNS cleanup** — Remove retired subdomains from `subdomain-registry.yaml`
6. **VM cleanup** — Delete `vm-ipai-supabase-dev` after data migration

---

*This is the target. Current state is documented in `.claude/rules/infrastructure.md`.*
*Microsoft reference patterns aligned: 2026-03-25.*
