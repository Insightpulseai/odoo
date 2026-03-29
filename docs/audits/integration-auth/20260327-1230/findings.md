# Audit Findings

**Audit Date**: 2026-03-27 12:30 PHT

---

## Critical

### C-1: Gmail Add-on Backend Endpoints Do Not Exist

- **Impacted Systems**: Gmail add-on, Odoo ERP
- **Current Behavior**: The Gmail add-on (`web/apps/gmail-odoo-addon/`) references six API endpoints under `/ipai/mail_plugin/` (session, provider_session, context, create_lead, create_ticket, log_note). No Odoo controller module implementing these routes exists in the codebase.
- **Expected Behavior**: An Odoo module (`ipai_mail_plugin`) should implement JSON-RPC controllers at these paths, handling session creation, provider token exchange, partner context lookup, and CRM actions.
- **Root Cause**: The add-on was scaffolded as a frontend-first design. The backend bridge module was planned but never built.
- **Recommended Fix**: Build `addons/ipai/ipai_mail_plugin/` with controllers for all six API paths. The controller must validate Bearer tokens, exchange provider codes for Odoo sessions, and proxy CRM operations.
- **Owner Lane**: Odoo backend (ERP plane)
- **Evidence**: `web/apps/gmail-odoo-addon/config.gs:22-29` (API_PATHS), `web/apps/gmail-odoo-addon/auth.gs:225-277` (provider_session call), `web/apps/gmail-odoo-addon/auth.gs:288-326` (session call). Grep for `ipai_mail_plugin` across `addons/ipai/` returns zero results.

### C-2: Entra OIDC Module Not Built

- **Impacted Systems**: Odoo workforce login, Gmail add-on provider auth, Superset SSO
- **Current Behavior**: `ipai_auth_oidc` is referenced in `infra/ssot/auth/oidc_clients.yaml:108` ("module: auth_oauth + ipai_auth_oidc"), `spec/entra-identity-migration/` (72 tasks, 5 phases), and 15+ SSOT/spec files. The module directory does not exist.
- **Expected Behavior**: Module should configure Entra ID as an `auth.oauth.provider` with PKCE support, RS256 token validation, JIT user provisioning, and Entra security group to Odoo `group_ids` sync.
- **Root Cause**: The Entra identity migration spec exists but implementation has not started.
- **Recommended Fix**: Implement `addons/ipai/ipai_auth_oidc/` per the spec at `spec/entra-identity-migration/`. Priority: Odoo login provider first, then Gmail add-on session bridge.
- **Owner Lane**: Identity plane / Odoo backend
- **Evidence**: `infra/ssot/auth/oidc_clients.yaml:108`, `ssot/entra/app_registrations.azure_native.yaml:30-69` (app registration exists with `client_id: 07bd9669-1eca-4d93-8880-fd3abb87f812`). Module not found via `ls addons/ipai/ipai_auth_oidc/`.

### C-3: 12 Real Credentials Exposed Across Archive Files (78+ Days)

- **Impacted Systems**: Production Odoo ERP, PostgreSQL database, Supabase (deprecated), DigitalOcean (deprecated)
- **Current Behavior**: Full credential scan of `archive/` found **12 real credentials** in git-tracked files:

  **Odoo admin password** (Base64-encoded, 5 locations):
  - `archive/root/scripts/prod_access_check.py:7`
  - `archive/root/scripts/prod_db_guess.py:6`
  - `archive/root/docs/architecture/runtime_snapshot/20260108_013846/PROOFS/odoo_conf.txt:29`
  - `archive/root/docs/architecture/runtime_snapshot/20260108_013846/PROOFS/docker_compose_config.txt:17,53`

  **PostgreSQL password** (Base64-encoded):
  - `archive/root/docs/architecture/runtime_snapshot/20260108_013846/PROOFS/docker_compose_config.txt:56`

  **Supabase SERVICE_ROLE key** (CRITICAL -- full admin access):
  - `archive/root/docs/guides/QUICK_START.md:13` -- `eyJhbGci...Rhdi18B5...`

  **Supabase ANON key** (2 locations):
  - `archive/work/apps/web/.env.local:2`
  - `archive/root/docs/guides/QUICK_START.md:12`

  **Supabase PostgreSQL pooler connection string** (embedded password):
  - `archive/root/docs/guides/QUICK_START.md:11` -- `postgres://postgres.spdtwktxdalcfigzeqrz:SHWYXDMFAwXI1drT@...`

  **Plaintext user passwords** (3 accounts):
  - `archive/addons/tbwa_spectra_integration/data/users_data.xml:17,29,41` -- `finance@tbwa2025`, `cfo@tbwa2025`, `finance.mgr@tbwa2025`

  **DigitalOcean PG hostname** (infrastructure exposure):
  - `archive/root/config/secrets_inventory.md:25-26`

