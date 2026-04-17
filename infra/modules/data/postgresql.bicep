// modules/data/postgresql.bicep
// Creates: pg-ipai-odoo-prd (PostgreSQL 16 Flexible Server)
// Databases: odoo | odoo_staging | odoo_dev
// Entra auth enabled; local auth disabled post-bootstrap
// wal_level=logical enables Fabric CDC mirroring (T-003 prerequisite)
targetScope = 'resourceGroup'

param prefix            string
param env               string
param location          string
param tags              object
@secure()
param adminLogin        string
@secure()
param adminPassword     string
param miPrincipalId     string
param keyVaultName      string
param keyVaultRgName    string

@description('PostgreSQL SKU — Burstable B2s for dev, General Purpose D4s for prd')
param skuName    string = 'Standard_D4s_v3'
param skuTier    string = 'GeneralPurpose'
param storageSizeGB int = 128

var pgName = 'pg-${prefix}-odoo-${env}'

// ── PostgreSQL Flexible Server ────────────────────────────────
resource pg 'Microsoft.DBforPostgreSQL/flexibleServers@2024-08-01' = {
  name:     pgName
  location: location
  tags:     tags
  sku: {
    name: skuName
    tier: skuTier
  }
  properties: {
    version:              '16'
    administratorLogin:        adminLogin
    administratorLoginPassword: adminPassword
    storage: {
      storageSizeGB:     storageSizeGB
      autoGrow:          'Enabled'
    }
    backup: {
      backupRetentionDays:   14
      geoRedundantBackup:    env == 'prd' ? 'Enabled' : 'Disabled'
    }
    highAvailability: {
      mode: env == 'prd' ? 'ZoneRedundant' : 'Disabled'
    }
    maintenanceWindow: {
      customWindow: 'Enabled'
      dayOfWeek:    0   // Sunday
      startHour:    2   // 2am local
      startMinute:  0
    }
    authConfig: {
      // Entra auth + password — disable local auth after first Entra login
      activeDirectoryAuth: 'Enabled'
      passwordAuth:        'Enabled'
      tenantId:            subscription().tenantId
    }
  }
}

// ── PG Configuration ─────────────────────────────────────────
// wal_level=logical: required for Fabric CDC mirroring (T-003)
resource pgParamWalLevel 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2024-08-01' = {
  name:   'wal_level'
  parent: pg
  properties: {
    value:  'logical'
    source: 'user-override'
  }
}
// PgBouncer connection pooling (T-004)
resource pgParamPgBouncer 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2024-08-01' = {
  name:   'pgbouncer.enabled'
  parent: pg
  properties: {
    value:  'True'
    source: 'user-override'
  }
}
resource pgParamMaxConn 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2024-08-01' = {
  name:   'max_connections'
  parent: pg
  properties: {
    value:  '200'
    source: 'user-override'
  }
}
// pg_stat_statements for query performance monitoring
resource pgParamStatStatements 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2024-08-01' = {
  name:   'shared_preload_libraries'
  parent: pg
  properties: {
    value:  'pg_stat_statements,pgaudit'
    source: 'user-override'
  }
}

// ── Databases ─────────────────────────────────────────────────
resource dbOdoo 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2024-08-01' = {
  name:   'odoo'
  parent: pg
  properties: {
    charset:   'utf8'
    collation: 'en_US.utf8'
  }
}
resource dbOdooStaging 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2024-08-01' = {
  name:   'odoo_staging'
  parent: pg
  properties: {
    charset:   'utf8'
    collation: 'en_US.utf8'
  }
}
resource dbOooDev 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2024-08-01' = {
  name:   'odoo_dev'
  parent: pg
  properties: {
    charset:   'utf8'
    collation: 'en_US.utf8'
  }
}

// ── Entra admin assignment (IPAI MI) ──────────────────────────
resource pgEntraAdmin 'Microsoft.DBforPostgreSQL/flexibleServers/administrators@2024-08-01' = {
  name:   miPrincipalId  // object ID of the MI
  parent: pg
  properties: {
    principalType: 'ServicePrincipal'
    principalName: 'id-${prefix}-${env}'
    tenantId:      subscription().tenantId
  }
}

// ── Resource lock ─────────────────────────────────────────────
resource pgLock 'Microsoft.Authorization/locks@2020-05-01' = {
  name:  'lock-${pgName}'
  scope: pg
  properties: {
    level: 'CanNotDelete'
    notes: 'Protects IPAI production Odoo database'
  }
}

// ── Outputs ────────────────────────────────────────────────────
// NOTE: KV secret write removed (BCP165 — cross-scope existing ref not allowed in modules).
// Parent main.bicep or post-deploy.sh is responsible for writing pg-odoo-fqdn to KV.
output pgFqdn        string = pg.properties.fullyQualifiedDomainName
output pgName        string = pg.name
output pgResourceId  string = pg.id
