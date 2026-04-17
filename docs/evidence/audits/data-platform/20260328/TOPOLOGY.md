# Data Platform Topology -- Discovered Architecture

> Audit date: 2026-03-28
> Method: SSOT file analysis + Azure CLI runtime probes + Databricks CLI config inspection

---

## Architecture Overview

The data platform follows a four-lane ingestion model with a medallion lakehouse architecture. The intended end state is:

```
Odoo PG (SoR) --> [Lane 1] Fabric Mirroring --> OneLake Bronze
                  [Lane 2] Lakehouse Federation --> Databricks UC Bronze
              --> DLT Pipelines --> Silver --> Gold
              --> Power BI / Copilot (consumption)
```

---

## Component Inventory

### 1. Source System: Azure PostgreSQL Flexible Server

| Property | Value | Status |
|----------|-------|--------|
| Server | `pg-ipai-odoo` | **VERIFIED (Ready)** |
| Resource Group | `rg-ipai-dev-odoo-data` | VERIFIED |
| Version | PostgreSQL 16 | VERIFIED |
| SKU Tier | General Purpose | VERIFIED |
| `wal_level` | `logical` | VERIFIED |
| `max_worker_processes` | 11 | VERIFIED |
| Databases | `odoo`, `odoo_staging`, `odoo_prod`, `postgres`, `azure_maintenance`, `azure_sys` | VERIFIED |
| Fabric Mirroring | **null (NOT CONFIGURED)** | VERIFIED |

### 2. Storage: ADLS Gen2

| Property | Value | Status |
|----------|-------|--------|
| Account | `stipaidevlake` | **VERIFIED (exists)** |
| Resource Group | `rg-ipai-ai-dev` | VERIFIED |
| Region | Southeast Asia | VERIFIED |
| Kind | StorageV2 | VERIFIED |
| HNS (hierarchical) | Enabled | VERIFIED |
| SKU | Standard_LRS | VERIFIED |

**Containers (all verified):**

| Container | Created | Data Present |
|-----------|---------|-------------|
| `bronze` | 2026-03-03 | UNKNOWN (no Storage Blob Data Reader) |
| `silver` | 2026-03-03 | UNKNOWN |
| `gold` | 2026-03-03 | UNKNOWN |
| `platinum` | 2026-03-03 | UNKNOWN |
| `checkpoints` | 2026-03-03 | UNKNOWN |
| `iceberg` | 2026-03-21 | UNKNOWN |

**Access issue:** Current CLI identity lacks `Storage Blob Data Reader` role on `stipaidevlake`. Cannot verify whether containers contain data.

### 3. Databricks Workspace

| Property | Value | Status |
|----------|-------|--------|
| Workspace | `dbw-ipai-dev` | **VERIFIED (Succeeded)** |
| URL | `adb-7405610347978231.11.azuredatabricks.net` | VERIFIED |
| SKU | Premium (required for Unity Catalog) | VERIFIED |
| Region | Southeast Asia | VERIFIED |
| Managed RG | `rg-dbw-managed-ipai-dev` | VERIFIED (from SSOT) |
| CLI Config | `~/.databrickscfg` profile `azure-dev`, auth_type `databricks-cli` | VERIFIED |
| CLI Auth | **BLOCKED (permission denied on CLI commands)** | NOT VERIFIED |

### 4. Unity Catalog

| Property | Value | Status |
|----------|-------|--------|
| Metastore | Pending (SSOT says "not yet confirmed") | NOT VERIFIED |
| Catalogs (SSOT) | `ipai_lakehouse_dev`, `ipai_lakehouse_staging`, `ipai_lakehouse` | CLAIMED VERIFIED in SSOT |
| Access Connector | `unity-catalog-access-connector` in `rg-dbw-managed-ipai-dev` | SSOT-confirmed |
| Role: SBDC on `stipaidevlake` | Assigned to access connector | SSOT-confirmed |

**Cannot confirm live state** -- Databricks CLI commands denied at runtime.

### 5. SQL Warehouse

