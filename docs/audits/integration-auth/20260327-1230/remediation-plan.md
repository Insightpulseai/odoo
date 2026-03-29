# Remediation Plan

**Audit Date**: 2026-03-27 12:30 PHT
**Target State**: `docs/audits/integration-auth/20260327-1230/target-state.md`

---

## P0 -- Immediate Hotfixes (Security, Credential Exposure)

### P0-1: Remove Hardcoded Production Credentials from Archive

- **Finding**: C-3
- **Subsystem**: PostgreSQL production database, git history
- **Files to change**:
  - `archive/root/scripts/prod_access_check.py` -- remove password value on line 7, replace with `password = os.environ.get("PG_PASSWORD", "")`
  - `archive/root/scripts/prod_db_guess.py` -- remove password value on line 6, same replacement
- **Change intent**: Eliminate plaintext production credentials from tracked files
- **Verification**: `grep -r 'UbQbX75Wi' .` returns zero results across the entire repo
- **Rollback**: Revert the commit. The credential itself must be rotated regardless of rollback.
- **Post-action**: If the credential `UbQbX75Wi+P3R+bItzO/NapptGbL4n/9MvIDVw71Oww=` is still active for any PostgreSQL server, rotate it immediately via `az postgres flexible-server update` or Azure Portal. The value persists in git history -- consider `git filter-repo` or accept the risk with rotation.

### P0-2: Rotate Platform Admin CLI Credential

- **Finding**: H-1
- **Subsystem**: Azure Entra app registration, platform admin operations
- **Files/systems to change**:
  - Azure Portal: Entra ID -> App registrations -> `ipai-platform-admin-cli-prod` (client_id: `b0172e9f-b179-4abe-9281-d3b56eda4489`) -> Certificates & secrets -> New client secret
  - Azure Key Vault `kv-ipai-dev`: Update stored secret value
  - `ssot/entra/app_registrations.azure_native.yaml` -- update `status` from `rotate_required` to `active`, update `last_rotated` timestamp
- **Change intent**: Prevent credential expiry that would break platform admin CLI operations
- **Verification**: `az ad app credential list --id b0172e9f-b179-4abe-9281-d3b56eda4489` shows new credential with expiry > 90 days from now. Old credential removed.
- **Rollback**: Old credential remains valid until its original expiry. New credential can be deleted if misconfigured. Both can coexist temporarily.

### P0-3: Remove Hardcoded Test Credentials from Load Test

- **Finding**: M-4
- **Subsystem**: Performance test suite
- **Files to change**:
  - `infra/tests/performance/odoo-comprehensive-load.js` lines 65-67 -- replace inline passwords (`Test@123`) with `__ENV.TEST_USER1_PASSWORD` pattern
- **Change intent**: No credentials in source code, even test credentials
- **Verification**: `grep -rn 'Test@123' infra/tests/` returns zero results
- **Rollback**: Revert commit. Load tests will need env vars set to run.

### P0-4: Remove Hardcoded db_password from Production Config

- **Finding**: M-2
- **Subsystem**: Odoo database connection configuration
- **Files to change**:
  - `config/prod/odoo.conf` line 17 -- change `db_password = odoo` to `; db_password injected via ACA env vars from Key Vault (see config/azure/odoo.conf)`
- **Change intent**: No plaintext passwords in config files. Azure config (`config/azure/odoo.conf`) already follows the correct pattern.
- **Verification**: `grep -n 'db_password.*=.*[^$]' config/prod/odoo.conf` returns zero results (no literal password assignments)
- **Rollback**: Revert commit. Docker Compose local dev may need `ODOO_DB_PASSWORD=odoo` env var set.

---

## P1 -- Short-Term Hardening (Build Missing Auth Modules)

### P1-1: Build `ipai_auth_oidc` Odoo Module

