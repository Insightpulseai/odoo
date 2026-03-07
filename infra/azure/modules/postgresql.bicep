// PostgreSQL Flexible Server (v16, HA)

@description('Name of the PostgreSQL server')
param serverName string

@description('Azure region')
param location string

@description('Resource tags')
param tags object

@description('Administrator login name')
param administratorLogin string = 'odoo_admin'

@description('Administrator login password')
@secure()
param administratorPassword string

@description('Key Vault name for storing secrets')
param keyVaultName string

@description('PostgreSQL SKU name')
param skuName string = 'Standard_D2ds_v4'

@description('Storage size in GB')
param storageSizeGB int = 128

@description('High availability mode')
@allowed(['Disabled', 'ZoneRedundant', 'SameZone'])
param haMode string = 'ZoneRedundant'

// PostgreSQL Flexible Server
resource postgresServer 'Microsoft.DBforPostgreSQL/flexibleServers@2023-03-01-preview' = {
  name: serverName
  location: location
  tags: tags
  sku: {
    name: skuName
    tier: 'GeneralPurpose'
  }
  properties: {
    version: '16'
    administratorLogin: administratorLogin
    administratorLoginPassword: administratorPassword
    storage: {
      storageSizeGB: storageSizeGB
    }
    backup: {
      backupRetentionDays: 35
      geoRedundantBackup: 'Enabled'
    }
    highAvailability: {
      mode: haMode
    }
    network: {
      publicNetworkAccess: 'Enabled'
    }
  }
}

// SSL enforcement configuration
resource sslConfig 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2023-03-01-preview' = {
  parent: postgresServer
  name: 'require_secure_transport'
  properties: {
    value: 'on'
    source: 'user-override'
  }
}

// Database: odoo
resource odooDatabase 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2023-03-01-preview' = {
  parent: postgresServer
  name: 'odoo'
  properties: {
    charset: 'UTF8'
    collation: 'en_US.utf8'
  }
}

// Firewall rule: Allow Azure services
resource firewallAllowAzure 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2023-03-01-preview' = {
  parent: postgresServer
  name: 'AllowAzureServices'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

// Store admin password in Key Vault
resource existingKeyVault 'Microsoft.KeyVault/vaults@2023-07-01' existing = {
  name: keyVaultName
}

resource pgPasswordSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: existingKeyVault
  name: 'postgres-admin-password'
  properties: {
    value: administratorPassword
    contentType: 'text/plain'
  }
}

output serverFqdn string = postgresServer.properties.fullyQualifiedDomainName
output serverId string = postgresServer.id
output databaseName string = odooDatabase.name
