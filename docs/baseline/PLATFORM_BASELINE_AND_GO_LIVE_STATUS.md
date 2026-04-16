# Platform Baseline and Go-Live Status (v2)

> Evidence-based audit, 2026-04-16. Conservative: no claim without proof.
> Status model: planned | repo-defined | provisioned | configured | verified-nonprod | verified-prod | live | blocked | unknown | stale | broken
> Readiness model: prerequisite-pending | readiness-review-pending | deployment-ready | cutover-ready | go-live-ready | stabilization-required | blocked | unknown
> v2 additions: sections 10-11 expanded; reporting plane; cutover assessment; readiness matrix; source-quality policy

---

## 1. Executive Summary

InsightPulseAI is a multi-plane platform built on Odoo CE 18 + Azure-native services. The platform is architecturally ambitious with extensive SSOT documentation but is NOT production-ready for customer-facing ERP operations.

**What is genuinely live today (verified 2026-04-16):**
- Odoo CE 18 base install on Azure Container Apps returning HTTP 200 at `erp.insightpulseai.com` with health check passing
- CSS/JS assets serving correctly (HTTP 200 on `/web/assets/d8d2511/web.assets_frontend.min.css`)
- Three static/CMS web surfaces (InsightPulseAI, PrismaLab, W9 Studio) returning HTTP 200
- PrismaLab RAG gateway functional
- DNS via Azure DNS resolving correctly for all tested domains
- PostgreSQL 16 (General Purpose D4s_v3) provisioned and Ready, 121 tables in `odoo` DB
- `ir_attachment.location` set to `db` (ephemeral filestore fix applied this session)
- Databricks workspace provisioned with Unity Catalog enabled
- Container registry with 20 repositories
- 4 AI model deployments active on ipai-copilot-resource

**What is NOT live despite documentation suggesting otherwise:**
- Only 12 base Odoo modules installed (no accounting, CRM, project, HR, or any ipai_* module)
- Zero custom ipai_* modules deployed to production runtime
- The `odoo_dev` database does not exist on Azure PG
- `odoo_staging` database exists but has 0 tables
- No Odoo business functionality is operational (no GL, AP/AR, invoicing, BIR compliance)
- No SSO/OAuth configured in the running Odoo instance
- No CI/CD pipeline has been verified as successfully deploying to production
- No semantic models, Power BI reports, or Fabric mirroring are operational
- Azure Front Door exists on Sub1 only, not on the Sponsored sub where the primary Odoo ACA lives
- No monitoring/alerting verified as functional
- Azure DevOps reporting plane (dashboards, analytics, OData) unverified

**Critical context from this session:** Odoo prod was DOWN for 3 days (2026-04-13 to 2026-04-16) with startup probe failing 18,526+ times. Root causes fixed: wrong DB_HOST, env var collision (PORT/USER), empty database (base not installed), ephemeral filestore. DNS was cut from blackstone (Sub 1) to blackriver (Sponsored sub) during this session.

**Go-live verdict: NOT READY. The platform is at infrastructure-provisioned stage, not application-configured or business-operational stage.**

---

## 2. Authority Model / Sources of Truth

| Layer | File/System | Role | Trust Level |
|---|---|---|---|
| Runtime truth | Azure live resources | What is actually deployed | Highest |
| Environment contract | `ssot/odoo/environment-contract.yaml` | Intended environment map | High (corrected this session) |
| Runtime contract | `ssot/odoo/runtime_contract.yaml` | Container/addon paths | Medium (references stale env `salmontree`) |
| DNS authority | `ssot/infrastructure/dns_mail_authority.yaml` | DNS/mail ownership | Accurate |
| Tenant registry | `ssot/tenants/tenant-registry.yaml` | Tenant model | Accurate (aspirational) |
| Identity boundary | `ssot/identity/identity-boundary-policy.yaml` | Identity type rules | Accurate |
| Enterprise apps state | `ssot/identity/enterprise-apps.runtime-state.yaml` | Entra app inventory | Observed evidence |
| Integration catalog | `ssot/odoo/odoo-integrations.catalog.yaml` | Integration inventory | Accurate for CE18 catalog |
| Agent interop | `ssot/governance/agent-interop-matrix.yaml` v2 | A2A/MCP/Agent365 routes | Accurate for design |
| Review gates | `ssot/assurance/review-gates.yaml` | Phase gate definitions | Active |
| Success measures | `ssot/assurance/success-measures.contract.yaml` | Health rating system | Active |
| Governance | `ssot/governance/` (30+ files) | Policy and strategy | Heavily aspirational |
| CLAUDE.md | Root + nested | Agent behavior doctrine | Accurate for doctrine; overstates readiness |
| Agent memory | `~/.claude/projects/*/memory/` | Operational notes | Mixed accuracy |

