// Azure Database for PostgreSQL Flexible Server module for Odoo

@description('Server name (must be globally unique)')
param serverName string

@description('Azure region')
param location string

@description('Resource tags')
param tags object

@description('PostgreSQL version')
@allowed(['14', '15', '16'])
param postgresVersion string = '16'

@description('Compute tier')
@allowed(['Burstable', 'GeneralPurpose', 'MemoryOptimized'])
param tier string = 'Burstable'

@description('Compute SKU name')
param skuName string = 'Standard_B1ms'

@description('Storage size in GB')
param storageSizeGB int = 32

@description('Administrator login name')
param adminLogin string = 'odoo_admin'

@secure()
@description('Administrator password (use Key Vault reference in production)')
param adminPassword string

@description('Database name to create')
param databaseName string = 'odoo'

@description('Subnet ID for VNet integration (empty for public access)')
param subnetId string = ''

resource server 'Microsoft.DBforPostgreSQL/flexibleServers@2023-06-01-preview' = {
  name: serverName
  location: location
  tags: tags
  sku: {
    name: skuName
    tier: tier
  }
  properties: {
    version: postgresVersion
    administratorLogin: adminLogin
    administratorLoginPassword: adminPassword
    storage: {
      storageSizeGB: storageSizeGB
      autoGrow: 'Enabled'
    }
    backup: {
      backupRetentionDays: 7
      geoRedundantBackup: 'Disabled'
    }
    highAvailability: {
      mode: 'Disabled'
    }
    network: subnetId != '' ? {
      delegatedSubnetResourceId: subnetId
    } : {}
  }
}

resource database 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2023-06-01-preview' = {
  parent: server
  name: databaseName
  properties: {
    charset: 'UTF8'
    collation: 'en_US.utf8'
  }
}

// Allow Azure services (Container Apps) to connect
resource firewallRule 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2023-06-01-preview' = if (subnetId == '') {
  parent: server
  name: 'AllowAzureServices'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

// Odoo-optimized PostgreSQL parameters
resource maxConnections 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2023-06-01-preview' = {
  parent: server
  name: 'max_connections'
  properties: {
    value: '100'
    source: 'user-override'
  }
}

resource sharedBuffers 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2023-06-01-preview' = {
  parent: server
  name: 'shared_buffers'
  properties: {
    value: '131072'
    source: 'user-override'
  }
}

output serverName string = server.name
output serverFqdn string = server.properties.fullyQualifiedDomainName
output serverId string = server.id
output databaseName string = database.name
