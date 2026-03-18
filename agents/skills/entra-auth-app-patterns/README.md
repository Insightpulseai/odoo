# entra-auth-app-patterns

Implement Microsoft Entra authentication in applications with keyless access patterns.

## Owner

entra-auth-integrator

## When to use

- New application needs authentication
- Migrating from Keycloak to Entra
- Implementing OpenAI + Entra keyless access
- Setting up service-to-service auth via managed identity

## Key principle

Keyless access via managed identity + Entra is the default. Keycloak is transitional. New integrations always target Entra directly.

## Related skills

- azd-secure-default-deployment (managed identity deployment)
- aca-app-deployment-patterns (ACA identity configuration)
- sample-to-contract-extraction (Entra auth sample patterns)
