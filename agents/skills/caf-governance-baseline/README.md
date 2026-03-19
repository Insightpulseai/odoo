# caf-governance-baseline

Establishes and enforces cloud governance baselines using CAF Govern phase methodology, covering Azure Policy, cost management, resource consistency, identity baseline, and governance maturity model.

## When to use
- Governance baseline establishment for new environment
- Azure Policy audit or new policy assignment
- Cost management review or budget alert triggered
- Resource naming or tagging inconsistency detected
- Governance maturity assessment requested

## Key rule
Governance policies should be deployed as audit-first, then deny. Policies must not block existing production workloads without a documented migration path. Cost optimization must align with the self-hosted, cost-minimized philosophy.

## CAF Phase
Govern

## Cross-references
- `agents/knowledge/benchmarks/microsoft-cloud-adoption-framework.md`
- `agents/personas/cloud-governance-operator.md`
- `agents/skills/azure-optimization-ops/`
- `agents/skills/caf-security-baseline/`
