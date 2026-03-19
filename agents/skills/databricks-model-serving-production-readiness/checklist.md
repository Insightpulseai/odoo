# Checklist — databricks-model-serving-production-readiness

- [ ] Model registered in Unity Catalog with full lineage (data, code, parameters)
- [ ] Staging-to-production promotion gate exists (not direct-to-prod)
- [ ] Staging validation results documented and passing
- [ ] Serving endpoint configured with throughput and latency SLA targets
- [ ] Autoscaling rules defined (min/max instances, scale-up/down thresholds)
- [ ] A/B serving or traffic splitting capability confirmed
- [ ] Endpoint security configured (authentication, rate limiting, network isolation)
- [ ] Monitoring configured (inference latency, error rate, data drift detection)
- [ ] Rollback path defined (previous model version, endpoint version restore)
- [ ] Model governance complete (approval workflow, audit trail, compliance tags)
- [ ] No Beta/Private Preview/Experimental features treated as production baseline
- [ ] Evidence collected and saved to docs/evidence/{stamp}/databricks/model-serving-readiness/