**Source-quality policy (new in v2):**
- Official docs (Microsoft Learn, Odoo docs, Azure REST API) > Blogs > Forums > Screenshots
- Agent memory is operational notes, NOT canonical architecture
- Screenshots are point-in-time, NOT refreshable evidence
- Reporting evidence requires: data recency timestamp, query source, at least one meaningful metric

**Key finding**: Many SSOT files describe intended state as if it were current. The `environment-contract.yaml` correctly distinguishes planned vs active, but the broader doc corpus does not.

---

## 3. Repo Topology and Ownership Boundaries

| Path | Purpose | File Count (approx) | Actively Used |
|---|---|---|---|
| `addons/ipai/` | 55 custom Odoo modules | ~2000 | Repo-only; 0/55 deployed |
| `addons/oca/` | OCA modules (git submodules) | sparse | Not hydrated at runtime |
| `agents/skills/` | ~180 agent skill definitions | ~1000 | Repo-only knowledge; audit grade D (44/100) |
| `agent-platform/` | Agent runtime engine | ~200 | Partially deployed (gateway) |
| `apps/` | Application packages | ~100 | Partially deployed |
| `ssot/` | 47 subdirectories, ~100+ YAML | ~150 | Reference only |
| `infra/azure/modules/` | Bicep IaC modules | ~10 | Used for provisioning |
| `infra/ssot/databricks/` | Databricks tooling contracts | ~5 | Reference only |
| `azure-pipelines/` | 15 pipeline definitions | 15 | Unknown run success rate |
| `deploy/` | Deployment artifacts | varies | Used for R3 provisioning |
| `docs/` | Documentation | ~500 | Reference only |
| `spec/` | 76 spec bundles | ~400 | Planning artifacts |

**Ownership boundaries (per ssot/org/repo-map.yaml):**
- Repo OWNS: Odoo config, custom modules, agent definitions, SSOT governance, IaC, CI/CD definitions
- Repo does NOT OWN: Azure runtime state, ADO board data, Entra tenant config, Databricks workspace state, Fabric/Power BI config

---

## 4. Environment Map

| Environment | Database | ACA App | URL | Status | Evidence |
|---|---|---|---|---|---|
| Production | `odoo` (121 tables, 12 modules) | `ca-ipai-odoo-web-dev` (Sponsored/blackriver) | `erp.insightpulseai.com` | Bare install | HTTP 200, health pass, assets serving |
| Staging | `odoo_staging` (0 tables) | None dedicated | `erp-staging.insightpulseai.com` | planned | DNS not created; DB empty |
| Dev (Azure) | `odoo_dev` DOES NOT EXIST | `ipai-odoo-dev-web` (Sub1/blackstone) | direct ACA FQDN | stale | ACA exists but DB missing; this is an older parallel |
| Dev (Local) | `odoo_dev` (local PG) | N/A | `localhost:8069` | unknown | Depends on developer machine |

**Critical finding**: The naming `ca-ipai-odoo-web-dev` serves production (`erp.insightpulseai.com`). The Sub1 `ipai-odoo-dev-web` appears to be an older/parallel deployment. Two ACA environments exist across two subscriptions with overlapping names.

---

## 5. Runtime/Platform Architecture

### Azure Subscriptions

| Subscription | ID | Role | Key Resources |
|---|---|---|---|
| Microsoft Azure Sponsorship | `eba824fb-332d-4623-9dfb-2c9f7ee83f4e` | Primary (canonical) | PG (pg-ipai-odoo), ACR, KV (kv-ipai-dev-sea), ACA (4 apps), Databricks, Purview, Service Bus, VNet, Backup Vault, AI Search, Storage (6), MI (6) |
| Azure subscription 1 | `536d8cf6-89e1-4815-aef3-d5f2c5f4d070` | Secondary (decommissioning) | ACA (15 apps), AFD, KV (kv-ipai-dev), AI services (5), Redis, Function App, Storage, Log Analytics, MI (7) |

