# Evals — azd-vs-azure-cli-decision

## Evaluation criteria

| Criterion | Weight | Pass condition |
|-----------|--------|----------------|
| Correct verdict | 40% | AZD/AZURE_CLI/BOTH matches decision matrix |
| Reasoning quality | 20% | Clear, concise, references decision matrix |
| Anti-pattern detection | 20% | Correctly flags wrong tool proposals |
| Boundary clarity (BOTH) | 10% | Clear delineation when both tools used |
| Consistency | 10% | Same task always gets same verdict |

## Test scenarios

1. **App deployment** — should return AZD
2. **Log query** — should return AZURE_CLI
3. **Deploy + verify** — should return BOTH with boundaries
4. **Scaling change** — should return AZURE_CLI
5. **CI/CD setup** — should return AZD
6. **Resource inventory** — should return AZURE_CLI
7. **Template browsing** — should return AZD
8. **Certificate rotation** — should return AZURE_CLI
9. **Wrong tool proposed** — should flag anti-pattern with correction
