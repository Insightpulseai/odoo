# Integration & Authentication Audit -- Executive Summary

**Audit Date**: 2026-03-27 12:30 PHT
**Scope**: All integration surfaces and authentication flows across the InsightPulseAI platform
**Auditor**: Claude Opus 4.6 (automated codebase audit)

---

## Integration Posture

The platform operates 21 distinct integration surfaces spanning Gmail add-on, Odoo ERP (Azure Container Apps behind Front Door), PostgreSQL, Zoho SMTP, Azure Key Vault, Microsoft Entra ID (planned), Google Workspace OAuth, MCP servers, Databricks, Fabric mirroring, Wix CMS, developer toolchain (GitHub, Azure DevOps, clasp), and developer-environment control surfaces (VS Code with Azure ML workspace `proj-ipai-claude`, Docker Desktop runtime, extension-bound credentials). The integration architecture is well-documented in SSOT YAML files with clear deprecation trails. However, the integration surface is wider than the operational identity layer can currently enforce: Entra ID is planned but not yet operational, leaving most services on basic/local auth. Several Front Door route definitions (n8n, Plane, Shelf, CRM, auth/Keycloak) reference decommissioned services and should be pruned to reduce attack surface.

## Auth Posture

Authentication is in a transitional state. The Gmail add-on has a well-designed provider-first flow (Microsoft Entra > Google OAuth > API key fallback) with proper nonce handling, but the backend endpoints it depends on (`/ipai/mail_plugin/provider_session`, `/ipai/mail_plugin/session`) do not yet exist -- the `ipai_auth_oidc` module is planned but not built. Odoo workforce auth currently relies on local password login; the Entra app registration (`ipai-odoo-login-prod`, client_id `07bd9669-...`) exists but the OIDC integration module has not been implemented. Google Workspace OAuth for W9 Studio is partially configured via `ipai_enterprise_bridge` but depends on DB-injected `auth.oauth.provider` records rather than repo-owned config. The platform admin CLI credential (`ipai-platform-admin-cli-prod`) is flagged as requiring immediate rotation. Keycloak was deployed but never operationalized and has been decommissioned. Supabase Auth is fully retired.

---

## Top 10 Risks

1. **CRITICAL -- Backend auth endpoints do not exist**: The Gmail add-on calls `/ipai/mail_plugin/session` and `/ipai/mail_plugin/provider_session` which have no corresponding Odoo controller. All add-on auth flows will fail at runtime.

2. **CRITICAL -- Entra OIDC module not built**: `ipai_auth_oidc` is referenced in OIDC SSOT and spec bundles but does not exist as a module. Workforce SSO via Microsoft Entra is non-functional.

3. **CRITICAL -- Hardcoded production database password in archive files**: `archive/root/scripts/prod_access_check.py` line 7 and `archive/root/scripts/prod_db_guess.py` line 6 contain a plaintext Base64-encoded password. Though in archive/, these files are tracked in git.

4. **HIGH -- Platform admin CLI credential requires rotation**: `ipai-platform-admin-cli-prod` is flagged `rotate_required` / `current_risk: expiring_soon` in `ssot/entra/app_registrations.azure_native.yaml`.

5. **HIGH -- CardService.newKeyValue() deprecated in Gmail add-on**: Used extensively in `auth.gs`, `homepage.gs`, and `context.gs`. Must migrate to `newDecoratedText()` before Marketplace submission. The `.gs` files use `.setContent()` while `.ts` sources partially use `.setText()`, creating a mismatch.

6. **HIGH -- Front Door routes reference decommissioned services**: `front-door-routes.yaml` defines origin groups and routes for n8n, Plane, Shelf, CRM, and auth (Keycloak) -- all decommissioned per `service-matrix.yaml`. These routes expose dormant endpoints.

7. **HIGH -- DNS authority conflict in CLAUDE.md files**: Parent `~/.claude/CLAUDE.md` says "DNS: Cloudflare", monorepo `CLAUDE.md` says "DNS: Azure DNS (authoritative, delegated from Squarespace)". These contradict each other.

8. **MEDIUM -- Supabase deprecation conflict**: Parent `~/.claude/CLAUDE.md` still references Supabase as active (`spdtwktxdalcfigzeqrz`), while monorepo `CLAUDE.md` declares all Supabase deprecated (2026-03-26). The `.mcp.json` still configures a Supabase MCP server.

9. **MEDIUM -- OAuth client secret stored in DB via Settings UI**: `ipai_enterprise_bridge` exposes `ipai_oauth_google_client_secret` as a `config_parameter` field. The secret is stored in `ir.config_parameter` (database), not in Azure Key Vault.

10. **MEDIUM -- Prod odoo.conf has plaintext db_password**: `config/prod/odoo.conf` line 17 sets `db_password = odoo`. The azure config correctly omits DB credentials, but the prod config file has a hardcoded value that may be used in non-ACA deployments.

---

## Top 10 Remediation Priorities

1. **Build `ipai_auth_oidc` module** with Entra OIDC provider, PKCE flow, RS256 validation, and JIT provisioning -- unblocks workforce SSO and Gmail add-on provider auth.

2. **Build `ipai_mail_plugin` controller** implementing `/ipai/mail_plugin/session`, `/ipai/mail_plugin/provider_session`, `/ipai/mail_plugin/context`, and action endpoints -- unblocks Gmail add-on.

3. **Rotate `ipai-platform-admin-cli-prod` credential** immediately and migrate to workload identity federation or certificate.

4. **Delete or purge hardcoded secrets** from `archive/root/scripts/prod_access_check.py` and `archive/root/scripts/prod_db_guess.py`.

5. **Prune Front Door routes** for decommissioned services (n8n, Plane, Shelf, CRM, auth).

6. **Migrate `newKeyValue()` to `newDecoratedText()`** across all Gmail add-on `.gs` files and resolve `.setContent()` vs `.setText()` mismatch between `.gs` and `.ts` sources.

7. **Resolve DNS authority conflict** in CLAUDE.md files -- establish single canonical statement.

8. **Move Google OAuth client_secret** from `ir.config_parameter` to Azure Key Vault with env-var injection.

9. **Remove Supabase MCP server** from `.mcp.json` and align all CLAUDE.md references.

10. **Remove `db_password = odoo`** from `config/prod/odoo.conf` -- ACA config correctly uses env vars; prod config should do the same.
