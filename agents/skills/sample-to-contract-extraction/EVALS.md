# Evals — sample-to-contract-extraction

## Evaluation criteria

| Criterion | Weight | Pass condition |
|-----------|--------|----------------|
| Pattern correctly identified | 25% | Core architecture pattern extracted |
| Security audit complete | 20% | MI, VNet, keyless, private endpoints assessed |
| Language abstraction | 15% | Pattern described without language dependency |
| Platform alignment | 15% | Deviations and adaptations documented |
| Contract completeness | 15% | All sections populated, provenance recorded |
| Index registration | 10% | Contract registered in platform index |

## Test scenarios

1. **Secure sample** — all defaults met, straightforward extraction
2. **Insecure sample** — missing MI or uses API keys, should flag gaps
3. **Multi-language sample** — should abstract across implementations
4. **Platform-incompatible sample** — should identify deviations clearly
5. **Wholesale adoption attempt** — should reject and require pattern extraction
