# Checklist — databricks-app-production-readiness

- [ ] App packaged as Databricks App bundle (not standalone notebook or script)
- [ ] Serverless compute allocation and scaling configured (min/max, timeout)
- [ ] Environment separation verified (dev/staging/prod workspaces or targets)
- [ ] Authentication integrated (SSO/OAuth) — no hardcoded credentials
- [ ] Data access scope follows least privilege (minimal catalog/schema/table access)
- [ ] Deployment path codified (CI/CD pipeline, CLI bundle deploy)
- [ ] Health checks configured (liveness/readiness probes, error monitoring)
- [ ] Rollback capability confirmed (version pinning, previous deployment restore)
- [ ] No Beta/Private Preview/Experimental features treated as production baseline
- [ ] Security review completed (auth, secrets, network isolation)
- [ ] Evidence collected and saved to docs/evidence/{stamp}/databricks/app-readiness/
