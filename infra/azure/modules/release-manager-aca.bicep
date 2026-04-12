// release-manager-aca.bicep — ACA container app + Redis cache for the Release Manager
//
// Deploys the Pulser Release Manager (forked from microsoft-foundry/Release-Manager-Assistant
// substrate). Includes Redis cache for session state (replaces RMA's in-memory ThreadSafeCache
// to comply with the IPAI stateless-agents invariant).
//
// Region: southeastasia — RMA hardcodes eastus2/westus2/centralus/westeurope/eastasia only.

targetScope = 'resourceGroup'

@description('ACA managed environment resource ID')
param managedEnvironmentId string

@description('Container image, e.g. acripaiodoo.azurecr.io/ipai-release-manager:v1')
param image string

@description('App name')
param appName string = 'ipai-release-manager'

@description('Location — forced to southeastasia. RMA would reject this; IPAI override.')
@allowed([
  'southeastasia'
  'eastasia'
  'eastus2'
  'westus2'
  'centralus'
  'westeurope'
])
param location string = 'southeastasia'

@description('User-assigned managed identity resource ID (id-ipai-dev)')
param managedIdentityId string

@description('ACR login server (acripaiodoo.azurecr.io)')
param acrServer string

@description('Foundry project endpoint — ipai-copilot-resource / ipai-copilot')
param foundryProjectEndpoint string = 'https://ipai-copilot-resource.services.ai.azure.com/api/projects/ipai-copilot'

@description('Key Vault name for secret references')
param keyVaultName string = 'kv-ipai-dev'

@description('Resource group of the Key Vault (if different from deployment RG)')
param keyVaultResourceGroup string = resourceGroup().name

@description('Stamp identifier (dev/staging/prod) — overrides YAML default')
@allowed(['dev', 'staging', 'prod'])
param stampId string = 'dev'

@description('Storage account for evidence bundles (stipaidev)')
param evidenceStorageAccount string = 'stipaidev'

@description('Log Analytics workspace ID for OTLP telemetry')
param logAnalyticsWorkspaceId string

@description('Tags')
param tags object = {}

// ---------------------------------------------------------------------------
// Redis cache — replaces RMA's ThreadSafeCache (stateless-agents invariant)
// ---------------------------------------------------------------------------
resource redis 'Microsoft.Cache/redis@2024-11-01' = {
  name: 'cache-ipai-${stampId}'
  location: location
  tags: tags
  properties: {
    sku: {
      name: stampId == 'prod' ? 'Standard' : 'Basic'
      family: 'C'
      capacity: stampId == 'prod' ? 2 : 0  // C0 for dev, C2 for prod
    }
    enableNonSslPort: false
    minimumTlsVersion: '1.2'
    publicNetworkAccess: 'Enabled'
    redisConfiguration: {
      'maxmemory-policy': 'allkeys-lru'
    }
  }
}

// Write the Redis primary key into Key Vault for the ACA app to pull
resource keyVault 'Microsoft.KeyVault/vaults@2024-04-01-preview' existing = {
  name: keyVaultName
  scope: resourceGroup(keyVaultResourceGroup)
}

// Deploy the secret into the KV's RG via a nested module
module redisKeySecret 'release-manager-kv-secret.bicep' = {
  name: 'deploy-rm-redis-secret'
  scope: resourceGroup(keyVaultResourceGroup)
  params: {
    keyVaultName: keyVaultName
    secretName: 'release-manager-redis-key'
    secretValue: redis.listKeys().primaryKey
  }
}

// ---------------------------------------------------------------------------
// Container App — internal ingress, ADO pipeline calls it via VNet
// ---------------------------------------------------------------------------
resource releaseManager 'Microsoft.App/containerApps@2024-03-01' = {
  name: appName
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentityId}': {}
    }
  }
  properties: {
    managedEnvironmentId: managedEnvironmentId
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        // Internal-only — ADO pipeline calls via VNet. Not public.
        external: false
        targetPort: 8000
        transport: 'http'
        allowInsecure: false
      }
      registries: [
        {
          server: acrServer
          identity: managedIdentityId
        }
      ]
      secrets: [
        {
          name: 'redis-key'
          keyVaultUrl: '${keyVault.properties.vaultUri}secrets/release-manager-redis-key'
          identity: managedIdentityId
        }
      ]
    }
    template: {
      containers: [
        {
          name: appName
          image: image
          env: [
            { name: 'STAMP',                   value: stampId }
            { name: 'IPAI_FOUNDRY_ENDPOINT',   value: foundryProjectEndpoint }
            { name: 'REDIS_URL',               value: 'rediss://${redis.properties.hostName}:${redis.properties.sslPort}' }
            { name: 'REDIS_KEY',               secretRef: 'redis-key' }
            { name: 'ODOO_MCP_URL',            value: 'https://erp.insightpulseai.com/mcp' }
            { name: 'EVIDENCE_STORAGE_ACCOUNT', value: evidenceStorageAccount }
            { name: 'LA_WORKSPACE_ID',         value: logAnalyticsWorkspaceId }
            { name: 'OTEL_EXPORTER_OTLP_ENDPOINT', value: 'http://localhost:4317' }
            { name: 'AZURE_CLIENT_ID',         value: reference(managedIdentityId, '2023-01-31').clientId }
          ]
          resources: {
            cpu: json('0.5')
            memory: '1.0Gi'
          }
          probes: [
            { type: 'Liveness',  httpGet: { path: '/health', port: 8000 }, initialDelaySeconds: 15, periodSeconds: 30 }
            { type: 'Readiness', httpGet: { path: '/health', port: 8000 }, initialDelaySeconds: 5,  periodSeconds: 10 }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
        rules: [
          { name: 'http-concurrent', http: { metadata: { concurrentRequests: '20' } } }
        ]
      }
    }
  }
}

// ---------------------------------------------------------------------------
// Outputs
// ---------------------------------------------------------------------------
output name string = releaseManager.name
output internalFqdn string = releaseManager.properties.configuration.ingress.fqdn
output redisHostName string = redis.properties.hostName
output principalId string = reference(managedIdentityId, '2023-01-31').principalId
