# Prompt — aca-app-deployment-patterns

You are deploying an application to Azure Container Apps on the InsightPulse AI platform.

Your job is to:
1. Verify the ACA environment is healthy
2. Configure container registry pull via managed identity
3. Define scaling rules appropriate for the workload
4. Configure ingress with TLS
5. Set up health probes (liveness, readiness, startup)
6. Deploy and verify accessibility

Platform context:
- ACA environment: `cae-ipai-dev` in `rg-ipai-dev`
- Container registries: `cripaidev`, `ipaiodoodevacr`
- Front Door: `ipai-fd-dev`
- Key Vault: `kv-ipai-dev`
- Existing apps: ipai-odoo-dev-web, ipai-odoo-dev-worker, ipai-odoo-dev-cron, ipai-auth-dev, ipai-mcp-dev, ipai-ocr-dev, ipai-superset-dev, ipai-plane-dev

Canonical Odoo ACA pattern:
- Web: external ingress on 8069, min 1 replica, HTTP scaling
- Worker: no ingress, min 1 replica, queue-based scaling
- Cron: no ingress, min 1 replica, schedule-based

Health probe pattern:
```yaml
probes:
  - type: liveness
    httpGet:
      path: /web/health
      port: 8069
    periodSeconds: 30
    failureThreshold: 3
  - type: readiness
    httpGet:
      path: /web/health
      port: 8069
    periodSeconds: 10
  - type: startup
    httpGet:
      path: /web/health
      port: 8069
    periodSeconds: 10
    failureThreshold: 30
```

Output format:
- Container App: name and FQDN
- Environment: verified (yes/no)
- Registry: pull via managed identity (yes/no)
- Scaling: min/max replicas, rules
- Ingress: type (external/internal), TLS (yes/no), port
- Health probes: liveness (pass/fail), readiness (pass/fail), startup (pass/fail)
- Front Door: origin configured (yes/no/not applicable)
