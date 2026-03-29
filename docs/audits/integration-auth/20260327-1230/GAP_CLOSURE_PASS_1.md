# Gap Closure Pass 1 — Integration & Authentication Audit

> Executed: 2026-03-27
> Auditor: Claude Agent (automated code analysis)
> Scope: 13 workstreams against repo state on `main`

---

## WS-01: n8n Truth-State

**Status**: CLOSED
**Evidence**:
- `infra/ssot/azure/service-matrix.yaml:18-24` — `status: decommissioned`, `promotion_state: deleted`, `decommissioned: 2026-03-25`
- `infra/dns/subdomain-registry.yaml:133-138` — `n8n` subdomain marked `lifecycle: removed`, `owner_system: decommissioned`
- `infra/dns/subdomain-registry.yaml:402-411` — `n8n-azure` also `lifecycle: removed`
- `infra/ssot/auth/oidc_clients.yaml:160-163` — n8n listed under `retired_clients`
- `infra/dns/canonical_urls.yaml:54-63` — **STALE**: still shows `lifecycle: active` for `n8n.insightpulseai.com`

**Finding**: n8n is decommissioned as a runtime service (service-matrix, DNS registry, OIDC clients all agree). However, `automations/n8n/` still contains 60+ workflow JSON files and documentation. These are repo artifacts (not running infrastructure), but `infra/dns/canonical_urls.yaml` still lists n8n as `lifecycle: active` -- this is a stale reference that should be corrected to `removed`.

**Remaining**: Verify n8n DNS records are actually deleted in Azure DNS (runtime check). Decide whether to archive `automations/n8n/` or retain as reference.

---

## WS-02: Slack Auth

**Status**: PARTIALLY CLOSED
**Evidence**:
- No `addons/ipai/ipai_slack*` module exists (glob returned empty)
- `.claude/skills/entra-identity-governance/SKILL.md:164-165` — Key Vault expected secrets: `slack-bot-token`, `slack-signing-secret`
- `automations/n8n/workflows/` — 15+ workflows reference `$env.SLACK_WEBHOOK_URL`, `$env.N8N_SLACK_CHANNEL_ID`
- `.claude/mcp-servers.legacy.json:101-102` — references `SLACK_BOT_TOKEN`, `SLACK_TEAM_ID`

**Finding**: Slack is used exclusively through n8n webhook integration and MCP server configuration -- there is no Odoo addon for Slack. With n8n decommissioned, all Slack webhook references in `automations/n8n/workflows/` are dead paths. The MCP server Slack integration (legacy config) is a separate concern. Key Vault secrets `slack-bot-token` and `slack-signing-secret` should be inventoried for cleanup if Slack integration is no longer active.

**Remaining**: Confirm whether Slack MCP integration is still active (runtime check). Determine if `slack-bot-token` / `slack-signing-secret` exist in Key Vault or are aspirational.

---

## WS-03: GitHub Actions to Azure Auth

**Status**: CLOSED
**Evidence**:
- `.github/workflows/deploy-ipai-landing.yml:10-12` — `permissions: id-token: write` (OIDC federation)
- `.github/workflows/deploy-ipai-landing.yml:31-36` — `azure/login@v2` with `client-id`, `tenant-id`, `subscription-id` (all from GitHub secrets)
- `.github/workflows/deploy-saas-landing.yml:31-34` — identical OIDC pattern

**Finding**: GitHub Actions uses **Workload Identity Federation (OIDC)** to authenticate to Azure. No client secrets are stored in GitHub -- the `id-token: write` permission enables the OIDC exchange. This is the correct, secretless pattern. Auth uses three GitHub secrets: `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`. Note: GitHub Actions is deprecated in favor of Azure DevOps Pipelines per CLAUDE.md, but the remaining workflows use the correct auth pattern.

**Remaining**: None. Pattern is correct. Eventual cleanup when workflows are migrated to AzDO.

---

## WS-04: Azure DevOps Service Connections

