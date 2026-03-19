# Evals — entra-auth-app-patterns

## Evaluation criteria

| Criterion | Weight | Pass condition |
|-----------|--------|----------------|
| Correct flow selection | 20% | Flow matches application type |
| Keyless access achieved | 25% | No API keys or embedded credentials |
| Managed identity used | 20% | DefaultAzureCredential in code |
| No secret in code/config | 15% | Zero client secrets in tracked files |
| Token validation | 10% | Tokens validated correctly |
| Documentation complete | 10% | App ID, permissions, flow documented |

## Test scenarios

1. **OpenAI keyless access** — managed identity token for Azure OpenAI
2. **Web app auth code flow** — PKCE, correct redirect URI, token cache
3. **Service-to-service** — managed identity, no client credentials
4. **Keycloak migration** — OIDC parity check, role mapping
5. **API key detected** — should flag and recommend Entra token
