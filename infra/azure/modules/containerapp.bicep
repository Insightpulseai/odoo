// Container Apps Environment + Container App for Odoo runtime

@description('Name of the Container Apps Environment')
param environmentName string

@description('Name of the Container App')
param appName string

@description('Azure region')
param location string

@description('Resource tags')
param tags object

@description('ACR login server FQDN')
param acrLoginServer string

@description('Key Vault name for secrets')
param keyVaultName string

@description('PostgreSQL server FQDN')
param postgresHost string

// Log Analytics workspace for Container Apps Environment
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: '${environmentName}-logs'
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

// Container Apps Environment
resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: environmentName
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
  }
}

// Container App — Odoo CE runtime
resource containerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: appName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    managedEnvironmentId: containerAppsEnvironment.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8069
        transport: 'http'
      }
      registries: [
        {
          server: acrLoginServer
          identity: 'system'
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'odoo-ce'
          image: '${acrLoginServer}/odoo-ce:latest'
          resources: {
            cpu: json('1.0')
            memory: '2Gi'
          }
          env: [
            {
              name: 'ODOO_DB_HOST'
              value: postgresHost
            }
            {
              name: 'ODOO_DB_PORT'
              value: '5432'
            }
            {
              name: 'ODOO_DB_NAME'
              value: 'odoo'
            }
            {
              name: 'KEY_VAULT_NAME'
              value: keyVaultName
            }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
      }
    }
  }
}

output appFqdn string = containerApp.properties.configuration.ingress.fqdn
output appId string = containerApp.id
output environmentId string = containerAppsEnvironment.id
