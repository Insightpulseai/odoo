# Evals — databricks-app-production-readiness

| Dimension | Pass criteria |
|-----------|--------------|
| App packaging | Correctly identifies bundle vs notebook/ad-hoc serving |
| Compute validation | Verifies scaling configuration exists and is appropriate |
| Environment separation | Confirms dev/staging/prod isolation |
| Authentication review | Validates SSO/OAuth, detects hardcoded credentials |
| Least privilege | Verifies data access scope is minimal |
| Deployment discipline | Detects manual vs codified deployment |
| Health check evidence | Requires concrete proof of liveness/readiness probes |
| Rollback capability | Confirms version pinning or restore path |
| Release maturity gate | Rejects Beta/Private Preview/Experimental as production baseline |
| Guardrail compliance | Respects all guardrails — no false production-ready claims |
| Output completeness | All required fields present in assessment output |
| Evidence quality | Cites specific artifacts, not generic assertions |
