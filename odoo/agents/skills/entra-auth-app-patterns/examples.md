# Examples — entra-auth-app-patterns

## Example 1: Azure OpenAI with Entra keyless access

```python
from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI

# Managed identity → Entra token → Azure OpenAI
# No API key needed
credential = DefaultAzureCredential()
token = credential.get_token("https://cognitiveservices.azure.com/.default")

client = AzureOpenAI(
    azure_endpoint="https://oai-ipai-dev.openai.azure.com/",
    azure_ad_token=token.token,
    api_version="2024-02-01"
)

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello"}]
)
```

**Required role assignment**:
```bash
az role assignment create \
  --assignee <managed-identity-principal-id> \
  --role "Cognitive Services OpenAI User" \
  --scope /subscriptions/<sub>/resourceGroups/rg-ipai-ai-dev/providers/Microsoft.CognitiveServices/accounts/oai-ipai-dev
```

---

## Example 2: Web app with authorization code flow

```python
# Flask/FastAPI with MSAL
from msal import ConfidentialClientApplication

app = ConfidentialClientApplication(
    client_id="<app-registration-client-id>",
    authority="https://login.microsoftonline.com/<tenant-id>",
    client_credential=certificate_data  # Certificate, not secret
)

# Initiate auth code flow
flow = app.initiate_auth_code_flow(
    scopes=["User.Read"],
    redirect_uri="https://erp.insightpulseai.com/auth/callback"
)
```

---

## Example 3: Service-to-service with managed identity

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# No credentials needed — managed identity handles auth
credential = DefaultAzureCredential()
kv_client = SecretClient(
    vault_url="https://kv-ipai-dev.vault.azure.net/",
    credential=credential
)
secret = kv_client.get_secret("database-connection")
```

---

## Anti-pattern: API key in environment variable

```python
# WRONG — API key auth
client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=os.environ["AZURE_OPENAI_API_KEY"],  # Key-based auth
)

# CORRECT — Entra keyless auth
credential = DefaultAzureCredential()
token = credential.get_token("https://cognitiveservices.azure.com/.default")
client = AzureOpenAI(azure_endpoint=endpoint, azure_ad_token=token.token)
```