- **Expected Behavior**: No credentials in any tracked file, including archive directories.
- **Root Cause**: Legacy scripts, runtime snapshots, quickstart docs, and .env.local files archived without sanitization. Runtime snapshot from 2026-01-08 captured live config with embedded credentials.
- **Recommended Fix**: (1) Rotate ALL exposed credentials immediately (Odoo admin, PostgreSQL, Supabase keys). (2) Sanitize or delete the affected archive files. (3) Consider `git filter-repo` / `bfg` to purge from git history. (4) Add pre-commit hook to scan for credential patterns. (5) Audit access logs for `erp.insightpulseai.com` during the 78+ day exposure window.
- **Owner Lane**: Security / Platform operations -- IMMEDIATE ACTION REQUIRED
- **Evidence**: Full scan results in `GAP_CLOSURE_PASS_1.md` (WS-09) and Pass 2 DG-05 expansion. Minimum exposure: 78+ days (runtime snapshot dated 2026-01-08).

---

## High

### H-1: Platform Admin CLI Credential Requires Immediate Rotation

- **Impacted Systems**: Azure platform operations, CLI access
- **Current Behavior**: `ipai-platform-admin-cli-prod` (client_id `b0172e9f-b179-4abe-9281-d3b56eda4489`) is flagged `status: rotate_required`, `current_risk: expiring_soon` in the SSOT.
- **Expected Behavior**: Credentials should be rotated before expiry. Preferred: migrate to workload identity federation or certificate.
- **Root Cause**: Client secret approaching expiry without rotation workflow.
- **Recommended Fix**: Rotate the client secret in Entra portal, update Azure Key Vault, and plan migration to federated identity.
- **Owner Lane**: Platform operations
- **Evidence**: `ssot/entra/app_registrations.azure_native.yaml:105-144`

### H-2: CardService.newKeyValue() Deprecated -- Gmail Add-on

- **Impacted Systems**: Gmail add-on Marketplace submission
- **Current Behavior**: `newKeyValue()` is used 16+ times across `auth.gs` (2 instances), `homepage.gs` (3 instances), and `context.gs` (5+ instances). The `.ts` sources partially use `setText()` (correct for `newDecoratedText()`) while `.gs` files use `.setContent()` (only valid for `newKeyValue()`). The `homepage.ts` file has one `newDecoratedText()` call at line 46, but `homepage.gs` uses `newKeyValue()` at the same position.
- **Expected Behavior**: All `newKeyValue()` calls migrated to `newDecoratedText()`. `.setContent()` migrated to `.setText()`. `.gs` and `.ts` files must be consistent.
- **Root Cause**: The `.gs` files were generated from `.ts` sources but the migration to `newDecoratedText()` was only partially applied.
- **Recommended Fix**: Migrate all `newKeyValue()` to `newDecoratedText()` in both `.ts` and `.gs` files. Replace `.setContent()` with `.setText()` throughout.
- **Owner Lane**: Gmail add-on / Frontend
- **Evidence**: `web/apps/gmail-odoo-addon/docs/MARKETPLACE_PUBLISHING_KNOWLEDGE_BASE.md:240-254` (documents the issue), `homepage.gs:32-48` vs `homepage.ts:32-49` (inconsistency)

### H-3: Front Door Routes Reference Decommissioned Services

- **Impacted Systems**: Azure Front Door, security posture
- **Current Behavior**: `front-door-routes.yaml` defines origin groups and routing rules for n8n (decommissioned 2026-03-25), Plane (decommissioned 2026-03-25), Shelf (decommissioned 2026-03-25), CRM (decommissioned 2026-03-25), and auth/Keycloak (decommissioned 2026-03-25). WAF overrides exist for n8n webhooks.
- **Expected Behavior**: Decommissioned services should have their Front Door routes removed to reduce attack surface.
- **Root Cause**: Infrastructure-as-code was not updated when services were decommissioned.
- **Recommended Fix**: Remove origin groups and route definitions for: `n8n`, `plane`, `shelf`, `crm`, `auth`. Remove associated WAF overrides and TLS custom domains.
- **Owner Lane**: Infrastructure / Azure
- **Evidence**: `infra/azure/front-door-routes.yaml:40-142` (origin groups), `infra/ssot/azure/service-matrix.yaml:18-46,108-136` (decommission records)

