# Checklist — odoo-staging-to-production-promotion

- [ ] Tester evidence exists with no real_defect blockers
- [ ] Platform admin confirms database backup taken before deployment
- [ ] Monitoring and alerting verified active (Azure Monitor, Application Insights)
- [ ] Rollback plan documented (previous revision ID + DB backup timestamp)
- [ ] No active incidents at time of deployment
- [ ] Production Container App revision updated
- [ ] Production health check passes (200 response)
- [ ] Production database migration completes successfully
- [ ] Bake-time observation period started (minimum 30 minutes)
- [ ] Error rate within threshold during bake-time
- [ ] Response time within threshold during bake-time
- [ ] No container restarts or OOM kills during bake-time
- [ ] Release classified as healthy only after bake-time evidence
- [ ] Evidence captured in `docs/evidence/{stamp}/odoo-delivery/odoo-staging-to-production-promotion/`
