# Databricks + Tableau BI Connection — Platform Skill

> Source: https://learn.microsoft.com/en-us/azure/databricks/partners/bi/tableau
> Domain: `platform` / `lakehouse`
> Last validated: 2026-03-15

---

## What this skill is for

Agents connecting Tableau (Desktop, Cloud, or Server) to Databricks Unity Catalog
use this skill to configure connections, optimize performance, and publish dashboards
fed by DLT Gold layer tables.

---

## Connection Methods

### 1. Partner Connect (Fastest)

```
Workspace sidebar → Marketplace → Partner Connect → Tableau tile
  → Select compute resource → Download .tds connection file
  → Open in Tableau Desktop → authenticate
```

### 2. Explore in Tableau Cloud (Direct from Catalog)

```
Catalog Explorer → Select schema/table → "Use with BI tools"
  → "Explore in Tableau Cloud" → OAuth sign-in
```

**Requirements**: Unity Catalog enabled compute, no Hive metastore.

### 3. Manual Connection (Tableau Desktop)

```
File → New → Connect to Data → Databricks connector
  → Server Hostname + HTTP Path → authenticate
```

### 4. Manual Connection (Tableau Cloud)

```
Data → New Data Source → Connectors → Databricks
  → Server Hostname + HTTP Path → authenticate → Sign In
```

---

## IPAI Connection Parameters

| Parameter | Value |
|-----------|-------|
| **Server Hostname** | `adb-7405610347978231.11.azuredatabricks.net` |
| **HTTP Path** | (from SQL warehouse or cluster advanced options) |
| **Catalog** | `ipai_gold` (prod) / `dev_ipai` (dev) |
| **Default Schema** | `gold` |
| **Auth Method** | Microsoft Entra ID (recommended) or PAT |
| **ODBC Driver** | Databricks ODBC >= 2.6.15 |

### Unity Catalog Configuration

In the Tableau **Advanced** tab:

```
Catalog=ipai_gold
```

Or via **Initial SQL**:

```sql
USE CATALOG ipai_gold;
USE SCHEMA gold;
```

---

## Authentication Options

| Method | When | IPAI Pattern |
|--------|------|--------------|
| Microsoft Entra ID | Tableau Cloud + Desktop | Recommended — SSO via Entra |
| Personal Access Token | Automated/service accounts | Service principal PAT from Key Vault |
| OAuth (user passthrough) | Per-user access control | Entra OIDC flow |

**Security**: Use service principal PATs for automated refresh. Never embed user PATs in published workbooks. Credentials via Azure Key Vault (`kv-ipai-dev`).

---

## Gold Tables Available to Tableau

All from DLT pipeline `finance_bir_pipeline.sql` → `ipai_gold.gold.*`:

| Table | Description | Dashboard Use |
|-------|-------------|---------------|
| `monthly_close_summary` | Revenue/expenses/net income by period | KPI cards, line charts |
| `bir_withholding_tax_1601c` | Monthly withholding tax for BIR filing | Bar charts by period |
| `aging_receivables` | AR aging buckets (current/30/60/90/90+) | Stacked bar, heatmap |
| `aging_payables` | AP aging buckets by vendor | Table, bar chart |
| `expense_analytics` | HR expenses with BIR deductibility flags | Pie chart, table |
| `bir_compliance_tracker` | Cross-form compliance status | Status table, KPIs |
| `timesheet_utilization` | Team utilization % by project | Heatmap, scatter |
| `project_profitability` | Project margin analysis | Scatter, waterfall |

### PK/FK Constraints for Tableau Relationships

Databricks Runtime 15.2+ supports informational PK/FK constraints. Tableau auto-detects these at the physical layer. Define in Gold:

```sql
-- Enable Tableau auto-relationship detection
ALTER TABLE ipai_gold.gold.aging_receivables
ADD CONSTRAINT pk_aging_receivables PRIMARY KEY (partner_id, company_id) NOT ENFORCED;

ALTER TABLE ipai_gold.gold.bir_compliance_tracker
ADD CONSTRAINT pk_bir_compliance PRIMARY KEY (fiscal_period) NOT ENFORCED;

ALTER TABLE ipai_gold.gold.bir_compliance_tracker
ADD CONSTRAINT fk_bir_close FOREIGN KEY (fiscal_period)
REFERENCES ipai_gold.gold.monthly_close_summary (fiscal_period) NOT ENFORCED;
```