### Container Apps (19 total across both subs)

**Sponsored sub (4 apps on blackriver-f68f8a9b + whitedesert-54fce6ca):**

| App | RG | Environment | FQDN | Purpose |
|---|---|---|---|---|
| `ca-ipai-odoo-web-dev` | rg-ipai-dev-odoo-sea | blackriver | `...blackriver-f68f8a9b.sea.azurecontainerapps.io` | Primary Odoo (erp.insightpulseai.com) |
| `ipai-prismalab-web` | rg-ipai-stg-odoo-runtime | whitedesert | `...whitedesert-54fce6ca.sea.azurecontainerapps.io` | PrismaLab site |
| `ipai-website-dev` | rg-ipai-stg-odoo-runtime | whitedesert | `...whitedesert-54fce6ca.sea.azurecontainerapps.io` | IPAI main site |
| `ipai-w9studio-dev` | rg-ipai-stg-odoo-runtime | whitedesert | `...whitedesert-54fce6ca.sea.azurecontainerapps.io` | W9 Studio site |

**Sub1 (15 apps on blackstone-0df78186 + bluemeadow-b895bd2e):**

| App | Purpose | Notes |
|---|---|---|
| `ipai-odoo-dev-web` | Older Odoo instance | Parallel to Sponsored sub Odoo |
| `ipai-odoo-dev-worker` | Odoo background worker | Internal |
| `ipai-odoo-dev-cron` | Odoo cron jobs | Internal |
| `ipai-copilot-gateway` | Pulser gateway | Internal endpoint |
| `ipai-mcp-dev` | MCP server | |
| `ipai-odoo-mcp` | Odoo MCP | Internal endpoint |
| `ipai-prismalab-gateway` | RAG gateway | |
| `ipai-bot-proxy-dev` | M365 bot proxy | |
| `ipai-release-manager` | Release manager | Internal endpoint |
| `ipai-ocr-dev` | OCR service | |
| `ipai-odoo-connector` | Odoo connector | |
| `ipai-website-dev` | Duplicate website | Same name as Sponsored |
| `ipai-w9studio-dev` | Duplicate W9 | Same name as Sponsored |
| `w9studio-landing-dev` | Landing page | |
| `ipai-pg-mcp-server-*` | PG MCP server | bluemeadow env |

### PostgreSQL

| Server | SKU | Storage | Version | DBs | Status |
|---|---|---|---|---|---|
| `pg-ipai-odoo` | Standard_D4s_v3 (General Purpose) | 128 GiB | 16 | `odoo` (121 tables), `odoo_staging` (0 tables), system DBs | Ready |

Note: `odoo_dev` does not exist on this server. Environment contract correctly says it is local-only.

### AI Services (Sub1, rg-data-intel-ph)

| Resource | Kind | Location | Status |
|---|---|---|---|
| `ipai-copilot-resource` | AIServices | East US 2 | Live (4 model deployments) |
| `pulser-intel-resource` | AIServices | South Central US | Provisioned |
| `pulser-resource` | AIServices | Central US | Provisioned |
| `admin-8376-resource` | AIServices | Australia East | Provisioned |
| `docai-ipai-dev` | FormRecognizer | East US 2 | Provisioned |

### Foundry Model Deployments (on ipai-copilot-resource)

| Deployment | Model | Capacity | Status |
|---|---|---|---|
| gpt-4.1 | gpt-4.1 | 50 TPM | Deployed |
| gpt-4.1-mini-20260415 | gpt-4.1-mini | 10 TPM | Deployed |
| text-embedding-3-small | text-embedding-3-small | 120 TPM | Deployed |
| w9-pulser | gpt-4o-mini | 10 TPM | Deployed |

### Other Infrastructure

