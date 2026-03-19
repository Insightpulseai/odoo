# Examples — azure-functions-azd-patterns

## Example 1: Python timer function with Flex Consumption

```python
# function_app.py
import azure.functions as func
import logging

app = func.FunctionApp()

@app.timer_trigger(schedule="0 */5 * * * *", arg_name="timer")
def process_queue(timer: func.TimerRequest) -> None:
    if timer.past_due:
        logging.info("Timer is past due")
    logging.info("Timer trigger executed")
```

**azure.yaml**:
```yaml
name: ipai-timer-func
services:
  func:
    project: ./src
    host: function
    language: python
```

**Deployment**:
```bash
azd up --environment dev
```

---

## Example 2: HTTP function with managed identity accessing Key Vault

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

@app.route(route="api/config", auth_level=func.AuthLevel.FUNCTION)
def get_config(req: func.HttpRequest) -> func.HttpResponse:
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url="https://kv-ipai-dev.vault.azure.net/",
                          credential=credential)
    # Access secret via managed identity — no connection string needed
    value = client.get_secret("config-key").value
    return func.HttpResponse(f"Config loaded", status_code=200)
```

---

## Example 3: Flex Consumption Bicep configuration

```bicep
resource functionApp 'Microsoft.Web/sites@2023-12-01' = {
  name: 'func-ipai-${environmentName}'
  location: location
  kind: 'functionapp,linux'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: flexPlan.id
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
    }
  }
}

resource flexPlan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: 'plan-func-ipai-${environmentName}'
  location: location
  sku: {
    tier: 'FlexConsumption'
    name: 'FC1'
  }
  properties: {
    reserved: true
  }
}
```

---

## Anti-pattern: Classic Consumption with connection strings

```python
# WRONG — connection string with embedded credentials
import os
conn_str = os.environ["COSMOS_CONNECTION_STRING"]  # Contains key

# CORRECT — managed identity
from azure.identity import DefaultAzureCredential
credential = DefaultAzureCredential()
client = CosmosClient(url, credential=credential)
```