| Property | Value | Status |
|----------|-------|--------|
| Warehouse ID | `e7d89eabce4c330c` | From SSOT/memory |
| Live State | UNKNOWN | Cannot verify (CLI blocked) |

### 6. Microsoft Fabric

| Property | Value | Status |
|----------|-------|--------|
| Service Matrix Status | `planned`, `not_deployed` | VERIFIED from SSOT |
| PG Server Mirroring | **null / NOT CONFIGURED** | VERIFIED via Azure CLI |
| Fabric Capacity | **Not provisioned** | Inferred (no mirroring active) |

### 7. Power BI

| Property | Value | Status |
|----------|-------|--------|
| Service Matrix Status | `planned`, `not_deployed` | VERIFIED from SSOT |
| Semantic Models | None deployed | No `.pbix` files in data-intelligence repo |
| Connection to SQL Warehouse | Not configured | Inferred |

### 8. Managed Identity

| Property | Value | Status |
|----------|-------|--------|
| Name | `id-ipai-databricks-dev` | SSOT-confirmed |
| Type | User-assigned | SSOT-confirmed |
| Key Vault Access | `kv-ipai-dev` | SSOT-confirmed |

---

## Repo Code Inventory

### Code Assets in `data-intelligence/`

| Path | Purpose | Operational? |
|------|---------|-------------|
| `databricks/databricks.yml` | DAB bundle config (Finance PPM) | Scaffolded, references `notion_token` (deprecated source) |
| `databricks/sql/schemas_odoo.sql` | UC schema DDL (bronze/silver/gold) | SQL ready, not deployed |
| `databricks/sql/bronze_odoo.sql` | Bronze table DDL (Notion + Azure RG) | SQL ready, not deployed |
| `databricks/sql/silver_odoo.sql` | Silver table DDL (programs, projects, budget) | SQL ready, not deployed |
| `databricks/sql/gold_odoo.sql` | Gold table DDL (PPM, forecasts, DQ) | SQL ready, not deployed |
| `databricks/sql/grants_odoo.sql` | UC grants (data-engineers, data-analysts) | SQL ready, not deployed |
| `notebooks/01_odoo_bronze_ingestion.py` | Lakehouse Federation ingestion notebook | Code ready, not run |
| `notebooks/tests/seed_synthetic.py` | Synthetic data generator for testing | Code ready, not run |
| `notebooks/tests/test_medallion_pipeline.py` | Full B->S->G test pipeline | Code ready, not run |
| `databricks/pipelines/medallion_test_dlt.py` | DLT pipeline with expectations | Code ready, not run |
| `databricks/bundles/medallion_test_job.yml` | DAB job definition for test harness | Scaffolded, not deployed |

### Two Parallel Catalog Naming Schemes

The code references **two different catalog names**, creating ambiguity:

1. **`ipai`** -- used in `notebooks/01_odoo_bronze_ingestion.py` (federation notebook)
2. **`dbw_ipai_dev`** -- used in `notebooks/tests/seed_synthetic.py` and `test_medallion_pipeline.py`
3. **`dev_ppm`** / `ppm` -- used in `databricks.yml` DAB config
4. **`ipai_lakehouse_dev`** -- declared in `workspace.yaml` SSOT

These four naming schemes have never been reconciled.

---

## Network Topology

```
[Odoo PG: pg-ipai-odoo]
    ├── Public access: enabled
    ├── wal_level: logical (Fabric-ready)
    └── fabricMirroring: null (NOT active)

[ADLS: stipaidevlake]
    ├── 6 containers: bronze, silver, gold, platinum, checkpoints, iceberg
    ├── HNS: enabled (ADLS Gen2)
    └── CLI user: NO blob read access

[Databricks: dbw-ipai-dev]
    ├── VNet injected (10.10.0.0/16)
    ├── Secure cluster connectivity: true
    ├── Unity Catalog: metastore "pending"
    └── CLI auth: databricks-cli (token status unknown)

[Fabric: NOT DEPLOYED]
[Power BI: NOT DEPLOYED]
```

---

*Discovered 2026-03-28 via Azure CLI + repo analysis*
