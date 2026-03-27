# databricks-agent-production-readiness

Assesses whether a Databricks agent meets production-readiness criteria for agent structure, evaluation coverage, monitoring/tracing, safety guardrails, and user trust validation.

## When to use
- New agent deployment to production
- Agent promotion from dev/staging to production
- Agent evaluation review

## Key rule
Databricks "production ready" is a benchmark for production discipline, not a blanket trust label.
An agent is production-grade only when: release maturity is GA or stable Public Preview, eval suite exists with measurable thresholds, tracing is enabled, and safety guardrails are configured.

## Cross-references
- `agents/knowledge/benchmarks/databricks-production-ready.md`
- `docs/architecture/data/ENTERPRISE_DATA_PLATFORM.md`
- `agent-platform/ssot/learning/databricks_production_ready_skill_map.yaml`
