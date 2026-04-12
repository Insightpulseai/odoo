// infra/azure/modules/aca-bot-proxy.bicep
//
// Deploys apps/bot-proxy as an ACA container app with EXTERNAL ingress.
// Hosts 6 Bot Framework routes (one per IPAI agent), forwards to the
// internal ipai-copilot-gateway via ACA-VNet DNS.
//
// Scope:   resourceGroup (target: rg-ipai-dev-odoo-runtime — same env as gateway)
// Deploy:  az deployment group create \
//            --resource-group rg-ipai-dev-odoo-runtime \
//            --template-file infra/azure/modules/aca-bot-proxy.bicep \
//            --parameters env=dev userAssignedMiResourceId=<id-pulser-rid> ...

@description('Environment suffix — dev | staging | prod')
@allowed([ 'dev', 'staging', 'prod' ])
param env string = 'dev'

@description('Existing ACA environment (must be the same env as ipai-copilot-gateway)')
param containerAppsEnvironmentName string = 'ipai-odoo-dev-env-v2'

@description('Container image (ACR + tag)')
param image string = 'ipaiodoodevacr.azurecr.io/ipai-bot-proxy:latest'

@description('User-assigned MI resource ID (typically id-ipai-agent-pulser-<env>)')
param userAssignedMiResourceId string

@description('User-assigned MI client ID (used as AZURE_CLIENT_ID in container env)')
param userAssignedMiClientId string

@description('Container listen port')
param containerPort int = 8088

@description('Internal gateway URL — ipai-copilot-gateway ACA VNet DNS')
param copilotGatewayUrl string = 'http://ipai-copilot-gateway.internal.blackstone-0df78186.southeastasia.azurecontainerapps.io:8088'

@description('Entra scope requested for gateway calls')
param copilotGatewayScope string = 'api://ipai-copilot-gateway/.default'

@description('Bot Framework App IDs, keyed by agent (set after atk provision)')
param botIds object = {
  PULSER: ''
  TAX_GURU: ''
  DOC_INTEL: ''
  BANK_RECON: ''
  AP_INVOICE: ''
  FINANCE_CLOSE: ''
}

@description('Key Vault ID containing bot-password-* secrets (kv-ipai-<env>)')
param keyVaultResourceId string = ''

@description('Resource tags')
param tags object = {
  project: 'ipai'
  env: env
  layer: 'agents'
  spec: 'pulser-entra-agent-id'
}

var location = resourceGroup().location

// ─── Reference existing ACA environment ─────────────────────────────────────
resource acaEnv 'Microsoft.App/managedEnvironments@2024-03-01' existing = {
  name: containerAppsEnvironmentName
}

