# Data Platform E2E Findings

> Audit date: 2026-03-28

---

## Executive Summary

The data platform has **solid infrastructure provisioning** (PG server, ADLS Gen2, Databricks workspace all exist and are correctly configured) but has **zero operational data flow**. The entire medallion pipeline exists only as code in the repo -- none of it has been deployed or executed. Fabric mirroring is not configured. Power BI is not deployed. The platform is in a "scaffolded but not wired" state.

---

## What Works

### 1. PostgreSQL Server is Fully Ready
- `pg-ipai-odoo` is General Purpose tier, PostgreSQL 16, `wal_level=logical`, `max_worker_processes=11`
- Contains three databases: `odoo`, `odoo_staging`, `odoo_prod`
- All prerequisites for Fabric mirroring are met at the PG server level
- Public access enabled (required for Databricks Lakehouse Federation)

### 2. ADLS Gen2 Storage is Provisioned
- `stipaidevlake` exists with HNS enabled (true ADLS Gen2)
- Six containers created: `bronze`, `silver`, `gold`, `platinum`, `checkpoints`, `iceberg`
- Container structure matches the medallion architecture design

### 3. Databricks Workspace is Live
- `dbw-ipai-dev` is provisioned (state: Succeeded)
- Premium SKU (required for Unity Catalog)
- VNet injection with secure cluster connectivity
- `~/.databrickscfg` exists with correct host URL

### 4. Code Quality is High
- Comprehensive DLT pipeline code with expectations (`medallion_test_dlt.py`)
- Synthetic data generator for testing (`seed_synthetic.py`)
- Full Bronze-Silver-Gold test pipeline (`test_medallion_pipeline.py`)
- DAB job definition for orchestrated test runs (`medallion_test_job.yml`)
- Lakehouse Federation ingestion notebook (`01_odoo_bronze_ingestion.py`)
- SQL DDL for all layers with proper commenting and constraints

---

## What is Broken

### B1: Fabric Mirroring Not Configured (CRITICAL)

**Evidence:** `az postgres flexible-server show` returns `fabricMirroring: null`

**Root cause:** Fabric mirroring requires:
1. Microsoft Fabric capacity (F64 or higher, or Fabric trial)
2. Fabric workspace created
3. PG server "fabric mirroring" feature enabled via Azure CLI
4. Mirrored database created from Fabric portal/API

None of these steps have been executed. The PG server prerequisites (wal_level, tier) are met, but the Fabric side is completely absent.

**Impact:** Lane 1 (Fabric-native operational analytics) is non-functional. The entire near-real-time CDC path from Odoo to OneLake does not exist.

### B2: Unity Catalog Metastore Not Confirmed (CRITICAL)

**Evidence:** `workspace.yaml` SSOT says metastore status is `pending: "not yet confirmed from live workspace"`

**Root cause:** While catalogs `ipai_lakehouse_dev/staging/prod` are claimed as "verified" in the SSOT, the metastore itself is marked pending. Without a metastore, no catalogs or schemas can exist. This is either:
- (a) The metastore was attached but the SSOT was never updated, or
- (b) The metastore was never attached, and the "verified" catalog claims are aspirational

Cannot verify either scenario because Databricks CLI access is blocked.

**Impact:** If no metastore, then no Unity Catalog, no data governance, no tables. The entire Databricks data layer would be non-functional.

### B3: No Data in ADLS Containers (LIKELY)

**Evidence:** CLI user lacks `Storage Blob Data Reader` on `stipaidevlake`. Containers were created on 2026-03-03 and never modified (based on lastModified dates). No blob listing possible.

**Root cause:** No pipeline has ever written data to these containers. They are empty provisioned buckets.

**Impact:** No bronze, silver, or gold data exists in the lake.

### B4: Databricks CLI Auth Broken

**Evidence:** All `databricks` CLI commands result in permission denied from the sandbox environment. The `~/.databrickscfg` uses `auth_type = databricks-cli` which requires a valid token or AAD authentication.

**Root cause:** Either:
- The Databricks CLI token has expired
- AAD token is not being forwarded
- The sandbox blocks external CLI calls

**Impact:** Cannot verify Unity Catalog state, cluster availability, SQL warehouse status, or run any Databricks operations from CLI.

### B5: Catalog Name Collision

**Evidence:** Four different catalog names used across code:
1. `ipai` (ingestion notebook)
2. `dbw_ipai_dev` (test notebooks)
3. `dev_ppm` / `ppm` (DAB bundle)
4. `ipai_lakehouse_dev` (workspace.yaml SSOT)

**Root cause:** No canonical catalog naming decision was made before code was written. Different authors used different naming conventions.

**Impact:** Even if the workspace is operational, running notebooks from different files would target different (potentially non-existent) catalogs.

### B6: Power BI Not Deployed

**Evidence:** Service matrix shows Power BI as `planned`, `not_deployed`. No `.pbix` files in the `data-intelligence` repo (only Microsoft sample PBIXes in `archive/templates/`).

**Root cause:** Power BI requires either Power BI Pro/PPU licenses or Fabric capacity. Neither appears to be provisioned.

**Impact:** No business consumption layer exists. The gold layer has no downstream consumer.

### B7: Deprecated Source References in Code

**Evidence:**
- `databricks.yml` references Notion database IDs (`NOTION_PROGRAMS_DB_ID`, etc.) -- Notion is deprecated per CLAUDE.md
- Bronze/Silver SQL DDL contains Notion-specific tables (`notion_raw_pages`, `notion_programs`, `notion_projects`)
- DAB bundle artifact references `services/notion-sync` which likely no longer exists

**Root cause:** The original pipeline was built for a Notion-based PPM system. The platform has since moved to Odoo, but the DAB bundle and SQL DDL were never updated.

**Impact:** The existing DAB bundle cannot be deployed as-is. It would attempt to sync from a deprecated source.

---

## Ambiguous / Unverifiable

| Item | Why Unverifiable | Risk |
|------|-----------------|------|
| Unity Catalog metastore | CLI blocked | HIGH -- entire data layer depends on this |
| SQL Warehouse status | CLI blocked | MEDIUM -- needed for ad-hoc queries and BI |
| Databricks secret scope | CLI blocked | HIGH -- needed for Lakehouse Federation |
| Cluster availability | CLI blocked | MEDIUM -- needed to run notebooks |
| Access connector RBAC | Cannot list role assignments | MEDIUM -- needed for UC storage access |
| ADLS data presence | No blob read RBAC | LOW -- likely empty based on timestamps |

---

## Failure Modes

### FM1: Fabric Capacity Cost Gate
Fabric capacity (F64) starts at ~$5,000/month. This is a significant cost commitment for a dev environment. A Fabric trial (60 days) can unblock mirroring evaluation without cost commitment.

### FM2: DDL on Mirrored Tables
Once Fabric mirroring is active, DDL changes on mirrored tables (ALTER TABLE, DROP TABLE) and TRUNCATE operations require pipeline restart. Odoo schema migrations could break the mirroring pipeline.

### FM3: Table Ownership Constraint
Fabric mirroring requires source tables to be owned by `azure_pg_admin`. Odoo typically creates tables owned by the application user. Ownership transfer may be required.

### FM4: Databricks Token Rotation
The `databricks-cli` auth_type in `~/.databrickscfg` relies on AAD or PAT tokens that expire. There is no automated token rotation mechanism visible in the repo.

---

*Findings compiled 2026-03-28*
