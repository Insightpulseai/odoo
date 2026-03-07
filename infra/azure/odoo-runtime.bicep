// Odoo 19 CE Runtime — Azure Infrastructure
// Deploys: ACR + Container Apps + PostgreSQL Flexible Server + Key Vault
// SSOT: docs/ops/AZURE_ODOO_AUTOMATION.md

targetScope = 'resourceGroup'

@description('Environment name')
@allowed(['dev', 'staging', 'prod'])
param environment string = 'dev'

@description('Azure region for resources')
param location string = resourceGroup().location

@description('Base name for resources')
param baseName string = 'ipai-odoo'

@description('ACR SKU')
@allowed(['Basic', 'Standard', 'Premium'])
param acrSku string = 'Basic'

@description('PostgreSQL admin login')
param pgAdminLogin string = 'odoo_admin'

@secure()
@description('PostgreSQL admin password')
param pgAdminPassword string

@description('PostgreSQL SKU')
param pgSkuName string = 'Standard_B1ms'

@description('PostgreSQL compute tier')
@allowed(['Burstable', 'GeneralPurpose', 'MemoryOptimized'])
param pgTier string = 'Burstable'

@description('PostgreSQL storage size in GB')
param pgStorageSizeGB int = 32

@description('Container App CPU cores')
param containerCpu string = '1.0'

@description('Container App memory')
param containerMemory string = '2Gi'

@description('Minimum container replicas')
param minReplicas int = 1

@description('Maximum container replicas')
param maxReplicas int = 3

// Variables
var resourcePrefix = '${baseName}-${environment}'
var acrName = replace('${baseName}${environment}acr', '-', '')
var tags = {
  Environment: environment
  Project: 'IPAI Odoo Runtime'
  ManagedBy: 'Bicep'
  Stack: 'Odoo 19 CE'
}

// Key Vault for secrets
module keyVault 'modules/keyvault.bicep' = {
  name: 'odooKeyVaultDeployment'
  params: {
    keyVaultName: '${resourcePrefix}-kv'
    location: location
    tags: tags
  }
}

// Azure Container Registry
module acr 'modules/acr.bicep' = {
  name: 'odooAcrDeployment'
  params: {
    acrName: acrName
    location: location
    tags: tags
    sku: acrSku
  }
}

// PostgreSQL Flexible Server
module postgres 'modules/postgres-flexible.bicep' = {
  name: 'odooPostgresDeployment'
  params: {
    serverName: '${resourcePrefix}-pg'
    location: location
    tags: tags
    postgresVersion: '16'
    tier: pgTier
    skuName: pgSkuName
    storageSizeGB: pgStorageSizeGB
    adminLogin: pgAdminLogin
    adminPassword: pgAdminPassword
    databaseName: 'odoo'
  }
}

// Container Apps Environment + Odoo Container App
module containerApps 'modules/container-apps.bicep' = {
  name: 'odooContainerAppsDeployment'
  params: {
    environmentName: '${resourcePrefix}-env'
    appName: '${resourcePrefix}-app'
    location: location
    tags: tags
    acrLoginServer: acr.outputs.acrLoginServer
    containerImage: 'odoo:latest'
    cpu: containerCpu
    memory: containerMemory
    minReplicas: minReplicas
    maxReplicas: maxReplicas
  }
}

// Grant Container App identity ACR pull access
resource acrPullRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(acr.outputs.acrId, containerApps.outputs.appPrincipalId, 'acrpull')
  scope: resourceGroup()
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')
    principalId: containerApps.outputs.appPrincipalId
    principalType: 'ServicePrincipal'
  }
}

// Outputs
output acrLoginServer string = acr.outputs.acrLoginServer
output acrName string = acr.outputs.acrName
output containerAppFqdn string = containerApps.outputs.appFqdn
output containerAppName string = containerApps.outputs.appName
output postgresServerFqdn string = postgres.outputs.serverFqdn
output postgresDatabaseName string = postgres.outputs.databaseName
output keyVaultName string = keyVault.outputs.keyVaultName
output keyVaultUri string = keyVault.outputs.keyVaultUri
