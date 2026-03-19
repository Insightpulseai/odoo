# databricks-model-serving-production-readiness

Assesses whether a model serving deployment meets production-readiness criteria for model lifecycle, staging-to-production gates, endpoint scalability/security, and model governance.

## When to use
- Model promotion to production
- Serving endpoint creation
- Model governance review

## Key rule
Databricks "production ready" is a benchmark for production discipline, not a blanket trust label.
A model serving deployment is production-grade only when: release maturity is GA or stable Public Preview, staging validation passed, drift monitoring exists, and governance approval trail is complete.

## Cross-references
- `agents/knowledge/benchmarks/databricks-production-ready.md`
- `docs/architecture/enterprise_data_platform.md`
- `agent-platform/ssot/learning/databricks_production_ready_skill_map.yaml`
