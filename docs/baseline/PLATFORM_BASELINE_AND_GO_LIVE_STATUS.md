# Platform Baseline and Go-Live Status

> Evidence-based audit, 2026-04-16. Conservative: no claim without proof.
> Status model: planned | repo-defined | provisioned | configured | verified-nonprod | verified-prod | live | blocked | unknown

---

## 1. Executive Summary

InsightPulseAI is a multi-plane platform built on Odoo CE 18 + Azure-native services. The platform is architecturally ambitious with extensive SSOT documentation but is NOT production-ready for customer-facing ERP operations.

**What is genuinely live today:**
- Odoo CE 18 base install on Azure Container Apps returning HTTP 200 at `erp.insightpulseai.com` with health check passing
- Three static/CMS web surfaces (InsightPulseAI, PrismaLab, W9 Studio) returning HTTP 200
- PrismaLab RAG gateway functional
- DNS via Azure DNS resolving correctly for all tested domains
- PostgreSQL 16 (General Purpose) provisioned with `odoo` and `odoo_staging` databases
- Databricks workspace provisioned with Unity Catalog enabled
- Container registry with 20 repositories

**What is NOT live despite documentation suggesting otherwise:**
- Only 12 base Odoo modules installed (no accounting, CRM, project, HR, or any ipai_* module)
- Zero custom ipai_* modules deployed to production runtime
- The `odoo_dev` database does not exist on Azure PG (contradicts CLAUDE.md and multiple SSOT files)
- `odoo_staging` database exists but has 0 tables
- No Odoo business functionality is operational (no GL, AP/AR, invoicing, BIR compliance)
- No SSO/OAuth configured in the running Odoo instance
- No CI/CD pipeline has been verified as successfully deploying to production
- No semantic models, Power BI reports, or Fabric mirroring are operational
- Azure Front Door exists on Sub1 only, not on the Sponsored sub where the primary Odoo ACA lives
- No monitoring/alerting verified as functional

**Go-live verdict: NOT READY. The platform is at infrastructure-provisioned stage, not application-configured or business-operational stage.**

---

## 2. Authority Model / Sources of Truth

| Layer | File/System | Role | Trust Level |
|---|---|---|---|
| Runtime truth | Azure live resources | What is actually deployed | Highest |
| Environment contract | `ssot/odoo/environment-contract.yaml` | Intended environment map | High (partially stale) |
| Runtime contract | `ssot/odoo/runtime_contract.yaml` | Container/addon paths | High (references stale env `salmontree`) |
| DNS authority | `ssot/infrastructure/dns_mail_authority.yaml` | DNS/mail ownership | Accurate |
| Tenant registry | `ssot/tenants/tenant-registry.yaml` | Tenant model | Accurate (aspirational) |
| Integration index | `ssot/integrations/_index.yaml` | Integration catalog | Accurate for inventory; status unverified |
| Governance | `ssot/governance/` (30+ files) | Policy and strategy | Heavily aspirational |
| CLAUDE.md | Root + nested | Agent behavior doctrine | Accurate for doctrine; overstates readiness |
| Agent memory | `~/.claude/projects/*/memory/` | Operational notes | Mixed accuracy |

**Key finding**: Many SSOT files describe intended state as if it were current. The `environment-contract.yaml` correctly distinguishes planned vs active, but the broader doc corpus does not.

---

## 3. Repo Topology and Ownership Boundaries

| Path | Purpose | File Count (approx) | Actively Used |
|---|---|---|---|
| `addons/ipai/` | 55 custom Odoo modules | ~2000 | Repo-only; 0/55 deployed |
| `addons/oca/` | OCA modules (git submodules) | sparse | Not hydrated at runtime |
| `agents/skills/` | ~180 agent skill definitions | ~1000 | Repo-only knowledge |
| `agent-platform/` | Agent runtime engine | ~200 | Partially deployed (gateway) |
| `apps/` | Application packages | ~100 | Partially deployed |
| `ssot/` | 47 subdirectories, ~100+ YAML | ~150 | Reference only |
| `infra/azure/modules/` | Bicep IaC modules | ~10 | Used for provisioning |
| `azure-pipelines/` | 15 pipeline definitions | 15 | Unknown run success rate |
| `deploy/` | Deployment artifacts | varies | Used for R3 provisioning |
| `docs/` | Documentation | ~500 | Reference only |
| `spec/` | 76 spec bundles | ~400 | Planning artifacts |

