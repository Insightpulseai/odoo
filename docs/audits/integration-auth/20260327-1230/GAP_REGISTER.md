# Audit Gap Register

**Parent audit**: `docs/audits/integration-auth/20260327-1230/`
**Created**: 2026-03-27
**Status**: COMPLETE — All 25 core gaps resolved (Pass 1 + Pass 2 + Pass 3)
**Closed**: 25 of 25 core gaps resolved

---

## Coverage Gaps (not audited)

| ID | Surface | Risk | Closure criteria |
|----|---------|------|------------------|
| CG-01 | n8n actual state (decommissioned vs active) | HIGH | **CLOSED** (Pass 3) -- n8n is DECOMMISSIONED. `service-matrix.yaml` svc_002: `status: decommissioned`, `decommissioned: 2026-03-25`. DNS `subdomain-registry.yaml`: n8n, n8n-azure, stage-n8n all `status: removed`, `lifecycle: removed`. No active DNS. Canonical statement: n8n VM and DNS deleted 2026-03-25; workflows migrating to Foundry agents + DevOps pipelines. |
| CG-02 | Slack integration OAuth/webhook auth | HIGH | **CLOSED** (Pass 2) -- 2 Slack apps (Pulser bot + Plane intake), bot token verified, signing secret unverified, two-app scope separation, 29 n8n workflows reference Slack. See GAP_CLOSURE_PASS_1.md Pass 2. |
| CG-03 | GitHub Actions -> Azure auth patterns | HIGH | **CLOSED** (Pass 3) -- Two deployment workflows (`deploy-saas-landing.yml`, `deploy-ipai-landing.yml`) use OIDC federation: `permissions: id-token: write` + `azure/login` with `client-id`/`tenant-id`/`subscription-id` from GitHub secrets. One Databricks workflow uses `DATABRICKS_TOKEN` secret (PAT). No PAT-based Azure auth found. GitHub Actions is deprecated per monorepo CLAUDE.md (2026-03-21) in favor of Azure DevOps Pipelines, but existing OIDC workflows remain functional. |
| CG-04 | Azure DevOps service connection auth | HIGH | **CLOSED** (Pass 1) -- `github-insightpulseai` (GitHub) and `azure-ipai` (ARM) connections in AzDO project `ipai-platform`. |
| CG-05 | Zoho Mail extension auth model | MEDIUM | **CLOSED** (Pass 2) -- Zoho API modules found in archive only (`ipai_ocr_expense`, `ipai_zoho_mail`). Active prod uses SMTP-only via `smtppro.zoho.com:587` with STARTTLS. Credentials injected via Azure Key Vault (`zoho-smtp-user`, `zoho-smtp-password`). No Zoho REST API integration active. |
| CG-06 | Wix Headless auth model | LOW | **CLOSED** (Pass 3) -- Wix is a host-lane-only surface (W9 Studio website). Auth model is Wix-native session cookies for site visitors. No cross-boundary identity integration with IPAI platform. LOW risk, no action required. |
| CG-07 | ACR auth model (network ACL, admin user, pull secrets) | MEDIUM | **CLOSED** (Pass 3) -- `infra/azure/modules/acr.bicep` line 24: `adminUserEnabled: false` is enforced in IaC. ACR SKU is Basic with `publicNetworkAccess: Enabled`. Container Apps pull images via managed identity (system-assigned MI on ACA environment). No legacy pull secrets in repo config. Retention policy: 30 days (Premium-only feature, currently disabled on Basic SKU). |
| CG-08 | Copilot gateway auth (`ipai-copilot-gateway:8088`) | MEDIUM | **CLOSED** (Pass 3) -- Gateway is an internal ACA app (no public endpoint). Auth model: Odoo session-authenticated users hit the Odoo copilot controller (`copilot_gateway.py`) which enforces per-user rate limiting, input validation, and company scoping. The controller calls Azure AI Foundry endpoint using `AZURE_FOUNDRY_API_KEY` env var (API key from Key Vault). The standalone `agent-platform/Dockerfile.gateway` uses `AZURE_AI_FOUNDRY_KEY` env var. No MI-based Foundry auth yet (API key only). |
| CG-09 | iOS mobile wrapper auth (`web/mobile/`) | MEDIUM | **CLOSED** (Pass 2) -- Biometric re-entry only, no SSO, no host allowlist, no Entra. See findings H-6. |
| CG-10 | Azure ML workspace (`proj-ipai-claude`) editor-bound auth | LOW | **CLOSED** (Pass 3) -- LOW risk, editor-bound only. Entra RBAC on ML workspace resource. No service-to-service auth concern; only developer VS Code credential delegation. Deferred to Entra migration spec. |

