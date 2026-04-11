// =============================================================================
// aca-odoo-services.bicep — Odoo ACA Runtime (web + worker + cron)
// =============================================================================
// Deploys 3 Container Apps for Odoo CE 19:
//   - odoo-web:    HTTP service (Front Door ingress)
//   - odoo-worker: Background queue workers (no ingress)
//   - odoo-cron:   Scheduled cron workers (no ingress)
//
// odoo-init is NOT included here — it runs as a Container App Job (separate module).
// =============================================================================

targetScope = 'resourceGroup'

// ---------------------------------------------------------------------------
// Parameters
// ---------------------------------------------------------------------------

@description('Existing Container Apps Environment name')
param environmentName string

@description('Resource group of the Container Apps Environment')
param environmentResourceGroup string = resourceGroup().name

@description('Container registry login server (e.g. myacr.azurecr.io)')
param containerRegistryServer string

@description('Managed identity resource ID for registry pull + Key Vault access')
param managedIdentityResourceId string

@description('Key Vault name for secret references')
param keyVaultName string

@description('PostgreSQL host FQDN')
param postgresHost string

@description('PostgreSQL database name')
param postgresDb string = 'odoo'

@description('Key Vault secret name for PostgreSQL user')
param postgresUserSecretName string = 'pg-odoo-user'

@description('Key Vault secret name for PostgreSQL password')
param postgresPasswordSecretName string = 'pg-odoo-password'

@description('Redis host (empty string disables Redis)')
param redisHost string = ''

@description('Container image name (without tag)')
param imageName string = 'odoo-ce'

@description('Container image tag')
param imageTag string = 'latest'

@description('Revision suffix for deployment tracking')
param revisionSuffix string = ''

// --- Sizing: web ---
@description('CPU cores for odoo-web')
param cpuWeb string = '1.0'

@description('Memory for odoo-web')
param memoryWeb string = '2Gi'

@description('Min replicas for odoo-web')
param minReplicasWeb int = 1

@description('Max replicas for odoo-web')
param maxReplicasWeb int = 3

// --- Sizing: worker ---
@description('CPU cores for odoo-worker')
param cpuWorker string = '0.5'

@description('Memory for odoo-worker')
param memoryWorker string = '1Gi'

@description('Min replicas for odoo-worker')
param minReplicasWorker int = 1

@description('Max replicas for odoo-worker')
param maxReplicasWorker int = 2

// --- Sizing: cron ---
@description('CPU cores for odoo-cron')
param cpuCron string = '0.5'

@description('Memory for odoo-cron')
param memoryCron string = '1Gi'

@description('Resource tags')
param tags object = {}

// ---------------------------------------------------------------------------
// References
// ---------------------------------------------------------------------------

resource acaEnvironment 'Microsoft.App/managedEnvironments@2023-05-01' existing = {
  name: environmentName
  scope: resourceGroup(environmentResourceGroup)
}

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' existing = {
  name: keyVaultName
}

// ---------------------------------------------------------------------------
// Variables
// ---------------------------------------------------------------------------

var fullImage = '${containerRegistryServer}/${imageName}:${imageTag}'

var sharedSecrets = [
  {
    name: 'db-user'
    keyVaultUrl: '${keyVault.properties.vaultUri}secrets/${postgresUserSecretName}'
    identity: managedIdentityResourceId
  }
  {
    name: 'db-password'
    keyVaultUrl: '${keyVault.properties.vaultUri}secrets/${postgresPasswordSecretName}'
    identity: managedIdentityResourceId
  }
]

var sharedEnv = concat([
  { name: 'DB_HOST'; value: postgresHost }
  { name: 'DB_NAME'; value: postgresDb }
  { name: 'DB_USER'; secretRef: 'db-user' }
  { name: 'DB_PASSWORD'; secretRef: 'db-password' }
  { name: 'ODOO_RC'; value: '/etc/odoo/odoo.conf' }
  { name: 'LIST_DB'; value: 'False' }
], !empty(redisHost) ? [
  { name: 'REDIS_HOST'; value: redisHost }
] : [])

var revisionSuffixProp = !empty(revisionSuffix) ? { revisionSuffix: revisionSuffix } : {}

// ---------------------------------------------------------------------------
// odoo-web — HTTP service, routable via Front Door
// ---------------------------------------------------------------------------

