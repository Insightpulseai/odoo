// agents/teams-surface/infra/azure.bicep
//
// Supplemental Bicep for the Pulser Teams surface. The bulk of the
// provisioning (Bot Channel Registration, Entra app reg) is handled
// by `atk provision` via teamsapp.yml (botAadApp/create + aadApp/create).
//
// This file deploys the ADDITIONAL infra needed beyond what atk provides:
//   - Application Insights component for bot telemetry
//   - User-assigned managed identity (references existing id-ipai-dev)
//   - Diagnostic settings for the Bot Channel Registration
//
// AFD routing for /api/messages is in ../../infra/azure/modules/bot-route.bicep.

@description('Environment suffix — dev | staging | prod')
param env string = 'dev'

@description('Bot ID from botAadApp/create (env: BOT_ID)')
param botId string

@description('Existing id-ipai-dev MI in rg-ipai-dev-odoo-runtime')
param userAssignedMiName string = 'id-ipai-dev'

@description('Resource group where id-ipai-dev lives')
param userAssignedMiRg string = 'rg-ipai-dev-odoo-runtime'

@description('Existing Log Analytics workspace name')
param logAnalyticsName string = 'log-ipai-${env}'

@description('Existing LA resource group')
param logAnalyticsRg string = 'rg-ipai-${env}-platform'

// ─── Reference existing resources ────────────────────────────────────────────
resource existingMi 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing = {
  name: userAssignedMiName
  scope: resourceGroup(userAssignedMiRg)
}

resource existingLa 'Microsoft.OperationalInsights/workspaces@2023-09-01' existing = {
  name: logAnalyticsName
  scope: resourceGroup(logAnalyticsRg)
}

// ─── App Insights for bot telemetry ──────────────────────────────────────────
resource aiComponent 'Microsoft.Insights/components@2020-02-02' = {
  name: 'ai-pulser-teams-${env}'
  location: resourceGroup().location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: existingLa.id
    RetentionInDays: 90
  }
}

// ─── Bot Channel Registration reference (created by botAadApp/create) ────────
// Teams-only channel is auto-configured by atk. This resource reference lets
// us attach diagnostic settings below.
resource bot 'Microsoft.BotService/botServices@2022-09-15' existing = {
  name: 'pulser-teams-bot-${env}'
}

resource botDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: 'send-to-la'
  scope: bot
  properties: {
    workspaceId: existingLa.id
    logs: [
      {
        category: 'BotRequest'
        enabled: true
        retentionPolicy: { days: 90, enabled: true }
      }
    ]
    metrics: [
      {
        category: 'AllMetrics'
        enabled: true
        retentionPolicy: { days: 30, enabled: true }
      }
    ]
  }
}

// ─── Outputs ─────────────────────────────────────────────────────────────────
output appInsightsConnectionString string = aiComponent.properties.ConnectionString
output appInsightsInstrumentationKey string = aiComponent.properties.InstrumentationKey
output botChannelRegistrationId string = bot.id
output userAssignedMiClientId string = existingMi.properties.clientId
output userAssignedMiPrincipalId string = existingMi.properties.principalId