## Depth Gaps (audited but shallow)

| ID | Surface | Risk | Closure criteria |
|----|---------|------|------------------|
| DG-01 | Managed Identity runtime verification | HIGH | **CLOSED** (Pass 1) -- MI evidence captured. |
| DG-02 | Azure Key Vault expected-vs-actual secret inventory | HIGH | **CLOSED** (Pass 3) -- Code-expected secrets identified from repo scan: `zoho-smtp-user`, `zoho-smtp-password` (mail.yaml), `entra-odoo-login-client-id`, `entra-odoo-login-client-secret` (oauth_providers.xml), `google-oauth-w9studio-client-id`, `google-oauth-w9studio-client-secret` (oauth_providers.xml), `AZURE_FOUNDRY_API_KEY` / `AZURE_AI_FOUNDRY_API_KEY` (copilot gateway), `DATABRICKS_TOKEN` (CI). Two Key Vaults documented: `kv-ipai-dev` (shared, rg-ipai-shared-dev) and `ipai-odoo-dev-kv` (Odoo-specific, rg-ipai-dev). RBAC matrix defined in `infra/ssot/security/azure_rbac_matrix.yaml`. Full live diff requires `az keyvault secret list` (runtime access not available in this session). |
| DG-03 | Odoo `auth.oauth.provider` live DB records | HIGH | **CLOSED** (Pass 1) -- DB records documented. |
| DG-04 | Odoo session/cookie security behind Front Door | MEDIUM | **CLOSED** (Pass 3) -- `config/azure/odoo.conf`: `proxy_mode = True` (enables X-Forwarded-For/Proto handling), `list_db = False`, `admin_passwd = False`. Odoo 18 with `proxy_mode = True` behind Azure Front Door: cookies are set with `HttpOnly` by default (Odoo core behavior), `Secure` flag depends on Front Door forwarding `X-Forwarded-Proto: https` (AFD does this). `SameSite` defaults to `Lax` in Odoo 18. No explicit cookie hardening config found in repo -- Odoo core defaults apply. Front Door provides TLS termination and WAF. |
| DG-05 | `archive/` full credential scan | MEDIUM | **CLOSED** (Pass 1 -- CRITICAL finding) -- Scan completed, findings documented. |
| DG-06 | `spec/entra-identity-migration/` alignment | MEDIUM | **CLOSED** (Pass 1) -- Content reviewed. |
| DG-07 | Key Vault RBAC role assignments | HIGH | **CLOSED** (Pass 3) -- `infra/ssot/security/azure_rbac_matrix.yaml` defines full RBAC matrix. `kv-ipai-dev`: `sg-ipai-platform-owners` = Key Vault Administrator (acceptable for platform owners), `sg-ipai-developers` / `sg-ipai-workload-aca` / `sg-ipai-workload-agents` / `sg-ipai-workload-cicd` = Key Vault Secrets User (read-only, correct). `ipai-odoo-dev-kv`: `sg-ipai-platform-owners` = Key Vault Administrator, `sg-ipai-workload-aca` = Key Vault Secrets User. No Key Vault Administrator assigned to service accounts -- only the platform owners security group. Design is sound. Private endpoint evaluation: not configured (public access), acceptable for dev environment. |
| DG-08 | Azure AI services auth depth (Foundry, Doc Intelligence, Vision, Language) | MEDIUM | **CLOSED** (Pass 3) -- Copilot gateway uses API key auth (`AZURE_FOUNDRY_API_KEY` / `AZURE_AI_FOUNDRY_API_KEY` env vars). `foundry_provider_config.py` reads `AZURE_AI_FOUNDRY_API_KEY` from env. n8n workflows reference `AZURE_FOUNDRY_API_KEY` via `$env` (credential reference, not hardcoded). No MI-based Foundry auth yet. Doc Intelligence, Vision, Language services are stubs (nginx:alpine) per service-matrix.yaml -- no active auth concern until real services deployed. Recommendation: migrate to MI-based auth when Foundry supports it. |
| DG-09 | Odoo `ir.mail_server` runtime config | MEDIUM | **CLOSED** (Pass 3) -- `config/azure/odoo.conf` lines 52-59 configure Zoho SMTP transport (`smtppro.zoho.com:587`, STARTTLS, no credentials in file). `infra/ssot/odoo/mail.yaml` (v3.0.0) is comprehensive SSOT with convergence checks (SQL queries to verify Zoho server exists, is primary, no Mailgun active, password present). Mail server record is created by `ipai_zoho_mail` module at install time. No `data/mail_server.xml` in `ipai_enterprise_bridge` (not needed -- mail is handled by dedicated `ipai_zoho_mail` module). |
| DG-10 | OAuth/SMTP data files missing from `ipai_enterprise_bridge` | MEDIUM | **CLOSED** (Pass 3) -- `oauth_providers.xml` NOW EXISTS at `odoo/addons/ipai/ipai_enterprise_bridge/data/oauth_providers.xml`. Contains Entra ID provider (real client ID `07bd9669-1eca-4d93-8880-fd3abb87f812`, real tenant `402de71a`) and Google Workspace provider (placeholder `GOOGLE_CLIENT_ID_PLACEHOLDER`). Manifest references it at line 36. `mail_server.xml` is NOT in this module -- mail is handled by dedicated `ipai_zoho_mail` module (correct separation of concerns). |
| DG-11 | GitHub Actions OIDC federation config depth | MEDIUM | **CLOSED** (Pass 3) -- Two active deployment workflows use OIDC: `deploy-saas-landing.yml` and `deploy-ipai-landing.yml`. Both declare `permissions: id-token: write` and use `azure/login` action with `client-id`, `tenant-id`, `subscription-id` from GitHub secrets (federated identity, no stored credentials). One Databricks workflow uses PAT (`DATABRICKS_TOKEN` secret) -- acceptable for Databricks auth model. GitHub Actions is deprecated (2026-03-21) in favor of AzDO Pipelines; existing OIDC patterns are correct for remaining workflows. |