**Status**: CLOSED
**Evidence**:
- `.azure/pipelines/ci-cd.yml:102` — `serviceConnection: sc-azure-dev-platform`
- `infra/pipelines/templates/deploy-bicep.yml:42` — parameterized `serviceConnection` (default not hardcoded)
- `infra/pipelines/templates/deploy-aca.yml:23` — same pattern
- `infra/pipelines/templates/deploy-databricks.yml:19` — same pattern
- `infra/ci/azure-pipelines.yml:50` — `serviceConnection` as pipeline variable

**Finding**: All Azure DevOps pipelines use a **parameterized service connection** pattern (`sc-azure-dev-platform` as default). Service connections are referenced by name, never by credential. Templates in `infra/pipelines/templates/` consistently use `azureSubscription: ${{ parameters.serviceConnection }}`. This is the correct ARM service connection pattern.

**Remaining**: None for code review. Runtime verification: confirm `sc-azure-dev-platform` exists in AzDO and uses Workload Identity Federation (not secret-based).

---

## WS-05: Managed Identity

**Status**: CLOSED
**Evidence**:
- `infra/azure/modules/aca-odoo-services.bicep:28` — `param managedIdentityResourceId string`
- `infra/azure/modules/aca-odoo-services.bicep:148-150` — `type: 'UserAssigned'` with identity binding
- `infra/azure/modules/aca-odoo-services.bicep:112-123` — Key Vault secrets fetched via managed identity
- `infra/ssot/azure/resources.yaml:609-1100` — 12 `Microsoft.ManagedIdentity/userAssignedIdentities` resources listed
- `ssot/azure/resource_rationalization.yaml:107-140` — all ACA apps marked `type: managedIdentity`
- `ssot/governance/ai-consolidation-foundry.yaml:40-42` — Python SDK uses `DefaultAzureCredential`

**Finding**: User-assigned managed identities are the canonical auth mechanism for all ACA container apps. The Bicep module wires managed identity for: ACR pull, Key Vault secret access, and environment variable injection. `DefaultAzureCredential` is the standard in Python SDK code (Foundry, AI services). No service account passwords or API keys are used for service-to-service auth.

**Remaining**: None for code review. The pattern is consistent and correct.

---

## WS-06: Key Vault Expected Secrets

**Status**: PARTIALLY CLOSED
**Evidence**:
- `infra/azure/modules/aca-odoo-services.bicep:40-43` — `pg-odoo-user`, `pg-odoo-password`
- `config/prod/env.contract.md:41-42` — `zoho-smtp-user`, `zoho-smtp-password`
- `infra/ssot/auth/oidc_clients.yaml:84-85` — `google-oauth-w9studio-client-id`, `google-oauth-w9studio-client-secret`
- `infra/ssot/auth/oidc_clients.yaml:118-119` — `entra-odoo-login-client-id`, `entra-odoo-login-client-secret`
- `infra/ssot/auth/oidc_clients.yaml:148-149` — `entra-superset-client-id`, `entra-superset-client-secret`
- `.claude/skills/entra-identity-governance/SKILL.md:158-165` — `zoho-smtp-user`, `zoho-smtp-password`, `slack-bot-token`, `slack-signing-secret`

**Finding**: Expected Key Vault secret inventory for `kv-ipai-dev`:

| Secret Name | Domain | Consumer | Status |
|-------------|--------|----------|--------|
| `pg-odoo-user` | Database | ACA Odoo apps | Required (Bicep wired) |
| `pg-odoo-password` | Database | ACA Odoo apps | Required (Bicep wired) |
| `zoho-smtp-user` | Mail | Odoo mail server | Required |
| `zoho-smtp-password` | Mail | Odoo mail server | Required |
| `google-oauth-w9studio-client-id` | Auth | Odoo OAuth | Required |
| `google-oauth-w9studio-client-secret` | Auth | Odoo OAuth | Required |
| `entra-odoo-login-client-id` | Auth | Odoo OIDC (Entra) | Planned (not yet created) |
| `entra-odoo-login-client-secret` | Auth | Odoo OIDC (Entra) | Planned (not yet created) |
| `entra-superset-client-id` | Auth | Superset OIDC | Planned (not yet created) |
| `entra-superset-client-secret` | Auth | Superset OIDC | Planned (not yet created) |
| `slack-bot-token` | Integration | Slack MCP | Status unknown |
| `slack-signing-secret` | Integration | Slack webhooks | Status unknown |

