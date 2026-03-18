# Checklist — azure-observability-ops

- [ ] Application Insights resource exists and is connected to the service
- [ ] Instrumentation key or connection string injected via Key Vault (not hardcoded)
- [ ] Log Analytics workspace exists and has received data in last 24 hours
- [ ] Log retention meets minimum policy (30 days)
- [ ] Alert rule for HTTP 5xx error rate exists and is enabled
- [ ] Alert rule for P95 latency threshold exists and is enabled
- [ ] Alert rule for container restart count exists and is enabled
- [ ] Action groups configured with correct notification targets (email, Slack webhook)
- [ ] KQL queries from catalog validated against workspace (no execution errors)
- [ ] Resource Graph queries return expected service inventory
- [ ] Custom availability tests configured for public endpoints (if applicable)
- [ ] Evidence saved to `docs/evidence/{stamp}/azure-ops/observability/`
