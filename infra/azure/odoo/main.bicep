// ==========================================================================
// Odoo-only Azure footprint — main stack
// ==========================================================================
//
// Scope: Odoo runtime on ACA only.
// Does NOT own: Databricks, non-Odoo apps, shared platform resources.
//
// Design rules:
//   1. Existing canonical resource names are reused, never renamed.
//   2. One tag contract applied to every managed resource.
//   3. Cross-sub resources (PG, ACR) are referenced by FQDN, not managed.
//
// SSOT: ssot/azure/odoo-footprint.yaml
// ==========================================================================

targetScope = 'resourceGroup'

// ---------------------------------------------------------------------------
// Parameters
// ---------------------------------------------------------------------------

@description('Location — inherits from the target resource group')
param location string = resourceGroup().location

@description('Canonical tag contract applied to all resources')
param tags object

@description('Existing ACA environment name (in this RG)')
param acaEnvironmentName string

@description('PostgreSQL FQDN (cross-sub, referenced not managed)')
param postgresFqdn string

@description('Database name')
param dbName string = 'odoo'

@description('Database user')
param dbUser string = 'odoo_admin'

@description('Key Vault URI (pre-resolved, avoids cross-RG scope)')
param keyVaultUri string

@description('Existing Log Analytics workspace name (in this RG)')
param logAnalyticsWorkspaceName string

@description('Existing user-assigned managed identity name (in this RG)')
param managedIdentityName string

@description('Odoo app names')
param webAppName string
param workerAppName string
param cronAppName string

@description('Container image for Odoo runtime')
param odooImage string

@description('ACA target port')
param targetPort int = 8069

@description('CPU/memory sizing')
param webCpu string = '2.0'
param webMemory string = '4Gi'
param workerCpu string = '1.0'
param workerMemory string = '2Gi'
param cronCpu string = '0.5'
param cronMemory string = '1Gi'

// ---------------------------------------------------------------------------
// Reference modules — existing resources, read-only
// ---------------------------------------------------------------------------

module acaEnv './modules/aca-env.bicep' = {
  name: 'ref-aca-env'
  params: {
    environmentName: acaEnvironmentName
  }
}

module monitoring './modules/monitoring-ref.bicep' = {
  name: 'ref-monitoring'
  params: {
    logAnalyticsWorkspaceName: logAnalyticsWorkspaceName
  }
}

module mi './modules/managed-identity-ref.bicep' = {
  name: 'ref-managed-identity'
  params: {
    managedIdentityName: managedIdentityName
  }
}

// ---------------------------------------------------------------------------
// Odoo ACA apps — the only resources this stack manages
// ---------------------------------------------------------------------------

module apps './modules/aca-odoo-apps.bicep' = {
  name: 'odoo-apps'
  params: {
    location: location
    tags: tags
    acaEnvironmentId: acaEnv.outputs.id
    odooImage: odooImage
    webAppName: webAppName
    workerAppName: workerAppName
    cronAppName: cronAppName
    enableExternalIngress: true
    targetPort: targetPort
    webCpu: webCpu
    webMemory: webMemory
    workerCpu: workerCpu
    workerMemory: workerMemory
    cronCpu: cronCpu
    cronMemory: cronMemory
    userAssignedIdentityId: mi.outputs.identityId
    keyVaultUri: keyVaultUri
    postgresFqdn: postgresFqdn
    dbName: dbName
    dbUser: dbUser
  }
}

// ---------------------------------------------------------------------------
// Outputs
// ---------------------------------------------------------------------------

output webFqdn string = apps.outputs.webFqdn
output webAppName string = webAppName
output workerAppName string = workerAppName
output cronAppName string = cronAppName
output postgresHost string = postgresFqdn
output keyVaultUri string = keyVaultUri
output managedIdentityClientId string = mi.outputs.clientId