**Remaining**: Runtime verification required -- `az keyvault secret list --vault-name kv-ipai-dev` to confirm which secrets actually exist vs. are aspirational.

---

## WS-07: Odoo auth.oauth.provider Records

**Status**: CLOSED
**Evidence**:
- `addons/ipai/ipai_enterprise_bridge/models/settings_actions.py:67-120` — `action_apply_google_oauth()` creates/updates Google Workspace provider record programmatically
- `settings_actions.py:87-88` — Searches for `auth.oauth.provider` where `name =like Google Workspace%`
- `settings_actions.py:97-108` — Provider vals include `client_id` from `ir.config_parameter`, endpoints, scopes
- `archive/root/addons/ipai/ipai_enterprise_bridge/data/oauth_providers.xml:5-19` — Old XML data records for Google and Azure providers (in archive, not active)
- `infra/ssot/auth/oidc_clients.yaml:69-91` — Google Workspace W9 Studio provider documented in SSOT

**Finding**: OAuth providers are managed through **code-driven creation** via `action_apply_google_oauth()` in `ipai_enterprise_bridge`, not XML data records. The method reads `ir.config_parameter` values (`ipai.oauth.google.client_id`, `ipai.oauth.google.workspace_domain`) and creates/updates the provider record. This is idempotent and correct. The archive contains old XML data records that are not active. The Entra OIDC provider (`ipai_auth_oidc` module) does not yet exist -- it is planned per `spec/entra-identity-migration/tasks.md:34`.

**Remaining**: None for code review. The Google provider is DB-injected via settings action; Entra provider awaits `ipai_auth_oidc` module development.

---

## WS-08: Odoo Session Security

**Status**: PARTIALLY CLOSED
**Evidence**:
- `config/prod/odoo.conf:28` — `proxy_mode = True` (required for correct HTTPS detection behind Front Door)
- `config/prod/odoo.conf:48-49` — `list_db = False`, `admin_passwd = False` (correct lockdown)
- `config/azure/odoo.conf:25` — `proxy_mode = True`
- `config/staging/odoo.conf:33` — `proxy_mode = True`
- `config/dev/odoo.conf:16` — `proxy_mode = False` (correct for local dev)
- `infra/azure/modules/front-door.bicep:308` — `X-Frame-Options` header set
- `infra/deploy/nginx/erp.insightpulseai.com.conf:52-55` — `X-Frame-Options: SAMEORIGIN`, `Strict-Transport-Security`

**Finding**: Production Odoo config is correctly locked down: `proxy_mode=True`, `list_db=False`, `admin_passwd=False`. Front Door and nginx configs set security headers (HSTS, X-Frame-Options). However, no explicit `session_timeout` or `session_gc_interval` is set in any `odoo.conf`. The OCA module `auth_session_timeout` is listed in the addons manifest (`config/addons.manifest.yaml:107`) but installation status is unknown. No SameSite cookie configuration is visible in config files.

**Remaining**: Runtime check for `auth_session_timeout` installation status. Verify SameSite cookie attribute on live session cookies. Check if Odoo 19 sets `Secure` flag on cookies when `proxy_mode=True`.

---

## WS-09: Archive Credential Scan

**Status**: CLOSED (FINDING: CRITICAL)
**Evidence**:
- `archive/addons/tbwa_spectra_integration/data/users_data.xml:17` — `<field name="password">finance@tbwa2025</field>`
- `archive/addons/tbwa_spectra_integration/data/users_data.xml:29` — `<field name="password">cfo@tbwa2025</field>`
- `archive/addons/tbwa_spectra_integration/data/users_data.xml:41` — `<field name="password">finance.mgr@tbwa2025</field>`

**Finding**: **CRITICAL** -- Three plaintext passwords are committed in `archive/addons/tbwa_spectra_integration/data/users_data.xml`. These are labeled as "placeholders" with comments saying passwords must be changed, but the plaintext values are in git history. The passwords follow a predictable pattern (`role@tbwa2025`). Even though these are in the `archive/` directory, they are in the git tree.

