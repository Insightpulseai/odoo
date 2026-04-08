# InsightPulseAI Target-State Architecture

> Principal architecture document for the reduced Azure-native platform.
> Covers: Odoo on Cloud, Pulser, Entra, Front Door, Foundry, Document Intelligence, Databricks.
> Updated: 2026-03-25

---

## 1. Executive Summary

InsightPulseAI operates a reduced Azure-native platform with seven active service planes and zero non-essential sidecars. The doctrinal split is:

- **Entra authenticates** — identity authority for all services
- **Front Door routes** — public entry, TLS, WAF
- **Foundry thinks** — agent reasoning, orchestration, tool calling
- **Document Intelligence reads** — OCR, document extraction
- **Odoo records** — transactional system of record
- **Databricks analyzes** — lakehouse, DLT, semantic prep, ML
- **Power BI presents** — business-facing dashboards

Retired services: Supabase, n8n, Plane, Shelf, standalone CRM, Keycloak. Cloudflare proxy role retired (DNS authority remains until Azure DNS migration). External exceptions: Squarespace (registrar only), Cloudflare (DNS-only, target: Azure DNS), Zoho Mail (domain email only), Gemini API (creative generation), fal (mixed media).

The platform serves four verticals (marketing, media, retail, financial services) through six Pulser assistant surfaces on a shared Foundry + Odoo runtime.

---

## 2. Canonical End-to-End Architecture

```
                     ┌───────────────────────┐
                     │   Squarespace          │  Registrar only (NS → Cloudflare)
                     └───────────┬───────────┘
                                 │
                     ┌───────────▼───────────┐
                     │   Cloudflare (DNS-only)│  Current DNS authority (target: Azure DNS)
                     └───────────┬───────────┘
                                 │
                     ┌───────────▼───────────┐
                     │   Azure Front Door     │  TLS termination, WAF, edge routing
                     │   (ipai-fd-dev)        │  Routes: /, /api, /pulser, /erp, /ocr
                     └───────────┬───────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                        │
┌────────▼────────┐   ┌─────────▼─────────┐   ┌─────────▼─────────┐
│  Web Surfaces   │   │  Pulser Gateway   │   │  Odoo CE 19       │
│  (ACA)          │   │  (ACA)            │   │  (ACA: web,       │
│  Landing, SaaS, │   │  Ask Pulser,      │   │   worker, cron)   │
│  public pages   │   │  authenticated    │   │                   │
└────────┬────────┘   └─────────┬─────────┘   └─────────┬─────────┘
         │                       │                        │
         │            ┌──────────▼──────────┐   ┌────────▼─────────┐
         │            │  Azure AI Foundry   │   │  Azure PostgreSQL│
         │            │  Agent runtime      │   │  (pg-ipai-odoo)  │
         │            │  Tool calling       │   └──────────────────┘
         │            └──────────┬──────────┘
         │                       │
         │     ┌─────────────────┼─────────────────┐
         │     │                 │                   │
         │  ┌──▼──────────┐  ┌──▼──────────┐  ┌────▼──────────┐
         │  │ Azure OpenAI│  │ Doc Intel   │  │ Gemini/fal    │
         │  │ (inference, │  │ (OCR,       │  │ (creative gen)│
         │  │  eval judge)│  │  extraction)│  │               │
         │  └─────────────┘  └─────────────┘  └───────────────┘
         │
         │            ┌──────────────────────┐
         └────────────▶  Azure Databricks    │  JDBC extract from Odoo PG
                      │  Lakehouse + UC      │  Bronze → Silver → Gold
                      │  DLT, ML serving     │  Semantic prep
                      └──────────┬───────────┘
                                 │
                      ┌──────────▼───────────┐
                      │  Power BI            │  Business dashboards
                      │  (consumption only)  │  Analyst self-service
                      └──────────────────────┘

Cross-cutting:
  Identity:    Microsoft Entra ID (all services)
  Secrets:     Azure Key Vault (kv-ipai-dev / staging / prod)
  CI/CD:       Azure DevOps Pipelines + GitHub Actions (transitional)
  Registry:    Azure Container Registry (cripaidev)
  Observability: Azure Monitor + Application Insights
  Mail:        Zoho SMTP (insightpulseai.com)
```

### 2.1 Surface Routing

