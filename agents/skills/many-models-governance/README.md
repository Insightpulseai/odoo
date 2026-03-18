# many-models-governance

Designs multi-model portfolio governance covering model splitting strategies, inventory management, cost control, routing architecture, and retirement criteria.

## When to use
- Multiple ML models serving different domains or segments
- Model portfolio governance review
- Multi-tenant model architecture design
- Model sprawl or cost control concerns

## Key rule
Default to fewer, well-governed models. Model splitting must be justified by measurable performance gains or isolation requirements -- not convenience. Every production model requires registry entry, cost attribution, and retirement criteria.

## Source
"Use the many-models architecture approach" -- Microsoft Learn architecture card.

## Cross-references
- `agents/knowledge/benchmarks/azure-databricks-architecture-cards.md` (Card 2)
- `agent-platform/ssot/learning/databricks_architecture_card_map.yaml`
- `agents/skills/databricks-model-serving-production-readiness/`
- `agents/skills/databricks-agent-production-readiness/`
