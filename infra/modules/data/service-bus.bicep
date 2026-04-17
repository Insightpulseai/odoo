// modules/data/service-bus.bicep
// Creates: sb-ipai-prd-sea (Standard tier) — async queues for agent workflows
// Queues: bir-inbox, ap-invoice, month-end, supplier-comms, po-events
targetScope = 'resourceGroup'

param prefix        string
param env           string
param location      string
param tags          object
param miPrincipalId string

var sbName = 'sb-${prefix}-${env}-sea'

resource sb 'Microsoft.ServiceBus/namespaces@2024-01-01' = {
  name:     sbName
  location: location
  tags:     tags
  sku: {
    name:     'Standard'
    tier:     'Standard'
    capacity: 1
  }
  properties: {
    disableLocalAuth:      true        // MI-only: no SAS keys
    minimumTlsVersion:    '1.2'
    publicNetworkAccess:  'Enabled'
  }
}

// ── Queues ────────────────────────────────────────────────────
var queues = [
  { name: 'bir-inbox',       purpose: 'BIR document upload → ADE processing pipeline' }
  { name: 'ap-invoice',      purpose: 'Vendor invoice → AP Invoice Bot ingestion queue' }
  { name: 'month-end',       purpose: 'Month-end close trigger → Month-End Agent' }
  { name: 'supplier-comms',  purpose: 'Vendor email → Supplier Communications Agent' }
  { name: 'po-events',       purpose: 'Reorder alert → PO Agent creation queue' }
  { name: 'agent-dlq',       purpose: 'Dead-letter queue for failed agent events (DLQ/backoff)' }
]

resource sbQueues 'Microsoft.ServiceBus/namespaces/queues@2024-01-01' = [for q in queues: {
  name:   q.name
  parent: sb
  properties: {
    maxSizeInMegabytes:           1024
    lockDuration:                'PT1M'
    defaultMessageTimeToLive:    'P1D'
    deadLetteringOnMessageExpiration: true
    maxDeliveryCount:            5
    enableBatchedOperations:     true
  }
}]

// ── Role: Service Bus Data Owner → MI ────────────────────────
var sbDataOwnerRoleId = '090c5cfd-751d-490a-894a-3ce6f1109419'
resource miSbOwner 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name:  guid(sb.id, miPrincipalId, sbDataOwnerRoleId)
  scope: sb
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', sbDataOwnerRoleId)
    principalId:      miPrincipalId
    principalType:    'ServicePrincipal'
    description:      'IPAI MI → Service Bus Data Owner (agent queues)'
  }
}

// ── Outputs ────────────────────────────────────────────────────
output namespaceUri    string = 'sb://${sb.name}.servicebus.windows.net/'
output sbName          string = sb.name
output sbResourceId    string = sb.id
