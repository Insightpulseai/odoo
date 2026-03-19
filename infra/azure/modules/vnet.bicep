// Azure Virtual Network module
// VNet with subnets for Odoo ACA, Databricks, and integration services

@description('Name of the Virtual Network')
param vnetName string

@description('Azure region')
param location string

@description('Resource tags')
param tags object

@description('VNet address prefix')
param addressPrefix string = '10.0.0.0/16'

@description('Subnet definitions')
param subnets array = [
  {
    name: 'snet-aca'
    addressPrefix: '10.0.1.0/24'
    delegations: [
      {
        name: 'Microsoft.App.environments'
        properties: {
          serviceName: 'Microsoft.App/environments'
        }
      }
    ]
  }
  {
    name: 'snet-postgres'
    addressPrefix: '10.0.2.0/24'
    delegations: [
      {
        name: 'Microsoft.DBforPostgreSQL.flexibleServers'
        properties: {
          serviceName: 'Microsoft.DBforPostgreSQL/flexibleServers'
        }
      }
    ]
  }
  {
    name: 'snet-databricks-public'
    addressPrefix: '10.0.3.0/24'
    delegations: [
      {
        name: 'Microsoft.Databricks.workspaces'
        properties: {
          serviceName: 'Microsoft.Databricks/workspaces'
        }
      }
    ]
  }
  {
    name: 'snet-databricks-private'
    addressPrefix: '10.0.4.0/24'
    delegations: [
      {
        name: 'Microsoft.Databricks.workspaces'
        properties: {
          serviceName: 'Microsoft.Databricks/workspaces'
        }
      }
    ]
  }
  {
    name: 'snet-integration'
    addressPrefix: '10.0.5.0/24'
    delegations: []
  }
]

resource vnet 'Microsoft.Network/virtualNetworks@2023-09-01' = {
  name: vnetName
  location: location
  tags: tags
  properties: {
    addressSpace: {
      addressPrefixes: [
        addressPrefix
      ]
    }
    subnets: [
      for subnet in subnets: {
        name: subnet.name
        properties: {
          addressPrefix: subnet.addressPrefix
          delegations: subnet.delegations
        }
      }
    ]
  }
}

output vnetId string = vnet.id
output vnetName string = vnet.name
