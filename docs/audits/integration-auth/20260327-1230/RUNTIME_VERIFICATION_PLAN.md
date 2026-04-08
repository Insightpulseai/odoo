# Runtime Verification Plan

**Parent audit**: `docs/audits/integration-auth/20260327-1230/`
**Phase**: Runtime verification (post repo-authoritative audit)
**Prerequisite**: Azure CLI authenticated, Odoo DB access, vendor/odoo checkout

---

## Purpose

The repo-based audit is complete. These items cannot be closed from static analysis
and require live runtime access. Each item has an exact verification command,
pass/fail criteria, and owner.

---

## RV-01: Azure Managed Identity runtime state

**Gap IDs**: DG-01
**Owner**: Infrastructure
**Risk**: HIGH — IaC may declare MI but runtime may not have it attached

**Verification commands**:
```bash
# Verify system-assigned or user-assigned MI on each ACA app
az containerapp identity show \
  --name ipai-odoo-dev-web \
  --resource-group rg-ipai-dev-odoo-runtime \
  -o json

# Repeat for: ipai-odoo-dev-worker, ipai-odoo-dev-cron, ipai-copilot-gateway
```

**Pass criteria**:
- `type` includes `SystemAssigned` or `UserAssigned`
- `principalId` is non-null
- Identity has Key Vault Secrets User role on `kv-ipai-dev`

**Fail criteria**:
- `type: None` or identity block missing
- No Key Vault role assignment for the principal

**Evidence to capture**: JSON output of `identity show` for each app

---

## RV-02: Azure Key Vault expected-vs-actual secret inventory

**Gap IDs**: DG-02, DG-07
**Owner**: Infrastructure / Security
**Risk**: HIGH — missing secrets cause silent runtime failures

**Expected secrets** (from repo grep):
| Secret name | Referenced by | Purpose |
|-------------|---------------|---------|
| `zoho-smtp-user` | `ssot-platform.md`, `mail.yaml` | Zoho SMTP username |
| `zoho-smtp-password` | `ssot-platform.md`, `mail.yaml` | Zoho SMTP password |
| `pg-odoo-user` | `aca-odoo-services.bicep` | PostgreSQL username |
| `pg-odoo-password` | `aca-odoo-services.bicep` | PostgreSQL password |
| `entra-odoo-login-client-id` | `oidc_clients.yaml` | Entra app client ID |
| `entra-odoo-login-client-secret` | `oidc_clients.yaml` | Entra app client secret |
| `google-oauth-w9studio-client-id` | `oidc_clients.yaml` | Google OAuth client ID |
| `google-oauth-w9studio-client-secret` | `oidc_clients.yaml` | Google OAuth client secret |
| `odoo-admin-password` | `odoo.conf` (admin_passwd) | Odoo master password |
| `foundry-api-key` | `res_config_settings.py` | AI Foundry access |
| `docai-api-key` | `res_config_settings.py` | Document Intelligence |
| `slack-bot-token` | n8n workflows (archived) | Slack bot token |

**Verification command**:
```bash
az keyvault secret list --vault-name kv-ipai-dev -o table
```

**Pass criteria**:
- All expected secrets exist
- No unexpected secrets that suggest credential sprawl
- Secret versions are not expired

**Fail criteria**:
- Any expected secret missing
- Secrets with `enabled: false` or past expiry

**Evidence to capture**: Table output (names only, never values)

---

## RV-03: Live Odoo auth.oauth.provider records

**Gap IDs**: DG-03
**Owner**: Odoo backend
**Risk**: HIGH — determines whether OAuth buttons actually appear on /web/login

**Verification command**:
```sql
-- Run against the `odoo` database on pg-ipai-odoo
SELECT id, name, client_id, enabled, auth_endpoint, validation_endpoint,
       scope, body, flow, token_endpoint
FROM auth_oauth_provider
ORDER BY id;
```

**Pass criteria**:
- Google provider exists with correct `client_id` and `enabled=true`
- Microsoft/Entra provider exists (or is known-absent pending `ipai_auth_oidc`)
- No stale/orphaned provider records

**Fail criteria**:
- No provider records at all (OAuth buttons won't render)
- Provider with wrong redirect URI or endpoint
- DB-drift: provider config doesn't match repo intent

**Evidence to capture**: Query output (redact client secrets if present)

---

## RV-04: Odoo session/cookie security behind Front Door

**Gap IDs**: DG-04
**Owner**: Odoo backend / Infrastructure
**Risk**: MEDIUM — incorrect cookie flags enable session hijacking

**Verification commands**:
```bash
# Check response headers from the live ERP
curl -sI https://erp.insightpulseai.com/web/login | grep -iE 'set-cookie|strict-transport|x-frame|x-content-type'

# Check specific cookie attributes
curl -s -c - https://erp.insightpulseai.com/web/login | grep session_id
```

**Pass criteria**:
- `session_id` cookie has `Secure` flag
- `session_id` cookie has `HttpOnly` flag
- `SameSite=Lax` or `SameSite=Strict`
- `Strict-Transport-Security` header present
- `X-Frame-Options: SAMEORIGIN` or CSP frame-ancestors

**Fail criteria**:
- Missing `Secure` flag (session sent over HTTP)
- Missing `HttpOnly` (JS can read session cookie)
- `SameSite=None` without `Secure` (CSRF risk)

**Evidence to capture**: Full response header dump

---

## RV-05: Vendor Odoo auth_oauth source validation

**Gap IDs**: RG-01
**Owner**: Odoo backend
**Risk**: MEDIUM — implicit flow vulnerability (issue #63965)

**Verification steps**:
```bash
# Ensure vendor checkout is hydrated
ls vendor/odoo/addons/auth_oauth/controllers/main.py

# Read the signin handler
grep -n 'def signin\|state\|access_token\|validation' \
  vendor/odoo/addons/auth_oauth/controllers/main.py
```

**Pass criteria**:
- `state` parameter is validated (CSRF check)
- Token is validated against provider's userinfo endpoint
- User matching uses `oauth_uid` + `oauth_provider_id`
- Implicit flow vulnerability is documented as known/accepted risk

**Fail criteria**:
- No state validation (CSRF vulnerable)
- Token accepted without server-side validation

**Evidence to capture**: Relevant function signatures and state handling code

---

## Execution protocol

1. Run RV-01 through RV-05 sequentially
2. Capture evidence as text files under `docs/audits/integration-auth/20260327-1230/evidence/`
3. For each RV item, update `GAP_REGISTER.md` status to CLOSED or ACCEPTED_RISK
4. When all RV items are resolved, update `SUMMARY.md` status to:
   - `COMPLETE` if all pass
   - `COMPLETE WITH ACCEPTED RISKS` if some are explicitly accepted
5. Final attestation requires all 5 RV items resolved

---

## Attestation condition

The audit may be marked **COMPLETE** when:
- All RV-01 through RV-05 have pass/fail evidence
- Any failures have a remediation ticket or explicit risk acceptance
- `SUMMARY.md` status is updated with justification
- `GAP_REGISTER.md` has no remaining HIGH or CRITICAL open items
