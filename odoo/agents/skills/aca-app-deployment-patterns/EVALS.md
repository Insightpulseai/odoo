# Evals — aca-app-deployment-patterns

## Evaluation criteria

| Criterion | Weight | Pass condition |
|-----------|--------|----------------|
| Managed identity for ACR | 20% | No admin credentials |
| Health probes configured | 20% | Liveness + readiness + startup |
| Scaling rules defined | 15% | Min/max replicas, scaling rule type |
| Ingress TLS | 15% | TLS enabled for external services |
| VNet integration | 15% | Environment connected to VNet |
| Front Door routing | 15% | Origin configured for external services |

## Test scenarios

1. **Web service** — external ingress, TLS, health probes, HTTP scaling
2. **Worker service** — no ingress, min 1 replica, no external access
3. **Missing health probes** — should flag as incomplete deployment
4. **Zero min replicas in prod** — should warn about cold start impact
5. **Admin credentials for ACR** — should flag and require managed identity
