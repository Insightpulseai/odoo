# Checklist — odoo-log-triage

- [ ] Log Analytics query covers specified time range
- [ ] Logs filtered by severity (ERROR, WARNING, CRITICAL)
- [ ] Each error classified by category (ORM, HTTP, module, database, timeout, memory, security)
- [ ] Recurring patterns identified with frequency counts
- [ ] Errors correlated with deployment events (revision changes)
- [ ] Secrets/credentials redacted from log output
- [ ] Root cause assessment provided for each error class
- [ ] No errors dismissed without classification
- [ ] Evidence captured in `docs/evidence/{stamp}/odoo-delivery/odoo-log-triage/`
