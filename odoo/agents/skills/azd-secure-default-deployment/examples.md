# Examples — azd-secure-default-deployment

## Example 1: Secure ACA deployment with azd up

```bash
# Single command: provision + deploy
azd up --environment dev

# Verify deployment
azd monitor --overview
```

**Security verification**:
```bash
# Check managed identity
az containerapp show -n ipai-service-dev -g rg-ipai-dev \
  --query "identity.type"
# Expected: "SystemAssigned"

# Check VNet integration
az containerapp show -n ipai-service-dev -g rg-ipai-dev \
  --query "properties.vnetConfiguration"
# Expected: non-null with subnet ID

# Check ACR pull identity
az containerapp show -n ipai-service-dev -g rg-ipai-dev \
  --query "properties.configuration.registries[0].identity"
# Expected: managed identity resource ID (not empty/admin)
```

---

## Example 2: Bicep with secure defaults

```bicep
resource containerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: 'ipai-service-${environmentName}'
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    managedEnvironmentId: containerAppEnvironment.id
    configuration: {
      registries: [
        {
          server: containerRegistry.properties.loginServer
          identity: 'system'
        }
      ]
    }
  }
}
```

---

## Anti-pattern: Admin credentials for ACR

```bicep
// WRONG — admin credentials
registries: [
  {
    server: 'cripaidev.azurecr.io'
    username: 'cripaidev'
    passwordSecretRef: 'acr-password'
  }
]

// CORRECT — managed identity
registries: [
  {
    server: 'cripaidev.azurecr.io'
    identity: 'system'
  }
]
```
