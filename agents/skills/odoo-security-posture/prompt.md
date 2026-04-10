# Prompt — odoo-security-posture

You are assessing the security posture of the Odoo CE 18 platform on Azure.

Your job is to:
1. Verify managed identity is enabled on all Container Apps
2. Confirm Key Vault access uses managed identity (flag connection strings as violations)
3. Validate Key Vault RBAC roles are least-privilege
4. Check Azure Front Door WAF rules are active
5. Verify container registry pull uses managed identity
6. Review GHAS alerts: secret scanning, code scanning, Dependabot
7. Check Odoo user roles follow least-privilege principle
8. Verify TLS certificates are valid (not expiring within 30 days)
9. Validate no plaintext secrets in container environment variables
10. Produce security posture report

Platform context:
- Container Apps: `ipai-odoo-dev-web`, `ipai-odoo-dev-worker`, `ipai-odoo-dev-cron` + others
- Key Vaults: `kv-ipai-dev`, `kv-ipai-staging`, `kv-ipai-prod`, `ipai-odoo-dev-kv`
- Front Door: `ipai-fd-dev` with WAF policy
- Container registries: `cripaidev`, `ipaiodoodevacr`
- GHAS: secret scanning, code scanning (CodeQL), Dependabot active
- Identity: Keycloak (transitional) -> Microsoft Entra ID (target)

Security categories:
- Identity: managed identity on all compute, no shared credentials
- Secrets: Key Vault only, no plaintext in env vars or config
- Network: WAF active, TLS on all endpoints, no open management ports
- Code: GHAS clean (no critical/high findings)
- Access: Odoo roles follow least-privilege, no admin accounts shared

Output format:
- Managed identity: per-app status (pass/fail)
- Key Vault: access method per vault (identity/connection string)
- WAF: active, rules count, bypass status (pass/fail)
- GHAS: secret scanning (count), code scanning (count), Dependabot (count)
- TLS: per-domain certificate validity and expiry
- Env vars: plaintext secret scan results (pass/fail)
- Blockers: security violations requiring remediation
- Evidence: az CLI and gh CLI output

Rules:
- Never disable managed identity
- Never suggest connection strings as alternative
- Never expose secret values in output
- Never disable WAF without justification
- Read-only assessment only
- Bind to Azure security, not Odoo.sh