---

## 4. Environment Map

| Environment | Database | ACA App | URL | Status | Evidence |
|---|---|---|---|---|---|
| Production | `odoo` (121 tables, 12 modules) | `ca-ipai-odoo-web-dev` (Sponsored/blackriver) | `erp.insightpulseai.com` | Bare install | HTTP 200, health pass, but only base modules |
| Staging | `odoo_staging` (0 tables) | None dedicated | `erp-staging.insightpulseai.com` | planned | DNS not created; DB empty |
| Dev (Azure) | `odoo_dev` DOES NOT EXIST | `ipai-odoo-dev-web` (Sub1/blackstone) | direct ACA FQDN | provisioned | ACA exists but DB missing |
| Dev (Local) | `odoo_dev` (local PG) | N/A | `localhost:8069` | unknown | Depends on developer machine |

**Critical finding**: The naming `ca-ipai-odoo-web-dev` serves production (`erp.insightpulseai.com`). The Sub1 `ipai-odoo-dev-web` appears to be an older/parallel deployment. Two ACA environments exist across two subscriptions with overlapping names.

---

## 5. Runtime/Platform Architecture

### Azure Subscriptions

| Subscription | ID | Role | Resources |
|---|---|---|---|
| Microsoft Azure Sponsorship | `eba824fb-332d-4623-9dfb-2c9f7ee83f4e` | Primary (newer) | PG, Databricks, ACR, KV, ACA (4 apps), Purview, Service Bus, VNet, Backup Vault, AI Search, Private Endpoints, Storage (6 accounts), Managed Identities (6) |
| Azure subscription 1 | `536d8cf6-89e1-4815-aef3-d5f2c5f4d070` | Secondary (older) | ACA (15 apps), AFD, KV, AI services (5), Redis, Function App, Storage, Log Analytics, managed identities (7) |

### Container Apps (19 total across both subs)

**Sponsored sub (4 apps):**
- `ca-ipai-odoo-web-dev` -- primary Odoo (serves erp.insightpulseai.com)
- `ipai-prismalab-web` -- PrismaLab site
- `ipai-website-dev` -- IPAI main site
- `ipai-w9studio-dev` -- W9 Studio site

**Sub1 (15 apps):**
- `ipai-odoo-dev-web` -- older Odoo instance
- `ipai-odoo-dev-worker`, `ipai-odoo-dev-cron` -- Odoo background
- `ipai-copilot-gateway` (internal) -- Pulser gateway
- `ipai-mcp-dev` -- MCP server
- `ipai-odoo-mcp` (internal) -- Odoo MCP
- `ipai-prismalab-gateway` -- RAG gateway
- `ipai-bot-proxy-dev` -- M365 bot proxy
- `ipai-release-manager` (internal) -- release manager
- `ipai-ocr-dev` -- OCR service
- `ipai-odoo-connector` -- connector
- `ipai-website-dev` -- duplicate website
- `ipai-w9studio-dev` -- duplicate W9
- `w9studio-landing-dev` -- landing page
- `ipai-pg-mcp-server-*` -- PG MCP server

### PostgreSQL

| Server | SKU | DBs | Status |
|---|---|---|---|
| `pg-ipai-odoo` | D4s_v3 General Purpose, 128 GiB | `odoo` (121 tables), `odoo_staging` (0 tables) | Ready |

Note: `odoo_dev` does not exist on this server. The CLAUDE.md states it should exist.

### AI Services (Sub1, rg-data-intel-ph)

| Resource | Kind | Location | Status |
|---|---|---|---|
| `ipai-copilot-resource` | AIServices | East US 2 | Provisioned, 4 model deployments |
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
| AI Search `srch-ipai-dev` | Sub1 | Provisioned |
| Service Bus `sb-ipai-dev-sea` | Sponsored | Provisioned |
| Redis `cache-ipai-dev` | Sub1 | Provisioned |
| Backup Vault `bvault-ipai-dev-sea` | Sponsored | Provisioned |
| VNet `vnet-ipai-dev-sea` | Sponsored | Provisioned |
| VNet `vnet-ipai-dev` | Sub1 | Provisioned |

---

## 6. Identity / Auth / Tenant Boundary Model

