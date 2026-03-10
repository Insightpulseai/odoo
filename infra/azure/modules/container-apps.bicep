// Azure Container Apps Environment + Odoo Container App module
// Supports official odoo:19.0 from Docker Hub (public) or custom ACR images

@description('Name of the Container Apps Environment')
param environmentName string

@description('Name of the Container App')
param appName string

@description('Azure region')
param location string

@description('Resource tags')
param tags object

@description('Container image reference (e.g. docker.io/library/odoo:19.0 or myacr.azurecr.io/odoo:latest)')
param containerImage string = 'docker.io/library/odoo:19.0'

@description('ACR login server for private images (empty = public Docker Hub)')
param acrLoginServer string = ''

@description('Log Analytics workspace ID for diagnostics')
param logAnalyticsWorkspaceId string = ''

@description('Log Analytics shared key')
@secure()
param logAnalyticsSharedKey string = ''

@description('Minimum replicas')
param minReplicas int = 1

@description('Maximum replicas')
param maxReplicas int = 3

@description('CPU cores per replica')
param cpu string = '1.0'

@description('Memory per replica')
param memory string = '2Gi'

@description('Container app role: web (with ingress), worker (no ingress, no HTTP), cron (no ingress, singleton)')
@allowed(['web', 'worker', 'cron'])
param role string = 'web'

@description('PostgreSQL host FQDN')
param dbHost string

@description('PostgreSQL port')
param dbPort string = '5432'

@description('PostgreSQL user')
param dbUser string = 'odoo_admin'

@description('PostgreSQL password')
@secure()
param dbPassword string

@description('Managed Identity resource ID for ACR pull')
param acrIdentityId string = ''

// Container Apps Environment
resource environment 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: environmentName
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: logAnalyticsWorkspaceId != '' ? {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalyticsWorkspaceId
        sharedKey: logAnalyticsSharedKey
      }
    } : {}
    zoneRedundant: false
  }
}

// Determine image source: ACR-prefixed or direct Docker Hub
var imageRef = acrLoginServer != '' ? '${acrLoginServer}/${containerImage}' : containerImage

// Ingress only for web role
var ingressConfig = role == 'web' ? {
  external: true
  targetPort: 8069
  transport: 'http'
  allowInsecure: false
  traffic: [
    {
      latestRevision: true
      weight: 100
    }
  ]
} : null

// Registry config only when using ACR
var registryConfig = acrLoginServer != '' ? [
  {
    server: acrLoginServer
    identity: acrIdentityId != '' ? acrIdentityId : 'system'
  }
] : []

// Role-specific command overrides
var commandOverride = role == 'worker' ? [
  'odoo'
  '--no-http'
  '--workers=2'
  '--db_host=${dbHost}'
] : role == 'cron' ? [
  'odoo'
  '--no-http'
  '--max-cron-threads=1'
  '--workers=0'
  '--db_host=${dbHost}'
] : []

// Odoo Container App
resource containerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: appName
  location: location
  tags: union(tags, { OdooRole: role })
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    managedEnvironmentId: environment.id
    configuration: {
      activeRevisionsMode: role == 'web' ? 'Multiple' : 'Single'
      ingress: ingressConfig
      registries: registryConfig
      secrets: [
        {
          name: 'db-password'
          value: dbPassword
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'odoo'
          image: imageRef
          command: !empty(commandOverride) ? commandOverride : null
          resources: {
            cpu: json(cpu)
            memory: memory
          }
          env: [
            {
              name: 'HOST'
              value: dbHost
            }
            {
              name: 'PORT'
              value: dbPort
            }
            {
              name: 'USER'
              value: dbUser
            }
            {
              name: 'PASSWORD'
              secretRef: 'db-password'
            }
          ]
          probes: role == 'web' ? [
            {
              type: 'Liveness'
              httpGet: {
                path: '/web/health'
                port: 8069
              }
              initialDelaySeconds: 60
              periodSeconds: 30
              timeoutSeconds: 10
              failureThreshold: 3
            }
            {
              type: 'Readiness'
              httpGet: {
                path: '/web/health'
                port: 8069
              }
              initialDelaySeconds: 30
              periodSeconds: 10
              timeoutSeconds: 5
              failureThreshold: 3
            }
          ] : []
        }
      ]
      scale: {
        minReplicas: role == 'cron' ? 1 : minReplicas
        maxReplicas: role == 'cron' ? 1 : maxReplicas
        rules: role == 'web' ? [
          {
            name: 'http-scaling'
            http: {
              metadata: {
                concurrentRequests: '50'
              }
            }
          }
        ] : []
      }
    }
  }
}

output environmentName string = environment.name
output environmentId string = environment.id
output appName string = containerApp.name
output appFqdn string = role == 'web' ? containerApp.properties.configuration.ingress.fqdn : ''
output appId string = containerApp.id
output appPrincipalId string = containerApp.identity.principalId
