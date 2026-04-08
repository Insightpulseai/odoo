# databricks-pipeline-production-readiness

Assesses whether a Databricks data pipeline meets production-readiness criteria for ingestion discipline, orchestration, observability, and rollback.

## When to use
- New pipeline deployment to production
- Pipeline promotion from dev/staging to production
- Quarterly pipeline readiness review

## Key rule
Databricks "production ready" is a benchmark for production discipline, not a blanket trust label.
A pipeline is production-grade only when: release maturity is GA or stable Public Preview, deployment is codified, observability exists, and rollback is defined.

## Cross-references
- `agents/knowledge/benchmarks/databricks-production-ready.md`
- `docs/architecture/data/ENTERPRISE_DATA_PLATFORM.md`
- `agent-platform/ssot/learning/databricks_production_ready_skill_map.yaml`
