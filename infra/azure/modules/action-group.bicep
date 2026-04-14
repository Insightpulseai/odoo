// =====================================================
// Azure Monitor Action Group — alert routing baseline
// AVM: avm/res/insights/action-group@0.8.0
// Doctrine: Engineering Execution — reuse AVM, thin delta only
// Deploys to: rg-ipai-dev-mon-sea (monitoring plane)
// =====================================================
targetScope = 'resourceGroup'

param prefix string = 'ipai'
param env string = 'dev'
param location string = 'global'
param tags object = {
  org: 'ipai'
  env: 'dev'
  platform: 'pulser-odoo'
  plane: 'observability'
  workload: 'alerting'
}

@description('Email recipients for alerts.')
param emailRecipients array = [
  {
    name: 'ops'
    emailAddress: 'ops@insightpulseai.com'
  }
]

@description('Optional Slack webhook URL. When empty, webhook receiver is skipped.')
@secure()
param slackWebhookUrl string = ''

var agName = 'ag-${prefix}-${env}-sea'
var webhookReceivers = empty(slackWebhookUrl) ? [] : [
  {
    name: 'slack-ipai-alerts'
    serviceUri: slackWebhookUrl
    useCommonAlertSchema: true
  }
]

module actionGroup 'br/public:avm/res/insights/action-group:0.8.0' = {
  name: 'avm-ag-${agName}'
  params: {
    name: agName
    location: location
    tags: tags
    groupShortName: 'ipai-${env}'
    enabled: true
    emailReceivers: [for r in emailRecipients: {
      name: r.name
      emailAddress: r.emailAddress
      useCommonAlertSchema: true
    }]
    webhookReceivers: webhookReceivers
  }
}

output actionGroupId string = actionGroup.outputs.resourceId
output actionGroupName string = actionGroup.outputs.name