| Route | Front Door Backend | Service | Auth |
|-------|-------------------|---------|------|
| `insightpulseai.com` | `ipai-website-dev` | Landing / marketing | Public |
| `insightpulseai.com/ask` | `ipai-copilot-gateway` | Ask Pulser widget | Public (anonymous) |
| `erp.insightpulseai.com` | `ipai-odoo-dev-web` | Odoo ERP | Entra OIDC |
| `erp.insightpulseai.com/api/v1/*` | `ipai-odoo-dev-web` | Odoo API facade | Bearer token (Entra) |
| `ocr.insightpulseai.com` | `ipai-ocr-dev` | Document upload + OCR | Entra bearer |
| `mcp.insightpulseai.com` | `ipai-mcp-dev` | MCP tool coordination | Entra managed identity |

### 2.2 DNS Migration (Cloudflare → Azure DNS)

| Record | Type | Target | Notes |
|--------|------|--------|-------|
| `@` | A / ALIAS | Front Door endpoint | Apex domain |
| `www` | CNAME | Front Door | Redirect to apex |
| `erp` | CNAME | Front Door | Odoo |
| `ocr` | CNAME | Front Door | Document Intelligence proxy |
| `mcp` | CNAME | Front Door | MCP (internal traffic only) |
| MX records | MX | Zoho MX servers | Unchanged |
| SPF/DKIM/DMARC | TXT | Zoho values | Unchanged |

Squarespace NS records updated to point to Azure DNS zone nameservers.

---

## 3. User Journeys

### 3.1 Anonymous Visitor → Landing Page

```
Browser → Front Door (insightpulseai.com) → ACA (ipai-website-dev) →
  Static landing page (React/Next.js from web/) →
  CTAs: "Book a Demo", "Try Ask Pulser", "Sign In"
```

No authentication. No Odoo coupling. Pure static + client-side rendering.

### 3.2 Visitor → Ask Pulser

```
Browser → Front Door (/ask) → ACA (ipai-copilot-gateway) →
  Foundry Agent (ask-pulser-agent) →
    Tools: approved_public_docs, pricing_faq, architecture_pages, release_notes →
  Response streamed to browser
```

Anonymous. Read-only. No PII. Grounded on approved public docs only. Rate-limited at Front Door WAF.

### 3.3 Visitor → Demo Booking / Lead Capture

```
Browser → Landing page form (web/) →
  POST /api/v1/leads (thin API facade on ACA) →
    Facade validates + sanitizes →
    Facade calls Odoo JSON-RPC (internal) →
      Odoo creates crm.lead record →
      Odoo triggers mail.mail (Zoho SMTP → sales team notification)
```

No direct browser-to-Odoo coupling. The API facade is a thin ACA container in `web/` that validates, rate-limits, and proxies to Odoo's internal API.

### 3.4 User → Entra Sign-In → Odoo

```
Browser → Front Door (erp.insightpulseai.com) →
  Odoo login page → "Sign in with Microsoft" button →
    Redirect to Entra ID authorization endpoint →
    User authenticates (MFA if configured via Conditional Access) →
    Entra returns authorization code →
    Odoo exchanges code for tokens at /auth_oauth/signin →
    Odoo creates/matches res.users record →
    Odoo session established
```

Entra provides SSO. Odoo retains internal authorization: `res.groups`, `ir.rule`, finance permissions, record rules. Entra does NOT replace Odoo's permission model.

### 3.5 User → Document Upload → OCR

```
User in Odoo → Uploads receipt/invoice/document →
  Odoo attachment saved to ir.attachment →
  Odoo calls Document Intelligence API (via ipai_doc_intelligence module) →
    Doc Intel Read/Layout model processes document →
    Returns: text, tables, key-value pairs, layout →
  Odoo maps extracted data to:
    account.move (vendor bill) / hr.expense / documents.document →
  Pulser (Foundry agent) reviews for exceptions →
    If confidence < threshold → flag for human review →
    If brand compliance issue → reject with reason
```

### 3.6 Internal Team → Pulser Inside Odoo

```
User in Odoo → Opens Pulser panel (ipai_ai_copilot module) →
  Pulser widget (embedded from web/packages/pulser-widget/) →
    Routes to Pulser Diva (orchestration shell) →
      Diva identifies mode: strategy | odoo | tax_guru | capability | governance →
      Foundry agent executes with Odoo tool bindings →
        Reads: sale.order, account.move, hr.expense, crm.lead via JSON-RPC →
        Writes: draft records, activity assignments, stage transitions →
      Response rendered in Pulser panel
```

