// =============================================================================
// managed-devops-pool.bicep — Managed DevOps Pool for Azure Pipelines
// =============================================================================
// Provisions a fully Azure-managed build agent pool.
// Replaces MS-hosted parallel job billing (which requires portal-only setup).
// Uses Microsoft.DevOpsInfrastructure/pools — IaC-native, no free tier.
// =============================================================================

targetScope = 'resourceGroup'

// ---------------------------------------------------------------------------
// Parameters
// ---------------------------------------------------------------------------

@minLength(3)
@maxLength(44)
@description('Name of the Managed DevOps Pool')
param poolName string

@maxLength(26)
@description('Name of the Dev Center')
param devCenterName string

@description('Name of the Dev Center project')
param devCenterProjectName string

@description('Azure DevOps organization URL')
param adoOrgUrl string

@description('VM image to use for agents')
param imageName string = 'ubuntu-24.04'

@description('Maximum concurrent agents')
param maxConcurrency int = 1

@description('Azure region')
param location string = resourceGroup().location

@description('VM SKU for agents')
param vmSku string = 'Standard_D2ads_v5'

@description('Resource tags')
param tags object = {}

// ---------------------------------------------------------------------------
// Dev Center + Project (required dependencies)
// ---------------------------------------------------------------------------

resource devCenter 'Microsoft.DevCenter/devcenters@2025-02-01' = {
  name: devCenterName
  location: location
  tags: tags
}

resource devCenterProject 'Microsoft.DevCenter/projects@2025-02-01' = {
  name: devCenterProjectName
  location: location
  tags: tags
  properties: {
    devCenterId: devCenter.id
  }
}

// ---------------------------------------------------------------------------
// Managed DevOps Pool
// ---------------------------------------------------------------------------

resource pool 'Microsoft.DevOpsInfrastructure/pools@2025-01-21' = {
  name: poolName
  location: location
  tags: union(tags, { purpose: 'azure-pipelines-agents' })
  properties: {
    organizationProfile: {
      organizations: [
        {
          url: adoOrgUrl
          parallelism: maxConcurrency
        }
      ]
      permissionProfile: {
        kind: 'CreatorOnly'
      }
      kind: 'AzureDevOps'
    }
    devCenterProjectResourceId: devCenterProject.id
    maximumConcurrency: maxConcurrency
    agentProfile: {
      kind: 'Stateless'
    }
    fabricProfile: {
      sku: {
        name: vmSku
      }
      images: [
        {
          wellKnownImageName: imageName
          buffer: '*'
        }
      ]
      kind: 'Vmss'
    }
  }
}

// ---------------------------------------------------------------------------
// Outputs
// ---------------------------------------------------------------------------

output poolName string = pool.name
output poolId string = pool.id
output devCenterName string = devCenter.name
output devCenterProjectName string = devCenterProject.name
