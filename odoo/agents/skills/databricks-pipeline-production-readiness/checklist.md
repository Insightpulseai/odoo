# Checklist — databricks-pipeline-production-readiness

- [ ] Pipeline type classified (batch, streaming, CDC, hybrid)
- [ ] Pipeline defined as code (SDP/DLT YAML, SQL, or Jobs workflow) — not ad-hoc notebook
- [ ] Data quality expectations defined (constraints, expectations, schema enforcement)
- [ ] Orchestration uses Jobs/Workflows with scheduling and dependencies
- [ ] Retry policy and error handling configured
- [ ] Observability configured: event log, metrics, alerting
- [ ] SLA defined with measurable thresholds (latency, freshness, completeness)
- [ ] Environment separation verified (dev/staging/prod workspaces or catalogs)
- [ ] Rollback path documented (checkpoints, versioned tables, restore procedure)
- [ ] No Beta/Private Preview/Experimental features treated as production baseline
- [ ] Evidence collected and saved to docs/evidence/{stamp}/databricks/pipeline-readiness/