### 3.7 Analytics → Odoo → Databricks → Power BI

```
Odoo PostgreSQL (pg-ipai-odoo) →
  Databricks JDBC connector extracts incrementally →
    Bronze layer: raw tables (sale_order, account_move, crm_lead, etc.) →
    Silver layer: cleaned, typed, deduplicated →
    Gold layer: business metrics, KPIs, aggregations →
      Unity Catalog governs access + lineage →
  Power BI connects to Databricks SQL endpoint →
    Dashboards: revenue, pipeline, expenses, document processing metrics
```

---

## 4. Integration Contracts

### 4.1 Route & CTA Contract

| Route | Method | Auth | Backend | Response |
|-------|--------|------|---------|----------|
| `GET /` | GET | Public | `ipai-website-dev` | Landing HTML |
| `GET /ask` | GET | Public | `ipai-copilot-gateway` | Ask Pulser widget |
| `POST /api/v1/leads` | POST | Public (CAPTCHA) | API facade → Odoo | `201 Created` |
| `POST /api/v1/demo` | POST | Public (CAPTCHA) | API facade → Odoo | `201 Created` |
| `GET /erp/*` | GET | Entra OIDC | `ipai-odoo-dev-web` | Odoo web client |

**Contract file**: `ssot/routes/public_routes.yaml`

### 4.2 Public API Facade Contract

The API facade is a thin container in `web/` that:
- Validates request schema (JSON Schema)
- Rate-limits (Front Door WAF + application-level)
- Sanitizes inputs (XSS, injection)
- Proxies to Odoo JSON-RPC (internal network only)
- Never exposes Odoo session cookies or internal endpoints to the browser

**Contract file**: `ssot/contracts/api_facade.yaml`

### 4.3 Foundry Tool Contract

Each Foundry agent tool maps to an Odoo API endpoint or external service:

| Tool Name | Target | Auth | Direction |
|-----------|--------|------|-----------|
| `odoo.read_records` | Odoo JSON-RPC `search_read` | Managed identity → API key | Read |
| `odoo.create_record` | Odoo JSON-RPC `create` | Managed identity → API key | Write |
| `odoo.execute_action` | Odoo JSON-RPC `call_kw` | Managed identity → API key | Write |
| `doc_intel.analyze` | Document Intelligence API | Managed identity | Read |
| `search.query` | Azure AI Search | Managed identity | Read |
| `creative.generate` | Gemini/Imagen via provider router | API key (Key Vault) | Read |

**Contract file**: `ssot/contracts/foundry_tools.yaml`

### 4.4 Odoo Integration Contract

| Integration | Direction | Protocol | Auth |
|-------------|-----------|----------|------|
| Entra SSO | Inbound | OAuth 2.0 / OIDC | Entra app registration |
| Foundry agents | Bidirectional | JSON-RPC (internal) | API key via Key Vault |
| Document Intelligence | Outbound | REST | Managed identity |
| Zoho SMTP | Outbound | SMTP/TLS (587) | Credentials in Key Vault |
| Databricks extract | Outbound | JDBC (read-only) | Service principal |

**Contract file**: `ssot/contracts/odoo_integration.yaml`

### 4.5 Document Upload / OCR Contract

```yaml
flow:
  trigger: ir.attachment.create (invoice/receipt/document type)
  step_1: Odoo sends binary to Document Intelligence Read/Layout endpoint
  step_2: Doc Intel returns structured JSON (text, tables, key-values)
  step_3: Odoo maps to target model (account.move, hr.expense, documents.document)
  step_4: If confidence < threshold, Pulser flags for human review
  step_5: Odoo stores final record + original attachment
```

**Contract file**: `ssot/contracts/document_ocr.yaml`

### 4.6 Identity / Authentication Contract

| Concern | Owner | Mechanism |
|---------|-------|-----------|
| User authentication | Entra ID | OAuth 2.0 / OIDC |
| User authorization | Odoo | `res.groups`, `ir.rule`, record rules |
| Agent identity | Entra Agent ID | Managed identity + app registration |
| Service-to-service | Entra | Managed identity → Key Vault |
| Public API | Front Door WAF | Rate limiting + CAPTCHA |
| MFA | Entra Conditional Access | Policy-driven per user group |

