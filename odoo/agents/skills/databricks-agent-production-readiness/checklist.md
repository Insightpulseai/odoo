# Checklist — databricks-agent-production-readiness

- [ ] Agent follows Databricks Agent Framework template (not ad-hoc LLM calls)
- [ ] Tool definitions registered in tool registry with scoped permissions
- [ ] Evaluation suite exists with measurable thresholds (accuracy, latency, safety)
- [ ] Monitoring/tracing enabled (MLflow traces, latency metrics, error rates)
- [ ] Agent deployed on Databricks Apps (not notebook-served)
- [ ] Safety guardrails configured (content filtering, tool boundaries, escalation path)
- [ ] A/B or shadow deployment capability exists for rollout
- [ ] User feedback loop implemented (thumbs up/down, corrections, stored feedback)
- [ ] No Beta/Private Preview/Experimental features treated as production baseline
- [ ] Environment separation verified (dev/staging/prod)
- [ ] Rollback path defined (previous agent version, endpoint rollback)
- [ ] Evidence collected and saved to docs/evidence/{stamp}/databricks/agent-readiness/
