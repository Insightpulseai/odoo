# Evals — databricks-model-serving-production-readiness

| Dimension | Pass criteria |
|-----------|--------------|
| Unity Catalog registration | Verifies model is registered with lineage |
| Staging gate enforcement | Detects direct-to-prod vs staging-validated promotion |
| Endpoint configuration | Validates throughput/latency SLA and autoscaling rules |
| Traffic management | Confirms A/B serving or traffic splitting exists |
| Endpoint security | Validates auth, rate limiting, network isolation |
| Monitoring coverage | Requires latency, error rate, and drift monitoring evidence |
| Rollback capability | Confirms model version or endpoint rollback path |
| Governance compliance | Validates approval workflow, audit trail, compliance tags |
| Release maturity gate | Rejects Beta/Private Preview/Experimental as production baseline |
| Guardrail compliance | Respects all guardrails — no false production-ready claims |
| Output completeness | All required fields present in assessment output |
| Evidence quality | Cites specific validation results and config, not generic assertions |