**Contract file**: `ssot/contracts/identity.yaml`

### 4.7 Analytics / Export / Semantic Contract

| Stage | Owner | Tool |
|-------|-------|------|
| Operational data | Odoo PostgreSQL | `pg-ipai-odoo` |
| Extract | Databricks | JDBC connector (incremental, read-only) |
| Transform | Databricks | DLT pipelines (Bronze → Silver → Gold) |
| Govern | Unity Catalog | Access policies, lineage, quality rules |
| Serve | Databricks SQL | SQL warehouse endpoints |
| Present | Power BI | DirectQuery or Import from Databricks SQL |

**Contract file**: `ssot/contracts/analytics_pipeline.yaml`

---

## 5. Repo Ownership Map

| Concern | Canonical Location | Never In |
|---------|-------------------|----------|
| Odoo modules / views / models / workflows | `addons/ipai/ipai_<domain>_<feature>/` | `web/`, `agents/`, `platform/` |
| Odoo configuration / settings | `addons/ipai/` + `config/odoo/` | `infra/`, `ssot/` |
| Pulser widget UI (React) | `web/packages/pulser-widget/` | `agents/`, `odoo/`, `platform/` |
| Pulser skills / judges / evals | `agents/skills/`, `agents/evals/`, `agents/personas/` | `web/`, `odoo/`, `infra/` |
| Prompt contracts | `agents/` + `prompts/` | `web/`, `platform/` |
| Service registry / SSOT | `ssot/architecture/services.yaml` | `platform/`, `docs/` |
| Route registry | `ssot/routes/public_routes.yaml` | `web/`, `infra/` |
| Tool contracts | `ssot/contracts/*.yaml` | `agents/`, `platform/` |
| Front Door config | `infra/azure/frontdoor/` | `platform/`, `web/` |
| Entra app registrations | `infra/azure/entra/` | `odoo/`, `agents/` |
| Key Vault references | `infra/azure/keyvault/` | Application code |
| ACA container definitions | `infra/azure/aca/` | `web/`, `odoo/` |
| DNS zone config | `infra/azure/dns/` | `infra/dns/` (Cloudflare — retired) |
| Networking / VNet / NSG | `infra/azure/network/` | `platform/` |
| Databricks notebooks / DLT | `data-intelligence/` | `platform/`, `infra/`, `agents/` |
| Unity Catalog schemas | `data-intelligence/catalog/` | `ssot/` |
| Power BI reports | `data-intelligence/reports/` | `web/` |
| Design tokens / OG assets | `design/tokens/`, `design/assets/` | `web/public/` (derived only) |
| Architecture docs | `docs/architecture/` | `platform/`, `ssot/` |
| Governance docs | `docs/governance/` | `platform/` |
| Decommission records | `docs/architecture/RETIRED_SERVICES.md` | Anywhere else |
| Evidence bundles | `docs/evidence/<stamp>/<scope>/` | `platform/`, `ssot/` |
| API facade (public → Odoo proxy) | `web/api/` or `web/packages/api-facade/` | `odoo/`, `agents/` |
| Landing page / marketing site | `web/ipai-landing/` | `odoo/` |
| CI/CD pipelines | `.github/workflows/` + `azure-pipelines/` | `infra/`, `platform/` |

---

## 6. Required Docs + SSOT Changes

### 6.1 Create (New Files)

| File | Purpose |
|------|---------|
| `docs/architecture/PUBLIC_TO_ODOO_INTEGRATION_FLOW.md` | Landing → API facade → Odoo flow |
| `docs/architecture/EDGE_DNS_MAIL_AUTHORITY.md` | Front Door + Azure DNS + Zoho Mail authority |
| `docs/governance/REPO_PURPOSES.md` | Canonical repo purpose definitions |
| `ssot/routes/public_routes.yaml` | Route registry (Front Door → backends) |
| `ssot/contracts/api_facade.yaml` | Public API facade contract |
| `ssot/contracts/foundry_tools.yaml` | Foundry tool → Odoo/service bindings |
| `ssot/contracts/odoo_integration.yaml` | Odoo integration points |
| `ssot/contracts/document_ocr.yaml` | Document upload/OCR flow |
| `ssot/contracts/identity.yaml` | Identity/auth contract |
| `ssot/contracts/analytics_pipeline.yaml` | Odoo → Databricks → Power BI contract |
| `ssot/external/dependencies.yaml` | External service exceptions |
| `infra/README.md` | Infrastructure directory guide |
| `infra/azure/dns/README.md` | Azure DNS migration from Cloudflare |

