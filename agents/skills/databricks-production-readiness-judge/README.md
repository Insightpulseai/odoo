# databricks-production-readiness-judge

Meta-skill that classifies whether a Databricks surface is actually production-grade based on release maturity, deployment evidence, observability, and rollback capability.

## When to use
- Any production-readiness skill output requires final judgment
- New Databricks feature adoption proposal
- Quarterly maturity review

## Key rule
Databricks "production ready" is a benchmark for production discipline, not a blanket trust label.
This judge determines the final classification: production-ready (GA-grade), preview-acceptable (Public Preview with stable interface/SLA/support), or not-production-grade (Beta/Private Preview/Experimental).

## Cross-references
- `agents/skills/databricks-pipeline-production-readiness/`
- `agents/skills/databricks-app-production-readiness/`
- `agents/skills/databricks-agent-production-readiness/`
- `agents/skills/databricks-model-serving-production-readiness/`
- `agents/knowledge/benchmarks/databricks-production-ready.md`
- `docs/architecture/data/ENTERPRISE_DATA_PLATFORM.md`
- `agent-platform/ssot/learning/databricks_production_ready_skill_map.yaml`
