# azd-secure-default-deployment

Deploy applications with secure-by-default posture via azd.

## Owner

app-hosting-engineer

## When to use

- First deployment of an azd-managed application
- Security posture review of existing deployment
- Upgrading from insecure to secure-default configuration

## Key principle

Managed identity + VNet + private endpoints + keyless access = secure-by-default. No exceptions for production deployments.

## Related skills

- azd-environment-bootstrap (prerequisite — environment must be configured)
- aca-app-deployment-patterns (ACA-specific deployment details)
- entra-auth-app-patterns (authentication layer)