### H-4: DNS Authority Conflict in CLAUDE.md Files

- **Impacted Systems**: Documentation governance, agent behavior
- **Current Behavior**: Parent `~/.claude/CLAUDE.md` states "DNS: Cloudflare (delegated from Spacesquare)". Monorepo `/Users/tbwa/Documents/GitHub/Insightpulseai/CLAUDE.md` states "DNS: Azure DNS (authoritative, delegated from Squarespace)". `~/.claude/rules/infrastructure.md` says "DNS Provider: Cloudflare (authoritative DNS-only mode for Front Door-backed records)".
- **Expected Behavior**: A single canonical statement about DNS authority.
- **Root Cause**: The DNS migration from Cloudflare to Azure DNS was documented in the monorepo CLAUDE.md but not propagated to the parent CLAUDE.md and rules files.
- **Recommended Fix**: Determine current DNS authority (check live NS records). Update all CLAUDE.md files to match. Add to deprecated list if Cloudflare was retired.
- **Owner Lane**: Platform / Documentation
- **Evidence**: `~/.claude/CLAUDE.md` (Cloudflare), monorepo `CLAUDE.md` (Azure DNS), `~/.claude/rules/infrastructure.md` (Cloudflare)

### H-5: Google OAuth Client Secret Stored in Database

- **Impacted Systems**: Odoo `ir.config_parameter`, Google OAuth security
- **Current Behavior**: `ipai_enterprise_bridge` defines `ipai_oauth_google_client_secret` as a `config_parameter` field (line 22-24 of `res_config_settings.py`). This stores the Google OAuth client secret in the `ir.config_parameter` table. The `action_apply_google_oauth()` method does not use the secret (it only uses client_id), but the field exists and users can enter the secret via the Settings UI.
- **Expected Behavior**: OAuth client secrets should be stored in Azure Key Vault and injected as environment variables, never in the Odoo database.
- **Root Cause**: The Settings UI was designed to allow in-app configuration, but secrets should not flow through `ir.config_parameter`.
- **Recommended Fix**: Remove the `ipai_oauth_google_client_secret` field from Settings. Reference Key Vault secret names instead. The client_secret is needed by Odoo's `auth_oauth` during token exchange -- inject it via env var.
- **Owner Lane**: Odoo backend / Security
- **Evidence**: `addons/ipai/ipai_enterprise_bridge/models/res_config_settings.py:22-24`

### H-6: iOS Mobile Wrapper Has No Host Allowlist and No SSO Integration

