// Azure Container Apps Environment + Odoo Container App module

@description('Name of the Container Apps Environment')
param environmentName string

@description('Name of the Container App')
param appName string

@description('Azure region')
param location string

@description('Resource tags')
param tags object

@description('ACR login server (e.g. myacr.azurecr.io)')
param acrLoginServer string

@description('Container image (e.g. odoo:latest)')
param containerImage string = 'odoo:latest'

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

@description('PostgreSQL connection string')
@secure()
param dbConnectionString string = ''

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

// Odoo Container App
resource containerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: appName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    managedEnvironmentId: environment.id
    configuration: {
      activeRevisionsMode: 'Multiple'
      ingress: {
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
      }
      registries: [
        {
          server: acrLoginServer
          identity: acrIdentityId != '' ? acrIdentityId : 'system'
        }
      ]
      secrets: dbConnectionString != '' ? [
        {
          name: 'db-connection-string'
          value: dbConnectionString
        }
      ] : []
    }
    template: {
      containers: [
        {
          name: 'odoo'
          image: '${acrLoginServer}/${containerImage}'
          resources: {
            cpu: json(cpu)
            memory: memory
          }
          env: [
            {
              name: 'ODOO_RC'
              value: '/etc/odoo/odoo.conf'
            }
          ]
          probes: [
            {
              type: 'Liveness'
              httpGet: {
                path: '/web/health'
                port: 8069
              }
              initialDelaySeconds: 90
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
          ]
        }
      ]
      scale: {
        minReplicas: minReplicas
        maxReplicas: maxReplicas
        rules: [
          {
            name: 'http-scaling'
            http: {
              metadata: {
                concurrentRequests: '50'
              }
            }
          }
        ]
      }
    }
  }
}

output environmentName string = environment.name
output environmentId string = environment.id
output appName string = containerApp.name
output appFqdn string = containerApp.properties.configuration.ingress.fqdn
output appId string = containerApp.id
output appPrincipalId string = containerApp.identity.principalId
