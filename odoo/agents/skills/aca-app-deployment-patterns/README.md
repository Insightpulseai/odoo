# aca-app-deployment-patterns

Deploy apps to Azure Container Apps using azd patterns with secure defaults.

## Owner

app-hosting-engineer

## When to use

- Deploying a new containerized application to ACA
- Updating scaling rules, ingress, or health probes
- Setting up container registry integration
- Adding a new service to the existing ACA environment

## Key principle

ACA is the canonical compute surface. Managed identity + VNet + health probes + TLS = production-ready deployment.

## Related skills

- azd-secure-default-deployment (secure deployment patterns)
- azd-template-selection (select ACA-appropriate template)
- azure-cli-resource-operations (post-deployment diagnostics)