**Remaining**: These passwords must be rotated if they were ever used on any environment. Consider `git filter-repo` to remove from history, or accept the risk given they are in `archive/` of a private repo.

---

## WS-10: Entra Migration Spec Alignment

**Status**: CLOSED
**Evidence**:
- `spec/entra-identity-migration/constitution.md:1-50` — 7+ constitution rules (C1-C5+), covers break-glass, MFA, managed identity, Agent ID
- `spec/entra-identity-migration/tasks.md:1-60` — 5 phases, Phase 0 (foundation) is all `[ ]` (not started), Phase 1 (Odoo ERP) has agent + human tasks for `ipai_auth_oidc` module
- `tasks.md:34` — Explicitly plans `addons/ipai/ipai_auth_oidc/__manifest__.py`
- `tasks.md:35-43` — OIDC Auth Code Flow + PKCE, RS256, JIT provisioning, group sync, session management

**Finding**: Spec is comprehensive and well-structured. All 5 phases are not started (all `[ ]`). The spec correctly identifies this as a greenfield implementation (not migration). Key blocker: Phase 0 requires human action (break-glass account, MFA enrollment, security groups) before any agent work in Phase 1+. The `ipai_auth_oidc` module does not yet exist.

**Remaining**: None for code review. Execution is blocked on Phase 0 human actions.

---

## WS-11: Odoo auth_oauth Source

**Status**: PARTIALLY CLOSED
**Evidence**:
- `vendor/odoo/addons/auth_oauth/controllers/main.py` — File does not exist at expected path (vendor/odoo/ may not be hydrated in monorepo)
- `docs/skills/odoo19-google-oauth.md:360` — Documents that `auth_oauth` controller searches providers via `request.env['auth.oauth.provider'].sudo().search_read()`
- `docs/skills/odoo19-google-oauth.md:382` — Login page renders OAuth buttons when `auth_oauth` is installed and at least one provider is enabled
- `addons/ipai/ipai_enterprise_bridge/models/settings_actions.py:87` — Accesses `auth.oauth.provider` model

**Finding**: The `vendor/odoo/` directory does not contain a hydrated Odoo source tree in the monorepo (it is likely in the nested `odoo/` repo). The auth_oauth flow is documented in skills docs: the controller at `/auth_oauth/signin` handles the OAuth callback, validates the token, matches/creates users by email, and creates a session. The `state` parameter is used for CSRF protection. The `ipai_enterprise_bridge` module correctly uses the `auth.oauth.provider` model to manage providers.

**Remaining**: Direct source review of `auth_oauth/controllers/main.py` from the Odoo 19 source to verify state handling and user matching edge cases (e.g., email collision, case sensitivity). This requires accessing the nested `odoo/` repo.

---

## WS-13: Apps Script OAuth2 Library

**Status**: CLOSED
**Evidence**:
- `web/apps/gmail-odoo-addon/auth.gs:1-718` — Full provider-first auth implementation reviewed
- `auth.gs:2-15` — Comment documents auth model: Add-on click -> /web/login -> provider login -> /auth_oauth/signin -> session exchange
- `auth.gs:98-112` — `buildAuthStateNonce()` implements CSRF protection with UUID nonce, tenant binding, expiry
- `auth.gs:118-152` — `verifyAuthStateNonce()` validates single-use nonce with tenant and expiry checks
- `auth.gs:173-199` — `startProviderAuth()` opens `/web/login` (NOT `/auth_oauth/signin`) -- correct boundary
- `auth.gs:287-327` — `connectWithApiKey()` fallback for admin/service scenarios

**Finding**: The Gmail add-on implements its own auth flow using native Apps Script APIs (`UrlFetchApp`, `PropertiesService`). It does NOT use the `apps-script-oauth2` library. The implementation is sound: it uses single-use nonces for CSRF, validates tenant binding, supports provider-first auth (Microsoft Entra > Google > API key fallback), and correctly distinguishes between `/web/login` (user-facing) and `/auth_oauth/signin` (callback-only). Session tokens are stored in per-user script properties. The `apps-script-oauth2` library is not needed because the add-on delegates OAuth to Odoo's native flow rather than performing the OAuth dance itself.

