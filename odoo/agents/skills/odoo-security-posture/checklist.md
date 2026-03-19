# Checklist — odoo-security-posture

- [ ] Managed identity enabled on all Container Apps
- [ ] Key Vault access uses managed identity (no connection strings)
- [ ] Key Vault RBAC roles are least-privilege
- [ ] Azure Front Door WAF rules active and not bypassed
- [ ] Container registry pull uses managed identity (no admin credentials)
- [ ] GHAS secret scanning: no active alerts
- [ ] GHAS code scanning: no critical/high findings
- [ ] Dependabot: no critical vulnerability alerts
- [ ] TLS certificates valid and not expiring within 30 days
- [ ] No plaintext secrets in container environment variables
- [ ] Odoo user roles follow least-privilege principle
- [ ] No shared admin accounts
- [ ] No secrets exposed in assessment output
- [ ] Evidence captured in `docs/evidence/{stamp}/odoo-delivery/odoo-security-posture/`
