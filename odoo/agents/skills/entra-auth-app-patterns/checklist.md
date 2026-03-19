# Checklist — entra-auth-app-patterns

## App registration

- [ ] App registration created in Entra
- [ ] Display name follows naming convention
- [ ] Redirect URIs configured correctly
- [ ] Supported account types set appropriately
- [ ] API permissions configured (minimal required)
- [ ] Admin consent granted where needed

## Authentication flow

- [ ] Correct flow selected for application type
- [ ] PKCE enabled for authorization code flows
- [ ] Token validation implemented in application
- [ ] Token cache configured for performance
- [ ] Refresh token handling implemented

## Managed identity

- [ ] System-assigned managed identity enabled on compute resource
- [ ] Role assignments granted for downstream services
- [ ] DefaultAzureCredential used in application code
- [ ] No fallback to client secrets in production

## Keyless access

- [ ] No API keys in application configuration
- [ ] No connection strings with embedded passwords
- [ ] Azure OpenAI accessed via Entra token (not API key)
- [ ] Key Vault accessed via managed identity

## Security

- [ ] Client secrets NOT stored in code or tracked config
- [ ] Certificate credentials preferred over secrets (where applicable)
- [ ] Token lifetimes follow defaults
- [ ] Cross-tenant access justified and documented

## Migration (Keycloak to Entra)

- [ ] OIDC/SAML parity verified
- [ ] Group/role mapping documented
- [ ] Service account replacement planned
- [ ] Break-glass admin configured
- [ ] Per-app cutover plan documented
