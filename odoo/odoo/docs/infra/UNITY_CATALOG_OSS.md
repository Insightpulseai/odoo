# Unity Catalog (Open Source)

Databricks open-sourced Unity Catalog as the industry's first universal catalog for data and AI governance.

## Overview

Unity Catalog OSS provides:
- **Universal interface** for any data format and compute engine
- **Open APIs** built on OpenAPI spec (Apache 2.0 license)
- **Multi-format support**: Delta Lake, Apache Iceberg, Parquet, CSV
- **Asset catalog**: Tables, files, functions, AI models

Hosted by [LF AI & Data](https://lfaidata.foundation/) (Linux Foundation).

## Compatibility

| Interface | Status |
|-----------|--------|
| Apache Hive Metastore API | Compatible |
| Apache Iceberg REST Catalog API | Full support (GA read, Preview write) |
| Delta Lake UniForm | Read via Iceberg/Hudi clients |

### Supported Compute Engines

- Databricks (native)
- Apache Spark
- Trino
- Snowflake
- Amazon EMR
- Any Iceberg-compatible engine

## Key Features (2025)

### Generally Available

| Feature | Description |
|---------|-------------|
| **Iceberg REST Catalog API (Read)** | External engines read Unity-managed Iceberg tables |
| **Unity Catalog Metrics** | Business metrics as first-class lakehouse assets |
| **External Lineage** | Augment auto-captured lineage with external workflows |

### Public Preview

| Feature | Description |
|---------|-------------|
| **Iceberg REST Catalog API (Write)** | External engines write to Unity-managed tables |
| **Managed Iceberg Tables** | Full integration with predictive optimization |
| **Foreign Iceberg Tables** | Read Iceberg from HMS, Glue, Snowflake Horizon |
| **Attribute-Based Access Control (ABAC)** | Dynamic tag-driven access policies |

### Coming Soon

| Feature | Description |
|---------|-------------|
| **Domains** | Organize data by business area |
| **Certifications & Deprecation Tags** | Signal data trust and relevance |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Unity Catalog (Governance)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  Catalogs   │  │   Schemas   │  │   Tables    │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│         │                │                │                      │
│         └────────────────┼────────────────┘                      │
│                          ▼                                       │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   Access Control                         │    │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐     │    │
│  │  │  RBAC   │  │  ABAC   │  │ Row/Col │  │ Lineage │     │    │
│  │  │ (roles) │  │ (tags)  │  │ (masks) │  │ (audit) │     │    │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘     │    │
│  └─────────────────────────────────────────────────────────┘    │
│                          │                                       │
│         ┌────────────────┼────────────────┐                      │
│         ▼                ▼                ▼                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ Delta Lake  │  │   Iceberg   │  │   Parquet   │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                          │
    ┌─────────────────────┼─────────────────────┐
    ▼                     ▼                     ▼
┌─────────┐        ┌─────────────┐        ┌─────────┐
│Databricks│        │   Trino     │        │Snowflake│
│ (native) │        │(Iceberg API)│        │(Iceberg)│
└─────────┘        └─────────────┘        └─────────┘
```

## Integration with InsightPulseAI

### Namespace Convention

```
unity_catalog
├── ipai_bronze          # Raw ingestion (Lakeflow Connect)
│   ├── salesforce_raw
│   ├── workday_raw
│   ├── jira_raw
│   └── odoo_export
├── ipai_silver          # Cleaned/normalized
│   ├── sales_normalized
│   ├── hr_normalized
│   └── dev_metrics
├── ipai_gold            # Business-ready
│   ├── finance_ppm
│   ├── bir_compliance
│   └── executive_kpis
└── ipai_ml              # ML assets
    ├── models
    ├── features
    └── experiments
```

### Access Control Setup

```sql
-- Create catalog for IPAI
CREATE CATALOG IF NOT EXISTS ipai;

-- Create schemas (medallion)
CREATE SCHEMA IF NOT EXISTS ipai.bronze;
CREATE SCHEMA IF NOT EXISTS ipai.silver;
CREATE SCHEMA IF NOT EXISTS ipai.gold;
CREATE SCHEMA IF NOT EXISTS ipai.ml;

-- Grant access by team
GRANT USAGE ON CATALOG ipai TO `data-engineers`;
GRANT ALL PRIVILEGES ON SCHEMA ipai.bronze TO `data-engineers`;
GRANT SELECT ON SCHEMA ipai.gold TO `analysts`;
GRANT SELECT ON SCHEMA ipai.gold TO `bi-team`;

-- ABAC: Tag-based access (Preview)
ALTER TABLE ipai.gold.finance_ppm SET TAGS ('pii' = 'false', 'domain' = 'finance');
```

### External Engine Access

For Trino/Superset to read Unity Catalog tables:

```sql
-- Trino connector config (iceberg catalog)
connector.name=iceberg
iceberg.catalog.type=rest
iceberg.rest-catalog.uri=https://<workspace>.cloud.databricks.com/api/2.1/unity-catalog/iceberg
iceberg.rest-catalog.warehouse=<catalog_name>
```

### Lineage Integration

Unity Catalog auto-captures lineage from Databricks jobs. For external workflows:

```python
# Add external lineage metadata
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# Register external upstream dependency
w.lineage.create_lineage_edge(
    source_table="external.erp.orders",  # External system
    target_table="ipai.bronze.odoo_orders",  # Unity table
    source_type="EXTERNAL"
)
```

## Open Source Deployment

For self-hosted Unity Catalog OSS:

```bash
# Clone Unity Catalog OSS
git clone https://github.com/unitycatalog/unitycatalog.git
cd unitycatalog

# Build and run
./build/sbt package
./bin/start-uc-server

# Server runs on http://localhost:8080
```

### Docker Deployment

```yaml
# docker-compose.yml
services:
  unity-catalog:
    image: unitycatalog/unitycatalog:latest
    ports:
      - "8080:8080"
    environment:
      - UC_SERVER_PORT=8080
      - UC_STORAGE_ROOT=/data
    volumes:
      - ./data:/data
```

## Metrics (Unity Catalog Metrics)

Define business metrics as first-class assets:

```sql
-- Create metric definition
CREATE METRIC ipai.gold.monthly_revenue AS
  SELECT SUM(amount) FROM ipai.gold.sales
  WHERE date BETWEEN start_date AND end_date
  GROUP BY month;

-- Use metric in queries
SELECT * FROM METRIC(ipai.gold.monthly_revenue, '2025-01-01', '2025-12-31');
```

## References

- [Unity Catalog Product Page](https://www.databricks.com/product/unity-catalog)
- [Unity Catalog Documentation](https://docs.databricks.com/aws/en/data-governance/unity-catalog/)
- [Unity Catalog OSS](https://www.unitycatalog.io/)
- [Open Sourcing Unity Catalog Blog](https://www.databricks.com/blog/open-sourcing-unity-catalog)
- [What's New at Data + AI Summit 2025](https://www.databricks.com/blog/whats-new-databricks-unity-catalog-data-ai-summit-2025)
