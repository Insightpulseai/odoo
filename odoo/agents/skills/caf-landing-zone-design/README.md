# caf-landing-zone-design

Designs Azure landing zone following CAF enterprise-scale architecture patterns, including management group hierarchy, subscription topology, identity baseline, network topology, and platform automation.

## When to use
- New Azure environment is being provisioned
- Subscription topology is being reviewed or restructured
- Network architecture redesign
- Platform automation foundation is being established
- Landing zone compliance audit

## Key rule
Every landing zone must have a defined management group hierarchy, subscription topology, identity baseline with RBAC, network topology with segmentation, and platform automation using IaC. Designs must align with existing `rg-ipai-*` conventions.

## CAF Phase
Ready

## Cross-references
- `agents/knowledge/benchmarks/microsoft-cloud-adoption-framework.md`
- `agents/personas/landing-zone-architect.md`
- `agents/skills/azure-deployment-ops/`
- `.claude/rules/infrastructure.md`
