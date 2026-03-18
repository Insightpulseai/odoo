# Examples — odoo-security-posture

## Example 1: Clean security posture

**Input**: Pre-deployment security readiness check

**Output**:
- Managed identity:
  - `ipai-odoo-dev-web`: system-assigned enabled — PASS
  - `ipai-odoo-dev-worker`: system-assigned enabled — PASS
  - `ipai-odoo-dev-cron`: system-assigned enabled — PASS
- Key Vault: `kv-ipai-dev` access via RBAC (Key Vault Secrets User role) — PASS
- WAF: active, 14 managed rules, 0 bypassed — PASS
- GHAS: secret scanning 0, code scanning 0 critical/high, Dependabot 2 medium — PASS
- TLS: `erp.insightpulseai.com` valid until 2026-09-15 (181 days) — PASS
- Env vars: no plaintext secrets detected — PASS
- Blockers: none
- Evidence: `az containerapp identity show`, `az keyvault role assignment list`

## Example 2: Connection string violation detected

**Input**: Security audit finds `POSTGRES_CONNECTION_STRING` in Container App env vars

**Output**:
- Key Vault: POLICY VIOLATION — `ipai-odoo-dev-web` has `POSTGRES_CONNECTION_STRING` as plaintext env var
- Blockers: [database connection string must be moved to Key Vault and referenced via secretref]
- Recommendation: Create Key Vault secret, update Container App template to use `secretref`
- Evidence: `az containerapp show --name ipai-odoo-dev-web --query "properties.template.containers[0].env" | grep -i connection`

## Example 3: Expiring TLS certificate

**Input**: Periodic certificate review

**Output**:
- TLS: `auth.insightpulseai.com` certificate expires in 12 days — FAIL (BLOCKER)
- Blockers: [TLS certificate renewal required within 30-day window]
- Recommendation: Verify Azure Front Door managed certificate auto-renewal or manually renew