| Resource | Sub | Status |
|---|---|---|
| Azure Front Door `afd-ipai-dev` | Sub1 | Active |
| Key Vault `kv-ipai-dev` | Sub1 | Provisioned |
| Key Vault `kv-ipai-dev-sea` | Sponsored | Provisioned |
| ACR `acripaiodoo` | Sponsored | Active, 20 repos |
| Databricks `dbw-ipai-dev` | Sponsored | Succeeded, UC enabled |
| Purview `pv-ipai-dev-sea` | Sponsored | Provisioned |
| AI Search `srch-ipai-dev-sea` | Sponsored | Provisioned |
| AI Search `srch-ipai-dev` | Sub1 | Provisioned (PrismaLab index) |
| Service Bus `sb-ipai-dev-sea` | Sponsored | Provisioned |
| Redis `cache-ipai-dev` | Sub1 | Provisioned |
| Backup Vault `bvault-ipai-dev-sea` | Sponsored | Provisioned |
| VNet `vnet-ipai-dev-sea` | Sponsored | Provisioned |
| VNet `vnet-ipai-dev` | Sub1 | Provisioned |

---

## 6. Identity / Auth / Tenant Boundary Model

### Identity Types

| Type | Description | Source |
|---|---|---|
| Entra user principal | Interactive human user | ssot/identity/identity-boundary-policy.yaml |
| Managed identity | Service-to-service (ACA, Functions, Foundry) | ssot/identity/identity-boundary-policy.yaml |
| App principal | Entra app registration (non-MI) | ssot/identity/identity-boundary-policy.yaml |
| Entra group-mapped | Group-based role mapping for BI/finance | ssot/identity/identity-boundary-policy.yaml |

### Enterprise Apps vs App Registrations vs Customer Tenancy

**Enterprise apps (11 observed in Entra):**
These are provider-side identity surfaces. They do NOT define customer tenant boundaries.

| App | Classification | Role |
|---|---|---|
| InsightPulse AI - Odoo Login | odoo_sso_enterprise_app | Browser login surface |
| ipai-copilot-gateway | internal_api_enterprise_app | Internal gateway surface |
| Databricks | external_platform_enterprise_app | Analytics workspace |
| GitHub Enterprise Cloud SAML SSO | external_saas_sso | Org SAML (cert expires 2028-03-30) |
| Zoho / Zoho Mail Admin | external_saas | Email integration |
| Microsoft Graph CLI Tools | microsoft_platform | CLI tooling |
| ipai-n8n-entra | deprecated | Flagged for deletion |

**App registrations (21 total):** Tracked separately from enterprise apps. Not enumerated in this audit.

**Customer tenancy model:**
- 4 tenants defined in `ssot/tenants/tenant-registry.yaml` using `res.company`
- IPAI (company 1, provider), W9 Studio (company 2, branch entity), OMC (company 3, pending), TBWA\SMP (company 4, prospect)
- Only IPAI (company 1) likely exists given bare Odoo install

### Google Workspace Boundary

W9 Studio uses Google Workspace on domain `w9studio.net`. This is a **collaboration workspace**, NOT a tenant boundary:
- Users: accounts@, finance@, business@ (w9studio.net)
- Role: email, calendar, docs, directory, admin console
- Identity authority: secondary (Entra is primary)
- Does NOT define customer data scope or business authorization

### Tenant ID Evidence

| Source | Tenant ID | Trust |
|---|---|---|
| `az account list` | `402de71a-87ec-4302-a609-fb76098d1da7` | Highest (live CLI) |
| `runtime_contract.yaml` | `402de71a-87ec-4302-a609-fb76098d1da7` | Matches CLI |
| `odoo-azure-oauth.yaml` | `9ba5e867-1fb2-41cb-8e94-7d7a2b8fe4a9` | WRONG — must be corrected |

---

## 7. Data and Analytics Architecture

| Component | Intended State | Actual State | Status |
|---|---|---|---|
| **Databricks workspace** | Bronze/Silver/Gold medallion | Workspace provisioned, UC enabled | provisioned |
| - Workspace access | Developer notebooks, SQL analytics | Workspace running | provisioned |
| - Admin console | Cluster policies, access control | Not assessed | unknown |
| - Developer tooling | VS Code ext, CLI, Databricks SDK | Contracts at `infra/ssot/databricks/` | repo-defined |
| - Apps runtime | Databricks Apps hosting | Not assessed | unknown |
| **Unity Catalog** | 3 catalogs (dev/staging/prod), 5 schemas each | Created per memory | configured (unverified) |
| **DLT pipelines** | CDM export (6 entities) | Created per memory, not run | repo-defined |
| **Fabric workspace** | `fcipaidev` for mirroring | Trial may expire ~2026-05-20 | unknown |
| **Power BI** | Primary BI surface | Pro trial expires ~2026-05-20; no models | planned |
| **Purview** | Metadata governance | Provisioned | provisioned |
| **AI Search** | RAG indexes | `prismalab-rag-v1` index per memory | configured |
| **Semantic models** | Gold layer serving | None published | planned |

