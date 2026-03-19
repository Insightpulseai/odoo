# Checklist — odoo-dev-to-staging-promotion

- [ ] All required CI checks pass on source branch
- [ ] Developer CI validation evidence exists and is cited
- [ ] No open blockers from developer or tester personas
- [ ] Staging branch created/updated from source (no force-push)
- [ ] Container image tagged for staging promotion
- [ ] Staging Container App revision updated
- [ ] Staging health check passes
- [ ] Staging database migration completes successfully
- [ ] Rollback path documented (previous revision ID + DB backup timestamp)
- [ ] Evidence captured in `docs/evidence/{stamp}/odoo-delivery/odoo-dev-to-staging-promotion/`