- **Finding**: C-2
- **Subsystem**: Odoo workforce login, Entra identity integration
- **Files to create**:
  - `addons/ipai/ipai_auth_oidc/__init__.py`
  - `addons/ipai/ipai_auth_oidc/__manifest__.py` -- depends on `auth_oauth`, version `19.0.1.0.0`
  - `addons/ipai/ipai_auth_oidc/models/__init__.py`
  - `addons/ipai/ipai_auth_oidc/models/auth_oauth_provider.py` -- extend `auth.oauth.provider` with PKCE support (`code_verifier`, `code_challenge_method`), RS256 token validation, JIT user provisioning logic
  - `addons/ipai/ipai_auth_oidc/data/auth_oauth_provider_data.xml` -- Entra provider record (client_id from env var, endpoints for v2.0), Google provider record (w9studio.net hosted domain)
  - `addons/ipai/ipai_auth_oidc/security/ir.model.access.csv`
- **Files to modify**:
  - `addons/ipai/ipai_enterprise_bridge/models/res_config_settings.py` -- remove `ipai_oauth_google_client_secret` field (finding H-5, consolidated here)
  - `addons/ipai/ipai_enterprise_bridge/models/settings_actions.py` -- remove `action_apply_google_oauth()` method (provider now managed by `ipai_auth_oidc` data file)
- **Change intent**: Enable Entra OIDC login for Odoo workforce and Google OAuth for portal users. Move provider configuration from DB-injected to module-managed.
- **Spec reference**: `spec/entra-identity-migration/` (72 tasks, 5 phases)
- **Verification**:
  1. Test install: `odoo-bin -d test_ipai_auth_oidc -i ipai_auth_oidc --stop-after-init --test-enable`
  2. Provider exists: `SELECT name, enabled, client_id FROM auth_oauth_provider WHERE name ILIKE '%entra%'` returns one row
  3. Login page at `/web/login` shows "Log in with Microsoft" button
  4. No client_secret in DB: `SELECT key FROM ir_config_parameter WHERE key LIKE '%client_secret%'` returns 0 rows
- **Rollback**: Uninstall module. Stock `auth_oauth` remains intact. Re-add `ipai_enterprise_bridge` fields if Google OAuth reverts to DB-injected pattern.
- **Dependencies**: Entra app registration `ipai-odoo-login-prod` exists (client_id: `07bd9669-1eca-4d93-8880-fd3abb87f812`). Client ID and secret must be provisioned in Key Vault as `entra-odoo-login-client-id` and `entra-odoo-login-client-secret`.

### P1-2: Build `ipai_mail_plugin` Odoo Controller Module

- **Finding**: C-1
- **Subsystem**: Gmail add-on backend, CRM bridge
- **Files to create**:
  - `addons/ipai/ipai_mail_plugin/__init__.py`
  - `addons/ipai/ipai_mail_plugin/__manifest__.py` -- depends on `mail`, `crm`, `project`, `ipai_auth_oidc`
  - `addons/ipai/ipai_mail_plugin/controllers/__init__.py`
  - `addons/ipai/ipai_mail_plugin/controllers/main.py` -- implement 6 JSON-RPC endpoints
  - `addons/ipai/ipai_mail_plugin/security/ir.model.access.csv`
- **Endpoints to implement**:
  - `POST /ipai/mail_plugin/session` -- email + API key validation -> session token
  - `POST /ipai/mail_plugin/provider_session` -- provider code + nonce -> session token (validates nonce, exchanges code)
  - `POST /ipai/mail_plugin/context` -- sender_email + subject -> partner/lead/ticket context data
  - `POST /ipai/mail_plugin/actions/create_lead` -- create `crm.lead` from Gmail context
  - `POST /ipai/mail_plugin/actions/create_ticket` -- create `project.task` from Gmail context
  - `POST /ipai/mail_plugin/actions/log_note` -- log chatter note on matched partner/lead
- **Change intent**: Provide the backend API surface that the Gmail add-on client code already calls
- **Verification**:
  1. Test install: `odoo-bin -d test_ipai_mail_plugin -i ipai_mail_plugin --stop-after-init --test-enable`
  2. Endpoint reachable: `curl -s -X POST https://erp.insightpulseai.com/ipai/mail_plugin/session -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","method":"call","params":{"email":"test@example.com","api_key":"invalid"}}' | jq .error` returns auth error (not 404)
  3. All 6 API paths return structured JSON-RPC responses (not 404)
- **Rollback**: Uninstall module: `odoo-bin -d odoo -u ipai_mail_plugin --stop-after-init`
- **Dependencies**: P1-1 (`ipai_auth_oidc`) must be built first for provider session exchange.

