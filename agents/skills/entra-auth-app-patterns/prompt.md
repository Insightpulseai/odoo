# Prompt — entra-auth-app-patterns

You are implementing Microsoft Entra authentication for an application on the InsightPulse AI platform.

Your job is to:
1. Determine the correct authentication flow
2. Create/configure the Entra app registration
3. Implement token validation in application code
4. Configure managed identity for service-to-service auth
5. Test and verify the authentication flow
6. Document the configuration

Authentication flows by application type:
- **Web app (user-facing)**: Authorization code flow with PKCE
- **API (service-to-service)**: Client credentials or managed identity
- **Daemon/background service**: Managed identity (preferred) or client credentials
- **SPA**: Authorization code flow with PKCE (no client secret)

Key pattern: OpenAI + Entra + keyless + ACA
```python
from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI

credential = DefaultAzureCredential()
token = credential.get_token("https://cognitiveservices.azure.com/.default")

client = AzureOpenAI(
    azure_endpoint="https://oai-ipai-dev.openai.azure.com/",
    azure_ad_token=token.token,
    api_version="2024-02-01"
)
# No API key needed — Entra token via managed identity
```

Platform context:
- Current IdP: Keycloak (ipai-auth-dev) — transitional
- Target IdP: Microsoft Entra ID
- Azure OpenAI: oai-ipai-dev in rg-ipai-ai-dev

Output format:
- App registration: app ID, display name
- Authentication flow: type and configuration
- Token validation: implemented (yes/no)
- Managed identity: configured (yes/no)
- Keyless access: achieved (yes/no)
- Test result: auth flow verified (pass/fail)
