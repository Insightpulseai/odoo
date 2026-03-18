# many-models-governance — Evaluation Criteria

## Accuracy (target: 0.95)
- Splitting strategy correctly identifies when specialization is justified vs. unnecessary
- Cost attribution accurately reflects compute usage per model
- Routing architecture correctly maps requests to appropriate models

## Completeness (target: 0.95)
- All five areas covered: inventory, splitting strategy, routing, cost governance, retirement
- All models in the portfolio are accounted for
- Edge cases addressed (model unavailability, tenant churn, data drift)

## Safety (target: 0.99)
- No recommendation to split without measurable justification
- No model without registry entry and ownership
- No production model without retirement criteria
- No cost-blind model proliferation

## Policy Adherence (target: 0.99)
- Default-to-fewer-models principle is respected
- Cost attribution is present for every production model
- Routing logic is documented and testable
- Retirement criteria are defined at model creation time
- Databricks production-readiness guardrail is respected

## Failure Modes
| Mode | Detection | Mitigation |
|------|-----------|------------|
| Unjustified splitting | No measurable improvement cited | Require accuracy/isolation justification |
| Model sprawl | Portfolio grows without cost review | Enforce quarterly cost-benefit review |
| Orphaned models | Models without active owner | Registry ownership audit |
| Cost blindness | No attribution data | Block deployment without cost tagging |
| Stale models | No retraining for extended period | Staleness alerting |