### P1-3: Prune Front Door Routes for Decommissioned Services

- **Finding**: H-3
- **Subsystem**: Azure Front Door, network security posture
- **Files to change**:
  - `infra/azure/front-door-routes.yaml` -- remove origin groups and route definitions for:
    - `n8n` (decommissioned 2026-03-25)
    - `plane` (decommissioned 2026-03-25)
    - `shelf` (decommissioned 2026-03-25)
    - `crm` (decommissioned 2026-03-25)
    - `auth` / Keycloak (decommissioned 2026-03-25)
  - Remove WAF overrides for `automation-n8n` webhook paths
  - Remove TLS custom domain bindings: `n8n.insightpulseai.com`, `plane.insightpulseai.com`, `shelf.insightpulseai.com`, `crm.insightpulseai.com`, `auth.insightpulseai.com`
- **Change intent**: Reduce attack surface by removing routing rules that point to non-existent ACA backends
- **Verification**: `grep -cE 'n8n|plane|shelf|crm|auth' infra/azure/front-door-routes.yaml` returns 0. After Bicep deploy, `az afd route list` confirms only active routes remain.
- **Rollback**: Revert commit. Front Door will re-enable routes on next Bicep deploy.

### P1-4: Migrate CardService `newKeyValue()` to `newDecoratedText()`

- **Finding**: H-2
- **Subsystem**: Gmail add-on, Google Marketplace compliance
- **Files to change**:
  - `web/apps/gmail-odoo-addon/src/auth.ts` -- 2 instances
  - `web/apps/gmail-odoo-addon/src/homepage.ts` -- 3 instances (line 46 already partially migrated)
  - `web/apps/gmail-odoo-addon/src/context.ts` -- 5+ instances
  - `web/apps/gmail-odoo-addon/auth.gs` -- 2 instances
  - `web/apps/gmail-odoo-addon/homepage.gs` -- 3 instances
  - `web/apps/gmail-odoo-addon/context.gs` -- 5+ instances
- **Migration pattern**: `CardService.newKeyValue().setTopLabel(x).setContent(y)` becomes `CardService.newDecoratedText().setTopLabel(x).setText(y)`
- **Change intent**: Replace deprecated CardService API calls before Google Marketplace submission
- **Verification**: `grep -c 'newKeyValue' web/apps/gmail-odoo-addon/*.gs web/apps/gmail-odoo-addon/src/*.ts` returns 0 for all files. `grep -c 'setContent' web/apps/gmail-odoo-addon/*.gs web/apps/gmail-odoo-addon/src/*.ts` returns 0 for all files (replaced by `setText`).
- **Rollback**: Revert commit. `newKeyValue()` still works at runtime (deprecated, not removed).

---

## P2 -- Architecture Cleanup (Config Consistency, Deprecated References)

### P2-1: Resolve DNS Authority Conflict in Documentation

- **Finding**: H-4
- **Subsystem**: Documentation governance, agent behavior consistency
- **Files to change**:
  - Determine actual DNS provider: run `dig NS insightpulseai.com` and record the authoritative nameservers
  - `~/.claude/CLAUDE.md` -- update DNS line to match reality
  - `~/.claude/rules/infrastructure.md` -- update "DNS Provider" to match reality
  - `/Users/tbwa/Documents/GitHub/Insightpulseai/CLAUDE.md` -- update DNS line to match reality
  - If Cloudflare is retired, add to "Deprecated" table in all three files
- **Change intent**: Single canonical statement about DNS authority across all agent instruction files
- **Verification**: All three files agree on DNS provider. `dig NS insightpulseai.com` output matches documentation. No contradictory statements exist.
- **Rollback**: N/A (documentation only).

### P2-2: Remove Deprecated MCP Server Configurations

- **Finding**: M-1
- **Subsystem**: Developer tooling, `.mcp.json` configuration
- **Files to change**:
  - `.mcp.json` -- remove `supabase` entry (lines 19-25, Supabase decommissioned 2026-03-26)
  - `.mcp.json` -- remove `plane` entry (lines 33-35, Plane decommissioned 2026-03-25)
