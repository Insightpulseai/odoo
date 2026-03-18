# Evals — databricks-agent-production-readiness

| Dimension | Pass criteria |
|-----------|--------------|
| Framework compliance | Correctly identifies Agent Framework vs ad-hoc LLM calls |
| Tool registry validation | Verifies tools are registered with scoped permissions |
| Eval coverage | Requires formal eval suite with measurable thresholds |
| Tracing verification | Confirms MLflow tracing enabled for all invocations |
| Deployment validation | Detects notebook-served vs Databricks App deployment |
| Safety review | Validates content filtering, tool boundaries, escalation path |
| Rollout capability | Confirms A/B or shadow deployment exists |
| Feedback loop | Verifies user feedback mechanism is implemented and stored |
| Release maturity gate | Rejects Beta/Private Preview/Experimental as production baseline |
| Guardrail compliance | Respects all guardrails — no false production-ready claims |
| Output completeness | All required fields present in assessment output |
| Evidence quality | Cites specific eval results and tracing config, not generic assertions |