resource odooWeb 'Microsoft.App/containerApps@2023-05-01' = {
  name: 'odoo-web'
  location: resourceGroup().location
  tags: union(tags, { 'odoo-role': 'http' })
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentityResourceId}': {}
    }
  }
  properties: union({
    managedEnvironmentId: acaEnvironment.id
    configuration: {
      activeRevisionsMode: 'Multiple'
      ingress: {
        external: false // Internal only — Front Door routes to this via private endpoint / environment FQDN
        targetPort: 8069
        transport: 'auto'
        allowInsecure: false
        traffic: [
          {
            latestRevision: true
            weight: 100
            label: 'latest'
          }
        ]
      }
      registries: [
        {
          server: containerRegistryServer
          identity: managedIdentityResourceId
        }
      ]
      secrets: sharedSecrets
    }
    template: {
      containers: [
        {
          name: 'odoo-web'
          image: fullImage
          resources: {
            cpu: json(cpuWeb)
            memory: memoryWeb
          }
          env: sharedEnv
          probes: [
            {
              type: 'Liveness'
              httpGet: { path: '/web/health'; port: 8069 }
              initialDelaySeconds: 30
              periodSeconds: 30
              failureThreshold: 3
            }
            {
              type: 'Readiness'
              httpGet: { path: '/web/health'; port: 8069 }
              initialDelaySeconds: 15
              periodSeconds: 10
              failureThreshold: 3
            }
            {
              type: 'Startup'
              httpGet: { path: '/web/health'; port: 8069 }
              initialDelaySeconds: 10
              periodSeconds: 5
              failureThreshold: 30
            }
          ]
        }
      ]
      scale: {
        minReplicas: minReplicasWeb
        maxReplicas: maxReplicasWeb
        rules: [
          {
            name: 'http-scaling'
            http: { metadata: { concurrentRequests: '50' } }
          }
        ]
      }
    }
  }, revisionSuffixProp)
}

// ---------------------------------------------------------------------------
// odoo-worker — Background queue workers, NO ingress
// ---------------------------------------------------------------------------

resource odooWorker 'Microsoft.App/containerApps@2023-05-01' = {
  name: 'odoo-worker'
  location: resourceGroup().location
  tags: union(tags, { 'odoo-role': 'background-worker' })
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentityResourceId}': {}
    }
  }
  properties: union({
    managedEnvironmentId: acaEnvironment.id
    configuration: {
      activeRevisionsMode: 'Single'
      // No ingress — workers are not externally reachable
      registries: [
        {
          server: containerRegistryServer
          identity: managedIdentityResourceId
        }
      ]
      secrets: sharedSecrets
    }
    template: {
      containers: [
        {
          name: 'odoo-worker'
          image: fullImage
          command: [ 'odoo' ]
          args: [ '--no-http', '--workers=2', '--db_host=$(DB_HOST)', '--db_user=$(DB_USER)', '--db_password=$(DB_PASSWORD)', '-d', '$(DB_NAME)' ]
          resources: {
            cpu: json(cpuWorker)
            memory: memoryWorker
          }
          env: sharedEnv
          probes: [
            {
              type: 'Liveness'
              tcpSocket: { port: 8069 }
              initialDelaySeconds: 30
              periodSeconds: 60
              failureThreshold: 5
            }
          ]
        }
      ]
      scale: {
        minReplicas: minReplicasWorker
        maxReplicas: maxReplicasWorker
      }
    }
  }, revisionSuffixProp)
}

// ---------------------------------------------------------------------------
// odoo-cron — Scheduled cron workers, NO ingress, single replica
// ---------------------------------------------------------------------------

resource odooCron 'Microsoft.App/containerApps@2023-05-01' = {
  name: 'odoo-cron'
  location: resourceGroup().location
  tags: union(tags, { 'odoo-role': 'scheduled-worker' })
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentityResourceId}': {}
    }
  }
  properties: union({
    managedEnvironmentId: acaEnvironment.id
    configuration: {
      activeRevisionsMode: 'Single'
      // No ingress — cron is not externally reachable
      registries: [
        {
          server: containerRegistryServer
          identity: managedIdentityResourceId
        }
      ]
      secrets: sharedSecrets
    }
    template: {
      containers: [
        {
          name: 'odoo-cron'
          image: fullImage
          command: [ 'odoo' ]
          args: [ '--no-http', '--max-cron-threads=2', '--db_host=$(DB_HOST)', '--db_user=$(DB_USER)', '--db_password=$(DB_PASSWORD)', '-d', '$(DB_NAME)' ]
          resources: {
            cpu: json(cpuCron)
            memory: memoryCron
          }
          env: sharedEnv
          probes: [
            {
              type: 'Liveness'
              tcpSocket: { port: 8069 }
              initialDelaySeconds: 30
              periodSeconds: 60
              failureThreshold: 5
            }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 1 // Cron must be single-replica to avoid duplicate scheduled actions
      }
    }
  }, revisionSuffixProp)
}

// ---------------------------------------------------------------------------
// Outputs
// ---------------------------------------------------------------------------

output odooWebFqdn string = odooWeb.properties.configuration.ingress.fqdn
output odooWebName string = odooWeb.name
output odooWorkerName string = odooWorker.name
output odooCronName string = odooCron.name
