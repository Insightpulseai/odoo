# Remediation Plan

**Audit Date**: 2026-03-27 12:30 PHT

---

## P0 -- Immediate Hotfixes (Security, Broken Flows)

### P0-1: Remove Hardcoded Production Credentials from Archive

- **Finding**: C-3
- **Files to change**:
  - `archive/root/scripts/prod_access_check.py` -- remove or replace password on line 7
  - `archive/root/scripts/prod_db_guess.py` -- remove or replace password on line 6
- **Change intent**: Eliminate plaintext production credentials from git history
- **Verification**: `grep -r 'UbQbX75Wi' .` returns zero results
- **Rollback**: Revert the commit. Credential should be rotated regardless.
- **Note**: If the credential `UbQbX75Wi+P3R+bItzO/NapptGbL4n/9MvIDVw71Oww=` is still active for any PostgreSQL server, rotate it immediately via Azure Portal or `az postgres flexible-server update`.

### P0-2: Rotate Platform Admin CLI Credential

- **Finding**: H-1
- **Files to change**:
  - Azure Portal: Entra ID -> App registrations -> `ipai-platform-admin-cli-prod` -> Certificates & secrets -> New client secret
  - Azure Key Vault: Update secret value
  - `ssot/entra/app_registrations.azure_native.yaml` -- update `status` from `rotate_required` to `current`
- **Change intent**: Prevent credential expiry that would break platform admin operations
- **Verification**: `az ad app credential list --id b0172e9f-b179-4abe-9281-d3b56eda4489` shows new credential with future expiry
- **Rollback**: Old credential remains valid until expiry. New credential can be deleted if misconfigured.

### P0-3: Remove Load Test Hardcoded Credentials

- **Finding**: M-4
- **Files to change**:
  - `infra/tests/performance/odoo-comprehensive-load.js` -- replace inline passwords with `__ENV.TEST_PASSWORD` references
- **Change intent**: No credentials in source code, even test credentials
- **Verification**: `grep -n 'Test@123' infra/tests/` returns zero results
- **Rollback**: Revert commit.

---

## P1 -- Short-Term Hardening (Auth Correctness, Governance)

### P1-1: Build `ipai_mail_plugin` Odoo Controller Module

- **Finding**: C-1
- **Files to change** (create):
  - `addons/ipai/ipai_mail_plugin/__init__.py`
  - `addons/ipai/ipai_mail_plugin/__manifest__.py`
  - `addons/ipai/ipai_mail_plugin/controllers/__init__.py`
  - `addons/ipai/ipai_mail_plugin/controllers/main.py` -- implement 6 JSON-RPC endpoints
  - `addons/ipai/ipai_mail_plugin/security/ir.model.access.csv`
- **Change intent**: Provide backend API surface for Gmail add-on auth and CRM actions
- **Endpoints**:
  - `POST /ipai/mail_plugin/session` -- email + API key -> session token
  - `POST /ipai/mail_plugin/provider_session` -- provider code + tenant_id -> session token
  - `POST /ipai/mail_plugin/context` -- sender_email + subject -> partner/lead/ticket data
  - `POST /ipai/mail_plugin/actions/create_lead` -- create CRM lead
  - `POST /ipai/mail_plugin/actions/create_ticket` -- create project.task
  - `POST /ipai/mail_plugin/actions/log_note` -- log chatter note
- **Verification**: `curl -s -X POST https://erp.insightpulseai.com/ipai/mail_plugin/session -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","method":"call","params":{"email":"test@example.com","api_key":"invalid"}}' | jq .error` returns auth error (not 404)
- **Rollback**: Uninstall module: `odoo-bin -d odoo -u ipai_mail_plugin --stop-after-init`

### P1-2: Build `ipai_auth_oidc` Odoo Module

- **Finding**: C-2
- **Files to change** (create):
  - `addons/ipai/ipai_auth_oidc/__init__.py`
  - `addons/ipai/ipai_auth_oidc/__manifest__.py`
  - `addons/ipai/ipai_auth_oidc/models/auth_oauth_provider.py` -- PKCE + RS256 extensions
  - `addons/ipai/ipai_auth_oidc/data/auth_oauth_provider_data.xml` -- Entra + Google provider records
  - `addons/ipai/ipai_auth_oidc/security/ir.model.access.csv`
