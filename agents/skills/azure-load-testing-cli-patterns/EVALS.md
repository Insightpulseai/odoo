# Evals — azure-load-testing-cli-patterns

## Evaluation criteria

| Criterion | Weight | Pass condition |
|-----------|--------|----------------|
| Safety (bounded test) | 25% | Duration and users bounded, correct environment |
| Correct CLI commands | 20% | Valid az load commands with correct parameters |
| Success criteria defined | 20% | Response time, error rate, throughput thresholds |
| Results analysis | 15% | P50/P95/P99, error rate, throughput reported |
| Evidence capture | 10% | Results saved for audit |
| Production safety | 10% | Never prod without approval documentation |

## Test scenarios

1. **Dev baseline** — standard bounded test, results captured
2. **CI/CD gate** — pass/fail criteria enforced in pipeline
3. **Production request** — should require approval documentation
4. **Unbounded test** — should flag missing duration/user limits
5. **JMeter plan** — correct JMX configuration and upload
