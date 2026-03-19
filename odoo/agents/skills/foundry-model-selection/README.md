# foundry-model-selection

Shortlists models for a concrete workload using Foundry leaderboard dimensions and scenario-specific requirements.

## When to use
- New agent design requires model selection
- Reviewing model assignment for an existing agent
- Workload change affects model requirements
- Cost optimization requires model re-evaluation

## Key rule
Every model selection must be workload-specific. No "best model everywhere" recommendations.
All four leaderboard dimensions (quality, safety, cost, throughput) must be evaluated.
Rejected models must have documented reasons.

## Cross-references
- `agents/knowledge/benchmarks/microsoft-foundry-models-and-tools.md`
- `agents/personas/foundry-model-governor.md`
