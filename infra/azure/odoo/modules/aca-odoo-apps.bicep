param location string
param tags object

param acaEnvironmentId string
param odooImage string

param webAppName string
param workerAppName string
param cronAppName string

param enableExternalIngress bool
param targetPort int

param webCpu string
param webMemory string
param workerCpu string
param workerMemory string
param cronCpu string
param cronMemory string

param userAssignedIdentityId string
param keyVaultUri string
param postgresFqdn string
param dbName string
param dbUser string

// ---------------------------------------------------------------------------
// Shared env var block
// ---------------------------------------------------------------------------
var baseEnvVars = [
  { name: 'DB_HOST', value: postgresFqdn }
  { name: 'DB_PORT', value: '5432' }
  { name: 'DB_USER', value: dbUser }
  { name: 'DB_NAME', value: dbName }
  { name: 'KEY_VAULT_URI', value: keyVaultUri }
]

// ---------------------------------------------------------------------------
// Odoo web (external ingress)
// ---------------------------------------------------------------------------
resource web 'Microsoft.App/containerApps@2024-03-01' = {
  name: webAppName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned, UserAssigned'
    userAssignedIdentities: {
      '${userAssignedIdentityId}': {}
    }
  }
  properties: {
    managedEnvironmentId: acaEnvironmentId
    configuration: {
      ingress: enableExternalIngress ? {
        external: true
        targetPort: targetPort
        transport: 'auto'
      } : null
      activeRevisionsMode: 'Single'
    }
    template: {
      containers: [
        {
          name: 'web'
          image: odooImage
          resources: {
            cpu: json(webCpu)
            memory: webMemory
          }
          env: concat(baseEnvVars, [
            { name: 'PROXY_MODE', value: 'True' }
            { name: 'LIST_DB', value: 'False' }
            { name: 'WITHOUT_DEMO', value: 'all' }
            { name: 'ODOO_ROLE', value: 'web' }
          ])
        }
      ]
    }
  }
}

// ---------------------------------------------------------------------------
// Odoo worker (internal only)
// ---------------------------------------------------------------------------
resource worker 'Microsoft.App/containerApps@2024-03-01' = {
  name: workerAppName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    managedEnvironmentId: acaEnvironmentId
    configuration: {
      activeRevisionsMode: 'Single'
    }
    template: {
      containers: [
        {
          name: 'worker'
          image: odooImage
          resources: {
            cpu: json(workerCpu)
            memory: workerMemory
          }
          env: concat(baseEnvVars, [
            { name: 'ODOO_ROLE', value: 'worker' }
          ])
        }
      ]
    }
  }
}

// ---------------------------------------------------------------------------
// Odoo cron (internal only)
// ---------------------------------------------------------------------------
resource cron 'Microsoft.App/containerApps@2024-03-01' = {
  name: cronAppName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    managedEnvironmentId: acaEnvironmentId
    configuration: {
      activeRevisionsMode: 'Single'
    }
    template: {
      containers: [
        {
          name: 'cron'
          image: odooImage
          resources: {
            cpu: json(cronCpu)
            memory: cronMemory
          }
          env: concat(baseEnvVars, [
            { name: 'ODOO_ROLE', value: 'cron' }
          ])
        }
      ]
    }
  }
}

output webFqdn string = web.properties.configuration.ingress.fqdn
output webId string = web.id
output workerId string = worker.id
output cronId string = cron.id