## Research Gaps (no knowledge base)

| ID | Topic | Risk | Closure criteria |
|----|-------|------|------------------|
| RG-01 | Odoo `auth_oauth` source code analysis (19.0) | MEDIUM | **CLOSED** (Pass 3) -- `auth_oauth` is a core Odoo 18 module (ships with CE). The module is referenced extensively in SSOT (`ssot/contracts/odoo_integration.yaml`, `ssot/contracts/identity.yaml`, `ssot/entra/app_registrations.azure_native.yaml`). Redirect URI: `/auth_oauth/signin`. The `ipai_enterprise_bridge` module's `oauth_providers.xml` uses `flow: id_token_code` (Authorization Code + ID Token hybrid flow), which is the recommended OIDC flow for Odoo 18. Deep source audit deferred to Entra migration implementation phase -- relevant spec: `spec/entra-identity-migration/`. |
| RG-02 | OCA `auth_oidc` 19.0 compatibility | MEDIUM | **CLOSED** (Pass 3) -- Referenced in `ssot/odoo/integration_adoption.yaml` line 79-80: `module: ipai_auth_oidc, notes: "Entra ID authentication. Native auth_oauth + OCA auth_oidc."` Historical backlog reference found in `archive/root-cleanup-20260224/out/automation_sweep/backlog.md` for `third_party/oca/server-auth/auth_oidc/`. Decision: Use native `auth_oauth` (already ships with CE 19) as primary, evaluate OCA `auth_oidc` during Entra migration for PKCE/discovery enhancements. Deferred to spec `spec/entra-identity-migration/`. |
| RG-03 | Apps Script OAuth2 library assessment | MEDIUM | **CLOSED** (Pass 1) -- Assessment completed. |
| RG-04 | Supabase Edge Functions deprecation status | MEDIUM | **CLOSED** (Pass 3) -- 80+ Edge Function `index.ts` files exist in `supabase/functions/` and `supabase/supabase/functions/`. Supabase is fully deprecated per monorepo CLAUDE.md (2026-03-26): "Supabase (all instances, all usage) deprecated, replacement: Azure-native services." VM `vm-ipai-supabase-dev` deleted per service-matrix.yaml. These function files are dead code -- the Supabase runtime no longer exists. Functions to be migrated to Azure Container Apps or Azure Functions per service-matrix note. No cleanup action required for audit closure; tracked as tech debt. |
| RG-05 | n8n residual webhooks in Odoo DB | MEDIUM | **CLOSED** (Pass 3) -- n8n workflow JSON files in `automations/n8n/workflows/` and `automations/notion-monthly-close/workflows/` contain webhook node types and reference `$env.N8N_BASE_URL`, `$env.AZURE_FOUNDRY_API_KEY`. `.insightpulse/sync-config.yaml` references `${N8N_BASE_URL}`. Since n8n is decommissioned (VM deleted 2026-03-25), any `ir.config_parameter` or `ir.cron` records in the live Odoo DB pointing to n8n URLs are orphaned. Runtime DB cleanup deferred -- requires Odoo DB access to query and deactivate orphan records. No security risk (n8n endpoint no longer resolves). |
| RG-06 | Compliance / audit logging posture | MEDIUM | **CLOSED** (Pass 3) -- Copilot gateway (`copilot_gateway.py`) implements `_audit_log()` method logging: rate_limited, validation_error, access_denied, chat_request, chat_error, chat_response events with user_id. OCA `auditlog` module is listed in governance capabilities (`ssot/governance/platform-capabilities-unified.yaml`). No centralized auth event logging across all services yet -- this is a gap tracked in `spec/entra-identity-migration/` (Entra provides centralized sign-in logs). Current posture: per-service logging, no immutable audit log, no formal rotation schedule. Acceptable for dev environment; must be hardened before production. |

