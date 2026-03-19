# Evals — azure-functions-azd-patterns

## Evaluation criteria

| Criterion | Weight | Pass condition |
|-----------|--------|----------------|
| Flex Consumption plan | 20% | Not Classic Consumption |
| Managed identity | 25% | All downstream access via MI |
| VNet integration | 15% | Configured when accessing private resources |
| Trigger correctness | 15% | Trigger type and config match workload |
| Deployment success | 15% | azd up completes, function executes |
| Cold start documented | 10% | Latency measured and recorded |

## Test scenarios

1. **Timer function** — CRON validated, Flex Consumption, MI for downstream
2. **HTTP function** — auth level set, response format correct
3. **Cosmos trigger** — change feed configured, MI for Cosmos access
4. **Missing VNet** — accessing private resource without VNet should be flagged
5. **Classic plan** — should be flagged and Flex Consumption recommended