- **Change intent**: Remove tooling references to decommissioned services. Prevents agent confusion and stale credential usage.
- **Verification**: `jq '.mcpServers | keys' .mcp.json` does not include `"supabase"` or `"plane"`. Remaining MCP servers: `github`, `azure`, `azure-devops`, `wix`, `docker`.
- **Rollback**: Revert commit. MCP servers can be re-added if services are restored.

### P2-3: Consolidate MCP Wix Server Configuration

- **Finding**: M-5
- **Subsystem**: Developer tooling, MCP transport consistency
- **Files to change**:
  - `.mcp.json` line 39-41 -- Wix configured as CLI (`npx -y @wix/mcp`)
  - `.vscode/mcp.json` line 8-13 -- Wix configured as HTTP SSE (`https://mcp.wix.com/sse`)
- **Change intent**: Single canonical Wix MCP transport. HTTP SSE is preferred for reliability.
- **Verification**: Both files use consistent transport, or a comment documents why different transports are needed per client.
- **Rollback**: Revert commit.

### P2-4: Align Supabase Deprecation Across All Documentation

- **Finding**: M-1 (documentation propagation)
- **Subsystem**: Agent instruction files
- **Files to change**:
  - `~/.claude/CLAUDE.md` -- update Supabase reference from active to deprecated, or remove the row and add to deprecated table
  - Verify monorepo `CLAUDE.md` deprecated table is authoritative (it already declares Supabase deprecated 2026-03-26)
- **Change intent**: All agent instruction files agree that Supabase is fully deprecated
- **Verification**: `grep -rn 'spdtwktxdalcfigzeqrz' ~/.claude/CLAUDE.md` returns zero results or results are within a "Deprecated" section
- **Rollback**: N/A (documentation only).

---

## P3 -- Optional Improvements (Hardening, UX, Future-Proofing)

### P3-1: Make Auth State Nonce Mandatory in Gmail Add-on

- **Finding**: M-3
- **Subsystem**: Gmail add-on OAuth CSRF protection
- **Files to change**:
  - `web/apps/gmail-odoo-addon/src/auth.ts` -- call `buildAuthStateNonce()` in `startProviderAuth()` before opening auth URL, include nonce in `state` parameter
  - `web/apps/gmail-odoo-addon/src/auth.ts` -- remove `if (returnedNonce)` guard in `exchangeSessionToken()`, make nonce validation unconditional
  - Mirror changes in `web/apps/gmail-odoo-addon/auth.gs`
- **Change intent**: Enforce CSRF protection on all provider auth flows. Empty nonce must be rejected.
- **Verification**: Manual test: `exchangeSessionToken()` called with empty nonce returns error card. Nonce round-trips through `state` parameter.
- **Rollback**: Revert commit. Current behavior (optional nonce) still works.
- **Dependency**: Requires P1-2 (`ipai_mail_plugin` backend) to be functional for end-to-end testing.

### P3-2: Unify .ts and .gs Source Files

- **Finding**: L-1
- **Subsystem**: Gmail add-on development workflow
- **Files to change**:
  - `web/apps/gmail-odoo-addon/package.json` -- add `build` script for clasp TypeScript transpilation
  - `web/apps/gmail-odoo-addon/tsconfig.json` -- configure output to match clasp expectations
  - Remove manually maintained `.gs` files from repo root (`auth.gs`, `homepage.gs`, `context.gs`, `actions.gs`, `config.gs`) -- these become build outputs
  - `.claspignore` -- update to exclude `.ts` source, include generated `.gs` output
- **Change intent**: Single source of truth for add-on code. `.ts` files are canonical, `.gs` files are generated by build step.
- **Verification**: `clasp push` succeeds from `.ts` sources only. `npm run build && clasp push` deploys correctly.
- **Rollback**: Restore `.gs` files from git history. Revert `package.json` changes.

### P3-3: Implement Credential Auto-Rotation Policy

- **Subsystem**: Azure Key Vault, Entra app registrations
- **Files/systems to change**:
  - Azure Key Vault `kv-ipai-dev`: Enable auto-rotation for PG credentials, SMTP credentials
  - Entra app registrations: Set 90-day max secret lifetime policy
  - `ssot/entra/app_registrations.azure_native.yaml` -- document rotation schedule for each registration
