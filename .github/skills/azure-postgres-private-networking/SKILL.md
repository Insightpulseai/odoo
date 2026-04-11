---
name: azure-postgres-private-networking
description: Harden PostgreSQL private networking with VNet integration, firewall restrictions, TLS enforcement, and private DNS zone
version: "1.0"
compatibility:
  hosts: [github-copilot, claude-code, codex-cli, cursor, gemini-cli]
tags: [security, postgres, networking, governance]
---

# azure-postgres-private-networking

**Impact tier**: P0 -- Security Exposure

## Purpose

Ensure PostgreSQL Flexible Server (`pg-ipai-odoo`) has private networking
enforced via VNet integration, firewall rules restricting access exclusively
to authorized subnets, TLS enforcement, and connection pooling configuration.
This skill extends `azure-pg-ha-dr` (data durability) and `aca-private-networking`
(network topology) with a deeper focus on the PG-specific security controls:
public access flag, private DNS zone, firewall rules, TLS mode, and optional
PgBouncer pooler placement.

## When to Use

- When the PG server has `publicNetworkAccess: 'Enabled'` in IaC or in the Azure portal.
- Before go-live: confirming no path to PG exists except through the ACA subnet.
- After a VNet topology change that could have re-exposed the PG endpoint.
- When adding a new service that needs PG access (must go through subnet allow-list).

## Required Evidence (inspect these repo paths first)

| Path | What to look for |
|------|-----------------|
| `ssot/azure/database_topology.yaml` | `pg-ipai-odoo` network mode, public access flag, firewall rules |
| `ssot/azure/estate_authority.yaml` | Resource group and subscription that owns PG |
| `infra/azure/modules/postgres-flexible.bicep` | `network.publicNetworkAccess`, `network.delegatedSubnetResourceId`, TLS settings |
| `docs/architecture/azure/BILL_OF_MATERIALS.md` | PG row: networking tier, private access mode noted |

## Microsoft Learn MCP Usage

Run at least these queries:

1. `microsoft_docs_search("Azure PostgreSQL Flexible Server private access VNet integration")`
   -- retrieves VNet-integrated private access vs private endpoint, delegation requirements.
2. `microsoft_docs_search("Azure PostgreSQL Flexible Server firewall rules disable public access")`
   -- retrieves `publicNetworkAccess: Disabled` behavior, firewall rule precedence.
3. `microsoft_docs_search("Azure PostgreSQL Flexible Server TLS enforcement minimum version")`
   -- retrieves `sslEnforcement`, `minimalTlsVersion` parameter values.
4. `microsoft_docs_search("PgBouncer Azure PostgreSQL Flexible Server connection pooling")`
   -- retrieves built-in PgBouncer on PG Flex, pool mode options, port 6432.

Optional:

5. `microsoft_code_sample_search("bicep postgresql flexible server private dns zone vnet", language="bicep")`
6. `microsoft_docs_fetch("https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/concepts-networking-private")`

## Workflow

1. **Inspect repo** -- Read `infra/azure/modules/postgres-flexible.bicep` and
   `ssot/azure/database_topology.yaml`. Record: `publicNetworkAccess` value,
   whether `delegatedSubnetResourceId` is set, whether a private DNS zone
   is linked, TLS version, and whether firewall rules exist for IP ranges.
2. **Query MCP** -- Run queries 1-4. Capture: private DNS zone name format
   (`<server>.private.postgres.database.azure.com`), delegation service name
   (`Microsoft.DBforPostgreSQL/flexibleServers`), minimum TLS version
   (`TLS1_2`), and PgBouncer port (`6432`).
3. **Compare** -- Identify: (a) `publicNetworkAccess` not set to `Disabled`,
   (b) missing private DNS zone link, (c) firewall rules allowing broad IP
   ranges (`0.0.0.0`-`255.255.255.255`), (d) `minimalTlsVersion` below
   `TLS1_2`, (e) no PgBouncer pooler on high-concurrency paths.
4. **Patch** -- Update Bicep: set `publicNetworkAccess: 'Disabled'`, configure
   `delegatedSubnetResourceId` to the PG subnet, link private DNS zone,
   set `minimalTlsVersion: 'TLS1_2'`. Remove any all-IP firewall rules.
   Update `ssot/azure/database_topology.yaml` with the hardened state.
5. **Verify** -- `az bicep build` lints clean. Grep confirms no
   `publicNetworkAccess: 'Enabled'` in any Bicep file. SSOT YAML updated.
   Evidence directory contains diff and MCP excerpts.

## Outputs

| File | Change |
|------|--------|
| `infra/azure/modules/postgres-flexible.bicep` | Disable public access, VNet integration, TLS, private DNS |
| `infra/azure/modules/postgres-private-dns.bicep` | Private DNS zone and VNet link (create if missing) |
| `ssot/azure/database_topology.yaml` | Network mode, TLS version, firewall state |
| `docs/architecture/azure/BILL_OF_MATERIALS.md` | PG row updated with private access confirmed |
| `docs/evidence/<stamp>/azure-postgres-private-networking/` | Bicep diffs, MCP excerpts |

## Completion Criteria

- [ ] `postgres-flexible.bicep` sets `publicNetworkAccess: 'Disabled'`.
- [ ] PG Flexible Server uses `delegatedSubnetResourceId` pointing to `snet-pg`.
- [ ] A private DNS zone (`*.private.postgres.database.azure.com`) is created and linked to the VNet.
- [ ] No firewall rules allow `startIpAddress: '0.0.0.0'` on the PG server.
- [ ] `minimalTlsVersion` is `TLS1_2` or higher.
- [ ] `ssot/azure/database_topology.yaml` reflects `public_access: disabled` and `network_mode: vnet_integrated`.
- [ ] No `publicNetworkAccess: 'Enabled'` appears in any file under `infra/azure/`.
- [ ] Evidence directory contains Bicep diff and MCP excerpts.