---

## Performance Optimization

### Connection-Level

| Setting | Value | Why |
|---------|-------|-----|
| `RowsFetchedPerBlock` | `100000` | Optimize heap memory for large results |
| `UseNativeQuery` | `1` | Push SQL directly to Databricks |
| `AutoReconnect` | `1` | Handle transient disconnects |

Apply via `.tds` file:
```
odbc-connect-string-extras='AutoReconnect=1,UseNativeQuery=1,RowsFetchedPerBlock=100000'
```

Or via `.tdc` file in `Documents/My Tableau Repository/Datasources/`:
```xml
<?xml version='1.0' encoding='utf-8' ?>
<connection-customization class='databricks' enabled='true' version='10.0'>
  <vendor name='databricks' />
  <driver name='databricks' />
  <customizations>
    <customization name='odbc-connect-string-extras'
      value='AutoReconnect=1,UseNativeQuery=1,RowsFetchedPerBlock=100000' />
  </customizations>
</connection-customization>
```

### Dashboard-Level

1. **Context filters** for static filters (don't change often)
2. **if/else** over **case/when** in calculated fields
3. **Push down filters** to data source (Databricks handles filtering)
4. **Avoid table calculations** (full dataset scan) — use Gold pre-aggregations instead
5. **Limit quick filters** — each filter on 5 charts = 10+ queries to Databricks
6. **Use actions** to drill between dashboards instead of multi-filter single dashboards
7. **Aggregate first** — Gold views are pre-aggregated; avoid granular mark explosion

### Caching Strategy

| Layer | Description | IPAI Recommendation |
|-------|-------------|---------------------|
| Tiles | Same dashboard reuses rendered tiles | Default on |
| Model | Mathematical calculation cache | Default on |
| Abstract | Aggregate query result cache | Default on |
| Native | Exact query match cache | Default on |

**Server setting**: "Refresh Less Often" (12h cache) for recurring dashboards (e.g., Monday morning BIR review). "Refresh More Often" for real-time monitoring.

**Cache warming**: Schedule Tableau subscription to render before viewing time.

---

## Tableau Server on Linux

`/etc/odbcinst.ini`:
```ini
[Simba Spark ODBC Driver 64-bit]
Description=Simba Spark ODBC Driver (64-bit)
Driver=/opt/simba/spark/lib/64/libsparkodbc_sb64.so
```

---

## Publishing Workflow

```
Tableau Desktop
  → Extract data (Data → <source> → Extract Data)
  → Publish data source to Tableau Cloud (Server → Publish Data Source)
  → Set refresh schedule (OAuth, "Allow refresh access")
  → Publish workbook (Server → Publish Workbook)
  → Tableau Cloud auto-refreshes on schedule
```

---

## IPAI Integration Architecture

```
Odoo PG (SOR)
  ↓ CDC
Supabase ETL → Iceberg → ADLS Bronze
  ↓ DLT Pipeline
Databricks Silver → Gold (ipai_gold.gold.*)
  ↓ Consumption
  ├── AI/BI Dashboard + Genie (native Databricks)
  ├── Tableau Cloud/Desktop (via Databricks connector)
  └── Apache Superset (via SQL warehouse JDBC)
```

---

## Anti-Patterns

1. **Using Hive metastore** — Unity Catalog required for Tableau Cloud explore
2. **Embedding user PATs in workbooks** — Use service principal + Key Vault
3. **Many quick filters on one dashboard** — Use actions + drill-through instead
4. **Table calculations on large datasets** — Pre-aggregate in Gold layer
5. **Connecting to Bronze/Silver** — Always connect Tableau to Gold only
6. **Skipping PK/FK constraints** — Define them for Tableau auto-relationship detection

---

## When to use this skill

- Connecting Tableau Desktop/Cloud/Server to Databricks workspace
- Publishing dashboards from Gold layer DLT tables
- Optimizing Tableau query performance against Databricks
- Setting up automated refresh schedules
- Configuring PK/FK constraints for Tableau data model

## When NOT to use this skill

- Native AI/BI Dashboard creation → use `finance_bir_dashboard.sql` directly
- Genie conversational analytics → native Databricks feature
- Superset BI → use JDBC/SQL warehouse connection
- DLT pipeline development → `databricks-data-engineering` skill