// ─── Bot-proxy container app ────────────────────────────────────────────────
resource botProxy 'Microsoft.App/containerApps@2024-03-01' = {
  name: 'ipai-bot-proxy-${env}'
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userAssignedMiResourceId}': {}
    }
  }
  properties: {
    environmentId: acaEnv.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: containerPort
        transport: 'Http'
        allowInsecure: false
        traffic: [
          {
            weight: 100
            latestRevision: true
          }
        ]
      }
      registries: [
        {
          server: 'ipaiodoodevacr.azurecr.io'
          identity: userAssignedMiResourceId
        }
      ]
      // Bot Framework passwords must be injected as ACA secrets.
      // Wire via Key Vault reference once secrets are seeded by atk provision.
      // Placeholder values; owner runbook (spec/pulser-entra-agent-id/deploy.md)
      // describes the KV secret seeding step.
      secrets: [
        {
          name: 'bot-password-pulser'
          keyVaultUrl: empty(keyVaultResourceId) ? null : '${reference(keyVaultResourceId, '2023-07-01').vaultUri}secrets/bot-password-pulser'
          identity: empty(keyVaultResourceId) ? null : userAssignedMiResourceId
        }
        {
          name: 'bot-password-tax-guru'
          keyVaultUrl: empty(keyVaultResourceId) ? null : '${reference(keyVaultResourceId, '2023-07-01').vaultUri}secrets/bot-password-tax-guru'
          identity: empty(keyVaultResourceId) ? null : userAssignedMiResourceId
        }
        {
          name: 'bot-password-doc-intel'
          keyVaultUrl: empty(keyVaultResourceId) ? null : '${reference(keyVaultResourceId, '2023-07-01').vaultUri}secrets/bot-password-doc-intel'
          identity: empty(keyVaultResourceId) ? null : userAssignedMiResourceId
        }
        {
          name: 'bot-password-bank-recon'
          keyVaultUrl: empty(keyVaultResourceId) ? null : '${reference(keyVaultResourceId, '2023-07-01').vaultUri}secrets/bot-password-bank-recon'
          identity: empty(keyVaultResourceId) ? null : userAssignedMiResourceId
        }
        {
          name: 'bot-password-ap-invoice'
          keyVaultUrl: empty(keyVaultResourceId) ? null : '${reference(keyVaultResourceId, '2023-07-01').vaultUri}secrets/bot-password-ap-invoice'
          identity: empty(keyVaultResourceId) ? null : userAssignedMiResourceId
        }
        {
          name: 'bot-password-finance-close'
          keyVaultUrl: empty(keyVaultResourceId) ? null : '${reference(keyVaultResourceId, '2023-07-01').vaultUri}secrets/bot-password-finance-close'
          identity: empty(keyVaultResourceId) ? null : userAssignedMiResourceId
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'bot-proxy'
          image: image
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: [
            { name: 'PORT',                  value: string(containerPort) }
            { name: 'COPILOT_GATEWAY_URL',   value: copilotGatewayUrl }
            { name: 'COPILOT_GATEWAY_SCOPE', value: copilotGatewayScope }
            { name: 'AZURE_CLIENT_ID',       value: userAssignedMiClientId }
            // Bot Framework App IDs — per-agent, populated after atk provision
            { name: 'BOT_ID_PULSER',         value: botIds.PULSER }
            { name: 'BOT_ID_TAX_GURU',       value: botIds.TAX_GURU }
            { name: 'BOT_ID_DOC_INTEL',      value: botIds.DOC_INTEL }
            { name: 'BOT_ID_BANK_RECON',     value: botIds.BANK_RECON }
            { name: 'BOT_ID_AP_INVOICE',     value: botIds.AP_INVOICE }
            { name: 'BOT_ID_FINANCE_CLOSE',  value: botIds.FINANCE_CLOSE }
            // Bot Framework passwords — secretRef → Key Vault
            { name: 'BOT_PASSWORD_PULSER',        secretRef: 'bot-password-pulser' }
            { name: 'BOT_PASSWORD_TAX_GURU',      secretRef: 'bot-password-tax-guru' }
            { name: 'BOT_PASSWORD_DOC_INTEL',     secretRef: 'bot-password-doc-intel' }
            { name: 'BOT_PASSWORD_BANK_RECON',    secretRef: 'bot-password-bank-recon' }
            { name: 'BOT_PASSWORD_AP_INVOICE',    secretRef: 'bot-password-ap-invoice' }
            { name: 'BOT_PASSWORD_FINANCE_CLOSE', secretRef: 'bot-password-finance-close' }
          ]
          probes: [
            {
              type: 'Liveness'
              httpGet: {
                path: '/healthz'
                port: containerPort
              }
              initialDelaySeconds: 30
              periodSeconds: 30
            }
            {
              type: 'Readiness'
              httpGet: {
                path: '/healthz'
                port: containerPort
              }
              initialDelaySeconds: 5
              periodSeconds: 10
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

// ─── Outputs ────────────────────────────────────────────────────────────────
output fqdn string = botProxy.properties.configuration.ingress.fqdn
output resourceId string = botProxy.id
output name string = botProxy.name
