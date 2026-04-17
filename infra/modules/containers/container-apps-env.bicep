// modules/containers/container-apps-env.bicep
// Creates: acae-ipai-prd-sea (Container Apps Managed Environment)
// Zone-redundant in production; log forwarding to Log Analytics
targetScope = 'resourceGroup'

param prefix                  string
param env                     string
param location                string
param tags                    object
param logAnalyticsWorkspaceId string
param zoneRedundant           bool = false

var acaeName = 'acae-${prefix}-${env}-sea'

resource acae 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name:     acaeName
  location: location
  tags:     tags
  properties: {
    zoneRedundant: false
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: reference(logAnalyticsWorkspaceId, '2023-09-01').customerId
        sharedKey:  listKeys(logAnalyticsWorkspaceId, '2023-09-01').primarySharedKey
      }
    }
    workloadProfiles: [
      {
        name:                'Consumption'
        workloadProfileType: 'Consumption'
      }
    ]
    peerAuthentication: {
      mtls: { enabled: false }
    }
  }
}

// ── Outputs ────────────────────────────────────────────────────
output acaeId    string = acae.id
output acaeName  string = acae.name
output acaeDefaultDomain string = acae.properties.defaultDomain
