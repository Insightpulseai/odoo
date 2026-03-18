# azure-load-testing-cli-patterns

Configure and execute Azure Load Testing via CLI for performance baselines and CI/CD gates.

## Owner

azure-cli-admin

## When to use

- Performance baseline needed before production deployment
- CI/CD pipeline needs load testing gate
- Capacity planning exercise
- Regression testing for performance-sensitive changes

## Key principle

Load test safely — bounded duration, bounded users, never production without approval. Results are evidence for performance decisions.

## Related skills

- azure-cli-resource-operations (general CLI operations)
- aca-app-deployment-patterns (target services on ACA)