### 6.2 Update (Existing Files)

| File | Change |
|------|--------|
| `docs/architecture/AZURE_NATIVE_TARGET_STATE.md` | Align with target-state architecture (done) |
| `docs/architecture/ACTIVE_PLATFORM_REFERENCE_MODEL.md` | Align Five-Layer Benchmark to this document |
| `docs/architecture/REPO_OWNERSHIP_DOCTRINE.md` | Add API facade ownership; clarify DNS authority |
| `docs/architecture/RETIRED_SERVICES.md` | Cloudflare proxy retired; DNS authority remains active (done) |
| `docs/architecture/ACTIVE_PLATFORM_BOUNDARIES.md` | Cloudflare DNS-only in active plane; proxy in retired (done) |
| `ssot/architecture/services.yaml` | Cloudflare DNS-only as active; add API facade (done) |

---

## 7. Security / Identity Model

### 7.1 Identity Plane

```
Microsoft Entra ID (Tenant)
├── App Registration: insightpulseai-odoo
│   ├── Redirect: erp.insightpulseai.com/auth_oauth/signin
│   ├── Scopes: User.Read
│   └── Conditional Access: MFA for finance group
├── App Registration: pulser-gateway
│   ├── Managed Identity → Key Vault (OpenAI, Gemini keys)
│   └── Scopes: Odoo API (custom)
├── App Registration: pulser-diva-agent
│   ├── Managed Identity → Key Vault + Odoo API
│   └── Foundry Agent Service binding
├── App Registration: pulser-studio-agent
│   ├── Managed Identity → Key Vault (Gemini, fal keys)
│   └── No Odoo write access
├── App Registration: pulser-docs-agent
│   ├── Managed Identity → Doc Intelligence endpoint
│   └── Odoo read access (attachments)
├── App Registration: databricks-extract
│   ├── Service Principal → pg-ipai-odoo (JDBC read-only)
│   └── No write access to Odoo
└── App Registration: ask-pulser-agent
    ├── Managed Identity → OpenAI only
    └── No Odoo access, no PII
```

### 7.2 Auth Boundaries

| Route | Auth Type | Token Source | Authorization Owner |
|-------|-----------|-------------|-------------------|
| `insightpulseai.com` (landing) | None (public) | — | — |
| `insightpulseai.com/ask` | None (anonymous) | — | Rate limit only |
| `POST /api/v1/leads` | CAPTCHA | Client-side token | Front Door WAF + facade validation |
| `erp.insightpulseai.com` | Entra OIDC | Entra access token | Odoo (`res.groups` + `ir.rule`) |
| `ocr.insightpulseai.com` | Entra bearer | Managed identity | Doc Intel RBAC |
| Foundry → Odoo | Managed identity | Entra service token | Odoo API key + IP allowlist |
| Databricks → Odoo PG | Service principal | JDBC credentials | PostgreSQL roles (read-only) |

### 7.3 Key Vault Secrets

| Secret Name | Service | Rotation |
|-------------|---------|----------|
| `odoo-admin-password` | Odoo | Manual (break-glass) |
| `odoo-api-key-pulser` | Foundry agents | 90 days |
| `openai-api-key` | Azure OpenAI | 90 days |
| `gemini-api-key` | Creative generation | 90 days |
| `fal-api-key` | Mixed media generation | 90 days |
| `zoho-smtp-user` | Odoo mail | Manual |
| `zoho-smtp-password` | Odoo mail | Manual |
| `pg-odoo-jdbc-password` | Databricks extract | 90 days |
| `doc-intel-endpoint` | OCR module | Static |
| `doc-intel-key` | OCR module | 90 days |

### 7.4 Public vs Authenticated

| Surface | Public? | Data Exposure | Protection |
|---------|---------|--------------|------------|
| Landing page | Yes | Marketing content only | Front Door WAF |
| Ask Pulser | Yes | Approved public docs only | Rate limit, no PII |
| Lead capture API | Yes | Write-only (creates lead) | CAPTCHA + schema validation + rate limit |
| Odoo ERP | No | Full business data | Entra OIDC + Odoo permissions |
| OCR endpoint | No | Document content | Entra bearer + upload size limit |
| Foundry agents | No | Business data via tools | Managed identity + tool-level RBAC |
| Databricks | No | Analytics data | Entra SSO + Unity Catalog ACLs |