- **Change intent**: Prevent credential expiry incidents. Automated rotation reduces operational burden.
- **Verification**: `az keyvault secret show --vault-name kv-ipai-dev --name pg-odoo-password --query attributes.expires` shows future date within rotation window. Entra app credential expiry < 90 days.
- **Rollback**: Disable auto-rotation policy. Manual rotation reverts to current process.

### P3-4: Implement Superset Entra SSO

- **Finding**: Inventory (Superset has no SSO, local login only)
- **Subsystem**: Superset BI, workforce authentication
- **Files to change**:
  - Superset `superset_config.py` -- configure Flask-AppBuilder OIDC with Entra provider
  - `infra/ssot/auth/oidc_clients.yaml` -- update Superset client status from `planned` to `active`
  - Azure Portal: Create Entra app registration for Superset
- **Change intent**: Unified workforce authentication across ERP and BI surfaces
- **Verification**: Login to `https://superset.insightpulseai.com` redirects to Entra login page. After Entra auth, user lands on Superset dashboard.
- **Rollback**: Revert Superset config. Local login still works as fallback.
- **Dependency**: Entra app registration for Superset must be created first.

### P3-5: Implement Foundry Agent Service Auth Pipeline

- **Finding**: Inventory (Foundry configured in Settings but not operational)
- **Subsystem**: Azure AI Foundry, Odoo AI integration
- **Files to change**:
  - `addons/ipai/ipai_enterprise_bridge/` -- implement Foundry API client using `DefaultAzureCredential` (managed identity first, API key fallback)
  - Azure Key Vault: Ensure Foundry endpoint and API key secrets are provisioned
- **Change intent**: Enable AI model inference and agent execution from Odoo via managed identity
- **Verification**: `action_test_foundry_connection()` in Odoo Settings returns success notification. API call reaches `oai-ipai-dev` endpoint.
- **Rollback**: Disable `ipai_foundry_enabled` in Settings. No functional regression.

---

## Execution Sequence

```text
Week 1 (P0 -- credential hygiene):
  P0-1: Remove hardcoded production credentials from archive
  P0-2: Rotate platform admin CLI credential
  P0-3: Remove hardcoded test credentials from load test
  P0-4: Remove hardcoded db_password from prod config

Week 2-3 (P1 -- build auth stack):
  P1-1: Build ipai_auth_oidc module (Entra + Google providers)
  P1-2: Build ipai_mail_plugin controller (Gmail add-on backend)
  P1-3: Prune Front Door routes for decommissioned services
  P1-4: Migrate newKeyValue() to newDecoratedText()

Week 4 (P2 -- config consistency):
  P2-1: Resolve DNS authority conflict
  P2-2: Remove deprecated MCP servers from .mcp.json
  P2-3: Consolidate Wix MCP transport
  P2-4: Align Supabase deprecation in all docs

Week 5+ (P3 -- hardening, optional):
  P3-1: Mandatory nonce in Gmail add-on (depends on P1-2)
  P3-2: Unify .ts/.gs source files
  P3-3: Credential auto-rotation policy
  P3-4: Superset Entra SSO
  P3-5: Foundry agent auth pipeline
```

---

## Cross-References

| Item | Finding | Target State Section |
|------|---------|---------------------|
| P0-1 | C-3 (hardcoded prod creds) | target-state.md SS4 (Key Vault sole secret store) |
| P0-2 | H-1 (admin CLI rotation) | target-state.md SS3 (platform admin CLI) |
| P1-1 | C-2 (Entra module missing) | target-state.md SS2 (Entra OIDC primary) |
| P1-2 | C-1 (backend endpoints missing) | target-state.md SS1 (mailbox host auth) |
| P1-3 | H-3 (dead Front Door routes) | target-state.md SS4 (backend-to-backend, Front Door) |
| P1-4 | H-2 (deprecated CardService API) | N/A (Marketplace compliance) |
| P2-1 | H-4 (DNS conflict) | N/A (documentation governance) |
| P2-2 | M-1 (deprecated MCP servers) | target-state.md SS6 (editor control surfaces) |
