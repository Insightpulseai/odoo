# Evals — azd-secure-default-deployment

## Evaluation criteria

| Criterion | Weight | Pass condition |
|-----------|--------|----------------|
| Managed identity enforced | 25% | All services use MI, no service principal secrets |
| VNet integration | 20% | VNet configured, data services on private endpoints |
| Keyless access | 20% | No embedded credentials in config |
| Successful deployment | 15% | azd up/deploy completes, health checks pass |
| Security posture report | 10% | Complete and accurate report generated |
| ACR pull via identity | 10% | No admin credentials for container pull |

## Test scenarios

1. **Clean secure deployment** — all secure defaults met, deployment succeeds
2. **Missing managed identity** — should flag and block deployment
3. **Public database endpoint** — should flag missing private endpoint
4. **Embedded connection string** — should detect and flag credential in config
5. **Failed health check** — should report deployment incomplete
