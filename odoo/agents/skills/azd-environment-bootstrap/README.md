# azd-environment-bootstrap

Initialize azd environment with correct subscription, region, and resource group targeting.

## Owner

azure-bootstrap-engineer

## When to use

- New project needs azd initialization
- New environment (dev/staging/prod) needs creation
- CI/CD pipeline needs setup for azd-managed project

## Key principle

azd environments map to platform environments (dev, staging, prod). Environment variables configure but never contain secrets in plaintext.

## Related skills

- azd-template-selection (prerequisite — template must be selected first)
- azd-secure-default-deployment (next step — deploy after bootstrap)