### 7.5 Audit Trail

| Event | Audit Surface |
|-------|--------------|
| User login | Entra sign-in logs + Odoo `res.users.log` |
| Odoo record changes | Odoo `auditlog` (OCA module) |
| Agent tool calls | Foundry agent telemetry + Application Insights |
| Document processing | Doc Intel API logs + Odoo `mail.tracking` |
| Data access | Unity Catalog audit logs |
| Secret access | Key Vault diagnostic logs |
| Public API calls | Front Door access logs |

---

## 8. Active vs Retired Service Matrix

### Active

| Service | Plane | Type | Resource |
|---------|-------|------|----------|
| **Odoo CE 19** | ERP | ACA-hosted | `ipai-odoo-dev-web`, `-worker`, `-cron` |
| **Pulser** (6 surfaces) | AI Assistant | Foundry-hosted | Via `ipai-copilot-gateway` |
| **Microsoft Entra ID** | Identity | Azure-native | Tenant-level |
| **Azure Front Door** | Edge | Azure-native | `ipai-fd-dev` |
| **Azure AI Foundry** | AI Platform | Azure-native | `aifoundry-ipai-dev` |
| **Azure AI Document Intelligence** | AI (OCR) | Azure-native | `docai-ipai-dev` |
| **Azure Databricks** | Data | Azure-native | `dbw-ipai-dev` |
| **Azure OpenAI** | AI (LLM) | Azure-native | `oai-ipai-dev` |
| **Azure PostgreSQL** | Database | Azure-native | `pg-ipai-odoo` |
| **Azure Key Vault** | Secrets | Azure-native | `kv-ipai-dev` |
| **Azure Container Apps** | Compute | Azure-native | `ipai-odoo-dev-env` |
| **Azure Container Registry** | Registry | Azure-native | `cripaidev` |
| **Cloudflare** | DNS (DNS-only mode) | External | Current; target: Azure DNS |
| **Azure Monitor** | Observability | Azure-native | Workspace-level |
| **Azure DevOps** | CI/CD | Azure-native | Organization-level |
| **Power BI** | Reporting | Azure SaaS | Consumption only |
| **Unity Catalog** | Governance | Via Databricks | Data lineage + ACLs |

### External Exceptions

| Service | Role | Justification | Boundary |
|---------|------|--------------|----------|
| **Squarespace** | Domain registrar | NS delegation to Cloudflare (current) | Registrar only — no hosting, no DNS records |
| **Zoho Mail** | Domain email | SMTP for `insightpulseai.com` | Mail only — credentials in Key Vault |
| **Gemini API** (direct) | Creative generation | Nano Banana/Imagen/Veo not on Azure OpenAI | API key in Key Vault; via provider router |
| **fal** | Mixed media | Kling/LTX/audio not on Azure | API key in Key Vault; via provider router |
| **GitHub** | Source control | Git hosting + Actions (transitional) | Mirrors to Azure DevOps |

### Retired / Deactivated

| Service | Status | Replacement | Date |
|---------|--------|-------------|------|
| **Cloudflare** (proxy role) | Proxy retired; DNS-only active | Front Door (edge); Azure DNS (target for DNS) | Proxy: 2026-03-25; DNS: TBD |
| **Supabase** (self-hosted VM) | Scaled to zero | Entra (auth), Databricks (data), ACA (functions) | 2026-Q2 |
| **n8n** | Deactivated | Foundry agents + DevOps pipelines | 2026-Q2 |
| **Plane** | Deactivated | Azure DevOps Boards | 2026-Q2 |
| **Shelf** | Deactivated | Odoo Knowledge + Databricks | 2026-Q2 |
| **Standalone CRM** (`ipai-crm-dev`) | Deactivated | Odoo CRM module | 2026-Q2 |
| **Keycloak** (`ipai-auth-dev`) | Never operationalized | Entra ID | 2026-Q2 |
| **Superset** (as primary BI) | Demoted | Power BI (primary), Superset (supplemental) | 2026-03-21 |
| **DigitalOcean** | Retired | Azure | 2026-03-15 |
| **Vercel** | Retired | ACA | 2026-03-11 |
| **Mailgun** | Retired | Zoho SMTP | 2026-03-11 |
| **Mattermost** | Retired | Slack | 2026-01-28 |

