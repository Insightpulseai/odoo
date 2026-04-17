// modules/containers/container-apps.bicep
// Creates ALL ACA workloads for the IPAI Pulser stack:
//   ca-ipai-odoo-web-prd      — Odoo HTTP (port 8069, external ingress)
//   ca-ipai-odoo-cron-prd     — Odoo scheduled actions (no ingress)
//   ca-ipai-odoo-worker-prd   — Odoo background queue jobs (no ingress)
//   ca-ipai-release-manager-prd — Release Manager agent
//   ca-ipai-ade-mcp-prd       — LandingAI ADE MCP server
//   caj-ipai-build-agent-prd  — CI/CD build agent (ACA Job, event-driven)
// All containers:
//   - Pull from acripaiprd via MI (no admin credentials)
//   - Read secrets from kv-ipai-prd-sea via MI secretRef
//   - Wire OpenTelemetry → appi-ipai-prd (configure_azure_monitor)
targetScope = 'resourceGroup'

param prefix               string
param env                  string
param location             string
param tags                 object
param acaeId               string
param acrLoginServer       string
param miResourceId         string
param miClientId           string
param kvUri                string
param pgHost               string
param appInsightsConnStr   string     // KV secret URI
param foundryEndpoint      string
param foundryProjectId     string
param aiSearchEndpoint     string
param sbNamespaceUri       string
param odooImageTag         string = 'latest'
param adlsAccountName      string

// ── Common secret refs (KV via MI) ────────────────────────────
var commonSecrets = [
  {
    name:        'azure-client-id'
    value:       miClientId
  }
  {
    name:        'appinsights-connection-string'
    keyVaultUrl: appInsightsConnStr
    identity:    miResourceId
  }
]

var commonEnv = [
  { name: 'AZURE_CLIENT_ID',                    secretRef: 'azure-client-id' }
  { name: 'APPLICATIONINSIGHTS_CONNECTION_STRING', secretRef: 'appinsights-connection-string' }
  { name: 'AZURE_FOUNDRY_ENDPOINT',             value: foundryEndpoint }
  { name: 'AZURE_FOUNDRY_PROJECT_ID',           value: foundryProjectId }
  { name: 'AZURE_AI_SEARCH_ENDPOINT',           value: aiSearchEndpoint }
  { name: 'AZURE_SERVICE_BUS_URI',              value: sbNamespaceUri }
  { name: 'ADLS_ACCOUNT_NAME',                  value: adlsAccountName }
]

var commonIdentity = {
  type: 'UserAssigned'
  userAssignedIdentities: { '${miResourceId}': {} }
}

var commonRegistry = [
  {
    server:   acrLoginServer
    identity: miResourceId
  }
]

// ── Odoo Web (ca-ipai-odoo-web-prd) ──────────────────────────
resource odooWeb 'Microsoft.App/containerApps@2024-03-01' = {
  name:     'ca-${prefix}-odoo-web-${env}'
  location: location
  tags: union(tags, { 'azd-service-name': 'odoo-web' })
  identity:  commonIdentity
  properties: {
    environmentId: acaeId
    configuration: {
      ingress: {
        external:       true
        targetPort:     8069
        transport:      'auto'
        allowInsecure:  false
        traffic: [{ weight: 100, latestRevision: true }]
        stickySessions: { affinity: 'sticky' }   // Odoo sessions require sticky
      }
      registries: commonRegistry
      secrets:    commonSecrets
      revisionMode: 'Single'
    }
    template: {
      containers: [{
        name:  'odoo-web'
        image: '${acrLoginServer}/odoo:${odooImageTag}'
        resources: {
          cpu:    '1.0'
          memory: '2Gi'
        }
        env: union(commonEnv, [
          { name: 'ODOO_ROLE',            value: 'web' }
          { name: 'DB_HOST',              value: pgHost }
          { name: 'DB_NAME',              value: 'odoo' }
          { name: 'DB_PORT',              value: '5432' }
          { name: 'ACA_SERVICE_NAME',     value: 'ca-${prefix}-odoo-web-${env}' }
          { name: 'ODOO_MAX_CRON_THREADS', value: '0' }   // Cron handled by dedicated container
        ])
        probes: [
          {
            type: 'Liveness'
            httpGet: { path: '/web/health', port: 8069 }
            periodSeconds:     30
            timeoutSeconds:    5
            failureThreshold:  3
          }
          {
            type: 'Readiness'
            httpGet: { path: '/web/health', port: 8069 }
            initialDelaySeconds: 20
            periodSeconds:       10
          }
        ]
      }]
      scale: {
        minReplicas: env == 'prd' ? 2 : 1
        maxReplicas: 5
        rules: [{
          name: 'http-scaling'
          http: { metadata: { concurrentRequests: '20' } }
        }]
      }
    }
  }
}

