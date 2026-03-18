# foundry-model-benchmark-judge

Judge skill that validates model selection against leaderboard evidence, safety requirements, and cost constraints.

## When to use
- Reviewing model selection output before promotion
- Pre-promotion gate for model readiness
- Quarterly model review and re-evaluation

## Key rule
All four leaderboard dimensions (quality, safety, cost, throughput) must be covered in the selection.
Safety dimension cannot be skipped. Cost must be within budget. Selection must be workload-specific.
Elevated thresholds apply (accuracy 0.98, safety 0.99, policy 0.99).

## Cross-references
- `agents/knowledge/benchmarks/microsoft-foundry-models-and-tools.md`
- `agents/personas/foundry-model-governor.md`
- `agents/skills/foundry-model-selection/skill-contract.yaml`