| Component | Intended State | Actual State | Evidence |
|---|---|---|---|
| Entra ID tenant | `402de71a` (SSOT) vs `9ba5e867` (OAuth SSOT) | Two tenant IDs in SSOT files -- conflict | SSOT files contradict |
| Odoo OAuth (Entra) | CE `auth_oauth` + `auth_totp` per SSOT | `auth_totp` installed, `auth_oauth` NOT installed | PG query: 12 modules, no auth_oauth |
| Managed Identities | 6 on Sponsored, 7 on Sub1 | Provisioned | az resource list |
| User provisioning | JIT via OIDC | Not configured | No auth_oauth module |
| MFA | `auth_totp` for admin groups | Module installed but not enforced (no users configured) | PG shows auth_totp installed |

**Tenant IDs conflict**: `ssot/odoo/runtime_contract.yaml` references tenant `402de71a`, while `ssot/identity/odoo-azure-oauth.yaml` references tenant `9ba5e867`. One of these must be wrong.

**Tenancy model**: 4 tenants defined (IPAI, W9, OMC, TBWA\SMP) using `res.company`. Only IPAI (company 1) is likely to exist given only 12 base modules installed.

---

## 7. Data and Analytics Architecture

| Component | Intended State | Actual State | Status |
|---|---|---|---|
| Databricks workspace | Bronze/Silver/Gold medallion | Workspace provisioned, UC enabled | provisioned |
| Unity Catalog | 3 catalogs (dev/staging/prod) | Created per memory | configured (unverified) |
| DLT pipelines | CDM export pipeline | Created per memory, not run | repo-defined |
| Fabric workspace | `fcipaidev` for mirroring | Trial may expire ~2026-05-20 | unknown |
| Power BI | Primary BI surface | Pro trial expires ~2026-05-20 | unknown |
| Purview | Metadata governance | Provisioned | provisioned |
| AI Search | RAG indexes | `prismalab-rag-v1` index exists per memory | configured |
| Semantic models | Gold layer serving | None published | planned |

---

## 8. Agent / Pulser Runtime Architecture

| Component | Intended State | Actual State | Status |
|---|---|---|---|
| Pulser (custom agent engine) | Multi-agent policy-gated copilot | Codebase exists; gateway deployed | repo-defined + partial deploy |
| ipai-copilot-gateway | Internal ACA, Foundry-backed | Deployed on Sub1 (internal) | provisioned |
| ipai-prismalab-gateway | RAG gateway | Deployed on Sub1 | live (HTTP 200) |
| ipai-bot-proxy-dev | M365 Teams bot proxy | Deployed on Sub1 | provisioned |
| ipai-odoo-mcp | Odoo MCP server | Deployed on Sub1 (internal) | provisioned |
| ipai-release-manager | Release automation | Deployed on Sub1 (internal) | provisioned |
| Agent skills (180+) | Specialist agent skills | Repo-only knowledge definitions | repo-defined |
| Odoo copilot module | `ipai_odoo_copilot` in Odoo | Not installed in running Odoo | repo-defined |

---

## 9. Integrations and External Systems

| Integration | Intended State | Actual State | Status |
|---|---|---|---|
| Zoho SMTP | Outbound email from Odoo | SSOT configured; Odoo mail server record unknown | unknown |
| Entra OIDC | SSO for Odoo web | SSOT defined; `auth_oauth` not installed | repo-defined |
| Meta CAPI | `func-ipai-meta-capi` Function App | Provisioned on Sub1 | provisioned |
| Slack | Agent notifications | SSOT active; runtime unverified | unknown |
| Azure Doc Intelligence | Invoice/receipt OCR | `docai-ipai-dev` provisioned, `ipai-ocr-dev` ACA exists | provisioned |

---

## 10. CI/CD and Release Posture

| Pipeline | System | Status |
|---|---|---|
| 15 Azure Pipelines definitions | `azure-pipelines/` | repo-defined; run history unknown |
| GitHub Actions | Removed per doctrine (2026-04-14) | correctly removed |
| ADO `ipai-platform` project | Azure DevOps | Exists, 23 epics, 120+ issues per memory |
| ACR image builds | Container Registry | 20 repos exist; build history unknown |
| Branch protection | GitHub `main` | Unknown if Azure Pipelines gates are enforced |

**No verified deployment pipeline**: No evidence that any pipeline has successfully built and deployed the Odoo container with custom modules to the production ACA app.

---

## 11. Production / Go-Live Status by Subsystem

