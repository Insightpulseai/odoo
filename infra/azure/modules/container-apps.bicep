// Azure Container Apps Environment + 9 service apps
// Consumption plan, internal ingress (Front Door handles public traffic)
// InsightPulse AI stack: Odoo (web/worker/cron), n8n, MCP, Superset, Plane, Shelf, CRM

// ---------------------------------------------------------------------------
// Parameters
// ---------------------------------------------------------------------------

@description('Azure region for resources')
param location string = resourceGroup().location

@description('Resource tags')
param tags object

@description('Name of the Container Apps Environment')
param environmentName string

@description('Log Analytics workspace resource ID')
param logAnalyticsWorkspaceId string

@description('Container registry login server (e.g. myregistry.azurecr.io)')
param containerRegistryServer string

@description('Container registry username')
@secure()
param containerRegistryUsername string

@description('Container registry password')
@secure()
param containerRegistryPassword string

@description('Odoo container image (use #{odooImage}# for CI/CD replacement)')
param odooImage string

@description('n8n container image')
param n8nImage string

@description('MCP Gateway container image')
param mcpImage string

@description('Superset container image')
param supersetImage string

@description('Plane container image')
param planeImage string

@description('Shelf container image')
param shelfImage string

@description('CRM container image')
param crmImage string

@description('PostgreSQL host (Key Vault reference or direct)')
@secure()
param databaseHost string

@description('PostgreSQL database name')
param databaseName string

@description('PostgreSQL user')
@secure()
param databaseUser string

@description('PostgreSQL password')
@secure()
param databasePassword string

@description('Enable VNet integration for internal-only ingress')
param vnetSubnetId string = ''

// ---------------------------------------------------------------------------
// Variables
// ---------------------------------------------------------------------------

var logAnalyticsCustomerId = reference(logAnalyticsWorkspaceId, '2023-09-01').customerId
var logAnalyticsSharedKey = listKeys(logAnalyticsWorkspaceId, '2023-09-01').primarySharedKey

var registryConfig = [
  {
    server: containerRegistryServer
    username: containerRegistryUsername
    passwordSecretRef: 'registry-password'
  }
]

var sharedSecrets = [
  { name: 'registry-password', value: containerRegistryPassword }
  { name: 'db-host', value: databaseHost }
  { name: 'db-user', value: databaseUser }
  { name: 'db-password', value: databasePassword }
]

var sharedEnv = [
  { name: 'DATABASE_HOST', secretRef: 'db-host' }
  { name: 'DATABASE_NAME', value: databaseName }
  { name: 'DATABASE_USER', secretRef: 'db-user' }
  { name: 'DATABASE_PASSWORD', secretRef: 'db-password' }
]

// Service definitions — central config for all 9 apps
var services = [
  {
    name: 'odoo-web'
    image: odooImage
    port: 8069
    healthPath: '/web/health'
    cpu: '1.0'
    memory: '2Gi'
    minReplicas: 1
    maxReplicas: 3
    command: []
    extraEnv: []
  }
  {
    name: 'odoo-worker'
    image: odooImage
    port: 8069
    healthPath: '/web/health'
    cpu: '0.5'
    memory: '1Gi'
    minReplicas: 1
    maxReplicas: 2
    command: [
      'odoo'
      '--no-http'
      '--workers=2'
    ]
    extraEnv: []
  }
  {
    name: 'odoo-cron'
    image: odooImage
    port: 8069
    healthPath: '/web/health'
    cpu: '0.5'
    memory: '1Gi'
    minReplicas: 1
    maxReplicas: 1
    command: [
      'odoo'
      '--no-http'
      '--max-cron-threads=2'
    ]
    extraEnv: []
  }
  {
    name: 'n8n'
    image: n8nImage
    port: 5678
    healthPath: '/healthz'
    cpu: '0.5'
    memory: '1Gi'
    minReplicas: 1
    maxReplicas: 2
    command: []
    extraEnv: []
  }
  {
    name: 'mcp-gateway'
    image: mcpImage
    port: 8766
    healthPath: '/healthz'
    cpu: '0.5'
    memory: '1Gi'
    minReplicas: 1
    maxReplicas: 2
    command: []
    extraEnv: []
  }
  {
    name: 'superset'
    image: supersetImage
    port: 8088
    healthPath: '/health'
    cpu: '0.5'
    memory: '1Gi'
    minReplicas: 1
    maxReplicas: 2
    command: []
    extraEnv: []
  }
  {
    name: 'plane'
    image: planeImage
    port: 3000
    healthPath: '/'
    cpu: '0.5'
    memory: '1Gi'
    minReplicas: 1
    maxReplicas: 1
    command: []
    extraEnv: []
  }
  {
    name: 'shelf'
    image: shelfImage
    port: 3000
    healthPath: '/healthcheck'
    cpu: '0.5'
    memory: '1Gi'
    minReplicas: 1
    maxReplicas: 1
    command: []
    extraEnv: []
  }
  {
    name: 'crm'
    image: crmImage
    port: 3000
    healthPath: '/'
    cpu: '0.5'
    memory: '1Gi'
    minReplicas: 1
    maxReplicas: 1
    command: []
    extraEnv: []
  }
]

