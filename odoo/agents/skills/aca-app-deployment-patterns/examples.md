# Examples — aca-app-deployment-patterns

## Example 1: Odoo web deployment pattern

```bicep
resource odooWeb 'Microsoft.App/containerApps@2023-05-01' = {
  name: 'ipai-odoo-dev-web'
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    managedEnvironmentId: acaEnvironment.id
    configuration: {
      registries: [{
        server: 'ipaiodoodevacr.azurecr.io'
        identity: 'system'
      }]
      ingress: {
        external: true
        targetPort: 8069
        transport: 'http'
        corsPolicy: {
          allowedOrigins: ['https://erp.insightpulseai.com']
        }
      }
    }
    template: {
      containers: [{
        name: 'odoo-web'
        image: 'ipaiodoodevacr.azurecr.io/odoo:19-latest'
        resources: {
          cpu: json('1.0')
          memory: '2Gi'
        }
        probes: [
          {
            type: 'Liveness'
            httpGet: { path: '/web/health', port: 8069 }
            periodSeconds: 30
          }
          {
            type: 'Readiness'
            httpGet: { path: '/web/health', port: 8069 }
            periodSeconds: 10
          }
          {
            type: 'Startup'
            httpGet: { path: '/web/health', port: 8069 }
            periodSeconds: 10
            failureThreshold: 30
          }
        ]
      }]
      scale: {
        minReplicas: 1
        maxReplicas: 3
        rules: [{
          name: 'http-scaling'
          http: { metadata: { concurrentRequests: '50' } }
        }]
      }
    }
  }
}
```

---

## Example 2: Worker (no ingress)

```bicep
resource odooWorker 'Microsoft.App/containerApps@2023-05-01' = {
  name: 'ipai-odoo-dev-worker'
  location: location
  identity: { type: 'SystemAssigned' }
  properties: {
    managedEnvironmentId: acaEnvironment.id
    configuration: {
      registries: [{
        server: 'ipaiodoodevacr.azurecr.io'
        identity: 'system'
      }]
      // No ingress — worker processes background jobs
    }
    template: {
      containers: [{
        name: 'odoo-worker'
        image: 'ipaiodoodevacr.azurecr.io/odoo:19-latest'
        command: ['odoo', '--workers=2', '--no-http']
        resources: { cpu: json('0.5'), memory: '1Gi' }
      }]
      scale: { minReplicas: 1, maxReplicas: 2 }
    }
  }
}
```

---

## Anti-pattern: Admin credentials for ACR + no health probes

```bicep
// WRONG
configuration: {
  registries: [{
    server: 'cripaidev.azurecr.io'
    username: 'cripaidev'
    passwordSecretRef: 'acr-pass'
  }]
}
// No probes defined — traffic routed to potentially unhealthy containers
```