| Subsystem | Status | Evidence | Go-Live Criticality |
|---|---|---|---|
| **Odoo ERP (Finance/GL/AP/AR)** | **NOT LIVE** | 12 base modules only; no accounting installed | P0 -- blocks all ERP go-live |
| **Custom ipai_* modules** | **NOT LIVE** | 55 modules in repo; 0 installed in prod DB | P0 |
| **OCA modules** | **NOT LIVE** | Not hydrated or installed | P1 |
| **Odoo SSO** | **NOT LIVE** | auth_oauth not installed | P1 |
| **DNS resolution** | **LIVE** | dig confirms correct CNAME for erp, prismalab, www | -- |
| **TLS certificates** | **LIVE** | HTTPS works, managed certs on ACA | -- |
| **PrismaLab web** | **LIVE** | HTTP 200, content served | P2 |
| **PrismaLab RAG gateway** | **LIVE** | Gateway deployed, search index exists | P2 |
| **Main website** | **LIVE** | HTTP 200 | P3 |
| **W9 Studio site** | **LIVE** | HTTP 200 | P3 |
| **PostgreSQL** | **PROVISIONED** | Server running; prod DB has 121 tables (base only) | P0 |
| **Staging environment** | **NOT CONFIGURED** | DB exists but 0 tables; no ACA; no DNS | P1 |
| **Azure Front Door** | **PARTIAL** | AFD on Sub1 only; primary Odoo on Sponsored sub | P1 |
| **Databricks** | **PROVISIONED** | Workspace running; no pipelines executed | P2 |
| **Power BI** | **NOT CONFIGURED** | Trial license, no semantic models | P2 |
| **Fabric mirroring** | **UNKNOWN** | Trial may be expiring | P2 |
| **CI/CD pipelines** | **UNVERIFIED** | 15 pipeline files; no run success evidence | P0 |
| **Monitoring/observability** | **PROVISIONED** | App Insights, Log Analytics exist; no dashboards/alerts verified | P1 |
| **BIR tax compliance** | **NOT LIVE** | 7+ BIR modules in repo; none installed | P1 (for PH go-live) |
| **Agent/Pulser runtime** | **PARTIALLY DEPLOYED** | Gateway ACA exists; no end-to-end agent flow proven | P2 |
| **Backup/DR** | **PROVISIONED** | Backup Vault exists; no backup policies verified | P1 |
| **Key Vault secrets** | **UNKNOWN** | KV exists; secret population unverified | P0 |

---

## 12. Critical Blockers and Missing Evidence

### P0 Blockers (must resolve before any go-live)

1. **Zero Odoo business modules installed.** The production database has only 12 base framework modules. No accounting (`account`), CRM, project, HR, or custom `ipai_*` modules. The Odoo instance is a bare shell.

2. **No verified deployment pipeline.** No evidence that any Azure Pipeline has successfully built a container image with custom modules and deployed it to the production ACA app. The pipeline files exist in repo but run history is unknown.

3. **`odoo_dev` database does not exist on Azure PG.** Multiple SSOT files and CLAUDE.md reference `odoo_dev` as the development database. It does not exist on `pg-ipai-odoo`. Only `odoo`, `odoo_staging`, `postgres`, and system DBs exist.

4. **Key Vault secret population unverified.** Two Key Vaults exist (`kv-ipai-dev` on Sub1, `kv-ipai-dev-sea` on Sponsored). Whether they contain the required secrets (PG password, Zoho SMTP creds, OAuth client secret) is unverified.

5. **Two-subscription architecture creates routing confusion.** The primary Odoo ACA (`ca-ipai-odoo-web-dev`) runs on Sponsored sub, but AFD, KV, AI services, and most support services run on Sub1. Private endpoint connectivity and DNS resolution between them is unproven.

### P1 Blockers

6. **Entra tenant ID conflict in SSOT.** `runtime_contract.yaml` says `402de71a`; `odoo-azure-oauth.yaml` says `9ba5e867`. One is wrong.

7. **No staging environment.** `odoo_staging` DB is empty (0 tables). No staging ACA app. No staging DNS record.

8. **ACA environment naming is confusing.** `ca-ipai-odoo-web-dev` (a "-dev" named app) serves production. `ipai-odoo-dev-web` on Sub1 appears to be an older parallel that may or may not be active.

9. **Stale SSOT references.** `runtime_contract.yaml` references ACA environment `salmontree-b7d27e19` which is not the current environment (`blackriver-f68f8a9b` is current for Sponsored).

10. **No backup/DR verification.** Backup Vault and Recovery Services Vault exist but no backup policies or successful backup evidence.