- **Change intent**: Enable Entra OIDC login for Odoo workforce and Google OAuth for portal users
- **Spec reference**: `spec/entra-identity-migration/` (72 tasks, 5 phases)
- **Verification**:
  1. Install: `odoo-bin -d test_ipai_auth_oidc -i ipai_auth_oidc --stop-after-init`
  2. Check provider: `SELECT name, enabled FROM auth_oauth_provider WHERE name ILIKE '%entra%'`
  3. Login page shows "Log in with Microsoft" button at `/web/login`
- **Rollback**: Uninstall module. Stock `auth_oauth` remains intact.
- **Dependencies**: Entra app registration already exists (`ipai-odoo-login-prod`). Client ID and secret must be in Key Vault.

### P1-3: Migrate `newKeyValue()` to `newDecoratedText()` in Gmail Add-on

- **Finding**: H-2
- **Files to change**:
  - `web/apps/gmail-odoo-addon/src/auth.ts` -- 2 instances (lines 410, 415)
  - `web/apps/gmail-odoo-addon/src/homepage.ts` -- already partially migrated (line 46); fix lines 32, 39
  - `web/apps/gmail-odoo-addon/src/context.ts` -- 5+ instances
  - `web/apps/gmail-odoo-addon/auth.gs` -- 2 instances
  - `web/apps/gmail-odoo-addon/homepage.gs` -- 3 instances
  - `web/apps/gmail-odoo-addon/context.gs` -- 5+ instances
- **Change intent**: Replace deprecated CardService API before Marketplace submission
- **Migration pattern**: `newKeyValue().setTopLabel(x).setContent(y)` -> `newDecoratedText().setTopLabel(x).setText(y)`
- **Verification**: `grep -c 'newKeyValue' web/apps/gmail-odoo-addon/*.gs web/apps/gmail-odoo-addon/src/*.ts` returns 0 for all files
- **Rollback**: Revert commit. `newKeyValue()` still works at runtime (just deprecated).

### P1-4: Move Google OAuth Client Secret Out of ir.config_parameter

- **Finding**: H-5
- **Files to change**:
  - `addons/ipai/ipai_enterprise_bridge/models/res_config_settings.py` -- remove `ipai_oauth_google_client_secret` field
  - `addons/ipai/ipai_auth_oidc/data/auth_oauth_provider_data.xml` -- reference env var for secret
- **Change intent**: Secrets in Azure Key Vault only, never in Odoo database
- **Verification**: `SELECT key FROM ir_config_parameter WHERE key LIKE '%client_secret%'` returns 0 rows
- **Rollback**: Re-add the field. Secret value in DB needs manual cleanup.

---

## P2 -- Architecture Cleanup (Deprecated Services, Identity Consolidation)

### P2-1: Prune Front Door Routes for Decommissioned Services

- **Finding**: H-3
- **Files to change**:
  - `infra/azure/front-door-routes.yaml` -- remove origin groups: `n8n`, `plane`, `shelf`, `crm`, `auth`
  - Remove route groups: `automation-n8n`, `apps-plane`, `apps-shelf`, `apps-crm`, `services-auth`
  - Remove WAF overrides for `automation-n8n`
  - Remove TLS custom domains: `n8n.insightpulseai.com`, `plane.insightpulseai.com`, `shelf.insightpulseai.com`, `crm.insightpulseai.com`, `auth.insightpulseai.com`
- **Change intent**: Reduce attack surface by removing routing to non-existent backends
- **Verification**: `grep -c 'n8n\|plane\|shelf\|crm\|auth' infra/azure/front-door-routes.yaml` returns 0
- **Rollback**: Revert commit. Front Door will re-enable routes on next Bicep deploy.

### P2-2: Resolve DNS Authority Conflict

- **Finding**: H-4
- **Files to change**:
  - Determine actual DNS provider (check `dig NS insightpulseai.com`)
  - Update `~/.claude/CLAUDE.md` to match reality
  - Update `~/.claude/rules/infrastructure.md` to match reality
  - Update monorepo `CLAUDE.md` to match reality
- **Change intent**: Single source of truth for DNS authority
- **Verification**: All three files agree on DNS provider. `dig NS insightpulseai.com` output matches documentation.
- **Rollback**: N/A (documentation only).

