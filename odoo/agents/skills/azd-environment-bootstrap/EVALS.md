# Evals — azd-environment-bootstrap

## Evaluation criteria

| Criterion | Weight | Pass condition |
|-----------|--------|----------------|
| Correct subscription targeting | 20% | Matches platform subscription |
| Region follows convention | 15% | southeastasia for compute, eastus for AI |
| Resource group naming | 15% | rg-ipai-{env} pattern |
| azure.yaml completeness | 20% | All services declared with correct hosts |
| No plaintext secrets | 15% | Environment variables contain no secret values |
| CI/CD federated credentials | 15% | Pipeline uses OIDC, not stored secrets |

## Test scenarios

1. **Single environment** — dev only, verify all conventions applied
2. **Multi-environment** — dev + staging + prod, verify isolation
3. **Secret leak detection** — attempt to set secret value, should be flagged
4. **CI/CD pipeline** — verify GitHub Actions workflow with federated credentials
5. **Invalid region** — non-platform region should be flagged