---

## 9. Phased Implementation Plan

### Phase 1: Doctrine / SSOT / Auth Pattern (Weeks 1-2)

| # | Task | Owner | Output |
|---|------|-------|--------|
| 1.1 | Create all docs listed in §6.1 | `docs/` | Architecture + governance docs |
| 1.2 | Update all docs listed in §6.2 | `docs/` | Aligned existing docs |
| 1.3 | Create SSOT contract files (§4) | `ssot/contracts/` | 7 contract YAML files |
| 1.4 | Create route registry | `ssot/routes/` | `public_routes.yaml` |
| 1.5 | Define Entra app registrations | `infra/azure/entra/` | Bicep/Terraform for 7 app registrations |
| 1.6 | Enforce Pulser split in CI | `.github/workflows/` | Lint rule: no agent logic in `web/`, no UI in `agents/` |
| 1.7 | (Deferred) Migrate DNS zone to Azure DNS | `infra/azure/dns/` | Zone file + NS delegation — only when ready |
| 1.8 | Update `subdomain-registry.yaml` | `infra/dns/` | Align with Cloudflare DNS-only + Front Door edge |
| 1.9 | Document Cloudflare proxy retirement | `docs/` | Decommission record for proxy role (done) |

### Phase 2: Integration (Weeks 3-5)

| # | Task | Owner | Output |
|---|------|-------|--------|
| 2.1 | Build API facade (lead capture, demo booking) | `web/packages/api-facade/` | Thin ACA container |
| 2.2 | Wire landing CTAs → API facade → Odoo | `web/ipai-landing/` | Working lead flow |
| 2.3 | Configure Entra OIDC for Odoo | `addons/ipai/ipai_auth_oidc/` | Odoo OAuth provider |
| 2.4 | Build Foundry tool bindings | `infra/azure/foundry/` | Tool definitions for Odoo API |
| 2.5 | Build `ipai_doc_intelligence` module | `addons/ipai/ipai_doc_intelligence/` | OCR intake in Odoo |
| 2.6 | Wire Ask Pulser through copilot gateway | `web/packages/pulser-widget/` + `agents/` | Public assistant flow |
| 2.7 | Deploy Pulser widget in Odoo | `addons/ipai/ipai_ai_copilot/` | Authenticated assistant |

### Phase 3: Data + Hardening (Weeks 6-8)

| # | Task | Owner | Output |
|---|------|-------|--------|
| 3.1 | Configure Databricks JDBC extract | `data-intelligence/` | Incremental extract from pg-ipai-odoo |
| 3.2 | Build DLT pipeline (Bronze → Silver → Gold) | `data-intelligence/pipelines/` | Governed data flow |
| 3.3 | Configure Power BI connection | `data-intelligence/reports/` | Business dashboards |
| 3.4 | Enable Azure Monitor + App Insights | `infra/azure/monitoring/` | Observability baseline |
| 3.5 | Run creative eval benchmarks | `agents/evals/creative/` | Benchmark report |
| 3.6 | Security hardening (VNet integration, NSG) | `infra/azure/network/` | Network isolation |
| 3.7 | Delete retired ACA apps | `infra/azure/aca/` | Clean container inventory |
| 3.8 | Delete Supabase VM | `infra/azure/` | Resource cleanup |
| 3.9 | Go-live checklist execution | `docs/architecture/GO_LIVE_CHECKLIST.md` | Production gate |

---

## 10. Minimal Patch Plan by File

### New Files to Create

```
docs/architecture/PUBLIC_TO_ODOO_INTEGRATION_FLOW.md
docs/architecture/EDGE_DNS_MAIL_AUTHORITY.md
docs/governance/REPO_PURPOSES.md
ssot/routes/public_routes.yaml
ssot/contracts/api_facade.yaml
ssot/contracts/foundry_tools.yaml
ssot/contracts/odoo_integration.yaml
ssot/contracts/document_ocr.yaml
ssot/contracts/identity.yaml
ssot/contracts/analytics_pipeline.yaml
ssot/external/dependencies.yaml
infra/README.md
infra/azure/dns/README.md
```

### Existing Files to Update