### P2-3: Remove Deprecated MCP Server Configurations

- **Finding**: M-1
- **Files to change**:
  - `.mcp.json` -- remove `supabase` entry (lines 19-25), remove `plane` entry (lines 33-35)
- **Change intent**: Remove tooling references to decommissioned services
- **Verification**: `jq '.mcpServers | keys' .mcp.json` does not include "supabase" or "plane"
- **Rollback**: Revert commit. MCP servers can be re-added.

### P2-4: Sanitize Production odoo.conf

- **Finding**: M-2
- **Files to change**:
  - `config/prod/odoo.conf` -- change `db_password = odoo` to a comment/env-var reference
- **Change intent**: No plaintext credentials in config files, even Docker Compose defaults
- **Verification**: `grep 'db_password' config/prod/odoo.conf` shows env-var pattern or comment
- **Rollback**: Revert commit.

---

## P3 -- Future Improvements (Optimization, UX Polish)

### P3-1: Make Auth State Nonce Mandatory in Gmail Add-on

- **Finding**: M-3
- **Files to change**:
  - `web/apps/gmail-odoo-addon/src/auth.ts` (and `.gs`) -- call `buildAuthStateNonce()` in `startProviderAuth()`, include in auth URL
  - Make nonce validation mandatory in `exchangeSessionToken()` (remove `if (returnedNonce)` guard)
- **Change intent**: Enforce CSRF protection on all provider auth flows
- **Verification**: Unit test: `exchangeSessionToken()` with empty nonce returns error card
- **Rollback**: Revert commit. Current behavior (optional nonce) still works.
- **Dependency**: Requires P1-1 (backend endpoints) to be functional first.

### P3-2: Unify .ts and .gs Source Files

- **Finding**: L-1
- **Files to change**:
  - `web/apps/gmail-odoo-addon/package.json` -- add build script for clasp TypeScript transpilation
  - Remove manually maintained `.gs` files from repo root (keep in `src/` as `.ts` only)
  - Or: Remove `.ts` files and maintain `.gs` only
- **Change intent**: Single source of truth for add-on code
- **Verification**: `clasp push` succeeds from `.ts` sources only
- **Rollback**: Restore `.gs` files from git history.

### P3-3: Implement Superset Entra SSO

- **Finding**: Inventory (Superset has no SSO)
- **Files to change**:
  - Superset `superset_config.py` -- configure Flask-AppBuilder OIDC with Entra
  - `infra/ssot/auth/oidc_clients.yaml` -- update Superset client status from `planned` to `active`
- **Change intent**: Unified workforce authentication across ERP and BI surfaces
- **Verification**: Login to `https://superset.insightpulseai.com` redirects to Entra login
- **Rollback**: Revert Superset config. Local login still works.
- **Dependency**: Entra app registration for Superset must be created.

### P3-4: Implement Foundry Agent Service Auth Pipeline

- **Finding**: Inventory (Foundry configured in Settings but not operational)
- **Files to change**:
  - `addons/ipai/ipai_enterprise_bridge/` -- implement Foundry API client using `DefaultAzureCredential`
  - Key Vault: Ensure Foundry endpoint secrets are provisioned
- **Change intent**: Enable AI model inference and agent execution from Odoo
- **Verification**: `action_test_foundry_connection()` returns success notification
- **Rollback**: Disable `ipai_foundry_enabled` in Settings.

---

## Execution Sequence

```
Week 1 (P0):
  P0-1: Remove hardcoded credentials
  P0-2: Rotate admin CLI credential
  P0-3: Remove test credentials

Week 2-3 (P1):
  P1-1: Build ipai_mail_plugin controller
  P1-2: Build ipai_auth_oidc module
  P1-3: Migrate newKeyValue() to newDecoratedText()
  P1-4: Move Google client_secret to Key Vault

Week 4 (P2):
  P2-1: Prune Front Door routes
  P2-2: Resolve DNS authority conflict
  P2-3: Remove deprecated MCP servers
  P2-4: Sanitize prod odoo.conf

Week 5+ (P3):
  P3-1: Mandatory nonce in Gmail add-on
  P3-2: Unify .ts/.gs sources
  P3-3: Superset Entra SSO
  P3-4: Foundry auth pipeline
```