// ── Odoo Cron (ca-ipai-odoo-cron-prd) ────────────────────────
resource odooCron 'Microsoft.App/containerApps@2024-03-01' = {
  name:     'ca-${prefix}-odoo-cron-${env}'
  location: location
  tags: union(tags, { 'azd-service-name': 'odoo-cron' })
  identity:  commonIdentity
  properties: {
    environmentId: acaeId
    configuration: {
      ingress:      null            // No ingress — internal only
      registries:   commonRegistry
      secrets:      commonSecrets
      revisionMode: 'Single'
    }
    template: {
      containers: [{
        name:  'odoo-cron'
        image: '${acrLoginServer}/odoo:${odooImageTag}'
        resources: { cpu: '0.5', memory: '1Gi' }
        env: union(commonEnv, [
          { name: 'ODOO_ROLE',             value: 'cron' }
          { name: 'DB_HOST',               value: pgHost }
          { name: 'DB_NAME',               value: 'odoo' }
          { name: 'ODOO_MAX_CRON_THREADS', value: '2' }
          { name: 'ACA_SERVICE_NAME',      value: 'ca-${prefix}-odoo-cron-${env}' }
        ])
      }]
      scale: { minReplicas: 1, maxReplicas: 1 }
    }
  }
}

// ── Odoo Worker (ca-ipai-odoo-worker-prd) ────────────────────
resource odooWorker 'Microsoft.App/containerApps@2024-03-01' = {
  name:     'ca-${prefix}-odoo-worker-${env}'
  location: location
  tags: union(tags, { 'azd-service-name': 'odoo-worker' })
  identity:  commonIdentity
  properties: {
    environmentId: acaeId
    configuration: {
      ingress:      null
      registries:   commonRegistry
      secrets:      commonSecrets
      revisionMode: 'Single'
    }
    template: {
      containers: [{
        name:  'odoo-worker'
        image: '${acrLoginServer}/odoo:${odooImageTag}'
        resources: { cpu: '0.5', memory: '1Gi' }
        env: union(commonEnv, [
          { name: 'ODOO_ROLE',        value: 'worker' }
          { name: 'DB_HOST',          value: pgHost }
          { name: 'DB_NAME',          value: 'odoo' }
          { name: 'ACA_SERVICE_NAME', value: 'ca-${prefix}-odoo-worker-${env}' }
        ])
      }]
      scale: {
        minReplicas: 1
        maxReplicas: 3
        rules: [{
          name: 'sb-queue-scaling'
          custom: {
            type: 'azure-servicebus'
            metadata: {
              namespace:     sbNamespaceUri
              queueName:     'ap-invoice'
              messageCount:  '5'
            }
            auth: [{ triggerParameter: 'connection', secretRef: 'azure-client-id' }]
          }
        }]
      }
    }
  }
}

