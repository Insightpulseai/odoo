# azure-aca-runtime -- Worked Examples

## Example 1: Container App with Probes and Scaling (Bicep)

Before (gap state):
```bicep
resource odooApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: 'ca-ipai-odoo'
  properties: {
    template: {
      containers: [{ name: 'odoo', image: acrImage }]
      scale: { minReplicas: 0, maxReplicas: 5 }
    }
    configuration: {
      ingress: { targetPort: 8069 }
    }
  }
}
```

After (closed):
```bicep
resource odooApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: 'ca-ipai-odoo'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    template: {
      containers: [
        {
          name: 'odoo'
          image: acrImage
          probes: [
            {
              type: 'Startup'
              httpGet: { path: '/web/health', port: 8069, scheme: 'HTTP' }
              initialDelaySeconds: 30
              periodSeconds: 10
              timeoutSeconds: 5
              failureThreshold: 30    // 30 * 10s = 300s total startup budget
            }
            {
              type: 'Liveness'
              httpGet: { path: '/web/health', port: 8069, scheme: 'HTTP' }
              periodSeconds: 30
              timeoutSeconds: 5
              failureThreshold: 3
            }
            {
              type: 'Readiness'
              httpGet: { path: '/web/health', port: 8069, scheme: 'HTTP' }
              initialDelaySeconds: 10
              periodSeconds: 10
              timeoutSeconds: 5
              failureThreshold: 3
            }
          ]
        }
      ]
      scale: {
        minReplicas: 1              // never zero for ERP production
        maxReplicas: 5
        rules: [
          {
            name: 'http-scaling'
            http: { metadata: { concurrentRequests: '50' } }
          }
        ]
      }
    }
    configuration: {
      activeRevisionsMode: 'Multiple'    // enables traffic split for zero-downtime
      ingress: {
        external: true
        targetPort: 8069
        traffic: [
          { latestRevision: true, weight: 100 }
        ]
      }
    }
  }
}
```

## Example 2: Managed Identity for Key Vault Secret Access

```bicep
// Grant ACA system-assigned MI access to Key Vault
resource kvSecretAccess 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(keyVault.id, odooApp.id, 'Key Vault Secrets User')
  scope: keyVault
  properties: {
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '4633458b-17de-408a-b874-0445c86b69e6'  // Key Vault Secrets User
    )
    principalId: odooApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

// Bind secret as environment variable in the container app
// In container definition:
env: [
  {
    name: 'ZOHO_SMTP_PASSWORD'
    secretRef: 'zoho-smtp-password'
  }
]
secrets: [
  {
    name: 'zoho-smtp-password'
    keyVaultUrl: 'https://kv-ipai-dev.vault.azure.net/secrets/zoho-smtp-password'
    identity: 'system'
  }
]
```

## Example 3: MCP Query Sequence

```
Step 1: microsoft_docs_search("Azure Container Apps health probes liveness readiness startup")
Result: Three probe types supported: Startup (gates other probes until ready),
        Liveness (restart if fails), Readiness (remove from load balancer if fails).
        Startup probe recommended for slow-starting apps. failureThreshold * periodSeconds
        = total startup budget. Odoo typically needs 60-180s.

Step 2: microsoft_docs_search("Azure Container Apps scaling rules HTTP KEDA")
Result: HTTP scaling rule: `concurrentRequests` triggers scale-out.
        minReplicas: 0 = scale to zero (cold start). For ERP, set minReplicas >= 1.
        KEDA allows custom scalers (service bus queue depth, PG connection count).

Step 3: microsoft_docs_search("Azure Front Door Container Apps origin private link")
Result: Front Door Premium supports Private Link origin for ACA.
        ACA environment must be external (not internal-only) for Front Door origin.
        Health probe: GET /web/health every 30s, 2 unhealthy threshold.
```
