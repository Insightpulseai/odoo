# odoo-security-posture

Validates security baseline on Azure — managed identity, Key Vault policies, WAF rules, GHAS alerts, TLS certificates, and access control.

## When to use
- Pre-deployment security readiness check
- Periodic security posture audit
- New service provisioned requiring security validation
- Access control change review

## Key rule
Managed identity is mandatory. Key Vault access via identity only. WAF rules must be active. Never expose secrets in assessment output.

## Cross-references
- `agents/knowledge/benchmarks/odoo-sh-persona-model.md`
- `agents/personas/odoo-platform-admin.md`
- `.claude/rules/security-baseline.md`
- `.claude/rules/infrastructure.md`