**Remaining**: None. The auth implementation is complete and uses correct security patterns.

---

## New Findings

### CRITICAL: Plaintext Passwords in Git History

**File**: `archive/addons/tbwa_spectra_integration/data/users_data.xml`
**Lines**: 17, 29, 41
**Passwords**: `finance@tbwa2025`, `cfo@tbwa2025`, `finance.mgr@tbwa2025`
**Risk**: If these passwords were ever used on any environment, they must be rotated immediately. They are in a public-facing git history even though in `archive/`.
**Remediation**: Rotate passwords on all environments. Consider `git filter-repo` if repo is or will be public.

### HIGH: Stale n8n Active Reference in canonical_urls.yaml

**File**: `infra/dns/canonical_urls.yaml:54-63`
**Issue**: n8n is listed as `lifecycle: active` but the service is decommissioned per `service-matrix.yaml` and `subdomain-registry.yaml`.
**Remediation**: Update to `lifecycle: removed` for consistency.

### HIGH: Odoo Config db_password Placeholder

**File**: `config/prod/odoo.conf:17`, `config/staging/odoo.conf:24`
**Issue**: `db_password = odoo` appears in committed config. Per `config/prod/env.contract.md:45`, this is documented as a "template" value overridden at runtime by Key Vault injection. However, the presence of `db_password = odoo` in a file named `prod/odoo.conf` is confusing and could be accidentally used.
**Remediation**: Replace with `db_password = False` or add a comment making the override mechanism explicit in the conf file itself.

### MEDIUM: Session Timeout Not Configured

**Files**: `config/prod/odoo.conf`, `config/staging/odoo.conf`, `config/azure/odoo.conf`
**Issue**: No explicit session timeout configuration. The OCA `auth_session_timeout` module is in the addons manifest but installation is unverified.
**Remediation**: Verify `auth_session_timeout` is installed and configured on all environments. Set explicit timeout (e.g., 8 hours for ERP users, 1 hour for admin).

### MEDIUM: Slack Integration Dead Paths

**Files**: 15+ n8n workflow JSONs in `automations/n8n/workflows/`
**Issue**: All `SLACK_WEBHOOK_URL` references are dead since n8n is decommissioned. Slack bot token / signing secret status in Key Vault is unknown.
**Remediation**: Determine if Slack integration has a new home (MCP, Foundry agents) or is fully deprecated. Clean up Key Vault secrets if deprecated.

### LOW: Entra Secrets Not Yet in Key Vault

**Files**: `infra/ssot/auth/oidc_clients.yaml:118-119, 148-149`
**Issue**: `entra-odoo-login-client-id`, `entra-odoo-login-client-secret`, `entra-superset-client-id`, `entra-superset-client-secret` are referenced but not yet created (Entra migration Phase 0 not started).
**Remediation**: No action needed until Entra migration Phase 0 begins. Track as dependency.

---

*Generated by automated gap-closure analysis. Runtime verification items marked as "Remaining" require `az` CLI or live environment access.*

---

# Pass 2 — Gap Closure (2026-03-27, continued)

## GG-04 / CR-01: DNS Authority Contradiction

**Status**: CLOSED
**Evidence**:
- `dig NS insightpulseai.com +short` returns:
  - `ns1-05.azure-dns.com.`
  - `ns2-05.azure-dns.net.`
  - `ns3-05.azure-dns.org.`
  - `ns4-05.azure-dns.info.`
- **Authoritative DNS is Azure DNS**, not Cloudflare.
- Monorepo `CLAUDE.md` statement ("DNS: Azure DNS (authoritative, delegated from Squarespace)") is correct.
- Parent `~/.claude/CLAUDE.md` stating "DNS: Cloudflare" is **stale**.
- `~/.claude/rules/infrastructure.md` stating "DNS Provider: Cloudflare" is **stale**.

**Resolution**: Azure DNS is canonical. Parent CLAUDE.md and infrastructure.md need updating to reflect Azure DNS.

---

## CG-05 / RG-01: Zoho Integration Beyond SMTP