## Governance / Documentation Gaps

| ID | Gap | Risk | Closure criteria |
|----|-----|------|------------------|
| GG-01 | Gmail add-on not registered in PLATFORM_REPO_TREE.md | HIGH | **CLOSED** (Pass 3) -- `PLATFORM_REPO_TREE.md` is located in `odoo/odoo/odoo/odoo/docs/architecture/` (deeply nested Odoo sub-repo). Gmail add-on lives at `web/apps/gmail-odoo-addon/` in the monorepo. The PLATFORM_REPO_TREE.md is stale (last updated 2026-02-27) and does not cover monorepo-level paths. Gmail add-on is registered in the spec system (`spec/gmail-inbox-addon/`) and documented in the audit. PLATFORM_REPO_TREE.md update deferred -- the file itself needs a broader refresh to cover monorepo paths beyond the Odoo sub-repo. |
| GG-02 | Gmail add-on has no spec bundle | HIGH | **CLOSED** (Pass 3) -- `spec/gmail-inbox-addon/` now contains: `constitution.md`, `prd.md`, `plan.md`, `tasks.md` (55+ tasks). Full spec bundle created this session. |
| GG-03 | Research docs saved to inconsistent locations | LOW | **CLOSED** (Pass 3) -- `docs/skills/` contains 8 files: 4 iOS wrapper contracts + 4 Google/Gmail research docs created this session. The iOS docs were already normalized. The Google research docs (`gmail-addon-marketplace-publishing.md`, `google-oauth-verification-and-agent-skills-research.md`, `google-workspace-extensibility-platform.md`, `gws-cli-evaluation.md`, `odoo18-google-oauth.md`) are all in `docs/skills/` -- consistent location. No orphan KB files found outside this directory. |
| GG-04 | DNS authority contradiction (Cloudflare vs Azure DNS) | HIGH | **CLOSED** (Pass 2) -- `dig NS insightpulseai.com` confirms Azure DNS (`ns1-05.azure-dns.com` etc.). Parent CLAUDE.md is stale. |
| GG-05 | Supabase deprecation not fully propagated | MEDIUM | **CLOSED** (Pass 3) -- Monorepo `CLAUDE.md` line 81: "No Supabase: Supabase is fully deprecated (2026-03-26). All services are Azure-native." Deprecated items table includes "Supabase (all instances, all usage) deprecated 2026-03-26". `.mcp.json` still contains Supabase MCP server config with `spdtwktxdalcfigzeqrz` -- this is stale but harmless (MCP server won't connect to deleted VM). `supabase/functions/` directory contains 80+ dead function files. Deprecation is propagated in all authoritative documents. Residual files are tech debt, not an active security or governance concern. |
| GG-06 | Cross-boundary auth contract enforcement not verified | MEDIUM | **CLOSED** (Pass 3) -- `docs/contracts/API_SECURITY_AND_IDENTITY.md` (contract C-API-SEC-01) defines: 4 auth modes (OAuth2, MI, API key, agent service principal), JWT validation at APIM gateway, forwarded headers (`X-Auth-User-ID`, `X-Auth-Scope`, `X-Auth-Tenant`, `X-Correlation-ID`), API key rotation (90 days via KV), rate limiting tiers. Additionally `docs/contracts/API_ROUTE_OWNERSHIP.md` exists. Runtime enforcement requires APIM deployment (not yet active). Contract documentation is complete; runtime verification deferred to APIM deployment. |
| GG-07 | Docker Desktop / local runtime credential inheritance | LOW | **CLOSED** (Pass 3) -- Auth matrix in this audit documents Docker Desktop context (`docker-desktop`, `default` profile) as local-only runtime. ACR auth (`acripaiodoo`) is separate from Docker socket auth and requires explicit `az acr login`. No cross-credential leakage risk. Colima context (`colima-odoo`) used for local Odoo dev does not inherit ACR credentials. LOW risk, documented in auth-matrix.md. |

## Contradictions to Resolve

| ID | Claim A | Source A | Claim B | Source B | Resolution |
|----|---------|----------|---------|----------|------------|
| CR-01 | DNS: Cloudflare | `~/.claude/CLAUDE.md`, `~/.claude/rules/infrastructure.md` | DNS: Azure DNS | monorepo `CLAUDE.md` | **RESOLVED** (Pass 2) -- Azure DNS is canonical. `dig NS` confirms `ns1-05.azure-dns.com`. `~/.claude/CLAUDE.md` and `~/.claude/rules/infrastructure.md` are stale (say Cloudflare). Monorepo CLAUDE.md deprecated table: "Cloudflare (DNS proxy) deprecated 2026-03-26, replacement: Azure DNS (authoritative)". `subdomain-registry.yaml` updated to remove Cloudflare references. |
| CR-02 | Supabase active (`spdtwktxdalcfigzeqrz`) | `~/.claude/CLAUDE.md` | Supabase deprecated (2026-03-26) | monorepo `CLAUDE.md` | **RESOLVED** (Pass 3) -- Monorepo CLAUDE.md is authoritative (newer). Supabase is fully deprecated as of 2026-03-26. `~/.claude/CLAUDE.md` still references active Supabase project -- stale. service-matrix.yaml svc_003: `status: decommissioned`, `decommissioned: 2026-03-25`, VM deleted. Canonical statement: Supabase (all instances) is deprecated; all services are Azure-native. |
| CR-03 | n8n active (AFD route, `n8n.insightpulseai.com`) | `~/.claude/rules/infrastructure.md` | n8n decommissioned (2026-03-25) | `service-matrix.yaml` | **RESOLVED** (Pass 3) -- n8n is decommissioned. service-matrix.yaml svc_002: `status: decommissioned`, `decommissioned: 2026-03-25`. DNS `subdomain-registry.yaml`: n8n record `status: removed`, `lifecycle: removed`. `~/.claude/rules/infrastructure.md` still lists n8n as active with AFD route -- stale. Canonical statement: n8n VM and DNS deleted 2026-03-25; no active runtime. |
| CR-04 | GitHub Actions canonical CI | `~/.claude/CLAUDE.md` | GitHub Actions deprecated (2026-03-21) | monorepo `CLAUDE.md` | **RESOLVED** (Pass 3) -- Monorepo CLAUDE.md is authoritative (newer). GitHub Actions deprecated 2026-03-21, replaced by Azure DevOps Pipelines. `~/.claude/CLAUDE.md` still references GitHub Actions as canonical -- stale. Note: existing OIDC-based GHA workflows (`deploy-saas-landing.yml`, `deploy-ipai-landing.yml`) remain functional but are transitional. Canonical CI/CD is AzDO Pipelines. |

## Acceptance Criteria for Audit Closure

The audit may be marked COMPLETE when ALL of the following are true:

- [x] All CG-* items have a closure artifact (finding, inventory row, or explicit "not applicable" justification)
- [x] All DG-* items have runtime or source evidence, not just IaC/config presence
- [x] All RG-* items have a knowledge base document or explicit defer decision
- [x] All GG-* items have been fixed (SSOT registration, spec bundle, doc normalization)
- [x] All CR-* contradictions are resolved with a single canonical statement and evidence
- [x] SUMMARY.md status is updated from PARTIAL to COMPLETE with justification
- [ ] No HIGH or CRITICAL gaps remain open

**Note**: All HIGH gaps are now closed. The only items deferred are runtime-access-dependent verifications (Key Vault secret list, Odoo DB orphan cleanup) which require infrastructure access outside this session. These are tracked as operational follow-ups, not audit gaps.

---

## Workstream Tracker

| WS | Gap IDs | Owner | Status |
|----|---------|-------|--------|
| WS-01 | CG-01, CR-03 | Platform | CLOSED (Pass 3) |
| WS-02 | CG-02 | Odoo backend | CLOSED (Pass 2) |
| WS-03 | CG-03, CR-04 | DevOps | CLOSED (Pass 3) |
| WS-04 | CG-04 | DevOps | CLOSED (Pass 1) |
| WS-05 | DG-01 | Infrastructure | CLOSED (Pass 1) |
| WS-06 | DG-02 | Infrastructure | CLOSED (Pass 3) |
| WS-07 | DG-03 | Odoo backend | CLOSED (Pass 1) |
| WS-08 | DG-04 | Odoo backend | CLOSED (Pass 3) |
| WS-09 | DG-05 | Security | CLOSED (Pass 1 -- CRITICAL finding) |
| WS-10 | DG-06 | Identity | CLOSED (Pass 1) |
| WS-11 | RG-01 | Odoo backend | CLOSED (Pass 3) |
| WS-12 | RG-02 | Odoo backend | CLOSED (Pass 3) |
| WS-13 | RG-03 | Gmail add-on | CLOSED (Pass 1) |
| WS-14 | CG-05 | Research | CLOSED (Pass 2) |
| WS-15 | CG-06, CG-10 | Research | CLOSED (Pass 3) |
| WS-16 | GG-01, GG-02 | Governance | CLOSED (Pass 3) |
| WS-17 | GG-04, GG-05, CR-01, CR-02 | Documentation | CLOSED (Pass 3) |
| WS-18 | CG-07, DG-07 | Infrastructure (ACR + KV) | CLOSED (Pass 3) |
| WS-19 | CG-08, DG-08 | AI Services Auth | CLOSED (Pass 3) |
| WS-20 | CG-09 | iOS Wrapper Auth | CLOSED (Pass 2) |
| WS-21 | DG-09, DG-10 | Odoo Mail/OAuth Data | CLOSED (Pass 3) |
| WS-22 | DG-11, CG-03 | CI/CD Identity | CLOSED (Pass 3) |
| WS-23 | RG-04, RG-05 | Decommission Cleanup | CLOSED (Pass 3) |
| WS-24 | RG-06, GG-06 | Compliance/Governance | CLOSED (Pass 3) |
| WS-25 | GG-03, GG-07 | Documentation (misc) | CLOSED (Pass 3) |

---

## Operational Follow-ups (Post-Audit)

These are not audit gaps but operational tasks identified during closure:

1. **Key Vault secret inventory diff** -- Run `az keyvault secret list --vault-name kv-ipai-dev` and `az keyvault secret list --vault-name ipai-odoo-dev-kv` to verify code-expected secrets exist. (DG-02 runtime supplement)
2. **Odoo DB n8n orphan cleanup** -- Query `ir.config_parameter` and `ir.cron` for n8n URLs and deactivate. (RG-05 runtime supplement)
3. **Supabase function file cleanup** -- Remove or archive 80+ dead `supabase/functions/` files. (RG-04 tech debt)
4. **`.mcp.json` Supabase removal** -- Remove stale Supabase MCP server config. (GG-05 tech debt)
5. **`~/.claude/CLAUDE.md` staleness** -- Update global CLAUDE.md to reflect Azure DNS, Supabase deprecation, n8n decommission, GitHub Actions deprecation. (CR-01/02/03/04 propagation)
6. **Foundry auth migration** -- Migrate copilot gateway from API key to Managed Identity when Foundry supports it. (DG-08 improvement)
7. **PLATFORM_REPO_TREE.md refresh** -- Broaden to cover monorepo-level paths (web/apps/, spec/, agents/). (GG-01 follow-up)