### Databricks Distinctions (new in v2)

The Databricks footprint has four distinct surfaces:
1. **Workspace** (notebook/SQL development) -- provisioned
2. **Admin console** (governance, cluster policies, access control) -- not assessed
3. **Developer tooling** (VS Code extension, CLI, SDK) -- contract defined at `infra/ssot/databricks/developer-tooling.contract.yaml`
4. **Apps runtime** (Databricks Apps for hosting dashboards/tools) -- not assessed

These are tracked separately because workspace provisioning does not imply admin governance or developer tooling readiness.

---

## 8. Agent / Pulser Runtime Architecture

| Component | Intended State | Actual State | Status |
|---|---|---|---|
| Pulser (custom agent engine) | Multi-agent policy-gated copilot | Codebase exists; gateway deployed | repo-defined + partial deploy |
| Agent interop matrix (v2) | A2A + MCP + Agent365 protocol | Committed, 8+ agents defined | repo-defined |
| Three-protocol model | A2A (agent-to-agent), MCP (tools), Agent365 (M365) | Documented | repo-defined |
| ipai-copilot-gateway | Internal ACA, Foundry-backed | Deployed on Sub1 (internal) | provisioned |
| ipai-prismalab-gateway | RAG gateway | Deployed on Sub1 | live (HTTP 200) |
| ipai-bot-proxy-dev | M365 Teams bot proxy | Deployed on Sub1 | provisioned |
| ipai-odoo-mcp | Odoo MCP server | Deployed on Sub1 (internal) | provisioned |
| ipai-release-manager | Release automation | Deployed on Sub1 (internal) | provisioned |
| Scrum Master agent | ADO integration specialist | Spec/skill 100%; code 50%; control 0% (65/100) | repo-defined |
| Agent skills (180+) | Specialist agent skills | Repo-only knowledge; audit grade D (44/100) | repo-defined |
| Odoo copilot module | `ipai_odoo_copilot` in Odoo | Not installed in running Odoo | repo-defined |
| Agent envelopes | Standard request/result format | Contracts at `agent-platform/contracts/` | repo-defined |

### agents/ Repo Health

The `agents/` directory audit scored **D (44/100)** with:
- 22 directories canonical (keep)
- 12 directories need migration to `agent-platform/` (boundary violations)
- 17 directories should be removed (deprecated/consolidated)
- 613 deprecated platform references across 157 files

---

## 9. Integrations and External Systems

| Integration | Intended State | Actual State | Status |
|---|---|---|---|
| Zoho SMTP | Outbound email from Odoo | SSOT configured; runtime unverified | unknown |
| Entra OIDC | SSO for Odoo web | Enterprise app registered; auth_oauth not installed | repo-defined |
| Meta CAPI | `func-ipai-meta-capi` Function App | Provisioned on Sub1 | provisioned |
| Slack | Agent notifications | SSOT active; runtime unverified | unknown |
| Azure Doc Intelligence | Invoice/receipt OCR | `docai-ipai-dev` + `ipai-ocr-dev` ACA | provisioned |
| Vercel GitHub App | Should be uninstalled | Still installed (deprecated) | stale |

### Integration Boundary Policy

Per `ssot/odoo/integration-boundary-policy.yaml` and `odoo-integrations.catalog.yaml`:
- CE18 native integrations checked first (payments: PayPal, Xendit; mail: Outlook/Gmail plugins)
- OCA for gaps not covered by CE
- `ipai_*` bridges only for Azure/Foundry service connections
- 14 payment providers available in CE18 catalog; 0 configured in running instance

---

## 10. Azure DevOps Reporting / Portfolio Visibility

**Separate evidence file:** `docs/baseline/azure_devops_reporting_status.yaml`

### Portfolio Planning (ADO Boards)

| Metric | Value | Source | Verified |
|---|---|---|---|
| Epics | 23 (normalizing to 9) | Agent memory | Not re-verified |
| Issues | 120+ | Agent memory | Not re-verified |
| Tasks | 250+ | Agent memory | Not re-verified |
| Iterations | 5 (R1 active) | Agent memory | Not re-verified |
| Area paths | 9 (normalized) | Agent memory | Not re-verified |

