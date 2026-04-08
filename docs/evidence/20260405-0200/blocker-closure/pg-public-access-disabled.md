# P0 Blocker Closure: PostgreSQL Public Network Access Disabled

**Date**: 2026-04-05T02:00+08:00
**Server**: `pg-ipai-odoo` (`rg-ipai-dev-odoo-data`, Southeast Asia)
**FQDN**: `pg-ipai-odoo.postgres.database.azure.com`
**Version**: PostgreSQL 16
**Databases**: `odoo` (prod), `odoo_dev` (dev), `odoo_staging` (staging)

---

## Before State

| Property | Value |
|----------|-------|
| Public Network Access | **Enabled** |
| Firewall Rules | `AllowAzureServices` (0.0.0.0), `aca-outbound-20260329` (20.198.128.64), `ClientIP` (130.105.68.4) |
| Private Endpoint | None |
| Delegated Subnet | None |
| Private DNS Zone | None (on server) |

---

## Changes Applied

### 1. Private Endpoint Created

```
Name:             pe-pg-ipai-odoo
Resource Group:   rg-ipai-dev-odoo-data
Subnet:           snet-pe (10.0.2.0/24) in vnet-ipai-dev (rg-ipai-dev-odoo-runtime)
Private IP:       10.0.2.6
Connection Name:  pg-ipai-odoo-pe-conn
Connection Status: Approved
Provisioning:     Succeeded
```

### 2. Private DNS Zone Group Created

```
DNS Zone Group:   pg-dns-zone-group
Zone:             privatelink.postgres.database.azure.com (rg-ipai-dev-odoo-runtime)
A Record:         pg-ipai-odoo -> 10.0.2.6 (TTL 10s, auto-registered)
```

### 3. Public Network Access Disabled

```
az postgres flexible-server update --name pg-ipai-odoo --resource-group rg-ipai-dev-odoo-data --public-access Disabled
```

---

## After State

| Property | Value |
|----------|-------|
| Public Network Access | **Disabled** |
| Firewall Rules | Inaccessible (expected when public access disabled) |
| Private Endpoint | `pe-pg-ipai-odoo` (10.0.2.6, Approved, Succeeded) |
| Private DNS A Record | `pg-ipai-odoo.privatelink.postgres.database.azure.com` -> 10.0.2.6 |
| Server State | Ready |

---

## Verification

```
$ az postgres flexible-server show --name pg-ipai-odoo --resource-group rg-ipai-dev-odoo-data \
    --query "{name:name, publicAccess:network.publicNetworkAccess, state:state}" --output table

Name          PublicAccess    State
------------  --------------  -------
pg-ipai-odoo  Disabled        Ready
```

Firewall rule query returns expected error:
```
ERROR: Firewall rule operations cannot be requested for a server that doesn't have public access enabled.
```

---

## Connectivity Path

All Container Apps in `ipai-odoo-dev-env` (ACA environment) connect via:
- VNet: `vnet-ipai-dev` (10.0.0.0/16)
- ACA subnet: `snet-aca` (10.0.0.0/23) -- apps egress through this
- PE subnet: `snet-pe` (10.0.2.0/24) -- PE NIC lives here
- Private DNS: `privatelink.postgres.database.azure.com` -- linked to VNet
- Resolution: `pg-ipai-odoo.postgres.database.azure.com` -> `10.0.2.6` (via private DNS)

No public internet path to the database exists.

---

## Risk Note

The prior firewall rules (AllowAzureServices, ClientIP, ACA outbound IP) are now irrelevant as public access is disabled. If public access is ever re-enabled, those rules would need to be recreated.

For local dev access, use Azure VPN Gateway or `az postgres flexible-server connect` via Cloud Shell.
