# Evals — azd-template-selection

## Evaluation criteria

| Criterion | Weight | Pass condition |
|-----------|--------|----------------|
| Correct workload categorization | 20% | Matches input workload type |
| Template exists and is accessible | 15% | Valid azd gallery entry |
| Secure-by-default assessment | 25% | Accurately identifies MI, VNet, keyless |
| Language/runtime compatibility | 15% | Matches or clearly flags mismatch |
| Platform alignment | 15% | Flags incompatibilities with canonical stack |
| Customization list completeness | 10% | All required changes identified |

## Test scenarios

1. **Simple ACA web app** — should select ACA-native template, flag secure defaults
2. **Functions workload** — should select Functions template, verify Flex Consumption
3. **Full-stack with auth** — should identify auth gap if template lacks Entra
4. **Incompatible runtime** — should flag when no matching template exists
5. **Stale template** — should warn about templates not updated in 12+ months
