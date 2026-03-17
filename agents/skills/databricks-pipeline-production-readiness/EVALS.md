# Evals — databricks-pipeline-production-readiness

| Dimension | Pass criteria |
|-----------|--------------|
| Pipeline classification | Correctly identifies pipeline type (batch/streaming/CDC/hybrid) |
| Code-defined verification | Detects ad-hoc notebook execution vs codified pipeline definition |
| Data quality check | Verifies expectations/constraints are defined, not assumed |
| Orchestration validation | Confirms Jobs/Workflows with scheduling, not manual triggers |
| Observability evidence | Requires concrete proof of event log, metrics, and alerting |
| SLA enforcement | Never approves pipeline without defined SLA |
| Environment separation | Verifies dev/staging/prod isolation exists |
| Rollback capability | Confirms checkpoint or versioned table rollback path |
| Release maturity gate | Rejects Beta/Private Preview/Experimental as production baseline |
| Guardrail compliance | Respects all guardrails — no false production-ready claims |
| Output completeness | All required fields present in assessment output |
| Evidence quality | Cites specific artifacts, not generic assertions |
