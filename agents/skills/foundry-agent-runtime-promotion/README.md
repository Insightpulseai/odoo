# foundry-agent-runtime-promotion

Moves a builder configuration into governed runtime — model + tools + auth + eval + promote with evidence.

## When to use
- Agent is ready for production promotion
- Runtime promotion request from a team
- Release gate review before deployment

## Key rule
Promotion requires evidence from both model governor and tool governor. Never promote without
eval results, a defined rollback path, and auth validation for every tool. Elevated thresholds
apply (accuracy 0.98, safety 0.99, policy 0.99).

## Cross-references
- `agents/knowledge/benchmarks/microsoft-foundry-models-and-tools.md`
- `agents/personas/foundry-runtime-builder.md`
- `agents/personas/foundry-eval-judge.md`
- `agents/skills/foundry-model-selection/skill-contract.yaml`
- `agents/skills/foundry-tool-catalog-curation/skill-contract.yaml`