### Reporting Surfaces

| Surface | Status | Evidence |
|---|---|---|
| ADO Dashboards | unknown | No dashboards verified |
| ADO Analytics views | unknown | Not queried |
| OData endpoint | unknown | Not queried |
| Power BI + ADO integration | unknown | No semantic model connecting ADO data |
| Pipeline analytics | unknown | No run history collected |
| Test results analytics | unknown | No test plans verified |

### Source-Quality Policy for Reporting Evidence

| Source Type | Trust Level | Acceptable As |
|---|---|---|
| Official docs (MS Learn, Azure REST API) | Highest | Architecture reference |
| ADO REST API / OData query results | High | Live evidence |
| Azure Portal screenshots | Medium | Point-in-time only (not refreshable) |
| Agent memory notes | Low | Operational context only |
| Blog posts / community forums | Low | Design inspiration only |

**Reporting evidence requirements:**
- Evidence must be refreshable (not a screenshot)
- Must show data recency (last refresh timestamp)
- Must show query source (OData, REST API, direct query)
- Must include at least one meaningful metric

**Verdict:** The ADO reporting plane cannot be used as evidence for go-live readiness until at least one refreshable report with live data is demonstrated.

---

## 11. Go-Live Readiness and Cutover Assessment

**Separate structured file:** `docs/baseline/go_live_readiness_matrix.yaml`

### Readiness by Stage

| Stage | Subsystems | Count |
|---|---|---|
| **blocked** | Accounting, custom modules, SSO, finance cutover, Power BI | 5 |
| **prerequisite-pending** | ERP core, Databricks, Pulser, monitoring, backup, tenant boundary | 6 |
| **unknown** | Fabric, CI/CD, ADO reporting | 3 |
| **deployment-ready** | Azure infrastructure | 1 |
| **stabilization-required** | Web surfaces | 1 |
| **cutover-ready** | (none) | 0 |
| **go-live-ready** | (none) | 0 |

### Finance/Accounting Cutover Checks (new in v2)

ALL checks below are BLOCKED because the `account` module is not installed:

| Check | Status | Evidence |
|---|---|---|
| Opening balances loaded | N/A | No account module |
| AR clearing complete | N/A | No account module |
| AP clearing complete | N/A | No account module |
| Trial balance reconciled | N/A | No account module |
| Bank clearing accounts | N/A | No account module |
| Multi-currency configured | N/A | No account module |
| Chart of accounts validated | N/A | No account module |
| Tax configuration (BIR) | N/A | 7+ BIR modules in repo; none installed |
| Payment providers configured | N/A | PayPal/Xendit available in CE; unconfigured |
| Fiscal year defined | N/A | No account module |

### Review Gate Assessment (per ssot/assurance/review-gates.yaml)

| Phase | Gate Review | Status |
|---|---|---|
| Discover | Discover checkpoint | Partially complete (scope/architecture docs exist; gap-fit incomplete) |
| Initiate | Solution blueprint review | Partially complete (architecture exists; env topology validated) |
| Implement | Implementation progress review | NOT STARTED (no sprint demos, no test coverage) |
| Prepare | Go-live readiness review | NOT STARTED (no UAT, no cutover plan, no mock go-live) |
| Operate | Hypercare exit review | NOT STARTED |

### Success Measure Rating

Per `ssot/assurance/success-measures.contract.yaml`: **RED**
- Trigger: "Blocking issue identified in mandatory review" (zero business modules)
- Trigger: "Go-live date at risk with no recovery plan"

---

## 12. Production / Go-Live Status by Subsystem