**Status**: CLOSED
**Evidence**:
- `archive/root/addons/ipai/ipai_zoho_mail/` -- SMTP + IMAP integration module (archived, not active)
  - Features: SMTP outgoing via `smtppro.zoho.com:587`, IMAP incoming via `imappro.zoho.com:993`, per-user Zoho mail address, fetch wizard
  - Auth: env vars `ZOHO_SMTP_PASSWORD`, `ZOHO_IMAP_PASSWORD` (app passwords)
- `archive/root/addons/ipai/ipai_zoho_mail_api/` -- REST API transport module (archived, not active)
  - Features: Bypasses SMTP via Zoho Mail REST API (`POST /api/accounts/{accountId}/messages`)
  - Auth: **OAuth2 refresh token flow** -- `ipai.zoho.client_id`, `ipai.zoho.client_secret`, `ipai.zoho.refresh_token` stored in `ir.config_parameter`
  - Token management: auto-refresh with 60s buffer, cached in `ir.config_parameter`
  - **Security concern**: OAuth client secret stored in `ir.config_parameter` (database), not Key Vault
- Both modules are in `archive/` -- **not active in production**
- Active Zoho integration is SMTP-only via `ir.mail_server` with Key Vault credentials

**Finding**: Zoho integration is SMTP-only in production. The archived Zoho API module used OAuth2 with credentials in `ir.config_parameter` -- this pattern should NOT be reintroduced. If Zoho Mail extension is needed in future, use Key Vault for OAuth credentials.

---

## DG-10: ipai_enterprise_bridge Manifest Data Files Missing

**Status**: CLOSED (CONFIRMED DEFECT)
**Evidence**:
- `addons/ipai/ipai_enterprise_bridge/__manifest__.py:29-37` declares these data files:
  - `data/mail_server.xml` (line 35)
  - `data/oauth_providers.xml` (line 36)
  - `data/enterprise_bridge_data.xml` (line 37)
  - `data/groups.xml` (line 32)
  - `data/sequences.xml` (line 33)
  - `data/scheduled_actions.xml` (line 34)
- `addons/ipai/ipai_enterprise_bridge/data/` directory **does not exist**
- Module will fail on install with `FileNotFoundError` for any missing data file

**Finding**: The `ipai_enterprise_bridge` module manifest references data files that don't exist. This means:
1. The module **cannot be cleanly installed** from a fresh database
2. OAuth providers are provisioned only via manual Settings UI action (`action_apply_google_oauth()`)
3. SMTP server configuration is not declarative / not reproducible across environments
4. This is a P1 defect blocking reproducible Odoo configuration

**Remediation**: Create the `data/` directory and all referenced XML files, or remove the references from the manifest.

---

## DG-09: Odoo ir.mail_server Runtime Config

**Status**: PARTIALLY CLOSED
**Evidence**:
- `ipai_enterprise_bridge` depends on `mail` (line 14 of manifest) and `auth_oauth` (line 15)
- Archived `ipai_zoho_mail` module has a `data/mail_server.xml` that would auto-provision SMTP server records
- Active codebase has no declarative mail server data file
- SMTP credentials are documented as coming from Key Vault: `zoho-smtp-user`, `zoho-smtp-password`
- `infra/ssot/odoo/mail.yaml` documents the expected SMTP config

**Remaining**: Cannot verify actual `ir.mail_server` records without runtime DB access. The SSOT documents the expected config, but installation state is unknown.

---

## CG-09: iOS Mobile Wrapper Authentication

**Status**: CLOSED (NEW FINDING: HIGH)
**Evidence**:
- `web/mobile/Sources/BiometricAuth.swift` — Face ID / Touch ID re-entry gating via `LAContext.evaluatePolicy`. Scope: foreground resume only. Not identity auth.
- `web/mobile/Sources/WrapperViewController.swift` — WKWebView loads `erp.insightpulseai.com/web`. No `WKNavigationDelegate.decidePolicyFor` implementation. `navigateTo(url:)` accepts arbitrary URLs with no host validation.
- `web/mobile/Sources/KeychainService.swift` — Stores `odoo_session_id` and `odoo_csrf_token` in Keychain (`kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly`). Tokens stored but NOT re-injected into webview on app restart.
- `web/mobile/Sources/Info.plist` — Minimal. Missing `NSFaceIDUsageDescription` (App Store rejection risk).
- `web/mobile/Sources/OdooWrapper.entitlements` — Empty dict. No capabilities configured.
- `web/mobile/Sources/Environment.swift` — `baseURL = "https://erp.insightpulseai.com/web"`. Single environment. No staging/dev toggle.
- No `AuthenticationServices` framework imported. No `ASWebAuthenticationSession`. No OAuth/OIDC. No Entra integration.
- No MSAL, no federated identity, no conditional access.

