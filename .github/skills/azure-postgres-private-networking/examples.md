# azure-postgres-private-networking -- Worked Examples

## Example 1: PG Flexible Server with Private Networking (Bicep)

Before (gap state):
```bicep
resource postgresServer 'Microsoft.DBforPostgreSQL/flexibleServers@2023-12-01-preview' = {
  name: 'pg-ipai-odoo'
  location: location
  properties: {
    version: '16'
    network: {
      publicNetworkAccess: 'Enabled'   // EXPOSED
    }
    authConfig: {
      activeDirectoryAuth: 'Disabled'
      passwordAuth: 'Enabled'
    }
  }
}
```

After (closed):
```bicep
resource postgresServer 'Microsoft.DBforPostgreSQL/flexibleServers@2023-12-01-preview' = {
  name: 'pg-ipai-odoo'
  location: location
  dependsOn: [privateDnsZoneLink]
  properties: {
    version: '16'
    network: {
      delegatedSubnetResourceId: vnet.properties.subnets[1].id   // snet-pg
      privateDnsZoneArmResourceId: privateDnsZone.id
      publicNetworkAccess: 'Disabled'
    }
    authConfig: {
      activeDirectoryAuth: 'Enabled'   // prefer Entra-based auth
      passwordAuth: 'Enabled'          // retain for Odoo compatibility
      tenantId: subscription().tenantId
    }
    highAvailability: {
      mode: 'ZoneRedundant'
    }
    backup: {
      retentionDays: 35
      geoRedundantBackup: 'Enabled'
    }
    // TLS: enforced by Flexible Server default (TLS1.2+); no sslEnforcement param in Flex API
  }
}

resource privateDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' = {
  name: 'pg-ipai-odoo.private.postgres.database.azure.com'
  location: 'global'
}

resource privateDnsZoneLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2020-06-01' = {
  parent: privateDnsZone
  name: 'pg-ipai-odoo-dns-link'
  location: 'global'
  properties: {
    virtualNetwork: { id: vnet.id }
    registrationEnabled: false
  }
}
```

## Example 2: Firewall Rule Audit

```bash
# Check for all-IP firewall rules on the PG server (these must not exist)
az postgres flexible-server firewall-rule list \
  --name pg-ipai-odoo \
  --resource-group rg-ipai-dev-odoo-data \
  --query "[?startIpAddress=='0.0.0.0']" \
  --output table

# Expected: empty result (no all-IP rules allowed once VNet-integrated)
# If any rule appears, remove it:
az postgres flexible-server firewall-rule delete \
  --name pg-ipai-odoo \
  --resource-group rg-ipai-dev-odoo-data \
  --rule-name AllowAllAzureIPs \
  --yes
```

## Example 3: SSOT Database Topology Update

```yaml
# ssot/azure/database_topology.yaml
databases:
  - name: pg-ipai-odoo
    type: Microsoft.DBforPostgreSQL/flexibleServers
    resource_group: rg-ipai-dev-odoo-data
    region: eastus2
    sku: Standard_D2ds_v5
    tier: GeneralPurpose
    version: "16"
    network_mode: vnet_integrated
    public_access: disabled
    subnet: snet-pg
    private_dns_zone: pg-ipai-odoo.private.postgres.database.azure.com
    tls_min_version: TLS1_2
    ha_mode: ZoneRedundant
    backup_retention_days: 35
    geo_redundant_backup: Enabled
    firewall_rules: []            # empty = no public rules, VNet-only access
    pgbouncer_enabled: false      # evaluate when concurrent sessions > 100
    databases:
      - odoo
      - odoo_staging
      - odoo_dev
```

## Example 4: MCP Query Sequence

```
Step 1: microsoft_docs_search("Azure PostgreSQL Flexible Server private access VNet integration")
Result: VNet-integrated deployment requires subnet delegation to
        Microsoft.DBforPostgreSQL/flexibleServers. Server is placed
        directly in the subnet (no private endpoint needed for Flex).
        Requires a private DNS zone linked to the VNet.

Step 2: microsoft_docs_search("Azure PostgreSQL Flexible Server TLS enforcement minimum version")
Result: PostgreSQL Flexible Server enforces TLS 1.2+ by default.
        No `sslEnforcement` parameter in the Flex API (unlike Single Server).
        Client connections still need `sslmode=require` in connection string.

Step 3: microsoft_docs_search("PgBouncer Azure PostgreSQL Flexible Server connection pooling")
Result: Built-in PgBouncer available on port 6432 (vs 5432 for direct).
        Pool modes: session (default), transaction, statement.
        Enable in server parameters: pgbouncer.enabled = on.
        Recommended for > 100 concurrent Odoo workers to avoid PG connection exhaustion.
```