```
docs/architecture/AZURE_NATIVE_TARGET_STATE.md       → Aligned with target-state (done)
docs/architecture/ACTIVE_PLATFORM_REFERENCE_MODEL.md  → Align to this master doc
docs/architecture/REPO_OWNERSHIP_DOCTRINE.md          → Add API facade; DNS authority
docs/architecture/RETIRED_SERVICES.md                 → Cloudflare proxy retired; DNS active (done)
docs/architecture/ACTIVE_PLATFORM_BOUNDARIES.md       → Cloudflare DNS-only in active (done)
ssot/architecture/services.yaml                       → Cloudflare DNS-only as active (done)
infra/dns/subdomain-registry.yaml                     → Align with Cloudflare DNS-only mode
```

---

## 11. Risks / Assumptions / Open Questions

### Risks

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Azure DNS propagation delay (when migration happens) | Temporary DNS resolution failures | Pre-provision Azure DNS zone; lower TTLs 48h before cutover; dual-stack briefly; migration is deferred |
| Odoo OAuth OIDC misconfiguration | Users locked out of ERP | Keep basic login as fallback until Entra flow is verified in staging |
| Foundry Agent Service preview limitations | Agent tool bindings may change | Abstract tool calls behind interface; pin API version |
| Document Intelligence model accuracy on PH tax forms | Misextracted fields | Train custom model on BIR form samples; human review gate |
| Databricks JDBC extract performance on large Odoo tables | Slow incremental loads | Partition by `write_date`; use change data capture if available |

### Assumptions

1. Squarespace supports NS record delegation (currently to Cloudflare; future Azure DNS if migrated)
2. Zoho Mail MX/SPF/DKIM records work on any standards-compliant DNS (currently Cloudflare, compatible with Azure DNS)
3. Odoo 19 `auth_oauth` module supports Microsoft Graph OIDC userinfo endpoint (confirmed per Odoo docs)
4. Foundry Agent Service supports custom tool definitions via function calling (confirmed per Azure docs)
5. Document Intelligence supports PH-specific document formats (BIR 2307, OR, SI) via custom models

### Open Questions

1. **Conditional Access scope**: Which Entra CA policies apply to which Odoo user groups? (Needs security policy input)
2. **API facade hosting**: Separate ACA app or sidecar on `ipai-website-dev`? (Recommend separate for isolation)
3. **Databricks cluster sizing**: What is the expected data volume from Odoo for JDBC extract? (Needs Odoo DBA input)
4. **Creative generation billing**: Gemini/fal usage caps and cost controls per Pulser Studio surface? (Needs budget input)

---

## 12. Verification Checklist

| # | Check | Method | Pass Criteria |
|---|-------|--------|---------------|
| 1 | Odoo remains transactional SoR | Review all write paths | All business state writes go to Odoo, never Foundry/Databricks |
| 2 | Entra is auth, not business authorization | Review Odoo permissions | `res.groups` + `ir.rule` unchanged; Entra provides SSO only |
| 3 | Foundry is agent plane, not record plane | Review Foundry tool bindings | All tools are read or delegated-write (via Odoo API), no direct DB |
| 4 | Document Intelligence is OCR plane | Review document flow | Doc Intel extracts; Odoo stores records + attachments |
| 5 | Databricks is primary data plane | Review data flows | No Fabric dataflows replace DLT; Power BI = consumption only |
| 6 | Front Door is edge/public entry | Review route table | All public traffic through Front Door; no direct ACA exposure |
| 7 | Repo ownership is non-overlapping | Grep for violations | No agent logic in `web/`; no UI in `agents/`; no Azure IaC outside `infra/` |
| 8 | Retired services not in active architecture | Grep for Supabase/n8n/Plane/Shelf in active configs | Zero references in active service configs |
| 9 | DNS authority operational | `dig insightpulseai.com NS` | Returns Cloudflare NS (current) or Azure DNS NS (after migration) |
| 10 | Entra app registrations exist | Azure CLI `az ad app list` | 7 app registrations per §7.1 |
| 11 | Key Vault secrets provisioned | Azure CLI `az keyvault secret list` | All secrets from §7.3 present |
| 12 | No browser-to-Odoo coupling | Review landing page code | All Odoo calls go through API facade, never direct JSON-RPC |

---

*This document is the single decisive target-state model. All other architecture docs align to it.*
*Produced: 2026-03-25*