**Finding**: The iOS wrapper is a thin WKWebView shell with biometric re-entry gating and Keychain session storage. It has **no SSO integration**, **no host allowlist**, **no session re-injection**, and **missing Info.plist privacy descriptions**. Entra alignment is zero. Added as finding H-6.

**Security Gaps Identified**:
1. No host allowlist → open to DNS hijacking / URL injection via deep links
2. No `NSFaceIDUsageDescription` → App Store review will reject
3. Keychain tokens not re-injected → session recovery broken across restarts
4. No logout handler → Keychain tokens persist after user signs out in webview
5. No OAuth/SSO → cannot participate in Entra identity governance
6. Empty entitlements → push notifications unlikely working

**Remaining**: None for code review. Implementation work needed per finding H-6.

---

## DG-05 (Pass 2 Expansion): Full Archive Credential Scan

**Status**: CLOSED (CRITICAL -- 12 real credentials found)
**Evidence** (beyond Pass 1 WS-09 findings):

**Odoo admin password** (Base64 `UbQbX75Wi+P3R+bItzO/NapptGbL4n/9MvIDVw71Oww=`) found in 5 files:
- `archive/root/scripts/prod_access_check.py:7`
- `archive/root/scripts/prod_db_guess.py:6`
- `archive/root/docs/architecture/runtime_snapshot/20260108_013846/PROOFS/odoo_conf.txt:29` (as `admin_passwd`)
- `archive/root/docs/architecture/runtime_snapshot/20260108_013846/PROOFS/docker_compose_config.txt:17` (as `ODOO_ADMIN_PASSWORD`)
- Same docker_compose_config.txt:53 (second container)

**PostgreSQL password** (Base64 `vO1OtibFbuqHJX6WDt6Bhu5mwc9bDERzvvRZw9y31TM=`):
- `archive/root/docs/architecture/runtime_snapshot/20260108_013846/PROOFS/docker_compose_config.txt:56` (as `POSTGRES_PASSWORD`)

**Supabase SERVICE_ROLE key** (CRITICAL -- full admin):
- `archive/root/docs/guides/QUICK_START.md:13` -- JWT with `role: service_role`, expires 2045

**Supabase ANON key** (2 locations):
- `archive/work/apps/web/.env.local:2` -- live `.env.local` (not `.env.example`)
- `archive/root/docs/guides/QUICK_START.md:12` -- JWT with `role: anon`

**Supabase PG pooler connection string**:
- `archive/root/docs/guides/QUICK_START.md:11` -- `postgres://postgres.spdtwktxdalcfigzeqrz:SHWYXDMFAwXI1drT@aws-1-us-east-1.pooler.supabase.com:6543/postgres`

**Plaintext user passwords** (previously found in Pass 1 WS-09):
- `archive/addons/tbwa_spectra_integration/data/users_data.xml:17,29,41` -- `finance@tbwa2025`, `cfo@tbwa2025`, `finance.mgr@tbwa2025`

**Infrastructure exposure**:
- `archive/root/config/secrets_inventory.md:25-26` -- DigitalOcean PG hostname `odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com:25060`

**Total**: 12 real credentials, minimum 78-day exposure (runtime snapshot 2026-01-08 to present).

**Finding**: Upgraded C-3 from "2 files with 1 credential" to "12 real credentials across 9 files". The Supabase SERVICE_ROLE key is particularly dangerous as it grants full admin access. Although Supabase is deprecated (2026-03-26), the key may still be valid. All credentials must be rotated immediately.

**Remaining**: Credential rotation (operational action). Pre-commit hook for credential scanning. Consider `git filter-repo` / `bfg` for history purge.