| Subsystem | Status | Evidence | Go-Live Criticality |
|---|---|---|---|
| **Odoo ERP (Finance/GL/AP/AR)** | **NOT LIVE** | 12 base modules only; no accounting | P0 |
| **Custom ipai_* modules** | **NOT LIVE** | 55 in repo; 0 installed | P0 |
| **OCA modules** | **NOT LIVE** | Not hydrated or installed | P1 |
| **Odoo SSO** | **NOT LIVE** | auth_oauth not installed; Entra app registered | P1 |
| **DNS resolution** | **LIVE** | dig confirms correct CNAME for erp, prismalab, www | -- |
| **TLS certificates** | **LIVE** | HTTPS works, managed certs on ACA | -- |
| **PrismaLab web** | **LIVE** | HTTP 200, content served | P2 |
| **PrismaLab RAG gateway** | **LIVE** | Gateway deployed, search index exists | P2 |
| **Main website** | **LIVE** | HTTP 200 | P3 |
| **W9 Studio site** | **LIVE** | HTTP 200 | P3 |
| **PostgreSQL** | **PROVISIONED** | Server Ready; prod DB has 121 tables (base only) | P0 |
| **Staging environment** | **NOT CONFIGURED** | DB exists but 0 tables; no ACA; no DNS | P1 |
| **Azure Front Door** | **PARTIAL** | AFD on Sub1 only; primary Odoo on Sponsored sub | P1 |
| **Databricks** | **PROVISIONED** | Workspace running; no pipelines executed | P2 |
| **Power BI** | **NOT CONFIGURED** | Trial license, no semantic models | P2 |
| **Fabric mirroring** | **UNKNOWN** | Trial may be expiring | P2 |
| **CI/CD pipelines** | **UNVERIFIED** | 15 pipeline files; no run success evidence | P0 |
| **Monitoring/observability** | **PROVISIONED** | App Insights, Log Analytics, 3 alerts; no dashboards | P1 |
| **BIR tax compliance** | **NOT LIVE** | 7+ BIR modules in repo; none installed | P1 (PH go-live) |
| **Agent/Pulser runtime** | **PARTIALLY DEPLOYED** | Gateway ACA exists; no e2e agent flow | P2 |
| **Backup/DR** | **PROVISIONED** | Backup Vault exists; no policies verified | P1 |
| **Key Vault secrets** | **UNKNOWN** | KV exists; secret population unverified | P0 |
| **ADO reporting plane** | **UNKNOWN** | No dashboards, analytics, or OData verified | P2 |
| **Finance cutover** | **BLOCKED** | All checks N/A without accounting module | P0 |

---

## 13. Critical Blockers and Missing Evidence

### P0 Blockers (must resolve before any go-live)

1. **Zero Odoo business modules installed.** The production database has only 12 base framework modules. No accounting (`account`), CRM, project, HR, or custom `ipai_*` modules.

2. **No verified deployment pipeline.** No evidence that any Azure Pipeline has successfully built a container image with custom modules and deployed it to the production ACA app.

3. **Finance cutover impossible.** All finance/accounting cutover checks (opening balances, AR/AP clearing, trial balance, bank clearing, multi-currency, chart of accounts, fiscal year) are blocked by the missing accounting module.

4. **Key Vault secret population unverified.** Two Key Vaults exist. Whether they contain required secrets (PG password, Zoho SMTP creds, OAuth client secret) is unverified. Known regression: plaintext PG password in ACA env vars.

5. **Two-subscription architecture creates routing confusion.** Primary Odoo ACA on Sponsored sub; AFD, KV, AI services on Sub1. Cross-sub private endpoint connectivity unproven.

### P1 Blockers

6. **Entra tenant ID conflict in SSOT.** `runtime_contract.yaml` says `402de71a` (matches `az account`); `odoo-azure-oauth.yaml` says `9ba5e867` (wrong).

7. **No staging environment.** `odoo_staging` DB is empty (0 tables). No staging ACA app. No staging DNS record.

8. **ACA environment naming confusion.** `ca-ipai-odoo-web-dev` (a "-dev" named app) serves production. `ipai-odoo-dev-web` on Sub1 is an older parallel.

9. **Stale SSOT references.** `runtime_contract.yaml` references `salmontree-b7d27e19` which is not current (blackriver or blackstone are current).

10. **No backup/DR verification.** Backup Vault provisioned but no policies or tested restores.

### P2 Risks