// ---------------------------------------------------------------------------
// Container Apps Environment — Consumption plan
// ---------------------------------------------------------------------------

resource environment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: environmentName
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalyticsCustomerId
        sharedKey: logAnalyticsSharedKey
      }
    }
    vnetConfiguration: vnetSubnetId != '' ? {
      infrastructureSubnetId: vnetSubnetId
      internal: true
    } : null
    zoneRedundant: false
    workloadProfiles: [
      {
        name: 'Consumption'
        workloadProfileType: 'Consumption'
      }
    ]
  }
}

// ---------------------------------------------------------------------------
// Container Apps — 9 services (loop-based deployment)
// ---------------------------------------------------------------------------

resource containerApps 'Microsoft.App/containerApps@2024-03-01' = [
  for svc in services: {
    name: svc.name
    location: location
    tags: tags
    properties: {
      environmentId: environment.id
      workloadProfileName: 'Consumption'
      configuration: {
        activeRevisionsMode: 'Single'
        ingress: {
          external: false
          targetPort: svc.port
          transport: 'http'
          allowInsecure: false
        }
        registries: registryConfig
        secrets: sharedSecrets
      }
      template: {
        containers: [
          {
            name: svc.name
            image: svc.image
            command: length(svc.command) > 0 ? svc.command : null
            resources: {
              cpu: json(svc.cpu)
              memory: svc.memory
            }
            env: concat(sharedEnv, svc.extraEnv)
            probes: [
              {
                type: 'Liveness'
                httpGet: {
                  path: svc.healthPath
                  port: svc.port
                  scheme: 'HTTP'
                }
                initialDelaySeconds: 30
                periodSeconds: 30
                failureThreshold: 3
                timeoutSeconds: 5
              }
              {
                type: 'Readiness'
                httpGet: {
                  path: svc.healthPath
                  port: svc.port
                  scheme: 'HTTP'
                }
                initialDelaySeconds: 10
                periodSeconds: 10
                failureThreshold: 3
                timeoutSeconds: 5
              }
            ]
          }
        ]
        scale: {
          minReplicas: svc.minReplicas
          maxReplicas: svc.maxReplicas
          rules: svc.maxReplicas > 1 ? [
            {
              name: 'http-scaling'
              http: {
                metadata: {
                  concurrentRequests: '50'
                }
              }
            }
          ] : []
        }
      }
    }
  }
]

// ---------------------------------------------------------------------------
// Outputs
// ---------------------------------------------------------------------------

@description('Container Apps Environment resource ID')
output environmentId string = environment.id
@description('Container Apps Environment default domain (FQDN suffix)')
output environmentDefaultDomain string = environment.properties.defaultDomain

@description('Container Apps Environment static IP (for DNS / Front Door origin)')
output environmentStaticIp string = environment.properties.staticIp

@description('Individual app FQDNs keyed by service name')
output appFqdns array = [
  for (svc, i) in services: {
    name: svc.name
    fqdn: containerApps[i].properties.configuration.ingress.fqdn
  }
]

@description('Odoo web app FQDN (primary origin for Front Door)')
output odooWebFqdn string = containerApps[0].properties.configuration.ingress.fqdn

@description('n8n app FQDN')
output n8nFqdn string = containerApps[3].properties.configuration.ingress.fqdn

@description('MCP Gateway app FQDN')
output mcpGatewayFqdn string = containerApps[4].properties.configuration.ingress.fqdn
