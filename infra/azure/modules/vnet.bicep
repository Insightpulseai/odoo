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

// NSG for ACA subnet — allow inbound HTTPS, outbound to PG
resource nsgAca 'Microsoft.Network/networkSecurityGroups@2023-09-01' = {
  name: '${vnetName}-nsg-aca'
  location: location
  tags: tags
  properties: {
    securityRules: [
      {
        name: 'AllowHttpsInbound'
        properties: {
          priority: 100
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourceAddressPrefix: 'Internet'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '443'
        }
      }
      {
        name: 'AllowPostgresOutbound'
        properties: {
          priority: 100
          direction: 'Outbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: '10.0.2.0/24'
          destinationPortRange: '5432'
        }
      }
    ]
  }
}

// NSG for PostgreSQL subnet — allow inbound 5432 only from ACA subnet
resource nsgPostgres 'Microsoft.Network/networkSecurityGroups@2023-09-01' = {
  name: '${vnetName}-nsg-postgres'
  location: location
  tags: tags
  properties: {
    securityRules: [
      {
        name: 'AllowPostgresFromAca'
        properties: {
          priority: 100
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourceAddressPrefix: '10.0.1.0/24'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '5432'
        }
      }
      {
        name: 'DenyAllOtherInbound'
        properties: {
          priority: 4000
          direction: 'Inbound'
          access: 'Deny'
          protocol: '*'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '*'
        }
      }
    ]
  }
}

// NSG for integration subnet (default deny, no custom rules needed yet)
resource nsgIntegration 'Microsoft.Network/networkSecurityGroups@2023-09-01' = {
  name: '${vnetName}-nsg-integration'
  location: location
  tags: tags
  properties: {
    securityRules: []
  }
}

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
          networkSecurityGroup: subnet.name == 'snet-aca' ? { id: nsgAca.id } : subnet.name == 'snet-postgres' ? { id: nsgPostgres.id } : subnet.name == 'snet-integration' ? { id: nsgIntegration.id } : null
        }
      }
    ]
  }
}

output vnetId string = vnet.id
output vnetName string = vnet.name
