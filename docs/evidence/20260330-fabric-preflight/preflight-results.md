# Fabric Mirroring Pre-Flight Results

> **Date**: 2026-03-30
> **Scope**: Pre-flight verification for Fabric Mirroring rehearsal (`odoo_staging` on `pg-ipai-odoo`)
> **Runbook**: `docs/runbooks/fabric-mirroring-rehearsal.md`
> **Config SSOT**: `data-intelligence/ssot/mirroring/fabric-mirror-config.yaml`

---

## Check 1: PostgreSQL Server Exists and Ready

**Command**:
```bash
az postgres flexible-server show \
  --resource-group rg-ipai-dev-odoo-data \
  --name pg-ipai-odoo \
  --query "{name:name, state:state, version:version, sku:sku.name, tier:sku.tier}" -o table
```

**Result**:
```
Name          State    Version    Sku               Tier
------------  -------  ---------  ----------------  --------------
pg-ipai-odoo  Ready    16         Standard_D2ds_v5  GeneralPurpose
```

**Expected**: State = `Ready`, Version = `16`, Tier = `GeneralPurpose`

**Verdict**: **PASS** -- Server is Ready, PostgreSQL 16, General Purpose tier (required for mirroring).

---

## Check 2: WAL Level is Logical

**Command**:
```bash
az postgres flexible-server parameter show \
  --resource-group rg-ipai-dev-odoo-data \
  --server-name pg-ipai-odoo \
  --name wal_level --query value -o tsv
```

**Result**:
```
logical
```

**Expected**: `logical`

**Verdict**: **PASS** -- WAL level is `logical`. No server restart needed for this parameter.

---

## Check 3: Max Replication Slots

**Command**:
```bash
az postgres flexible-server parameter show \
  --resource-group rg-ipai-dev-odoo-data \
  --server-name pg-ipai-odoo \
  --name max_replication_slots --query value -o tsv
```

**Result**:
```
10
```

**Expected**: >= 4

**Verdict**: **PASS** -- 10 replication slots available. Fabric uses 1 per mirrored database. Ample headroom.

---

## Check 4: Max Worker Processes

**Command**:
```bash
az postgres flexible-server parameter show \
  --resource-group rg-ipai-dev-odoo-data \
  --server-name pg-ipai-odoo \
  --name max_worker_processes --query value -o tsv
```

**Result**:
```
23
```

**Expected**: >= 8

**Verdict**: **PASS** -- 23 worker processes configured. Well above the minimum threshold.

---

## Check 5: Database `odoo_staging` Exists

**Command**:
```bash
az postgres flexible-server db show \
  --resource-group rg-ipai-dev-odoo-data \
  --server-name pg-ipai-odoo \
  --database-name odoo_staging -o table
```

**Result**:
```
Charset    Collation    Name          ResourceGroup
---------  -----------  ------------  ---------------------
UTF8       en_US.utf8   odoo_staging  rg-ipai-dev-odoo-data
```

**Expected**: Database exists, collation = `en_US.utf8`

**Verdict**: **PASS** -- Database exists with expected charset (UTF8) and collation (en_US.utf8).

---

## Check 6: Fabric Capacity Status

**Command**:
```bash
az graph query -q "Resources | where type =~ 'Microsoft.Fabric/capacities' | project name, location, resourceGroup, sku, properties" -o json
```

**Result**:
```json
{
  "count": 1,
  "data": [
    {
      "location": "southeastasia",
      "name": "fcipaidev",
      "properties": {
        "administration": {
          "members": ["admin@insightpulseai.com"]
        },
        "provisioningState": "Succeeded",
        "state": "Active"
      },
      "resourceGroup": "rg-ipai-ai-dev",
      "sku": { "name": "F2", "tier": "Fabric" }
    }
  ]
}
```

**Expected**: Active Fabric capacity (F2 minimum) in `southeastasia` region.

**Verdict**: **PASS** -- Fabric capacity `fcipaidev` is Active, F2 SKU, `southeastasia`, in `rg-ipai-ai-dev`. Admin: `admin@insightpulseai.com`.

---

## Check 7: Firewall Rules (Fabric Access)

**Command**:
```bash
az postgres flexible-server firewall-rule list \
  --resource-group rg-ipai-dev-odoo-data \
  --name pg-ipai-odoo -o table
```

**Result**:
```
EndIpAddress    Name                   ResourceGroup          StartIpAddress
--------------  ---------------------  ---------------------  ----------------
20.198.128.64   aca-outbound-20260329  rg-ipai-dev-odoo-data  20.198.128.64
0.0.0.0         AllowAzureServices     rg-ipai-dev-odoo-data  0.0.0.0
130.105.68.4    ClientIP               rg-ipai-dev-odoo-data  130.105.68.4
```

**Expected**: `AllowAzureServices` rule with start/end IP `0.0.0.0` (allows Azure services including Fabric to connect).

**Verdict**: **PASS** -- The `AllowAzureServices` firewall rule is present (0.0.0.0 - 0.0.0.0). Fabric will be able to connect to the PG server.

---

## Summary

| # | Check | Expected | Actual | Verdict |
|---|-------|----------|--------|---------|
| 1 | PG server exists and ready | Ready, v16, GeneralPurpose | Ready, v16, GeneralPurpose | **PASS** |
| 2 | WAL level = logical | logical | logical | **PASS** |
| 3 | max_replication_slots >= 4 | >= 4 | 10 | **PASS** |
| 4 | max_worker_processes >= 8 | >= 8 | 23 | **PASS** |
| 5 | odoo_staging database exists | exists, en_US.utf8 | exists, en_US.utf8 | **PASS** |
| 6 | Fabric capacity provisioned | Active F2 capacity | `fcipaidev` Active F2 southeastasia | **PASS** |
| 7 | Firewall allows Azure services | AllowAzureServices rule | AllowAzureServices present | **PASS** |

---

## Overall Verdict: GO

**7 of 7 checks passed.**

All prerequisites met:
- PostgreSQL server `pg-ipai-odoo` is Ready (v16, General Purpose, `wal_level=logical`)
- `odoo_staging` database exists with correct collation
- Fabric capacity `fcipaidev` is Active (F2, `southeastasia`, `rg-ipai-ai-dev`)
- Firewall allows Azure services

### Next Steps

1. **Create Fabric workspace** `ipai-data-mirror-dev` and assign to capacity `fcipaidev`
2. **Create mirrored database** for `odoo_staging` via Fabric portal
3. **Validate** data flow with row count comparison queries
4. **48h soak** monitoring per runbook section 8
