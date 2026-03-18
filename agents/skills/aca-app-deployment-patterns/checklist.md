# Checklist — aca-app-deployment-patterns

## Environment

- [ ] ACA environment exists and is healthy
- [ ] VNet integration configured on environment
- [ ] Log Analytics workspace connected

## Container configuration

- [ ] Container image built and pushed to ACR
- [ ] ACR pull configured via managed identity (not admin)
- [ ] Environment variables set (no plaintext secrets)
- [ ] Key Vault references used for secrets
- [ ] Resource limits (CPU, memory) defined

## Scaling

- [ ] Min replicas set (>= 1 for production)
- [ ] Max replicas set with cost ceiling
- [ ] Scaling rules defined (HTTP, CPU, custom)
- [ ] Cold start impact assessed

## Ingress

- [ ] Ingress type selected (external/internal)
- [ ] Target port configured correctly
- [ ] TLS enabled for external ingress
- [ ] CORS configured if needed

## Health probes

- [ ] Liveness probe configured
- [ ] Readiness probe configured
- [ ] Startup probe configured (with sufficient failure threshold)
- [ ] Probe paths return correct status codes

## Front Door (external services only)

- [ ] Origin group configured in Front Door
- [ ] Health probe path set in Front Door
- [ ] Custom domain bound with TLS
- [ ] WAF rules applied
