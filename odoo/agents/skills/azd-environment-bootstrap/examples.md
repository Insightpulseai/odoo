# Examples — azd-environment-bootstrap

## Example 1: Bootstrap dev environment for ACA web app

```bash
# Initialize from template
azd init --template azure-samples/todo-python-mongo-aca

# Create dev environment
azd env new dev

# Configure environment
azd env set AZURE_SUBSCRIPTION_ID "<subscription-id>"
azd env set AZURE_LOCATION "southeastasia"
azd env set AZURE_RESOURCE_GROUP "rg-ipai-dev"
azd env set AZURE_CONTAINER_REGISTRY "cripaidev"

# Set up CI/CD
azd pipeline config --provider github
```

---

## Example 2: Multi-environment setup

```bash
# Create all three environments
for env in dev staging prod; do
  azd env new $env
  azd env set AZURE_LOCATION "southeastasia" --env $env
  azd env set AZURE_RESOURCE_GROUP "rg-ipai-$env" --env $env
done
```

---

## Example 3: azure.yaml structure

```yaml
name: ipai-service
metadata:
  template: azure-samples/todo-python-mongo-aca
services:
  web:
    project: ./src/web
    host: containerapp
    language: python
  api:
    project: ./src/api
    host: containerapp
    language: python
```

---

## Anti-pattern: Secrets in environment variables

```bash
# WRONG — never put secrets in azd env
azd env set DATABASE_PASSWORD "my-secret-password"

# CORRECT — use Key Vault reference
azd env set DATABASE_PASSWORD_KV_REF "kv-ipai-dev/database-password"
```
