# Fabric Capacity Scope Decision

**Blocker**: B-5
**Status**: CLOSED -- explicitly deferred to post-go-live enablement

---

## Decision

**Fabric capacity is deferred to post-go-live enablement.** It is not a prerequisite for the initial ERP go-live.

---

## Current State

| Component | Status |
|-----------|--------|
| `pg-ipai-odoo` (General Purpose PG) | Active, mirroring-enabled |
| Fabric mirroring configuration | Enabled on server, `odoo_staging` scoped |
| Fabric capacity (F2/F4/F64) | **Not provisioned** |
| Power BI Premium/PPU | **Not provisioned** |
| XMLA endpoint | **Not configured** (requires capacity) |

---

## Rationale

1. **Core ERP does not depend on Fabric**. Odoo operational workloads (accounting, HR, CRM, invoicing) run entirely on `pg-ipai-odoo` with no Fabric dependency.

2. **Fabric is a consumption/analytics layer**. It mirrors Odoo data for BI/analytics purposes. The ERP is fully functional without it.

3. **Databricks is the engineering core**. `dbw-ipai-dev` with SQL Warehouse `e7d89eabce4c330c` handles all data engineering workloads independently of Fabric.

4. **Cost timing**. Fabric capacity (even F2) has a non-trivial monthly cost. Provisioning should align with when analytics consumers are ready to use it.

5. **Mirroring is pre-staged**. `pg-ipai-odoo` already has mirroring enabled. When Fabric capacity is provisioned, mirroring will activate without database-side changes.

---

## What This Changes in the Go-Live Checklist

### Downgraded from Blocker to Post-Launch

| Section | Item | Previous | New |
|---------|------|----------|-----|
| 4. Fabric Mirroring | Fabric capacity is active | Blocker | Post-launch |
| 5. Power BI | Data published via UC-enabled compute | Blocker | Post-launch |
| 5. Power BI | Power BI Premium/PPU/Fabric capacity active | Blocker | Post-launch |
| 5. Power BI | XMLA endpoint set to Read Write | Blocker | Post-launch |
| 5. Power BI | Serving contract defined | Blocker | Post-launch |

### Remain Blocking

| Section | Item | Status |
|---------|------|--------|
| 1. Identity | Entra ID operational (B-1) | DOCUMENTED |
| 1. Identity | Break-glass accounts (B-3) | DOCUMENTED |
| 1. Identity | No credentials in tracked files (B-2) | IN PROGRESS |
| 9. Operations | Incident/rollback plans (B-4) | CLOSED |

---

## Post-Go-Live Enablement Plan

When the organization is ready to enable Fabric analytics:

1. **Provision Fabric capacity** (F2 minimum for dev/test, F64 for production):
   ```bash
   az fabric capacity create \
     --resource-group rg-ipai-data-dev \
     --capacity-name fabric-ipai-dev \
     --sku-name F2 \
     --location southeastasia \
     --admin-members platform-owner@insightpulseai.com
   ```

2. **Activate Fabric mirroring** for `pg-ipai-odoo` database `odoo_staging` (then `odoo`):
   - Mirroring configuration is pre-staged
   - Verify table replication status in Fabric portal

3. **Configure Power BI workspace**:
   - Assign workspace to Fabric capacity
   - Enable XMLA endpoint (Read Write)
   - Create Direct Lake datasets from mirrored tables

4. **Define serving contract**:
   - Document which tables/views are exposed via Databricks SQL Warehouse vs Direct Lake
   - Publish to `ssot/data/serving_contract.yaml`

---

*Last updated: 2026-03-27*
