# Data Platform E2E Test Matrix

> Audit date: 2026-03-28

---

## Test Cases

### T1: Infrastructure Existence

| # | Test Case | Expected | Actual | Result |
|---|-----------|----------|--------|--------|
| T1.1 | PG server `pg-ipai-odoo` exists and is Ready | Ready | Ready | **PASS** |
| T1.2 | PG version is 16 | 16 | 16 | **PASS** |
| T1.3 | PG tier is General Purpose | GeneralPurpose | GeneralPurpose | **PASS** |
| T1.4 | PG `wal_level` is `logical` | logical | logical | **PASS** |
| T1.5 | PG `max_worker_processes` >= 8 | >= 8 | 11 | **PASS** |
| T1.6 | ADLS `stipaidevlake` exists | Exists | Exists | **PASS** |
| T1.7 | ADLS has HNS enabled (Gen2) | true | true | **PASS** |
| T1.8 | ADLS has bronze/silver/gold containers | Present | Present | **PASS** |
| T1.9 | Databricks workspace `dbw-ipai-dev` provisioned | Succeeded | Succeeded | **PASS** |
| T1.10 | Databricks SKU is Premium | Premium | Premium | **PASS** |

### T2: Identity and Permissions

| # | Test Case | Expected | Actual | Result |
|---|-----------|----------|--------|--------|
| T2.1 | CLI user has Storage Blob Data Reader on `stipaidevlake` | Assigned | **NOT assigned** | **FAIL** |
| T2.2 | Databricks CLI auth works (`databricks workspace list`) | Success | **Permission denied (CLI blocked)** | **BLOCKED** |
| T2.3 | Unity Catalog access connector has SBDC on `stipaidevlake` | Assigned (per SSOT) | Cannot verify live | **UNVERIFIED** |
| T2.4 | Databricks secret scope `ipai-odoo-pg` exists | Exists | Cannot verify (CLI blocked) | **BLOCKED** |
| T2.5 | Managed identity `id-ipai-databricks-dev` exists | Exists (per SSOT) | Cannot verify | **UNVERIFIED** |

### T3: Fabric Mirroring (Lane 1)

| # | Test Case | Expected | Actual | Result |
|---|-----------|----------|--------|--------|
| T3.1 | Fabric mirroring configured on `pg-ipai-odoo` | Configured | **null** | **FAIL** |
| T3.2 | Fabric capacity provisioned | Provisioned | **Not provisioned** | **FAIL** |
| T3.3 | Mirrored database created in Fabric | Created | Not possible (no capacity) | **BLOCKED** |
| T3.4 | OneLake contains mirrored Odoo tables | Tables present | Not possible | **BLOCKED** |
| T3.5 | CDC replication is functional | Replicating | Not possible | **BLOCKED** |

### T4: Databricks / Unity Catalog (Lane 2)

| # | Test Case | Expected | Actual | Result |
|---|-----------|----------|--------|--------|
| T4.1 | Unity Catalog metastore attached | Attached | **"pending" per SSOT** | **FAIL** |
| T4.2 | Catalog `ipai` (or `ipai_lakehouse_dev`) exists | Exists | Cannot verify (CLI blocked) | **BLOCKED** |
| T4.3 | Schemas `bronze`, `silver`, `gold` exist in catalog | Exist | Cannot verify | **BLOCKED** |
| T4.4 | Lakehouse Federation connection `odoo_pg` exists | Exists | Cannot verify | **BLOCKED** |
| T4.5 | Foreign catalog `odoo_federated` exists | Exists | Cannot verify | **BLOCKED** |
| T4.6 | SQL Warehouse `e7d89eabce4c330c` is running | Running | Cannot verify | **BLOCKED** |

### T5: Bronze Layer Ingestion

| # | Test Case | Expected | Actual | Result |
|---|-----------|----------|--------|--------|
| T5.1 | Bronze tables contain data from Odoo PG | Data present | Cannot verify | **BLOCKED** |
| T5.2 | `ipai.bronze.odoo_res_partner` exists with rows | Populated | Cannot verify | **BLOCKED** |
| T5.3 | `ipai.bronze.odoo_account_move` exists with rows | Populated | Cannot verify | **BLOCKED** |
| T5.4 | ADLS `bronze` container has Delta files | Files present | **Cannot read (no RBAC)** | **FAIL** |

### T6: Silver Layer Transformation

| # | Test Case | Expected | Actual | Result |
|---|-----------|----------|--------|--------|
| T6.1 | Silver tables contain deduplicated data | Populated | Cannot verify | **BLOCKED** |
| T6.2 | DLT expectations enforced (non-null keys, valid dates) | Enforced | Cannot verify | **BLOCKED** |
| T6.3 | Quarantine tables capture rejected rows | Populated | Cannot verify | **BLOCKED** |

### T7: Gold Layer Serving

| # | Test Case | Expected | Actual | Result |
|---|-----------|----------|--------|--------|
| T7.1 | Gold tables contain aggregated business data | Populated | Cannot verify | **BLOCKED** |
| T7.2 | Revenue summary, customer KPIs, payment aging exist | Exist | Cannot verify | **BLOCKED** |
| T7.3 | Gold tables readable via SQL Warehouse | Queryable | Cannot verify | **BLOCKED** |

### T8: Power BI Consumption

| # | Test Case | Expected | Actual | Result |
|---|-----------|----------|--------|--------|
| T8.1 | Power BI workspace exists | Exists | **Not deployed** | **FAIL** |
| T8.2 | Semantic model connected to SQL Warehouse | Connected | Not possible | **BLOCKED** |
| T8.3 | Dashboard renders gold data | Renders | Not possible | **BLOCKED** |

### T9: Cleanup and Recovery

| # | Test Case | Expected | Actual | Result |
|---|-----------|----------|--------|--------|
| T9.1 | Test schemas can be dropped without affecting prod | Isolated | Cannot verify | **BLOCKED** |
| T9.2 | Cleanup notebook exists | Exists | `tests/cleanup_test_data.py` present | **PASS** |

---

## Summary

| Category | Total | Pass | Fail | Blocked | Unverified |
|----------|-------|------|------|---------|------------|
| T1: Infrastructure | 10 | 10 | 0 | 0 | 0 |
| T2: Identity | 5 | 0 | 1 | 2 | 2 |
| T3: Fabric Mirroring | 5 | 0 | 2 | 3 | 0 |
| T4: Databricks/UC | 6 | 0 | 1 | 5 | 0 |
| T5: Bronze | 4 | 0 | 1 | 3 | 0 |
| T6: Silver | 3 | 0 | 0 | 3 | 0 |
| T7: Gold | 3 | 0 | 0 | 3 | 0 |
| T8: Power BI | 3 | 0 | 1 | 2 | 0 |
| T9: Cleanup | 2 | 1 | 0 | 1 | 0 |
| **TOTAL** | **41** | **11** | **6** | **22** | **2** |

**Overall: 11 PASS / 6 FAIL / 22 BLOCKED / 2 UNVERIFIED**

---

*Tested 2026-03-28*
