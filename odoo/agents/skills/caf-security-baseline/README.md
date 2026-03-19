# caf-security-baseline

Secures Azure environment following CAF Secure phase methodology, covering zero trust architecture, Defender for Cloud, identity perimeter, network segmentation, data protection, and threat detection.

## When to use
- Security baseline establishment for new environment
- Security posture assessment or compliance audit
- New service deployment requiring security review
- Identity perimeter change (Keycloak to Entra migration)
- Security incident or vulnerability discovered

## Key rule
Security designs must account for the transitional Keycloak-to-Entra ID state. Never propose security controls requiring Enterprise SKU without documenting cost impact. All secrets must use Azure Key Vault with managed identity access.

## CAF Phase
Secure

## Cross-references
- `agents/knowledge/benchmarks/microsoft-cloud-adoption-framework.md`
- `agents/personas/cloud-security-architect.md`
- `agents/skills/azure-resiliency-ops/`
- `agents/skills/caf-governance-baseline/`
- `.claude/rules/security-baseline.md`