- **Impacted Systems**: iOS OdooWrapper app, mobile ERP access security
- **Current Behavior**: The iOS wrapper (`web/mobile/`) accepts arbitrary URLs via `navigateTo(url:)` with no `WKNavigationDelegate` host validation. No `ASWebAuthenticationSession` for OAuth/SSO. No Entra integration. Biometric auth is re-entry gating only (not identity). Keychain stores `odoo_session_id` and `odoo_csrf_token` but does NOT re-inject them on app restart. `Info.plist` is missing `NSFaceIDUsageDescription` (App Store rejection risk). Entitlements file is empty.
- **Expected Behavior**: Host allowlist policy struct enforcing navigation to `erp.insightpulseai.com` only. `ASWebAuthenticationSession` for Entra/Google OAuth. `NSFaceIDUsageDescription` in Info.plist. Session tokens re-injected on app resume.
- **Root Cause**: Wrapper was built as a minimal WKWebView shell. Auth and navigation policy were deferred.
- **Recommended Fix**: (1) Add `WKNavigationDelegate` with host allowlist. (2) Add `NSFaceIDUsageDescription` to Info.plist. (3) Implement session token re-injection from Keychain. (4) Add explicit logout handler. (5) Plan `ASWebAuthenticationSession` for Entra SSO when `ipai_auth_oidc` is built.
- **Owner Lane**: iOS / Mobile
- **Evidence**: `web/mobile/Sources/WrapperViewController.swift` (no `decidePolicyFor` delegate), `web/mobile/Sources/Info.plist` (minimal, no Face ID description), `web/mobile/Sources/OdooWrapper.entitlements` (empty dict), `web/mobile/Sources/KeychainService.swift` (stores but doesn't re-inject)

### H-7: ipai_enterprise_bridge Data Files Missing in Monorepo (Out of Sync with odoo/ Repo)

- **Impacted Systems**: Odoo module installation, reproducible environment setup
- **Current Behavior**: `ipai_enterprise_bridge/__manifest__.py` declares `data/mail_server.xml`, `data/oauth_providers.xml`, and 4 other data files. The `data/` directory does not exist at `addons/ipai/ipai_enterprise_bridge/data/` in the monorepo. **However**, the nested `odoo/` repo has `odoo/addons/ipai/ipai_enterprise_bridge/data/oauth_providers.xml` with well-structured Entra ID + Google Workspace providers using Key Vault placeholders. The two repos are out of sync.
- **Expected Behavior**: Data files synced between monorepo and nested odoo/ repo. Module installable from either location.
- **Root Cause**: Monorepo and nested `odoo/` repo have diverged. The `odoo/` repo is ahead with a proper `data/` directory; the monorepo copy is behind.
- **Recommended Fix**: Sync `odoo/addons/ipai/ipai_enterprise_bridge/data/` to `addons/ipai/ipai_enterprise_bridge/data/`. Create remaining missing data files (`mail_server.xml`, `groups.xml`, `sequences.xml`, `scheduled_actions.xml`, `enterprise_bridge_data.xml`).
- **Owner Lane**: Odoo backend / Repo governance
- **Evidence**: `ls addons/ipai/ipai_enterprise_bridge/data/` (not found), `ls odoo/addons/ipai/ipai_enterprise_bridge/data/` (contains `oauth_providers.xml` with Entra + Google providers)

---

## Medium

### M-1: Supabase Deprecation Not Fully Propagated

- **Impacted Systems**: `.mcp.json`, agent tooling, documentation consistency
- **Current Behavior**: `.mcp.json` still configures a Supabase MCP server (lines 19-25) pointing to project `spdtwktxdalcfigzeqrz`. Parent `~/.claude/CLAUDE.md` references Supabase as active. Monorepo `CLAUDE.md` declares all Supabase deprecated (2026-03-26).
- **Expected Behavior**: All Supabase references removed or clearly marked deprecated. MCP server config removed.
- **Root Cause**: Deprecation was declared in monorepo CLAUDE.md but not propagated to all config files and parent documentation.
- **Recommended Fix**: Remove the `supabase` entry from `.mcp.json`. Update parent CLAUDE.md. Remove `plane` entry too (also decommissioned).
- **Owner Lane**: Platform / Documentation
- **Evidence**: `.mcp.json:19-25`, monorepo `CLAUDE.md` (deprecated table)

### M-2: Production odoo.conf Contains Hardcoded db_password

- **Impacted Systems**: Odoo database connection (non-ACA deployments)
- **Current Behavior**: `config/prod/odoo.conf` line 17 has `db_password = odoo`. The Azure config (`config/azure/odoo.conf`) correctly omits DB credentials and documents that they come from ACA env vars.
- **Expected Behavior**: Production config should never contain plaintext passwords, even if they are Docker-compose defaults.
- **Root Cause**: The prod config was designed for Docker Compose local deployment, not ACA. The Azure config was added later as the correct template.
- **Recommended Fix**: Change `db_password = odoo` to `db_password = ${ODOO_DB_PASSWORD}` or remove it entirely with a comment pointing to env var injection.
- **Owner Lane**: Infrastructure / Odoo config
- **Evidence**: `config/prod/odoo.conf:17`, `config/azure/odoo.conf:6-12` (correct pattern)

### M-3: Gmail Add-on Nonce Not Generated Before Provider Auth Start

- **Impacted Systems**: Gmail add-on OAuth security
- **Current Behavior**: `startProviderAuth()` opens the Odoo login page but does NOT call `buildAuthStateNonce()` before opening the URL. The nonce generation function exists and is well-implemented, but it is never invoked in the auth start flow. The `exchangeSessionToken()` function validates the nonce only if `returnedNonce` is non-empty (line 215/222 of auth.gs: `if (returnedNonce)`), meaning empty nonce passes validation.
- **Expected Behavior**: `buildAuthStateNonce()` should be called before opening the auth URL, and the nonce should be passed as a `state` parameter. The exchange should require the nonce, not treat it as optional.
- **Root Cause**: The nonce system was designed for a future backend-driven flow where the state would round-trip through the provider. The current flow (browser overlay + reload) does not have a mechanism to pass state back.
- **Recommended Fix**: When the backend bridge is built, include the nonce in the auth URL state parameter. Make nonce validation mandatory in `exchangeSessionToken()` (remove the `if (returnedNonce)` guard).
- **Owner Lane**: Gmail add-on / Backend
- **Evidence**: `web/apps/gmail-odoo-addon/auth.gs:173-199` (no nonce generation), `web/apps/gmail-odoo-addon/auth.gs:214-216` (optional validation)

### M-4: Load Test File Contains Test Credentials

- **Impacted Systems**: Performance test suite
- **Current Behavior**: `infra/tests/performance/odoo-comprehensive-load.js` lines 65-67 contain test user emails and passwords (`Test@123`).
- **Expected Behavior**: Test credentials should be in env vars or test fixtures, not hardcoded in source.
- **Root Cause**: Load test script written for convenience with inline credentials.
- **Recommended Fix**: Move test credentials to env vars. Use `__ENV.TEST_USER1_PASSWORD` pattern.
- **Owner Lane**: QA / Testing
- **Evidence**: `infra/tests/performance/odoo-comprehensive-load.js:65-67`

### M-5: Wix MCP Server URL Inconsistency

- **Impacted Systems**: Developer tooling
- **Current Behavior**: `.mcp.json` configures Wix as `"command": "npx", "args": ["-y", "@wix/mcp"]` (CLI-based). `.vscode/mcp.json` configures Wix as `"type": "http", "url": "https://mcp.wix.com/sse"` (HTTP SSE-based). Two different transports for the same service.
- **Expected Behavior**: Single canonical Wix MCP configuration.
- **Root Cause**: Different MCP client implementations (Claude Code vs VS Code) may require different transport configs.
- **Recommended Fix**: Consolidate on one transport. HTTP SSE is generally preferred for reliability. Document why both exist if both are needed.
- **Owner Lane**: Developer experience
- **Evidence**: `.mcp.json:39-41`, `.vscode/mcp.json:8-13`

---

## Low

### L-1: .gs and .ts Source Files Are Duplicated

- **Impacted Systems**: Gmail add-on development workflow
- **Current Behavior**: Both `.gs` (transpiled/deployed) and `.ts` (source) files exist in the repo root of the add-on. The `.gs` files appear to be manually maintained copies rather than build outputs. They have subtle differences (e.g., `homepage.gs` uses `newKeyValue()` at line 46 while `homepage.ts` uses `newDecoratedText()` at line 46).
- **Expected Behavior**: `.ts` files should be the source of truth, and `.gs` files should be generated by a build step (or `.ts` should be transpiled via clasp).
- **Root Cause**: clasp supports TypeScript transpilation, but the current setup maintains both manually.
- **Recommended Fix**: Either configure clasp to transpile `.ts` to `.gs` automatically, or remove `.ts` files and maintain `.gs` only. Add a build step to `package.json`.
- **Owner Lane**: Gmail add-on / DevEx
- **Evidence**: `web/apps/gmail-odoo-addon/auth.gs` vs `web/apps/gmail-odoo-addon/src/auth.ts`, `homepage.gs:46` vs `homepage.ts:46` (API call mismatch)

### L-2: Odoo ACA Proxy Module Uses Monkey Patching

- **Impacted Systems**: Odoo HTTP stack stability
- **Current Behavior**: `ipai_aca_proxy` uses `post_load` hook to monkey-patch `odoo.http.Application.__call__` to inject `X-Forwarded-Host`. This is fragile across Odoo version upgrades.
- **Expected Behavior**: The fix is architecturally correct for the ACA constraint (ACA does not send X-Forwarded-Host). Consider contributing upstream or using Odoo's `server_environment` pattern.
- **Root Cause**: Azure Container Apps ingress limitation (no X-Forwarded-Host header).
- **Recommended Fix**: No immediate action needed -- the patch is well-documented and solves a real problem. Monitor during Odoo version upgrades.
- **Owner Lane**: Odoo backend
- **Evidence**: `addons/ipai/ipai_aca_proxy/__init__.py:28-49`

### L-3: Google Workspace Domain Hardcoded as Default

- **Impacted Systems**: Multi-tenant flexibility
- **Current Behavior**: `ipai_enterprise_bridge` defaults `ipai_oauth_google_workspace_domain` to `"w9studio.net"` (line 28 of `res_config_settings.py`). This is a code-level default for a tenant-specific value.
- **Expected Behavior**: Domain-specific defaults should come from SSOT config or env vars, not module defaults.
- **Root Cause**: Single-tenant assumption baked into module defaults.
- **Recommended Fix**: Change default to empty string. Populate from SSOT or deployment config.
- **Owner Lane**: Odoo backend
- **Evidence**: `addons/ipai/ipai_enterprise_bridge/models/res_config_settings.py:28`
