# sample-to-contract-extraction

Extract reusable patterns from Azure sample catalog into platform contracts.

## Owner

sample-fixture-curator

## When to use

- New Azure sample identified as relevant to platform
- Need a standardized pattern for a workload type
- Reviewing sample-derived patterns for security posture

## Key principle

Samples are fixtures not architecture. Extract the pattern, verify security, abstract away language specifics, produce a contract.

## Related skills

- azd-template-selection (samples often become azd templates)
- azd-secure-default-deployment (security verification)
- entra-auth-app-patterns (auth pattern extraction)
