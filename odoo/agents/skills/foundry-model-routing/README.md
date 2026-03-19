# foundry-model-routing

Decides whether to pin one model or use model router for quality/cost/latency optimization.

## When to use
- Multi-model evaluation for a workload
- Cost optimization requires routing analysis
- Latency optimization requires routing analysis
- Quality trade-off analysis between pinned and routed configurations

## Key rule
Model router is a conditional optimization surface, not a default-on feature.
Pinned model is the default. Router requires workload variability evidence and a fallback strategy.

## Cross-references
- `agents/knowledge/benchmarks/microsoft-foundry-models-and-tools.md`
- `agents/personas/foundry-model-governor.md`
- `agents/skills/foundry-model-selection/skill-contract.yaml`