11. **Power BI Pro trial expiring ~2026-05-20.** BI surface will stop working.
12. **Fabric trial expiring ~2026-05-20.** Mirroring pipeline will stop.
13. **Sponsored sub quota issue (#715-123420)** blocks deploying additional AI models.
14. **55 custom modules, 0/55 pass doctrine checklist.**
15. **180+ agent skills are knowledge definitions only** -- no runtime agent framework executing them.
16. **ADO reporting plane entirely unverified** -- no dashboards, analytics, or OData connections confirmed.
17. **Vercel GitHub App still installed** -- deprecated, needs uninstall.
18. **Duplicate resources across subscriptions** (website, W9, AI Search, KV, managed identity on both subs).

---

## 14. Recommended Path to Clean Go-Live

Priority order -- each step must produce verifiable evidence:

1. **Build and verify a deployment pipeline.** Get one Azure Pipeline to successfully: build Odoo container with `account` + core modules -> push to ACR -> deploy to ACA -> verify health + module list at runtime.

2. **Install core Odoo modules.** At minimum: `account`, `sale`, `purchase`, `crm`, `project`, `hr`, `auth_oauth`. Verify via `/web/session/modules` endpoint.

3. **Resolve the two-subscription architecture.** Either consolidate to one sub or document cross-sub network topology with verified private endpoint connectivity.

4. **Configure SSO.** Install `auth_oauth`, configure Entra provider record, verify login flow. Fix tenant ID conflict first.

5. **Run finance cutover preparation.** Load chart of accounts, configure fiscal year, load opening balances, configure payment providers.

6. **Stand up staging.** Initialize `odoo_staging` with modules, deploy staging ACA, create DNS record.

7. **Verify Key Vault secrets.** Confirm all required secrets exist. Rotate the password exposed this session.

8. **Configure monitoring.** Set up ACA health alerts, PG connection/CPU alerts, error rate dashboard.

9. **Install and verify one ipai_* module.** Start with `ipai_odoo_copilot` as proof of custom module pipeline.

10. **Establish ADO reporting.** Create at least one refreshable dashboard with sprint burndown and pipeline health metrics.

---

## 15. Appendix: Evidence References

| Evidence | Source | Date | Result |
|---|---|---|---|
| Odoo health check | `curl erp.insightpulseai.com/web/health` | 2026-04-16 | HTTP 200, `{status: pass}` |
| Odoo login page | `curl erp.insightpulseai.com/web/login` | 2026-04-16 | HTTP 200, `<html>` |
| CSS assets serving | `curl erp.insightpulseai.com/web/assets/d8d2511/web.assets_frontend.min.css` | 2026-04-16 | HTTP 200 |
| DNS `erp` | `dig +short` | 2026-04-16 | `ca-ipai-odoo-web-dev.blackriver-f68f8a9b...` -> `104.43.98.178` |
| DNS `prismalab` | `dig +short` | 2026-04-16 | `ipai-prismalab-web.whitedesert-54fce6ca...` -> `57.155.20.163` |
| DNS `www` | `dig +short` | 2026-04-16 | `ipai-website-dev.blackstone-0df78186...` -> `20.43.154.179` |
| PG databases | psycopg2 (prior in session) | 2026-04-16 | `[odoo, odoo_staging, postgres, azure_maintenance, azure_sys]` |
| PG `odoo` tables | psycopg2 (prior in session) | 2026-04-16 | 121 tables |
| PG `odoo_staging` tables | psycopg2 (prior in session) | 2026-04-16 | 0 tables |
| PG `odoo_dev` | psycopg2 (prior in session) | 2026-04-16 | DOES NOT EXIST |
| Installed modules | psycopg2 (prior in session) | 2026-04-16 | 12 modules (base framework only) |
| ir_attachment.location | psycopg2 (prior in session) | 2026-04-16 | `db` |
| ACA apps (Sponsored) | `az containerapp list` | 2026-04-16 | 4 apps |
| ACA apps (Sub1) | `az containerapp list` | 2026-04-16 | 15 apps |
| PG server | `az postgres flexible-server list` | 2026-04-16 | `pg-ipai-odoo`, D4s_v3, 128GiB, v16, Ready |
| Entra enterprise apps | ssot/identity/enterprise-apps.runtime-state.yaml | 2026-04-16 | 11 apps (observed evidence) |
| Foundry models | ssot/governance/foundry-model-routing.yaml | 2026-04-15 | 4 deployments |
| Agent interop | ssot/governance/agent-interop-matrix.yaml v2 | 2026-04-16 | 8+ agents defined |
| Review gates | ssot/assurance/review-gates.yaml | 2026-04-15 | 5 phases defined |
| Outage evidence | This session | 2026-04-16 | 3-day outage (04-13 to 04-16), 18,526+ probe failures |

---

*Generated 2026-04-16 v2 by evidence-based platform audit. No claim made without runtime or infrastructure verification.*