// ── Release Manager Agent (ca-ipai-release-manager-prd) ──────
resource releaseManager 'Microsoft.App/containerApps@2024-03-01' = {
  name:     'ca-${prefix}-release-manager-${env}'
  location: location
  tags: union(tags, { 'azd-service-name': 'release-manager' })
  identity:  commonIdentity
  properties: {
    environmentId: acaeId
    configuration: {
      ingress: {
        external:      false          // Internal only — triggered by CI pipeline
        targetPort:    8080
        transport:     'auto'
      }
      registries:   commonRegistry
      secrets:      commonSecrets
      revisionMode: 'Single'
    }
    template: {
      containers: [{
        name:  'release-manager'
        image: '${acrLoginServer}/ipai-release-manager:${odooImageTag}'
        resources: { cpu: '0.5', memory: '1Gi' }
        env: union(commonEnv, [
          { name: 'ACA_SERVICE_NAME',     value: 'ca-${prefix}-release-manager-${env}' }
          { name: 'ADO_ORG',              value: 'insightpulseai' }
          { name: 'ADO_PROJECT',          value: 'ipai-platform' }
          { name: 'EVAL_THRESHOLD_REGRESSION', value: '0.95' }
          { name: 'EVAL_THRESHOLD_CAPABILITY', value: '0.70' }
        ])
      }]
      scale: { minReplicas: 1, maxReplicas: 1 }
    }
  }
}

// ── ADE MCP Server (ca-ipai-ade-mcp-prd) ─────────────────────
resource adeMcp 'Microsoft.App/containerApps@2024-03-01' = {
  name:     'ca-${prefix}-ade-mcp-${env}'
  location: location
  tags: union(tags, { 'azd-service-name': 'ade-mcp' })
  identity:  commonIdentity
  properties: {
    environmentId: acaeId
    configuration: {
      ingress: {
        external:   false       // Internal MCP endpoint for Pulser agents
        targetPort: 8000
        transport:  'auto'
      }
      registries: commonRegistry
      secrets: union(commonSecrets, [
        {
          name:        'ade-api-key'
          keyVaultUrl: '${kvUri}secrets/ade-vision-agent-api-key'
          identity:    miResourceId
        }
      ])
      revisionMode: 'Single'
    }
    template: {
      containers: [{
        name:  'ade-mcp'
        image: '${acrLoginServer}/ipai-ade-mcp:${odooImageTag}'
        resources: { cpu: '0.5', memory: '1Gi' }
        env: union(commonEnv, [
          { name: 'VISION_AGENT_API_KEY', secretRef: 'ade-api-key' }
          { name: 'ACA_SERVICE_NAME',     value: 'ca-${prefix}-ade-mcp-${env}' }
          { name: 'ADE_MODEL',            value: 'dpt-2-latest' }
        ])
      }]
      scale: { minReplicas: 1, maxReplicas: 3 }
    }
  }
}

// ── Build Agent ACA Job (caj-ipai-build-agent-prd) ───────────
// Event-driven: triggers on ADO pipeline job pickup
resource buildAgent 'Microsoft.App/jobs@2024-03-01' = {
  name:     'caj-${prefix}-build-agent-${env}'
  location: location
  tags: union(tags, { 'azd-service-name': 'build-agent' })
  identity:  commonIdentity
  properties: {
    environmentId: acaeId
    configuration: {
      triggerType:      'Event'
      replicaTimeout:   1800          // 30-minute job timeout
      replicaRetryLimit: 1
      eventTriggerConfig: {
        replicaCompletionCount: 1
        parallelism:            1
        scale: {
          minExecutions: 0
          maxExecutions: 5
          rules: [{
            name: 'ado-pipeline-scale'
            type: 'azure-pipelines'
            metadata: {
              poolName:         'ipai-build-agent'
              targetPipelinesQueueLength: '1'
            }
          }]
        }
      }
      registries: commonRegistry
      secrets:    commonSecrets
    }
    template: {
      containers: [{
        name:  'build-agent'
        image: '${acrLoginServer}/ipai-build-agent:${odooImageTag}'
        resources: { cpu: '2.0', memory: '4Gi' }
        env: union(commonEnv, [
          { name: 'ACA_SERVICE_NAME', value: 'caj-${prefix}-build-agent-${env}' }
          { name: 'ACR_ENDPOINT',     value: acrLoginServer }
        ])
      }]
    }
  }
}

// ── Outputs ────────────────────────────────────────────────────
output odooWebFqdn          string = odooWeb.properties.configuration.ingress.fqdn
output odooWebName          string = odooWeb.name
output releaseManagerName   string = releaseManager.name
output adeMcpName           string = adeMcp.name
output buildAgentName       string = buildAgent.name
