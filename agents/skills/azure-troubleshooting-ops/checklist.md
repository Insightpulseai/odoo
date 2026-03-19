# Checklist — azure-troubleshooting-ops

- [ ] Symptoms documented (HTTP status, error message, alert details)
- [ ] Timeline established (start time, recent deployments, config changes)
- [ ] Container logs reviewed (last 100 lines, crash loops, OOM kills)
- [ ] DNS resolution verified for service FQDN and custom domain
- [ ] Key Vault RBAC validated (managed identity has Secret Get/List)
- [ ] TLS certificate chain inspected (expiry, binding, intermediates)
- [ ] Network security rules reviewed (NSG, ACA ingress, CORS)
- [ ] Dependent services health checked (PostgreSQL, Redis, Key Vault)
- [ ] Application Insights exceptions correlated with incident timeline
- [ ] Root cause identified or escalation triggered (after 3 checks)
- [ ] No secrets exposed in diagnostic output
- [ ] Evidence saved to `docs/evidence/{stamp}/azure-ops/troubleshooting/`
