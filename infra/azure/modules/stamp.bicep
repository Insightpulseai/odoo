// =============================================================================
// stamp.bicep — Pulser Deployment Stamp Orchestration
// =============================================================================
// A "Stamp" is the canonical unit of scale and isolation (BOM 8).
// Each stamp is a self-contained slice of the platform.
// =============================================================================

targetScope = 'resourceGroup'

@description('Unique identifier for this stamp (e.g. 00, 01, 02)')
param stampId string

@description('Rollout group this stamp belongs to')
@allowed(['canary', 'early-adopter', 'general-availability'])
param rolloutGroup string = 'early-adopter'

@description('Azure region for the stamp resources')
param location string = resourceGroup().location

@description('Environment name')
@allowed(['dev', 'staging', 'prod'])
param environment string = 'prod'

@description('Base name for resource prefixing')
param baseName string = 'ipai'

@description('Container Apps Environment name where the apps will reside')
param acaEnvironmentName string

@description('Container registry server')
param containerRegistryServer string

@description('Managed identity resource ID for services')
param managedIdentityResourceId string

@description('Key Vault name for secrets')
param keyVaultName string

@description('Revision labeling for progressive rollout')
param revisionLabel string = 'latest'

@description('Odoo container image tag')
param odooImageTag string = 'latest'

// Variables
var resourcePrefix = '${baseName}-${environment}-s${stampId}'
var tags = {
  Environment: environment
  Project: 'InsightPulse AI'
  Stamp: stampId
  RolloutGroup: rolloutGroup
  ManagedBy: 'Bicep'
}

// 1. Dedicated PostgreSQL Flexible Server for the Stamp
module postgres 'postgres-flexible.bicep' = {
  name: '${resourcePrefix}-pg-deploy'
  params: {
    serverName: '${resourcePrefix}-pg'
    location: location
    skuName: 'Standard_B1ms' // Stamp-size default
    tier: 'Burstable'
    storageSizeGB: 32
    tags: tags
  }
}

// 2. Dedicated Storage Account for Odoo Evidence (Odoo Documents)
module storage 'storage.bicep' = {
  name: '${resourcePrefix}-st-deploy'
  params: {
    storageAccountName: replace('${resourcePrefix}docs', '-', '')
    location: location
    tags: tags
  }
}

// 3. Odoo ACA Services (Web, Worker, Cron)
module odoo 'aca-odoo-services.bicep' = {
  name: '${resourcePrefix}-odoo-deploy'
  params: {
    environmentName: acaEnvironmentName
    containerRegistryServer: containerRegistryServer
    managedIdentityResourceId: managedIdentityResourceId
    keyVaultName: keyVaultName
    postgresHost: postgres.outputs.serverFqdn
    postgresDb: 'odoo'
    imageTag: odooImageTag
    revisionSuffix: revisionLabel
    tags: tags
  }
}

// Outputs
output stampId string = stampId
output rolloutGroup string = rolloutGroup
output odooWebFqdn string = odoo.outputs.odooWebFqdn
output postgresHost string = postgres.outputs.serverFqdn
output storageAccountName string = storage.outputs.storageAccountName
