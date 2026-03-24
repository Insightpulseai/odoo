# aca-private-networking -- Worked Examples

## Example 1: VNet with ACA and PG Subnets (Bicep)

```bicep
resource vnet 'Microsoft.Network/virtualNetworks@2023-11-01' = {
  name: 'vnet-ipai-dev'
  location: location
  properties: {
    addressSpace: { addressPrefixes: ['10.0.0.0/16'] }
    subnets: [
      {
        name: 'snet-aca'
        properties: {
          addressPrefix: '10.0.0.0/23'   // /23 minimum for ACA
          delegations: [
            {
              name: 'aca-delegation'
              properties: {
                serviceName: 'Microsoft.App/environments'
              }
            }
          ]
        }
      }
      {
        name: 'snet-pg'
        properties: {
          addressPrefix: '10.0.2.0/24'
          networkSecurityGroup: { id: nsgPostgres.id }
          delegations: [
            {
              name: 'pg-delegation'
              properties: {
                serviceName: 'Microsoft.DBforPostgreSQL/flexibleServers'
              }
            }
          ]
        }
      }
    ]
  }
}
```

## Example 2: NSG Restricting PG to ACA Subnet

```bicep
resource nsgPostgres 'Microsoft.Network/networkSecurityGroups@2023-11-01' = {
  name: 'nsg-ipai-dev-pg'
  location: location
  properties: {
    securityRules: [
      {
        name: 'AllowACAToPostgres'
        properties: {
          priority: 100
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourceAddressPrefix: '10.0.0.0/23'   // snet-aca CIDR
          sourcePortRange: '*'
          destinationAddressPrefix: '10.0.2.0/24'
          destinationPortRange: '5432'
        }
      }
      {
        name: 'DenyAllInbound'
        properties: {
          priority: 4096
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
```

## Example 3: PG Flexible Server with VNet Integration

```bicep
resource postgresServer 'Microsoft.DBforPostgreSQL/flexibleServers@2023-12-01-preview' = {
  name: pgServerName
  location: location
  properties: {
    version: '16'
    network: {
      delegatedSubnetResourceId: vnet.properties.subnets[1].id  // snet-pg
      privateDnsZoneArmResourceId: privateDnsZone.id
      publicNetworkAccess: 'Disabled'
    }
    // ... other properties
  }
}

resource privateDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' = {
  name: 'ipai-dev.private.postgres.database.azure.com'
  location: 'global'
}
```

## Example 4: ACA Environment with VNet

```bicep
resource acaEnv 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: 'ipai-odoo-dev-env'
  location: location
  properties: {
    vnetConfiguration: {
      infrastructureSubnetId: vnet.properties.subnets[0].id  // snet-aca
      internal: false   // false = public ingress via Front Door; true = internal only
    }
    zoneRedundant: true
  }
}
```

## Example 5: MCP Query Sequence

```
Step 1: microsoft_docs_search("Azure Container Apps VNet integration internal environment")
Result: ACA supports custom VNet with infrastructure subnet (/23 min).
        Internal environments have no public IP. External environments get
        a public IP but can be front-ended by Front Door.

Step 2: microsoft_docs_search("Azure PostgreSQL Flexible Server private endpoint VNet")
Result: PG Flex supports VNet integration (delegated subnet) OR private
        endpoint. VNet integration is simpler for single-VNet topologies.
        Requires private DNS zone.

Step 3: microsoft_docs_search("Azure NSG rules deny public access PostgreSQL subnet")
Result: Apply NSG to PG subnet. Allow 5432 from ACA subnet only. Deny-all
        as last rule. PG VNet integration already blocks public access when
        publicNetworkAccess is Disabled.
```