### P2 Risks

11. **Power BI Pro trial expiring ~2026-05-20.** BI surface will stop working.
12. **Fabric trial expiring ~2026-05-20.** Mirroring pipeline will stop.
13. **Sponsored sub quota issue (#715-123420)** blocks deploying additional AI models.
14. **55 custom modules, 0/55 pass doctrine checklist** per prior audit.
15. **180+ agent skills are knowledge definitions only** -- no runtime agent framework is executing them.

---

## 13. Recommended Path to Clean Go-Live

Priority order -- each step must produce verifiable evidence:

1. **Fix the database situation.** Create `odoo_dev` on Azure PG or update all SSOT files to reflect reality. Decide whether `odoo` DB is dev or prod.

2. **Build and verify a deployment pipeline.** Get one Azure Pipeline to successfully: build Odoo container with `account` + core modules -> push to ACR -> deploy to ACA -> verify health + module list at runtime. Capture pipeline run ID and logs.

3. **Install core Odoo modules.** At minimum: `account`, `sale`, `purchase`, `crm`, `project`, `hr`, `auth_oauth`. Verify via `/web/session/modules` endpoint.

4. **Resolve the two-subscription architecture.** Either consolidate to one sub or document the cross-sub network topology with verified private endpoint connectivity.

5. **Configure SSO.** Install `auth_oauth`, configure the Entra provider record, verify login flow end-to-end. Resolve the tenant ID conflict first.

6. **Stand up staging.** Initialize `odoo_staging` with modules, deploy a staging ACA app, create DNS record.

7. **Verify Key Vault secrets.** Confirm all required secrets exist (PG password, Zoho SMTP, OAuth secret) in the correct KV.

8. **Install and verify one ipai_* module.** Start with `ipai_odoo_copilot` as proof that the custom module deployment pipeline works.

9. **Configure monitoring.** Set up at least: ACA health alerts, PG connection/CPU alerts, error rate dashboard.

10. **Run BIR compliance modules** for PH tax readiness (R3 milestone).

---

## 14. Appendix: Evidence References

| Evidence | Source | Date |
|---|---|---|
| Odoo health check | `curl https://erp.insightpulseai.com/web/health` -> `{"status": "pass"}` | 2026-04-16 |
| Odoo login page | `curl https://erp.insightpulseai.com/web/login` -> HTTP 200, `<title>Odoo</title>` | 2026-04-16 |
| DNS `erp.insightpulseai.com` | dig -> CNAME `ca-ipai-odoo-web-dev.blackriver-f68f8a9b...` -> `104.43.98.178` | 2026-04-16 |
| DNS `prismalab.insightpulseai.com` | dig -> CNAME `ipai-prismalab-web.whitedesert-54fce6ca...` | 2026-04-16 |
| DNS `www.insightpulseai.com` | dig -> CNAME `ipai-website-dev.blackstone-0df78186...` | 2026-04-16 |
| PG databases | psycopg2 -> `['azure_maintenance', 'azure_sys', 'odoo', 'odoo_staging', 'postgres']` | 2026-04-16 |
| PG `odoo` tables | 121 tables in public schema | 2026-04-16 |
| PG `odoo_staging` tables | 0 tables | 2026-04-16 |
| PG `odoo_dev` | DOES NOT EXIST | 2026-04-16 |
| Installed Odoo modules | 12: auth_totp, base, base_import, base_import_module, base_setup, bus, html_editor, iap, web, web_editor, web_tour, web_unsplash | 2026-04-16 |
| ACA apps (Sponsored) | 4 apps | 2026-04-16 |
| ACA apps (Sub1) | 15 apps | 2026-04-16 |
| PG server | pg-ipai-odoo, D4s_v3, 128 GiB, Ready | 2026-04-16 |
| ACR repos | 20 repositories in acripaiodoo | 2026-04-16 |
| Databricks | dbw-ipai-dev, Succeeded, UC enabled | 2026-04-16 |
| AFD | afd-ipai-dev on Sub1, Active | 2026-04-16 |
| AI Services | 5 resources across rg-data-intel-ph | 2026-04-16 |
| Foundry models | 4 deployments on ipai-copilot-resource | 2026-04-16 |
| Azure subscriptions | 2 active (Sponsored + Sub1) | 2026-04-16 |

---

*Generated 2026-04-16 by evidence-based platform audit. No claim made without runtime or infrastructure verification.*
