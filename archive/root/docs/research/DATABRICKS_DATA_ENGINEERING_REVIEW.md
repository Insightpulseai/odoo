# Databricks Data Engineering -- Product Review & IPAI Stack Relevance

**Source URL**: `https://www.databricks.com/product/data-engineering#use-cases`
**Research Date**: 2026-03-07
**Branch**: `claude/review-signavio-url-HffM8`

> Databricks Lakeflow is a unified data engineering platform for ingestion, transformation, and orchestration built on Apache Spark + Delta Lake. This review covers the product page's features and use cases, and assesses relevance to our self-hosted Odoo CE + PostgreSQL + Supabase + n8n stack.

---

## Table of Contents

1. [Product Overview](#1-product-overview)
2. [Lakeflow Components](#2-lakeflow-components)
3. [Spark Declarative Pipelines (formerly DLT)](#3-spark-declarative-pipelines-formerly-dlt)
4. [Lakeflow Connect (Ingestion)](#4-lakeflow-connect-ingestion)
5. [Lakeflow Jobs (Orchestration)](#5-lakeflow-jobs-orchestration)
6. [Medallion Architecture](#6-medallion-architecture)
7. [Use Cases](#7-use-cases)
8. [Pricing](#8-pricing)
9. [Competitive Landscape](#9-competitive-landscape)
10. [IPAI Stack Parity Analysis](#10-ipai-stack-parity-analysis)
11. [Verdict & Recommendations](#11-verdict--recommendations)

---

## 1. Product Overview

| Attribute | Value |
|-----------|-------|
| **Product** | Databricks Lakeflow (Unified Data Engineering) |
| **Owner** | Databricks, Inc. |
| **Rebranded** | June 2025 (Data + AI Summit); unified under "Lakeflow" |
| **Engine** | Apache Spark + Photon (C++ native query engine) |
| **Storage** | Delta Lake (open-source, ACID on data lakes) |
| **Governance** | Unity Catalog (access control, audit, lineage) |
| **Deployment** | AWS, Azure, GCP (managed SaaS) |
| **Revenue** | $4B+ annual run-rate (company-wide); AI products alone at $1B |
| **Customers** | 60%+ of Fortune 500 |
| **Recognition** | Gartner Magic Quadrant Leader |

Databricks enables you to implement ETL pipelines to filter, enrich, clean, and aggregate data following the medallion architecture (Bronze → Silver → Gold), ready for analytics, AI, and BI.

---

## 2. Lakeflow Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Databricks Lakeflow                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐  ┌──────────────────┐  ┌───────────┐  │
│  │ Lakeflow        │  │ Spark Declarative│  │ Lakeflow  │  │
│  │ Connect         │  │ Pipelines (SDP)  │  │ Jobs      │  │
│  │ (Ingestion)     │  │ (Transformation) │  │ (Orch.)   │  │
│  └────────┬────────┘  └────────┬─────────┘  └─────┬─────┘  │
│           │                    │                   │         │
│           ▼                    ▼                   ▼         │
│  ┌─────────────────────────────────────────────────────────┐│
│  │              Delta Lake (ACID Storage)                   ││
│  │  Bronze (Raw) → Silver (Validated) → Gold (Enriched)    ││
│  └─────────────────────────────────────────────────────────┘│
│                           │                                  │
│  ┌─────────────────────────────────────────────────────────┐│
│  │              Unity Catalog (Governance)                  ││
│  │  Access Control │ Audit │ Lineage │ Data Discovery      ││
│  └─────────────────────────────────────────────────────────┘│
│                                                             │
│  Compute: Apache Spark + Photon │ Serverless │ Classic      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

| Component | Previous Name | Purpose |
|-----------|-------------|---------|
| **Lakeflow Connect** | (new) | Low-code/no-code data ingestion from SaaS, databases, files |
| **Spark Declarative Pipelines (SDP)** | Delta Live Tables (DLT) | Declarative ETL framework; batch + streaming + CDC |
| **Lakeflow Jobs** | Databricks Workflows | Multi-task orchestration; DAGs; scheduling; monitoring |

---

## 3. Spark Declarative Pipelines (formerly DLT)

### Core Capabilities

| Feature | Description |
|---------|-------------|
| **Declarative ETL** | Define *what* data should look like, not *how* to process it; SQL or Python |
| **Unified Batch + Streaming** | Single API for both modes; toggle between processing modes |
| **CDC (Change Data Capture)** | APPLY CHANGES API; SCD Type 1 & 2; auto-handles out-of-sequence records |
| **Data Quality Expectations** | Built-in quality constraints; fail/warn/drop on violation |
| **Auto-Optimization** | Automatic cluster management, scaling, Delta optimizations (liquid clustering) |
| **Incremental Processing** | Only process new/changed data; Auto Loader for cloud file ingestion |

### Pipeline Dataset Types

| Type | Purpose | Behavior |
|------|---------|----------|
| **Streaming Tables** | Append-only sources | Native Auto Loader support; real-time ingestion |
| **Materialized Views** | Pre-computed aggregations | Refreshed on each pipeline update; multi-consumer |
| **Views** | Intermediate queries | Not published outside pipeline; internal computation |

### SDP Editions

| Edition | Capabilities |
|---------|-------------|
| **Core** | Basic declarative pipelines; batch |
| **Pro** | + CDC APIs, + advanced streaming |
| **Advanced** | + SCD Type 2, + advanced data quality |

### Limitations

- Cannot run DLT notebooks directly (must run as pipeline)
- Cannot mix SQL and Python in same DLT notebook
- Less fine-grained control over Spark settings (declarative nature)
- Young but rapidly maturing technology

---

## 4. Lakeflow Connect (Ingestion)

### GA Connectors (as of June 2025)

| Category | Connectors |
|----------|-----------|
| **CRM / SaaS** | Salesforce Sales Cloud, Workday, Google Analytics 4, ServiceNow, SharePoint, Oracle NetSuite |
| **Databases** | Microsoft SQL Server, PostgreSQL |
| **ERP** | SAP (via SAP BDC Connect + Delta Sharing; zero-copy) |

### Upcoming Connectors

| Category | Connectors |
|----------|-----------|
| **Databases** | MySQL, IBM DB2, MongoDB, Amazon DynamoDB |
| **File** | SFTP, XML, Excel |
| **Data Warehouses** | Snowflake, Redshift |

### Key Features

| Feature | Description |
|---------|-------------|
| **Serverless** | 100% serverless; no cluster provisioning |
| **Incremental** | Efficient incremental reads/writes |
| **CDC** | Advanced CDC for real-time replication |
| **Governance** | Unity Catalog integration |
| **Private Link** | Database connectors support Private Link |
| **Zero-Copy** | Salesforce Data 360 + SAP BDC via Delta Sharing |

### Salesforce Integration (Deep Dive)

| Connector Type | Method | Data Movement |
|----------------|--------|---------------|
| **Ingestion Connector** | API-based extraction | Copies data into Delta Lake |
| **Data 360 File Sharing** | Delta Sharing | Zero-copy (no data movement) |
| **Data 360 Query Federation** | Lakehouse Federation | Zero-copy (query in place) |

---

## 5. Lakeflow Jobs (Orchestration)

| Feature | Description |
|---------|-------------|
| **Multi-task DAGs** | Complex dependency graphs; conditional execution; looping |
| **Task Types** | Notebooks, DLT pipelines, SQL, Python scripts, dbt, JAR, shell |
| **Triggers** | Scheduled (cron), file arrival, continuous, manual |
| **Observability** | Built-in monitoring; alerting; run history; lineage |
| **Serverless** | Serverless compute option |
| **Error Handling** | Automatic retries; failure notifications |

### vs Apache Airflow

| Aspect | Lakeflow Jobs | Apache Airflow |
|--------|--------------|----------------|
| **Setup** | Zero (managed) | Days-weeks (self-hosted) |
| **Best For** | Spark-centric workflows | Multi-system orchestration |
| **DAG Definition** | UI + YAML + API | Python code |
| **Integration** | Deep Databricks integration | 400+ operators (broader) |
| **Cost** | Included in DBU pricing | Free (self-hosted infra costs) |
| **Recommendation** | Use together (hybrid) | Use together (hybrid) |

---

## 6. Medallion Architecture

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   BRONZE     │    │   SILVER     │    │    GOLD      │
│   (Raw)      │───►│  (Validated) │───►│  (Enriched)  │
├──────────────┤    ├──────────────┤    ├──────────────┤
│ Raw state    │    │ Cleansed     │    │ Aggregated   │
│ All formats  │    │ Deduplicated │    │ Denormalized │
│ Append-only  │    │ Conformed    │    │ Read-optimized│
│ Source of    │    │ 3NF-like     │    │ Star/snowflake│
│ truth        │    │ "Just enough"│    │ Project-      │
│ Audit trail  │    │ transforms   │    │ specific     │
└──────────────┘    └──────────────┘    └──────────────┘
```

| Layer | Purpose | Data Model | Consumers |
|-------|---------|-----------|-----------|
| **Bronze** | Preserve raw data; single source of truth; enable reprocessing | Raw (original format) | Silver layer pipelines |
| **Silver** | Validate, cleanse, conform; "just enough" transforms | 3NF-like (normalized) | Gold layer pipelines, data scientists |
| **Gold** | Business-ready; aggregated; consumption-optimized | Star/snowflake (denormalized) | BI dashboards, reports, ML models, APIs |

### Delta Lake Foundation

| Feature | Description |
|---------|-------------|
| **ACID Transactions** | Reliable writes on data lakes |
| **Schema Enforcement** | Reject bad data at write time |
| **Schema Evolution** | Safely add/modify columns |
| **Time Travel** | Query historical versions; rollback |
| **Liquid Clustering** | Dynamic data layout optimization (replaces Z-ordering) |
| **Optimized Writes** | Automatic file compaction |
| **VACUUM** | Clean up old file versions |

---

## 7. Use Cases

### From the Product Page

| Use Case | Description | Databricks Feature |
|----------|------------|-------------------|
| **ETL/ELT Pipelines** | Filter, enrich, clean, aggregate data for analytics/AI/BI | SDP + Medallion Architecture |
| **Real-Time Streaming** | Process sensor, clickstream, IoT data in real-time | Structured Streaming + SDP |
| **Change Data Capture** | Replicate database changes incrementally | APPLY CHANGES API (SCD 1 & 2) |
| **Data Warehousing** | Modern lakehouse-based DWH with AI capabilities | SQL Warehouses + Photon |
| **Data Ingestion** | Ingest from SaaS, databases, files, streams | Lakeflow Connect + Auto Loader |
| **Pipeline Orchestration** | Multi-task DAGs for complex workflows | Lakeflow Jobs |

### Industry Customer Stories

| Company | Industry | Use Case | Result |
|---------|----------|----------|--------|
| **Block** | Finance | GenAI apps & financial services | 12x reduction in computing costs |
| **Mastercard** | Finance | Delta Lake pipeline optimization | 80% query time reduction, 70% storage reduction |
| **Minecraft** | Gaming | Data processing modernization | 66% processing time reduction |
| **Edmunds** | Automotive | Vehicle inventory system migration | Processing cut from 4h to 15min |
| **Porsche** | Automotive | CRM data ingestion via Salesforce connector | Improved customer experience |
| **Volvo** | Automotive | Real-time global spare parts inventory | Hundreds of thousands of parts |
| **Hinge Health** | Healthcare | Patient care personalization | 10x data growth managed |
| **Shell** | Energy | Data governance with Unity Catalog | Business-owned data products |
| **Corning** | Manufacturing | Data orchestration across teams | Automated medallion pipelines |
| **Albertsons** | Retail | Pricing analytics model serving | Near real-time response |
| **Supercell** | Gaming | Privacy-compliant real-time insights | Scalable data platform |
| **Alabama Power** | Energy | Grid management + storm preparedness | Predictive analytics for reliability |

### Common Patterns

| Pattern | Description |
|---------|-------------|
| **Batch ETL** | Scheduled loads from databases/files → Bronze → Silver → Gold |
| **Streaming ETL** | Continuous ingestion from Kafka/Event Hubs → streaming tables |
| **CDC Replication** | Database CDC → APPLY CHANGES → SCD Type 1/2 |
| **Hybrid Batch+Streaming** | Mix modes in same pipeline; toggle per source |
| **Data Quality Gates** | Expectations at each medallion layer |
| **Multi-Team Orchestration** | Lakeflow Jobs coordinating across teams |

---

## 8. Pricing

### Pricing Model: Databricks Units (DBU)

DBU = unit of processing capability, consumed per hour of compute usage.

**Cost = DBU consumed × $/DBU rate + Cloud infrastructure costs**

### DBU Rates (2026)

| Workload | Standard | Premium | Enterprise |
|----------|----------|---------|-----------|
| **All-Purpose Compute** | Deprecated | ~$0.55/DBU | ~$0.65/DBU |
| **Jobs Compute** | Deprecated | ~$0.25/DBU | ~$0.30/DBU |
| **SQL Warehouses** | Deprecated | ~$0.35/DBU | ~$0.40/DBU |
| **Serverless SQL** | -- | ~$0.70/DBU | ~$0.70/DBU |
| **DLT (Core)** | -- | ~$0.20/DBU | -- |
| **DLT (Pro)** | -- | ~$0.25/DBU | -- |
| **DLT (Advanced)** | -- | ~$0.36/DBU | -- |

**Note**: Standard tier EOL October 2025 (AWS/GCP) / October 2026 (Azure). All must migrate to Premium.

### Typical Monthly Costs

| Team Size | Databricks DBUs | Cloud Infra | Total |
|-----------|----------------|-------------|-------|
| Small (1-3 engineers) | $500-$2,000 | $500-$2,000 | **$1,000-$4,000** |
| Medium (5-10 engineers) | $2,000-$10,000 | $2,000-$10,000 | **$4,000-$20,000** |
| Large (20+ engineers) | $10,000-$100,000+ | $10,000-$100,000+ | **$20,000-$200,000+** |

### Hidden Costs

| Cost | Detail |
|------|--------|
| **Cloud Infrastructure** | 50-200% of DBU charges; often underestimated |
| **Photon** | Higher DBU rate for native acceleration |
| **Unity Catalog** | Included in Premium/Enterprise (not Standard) |
| **Serverless** | Single bill (DBU includes infra) but higher rate |
| **Egress** | Cloud provider egress fees |

### Savings Options

| Option | Savings |
|--------|---------|
| **Committed Use (DBCU)** | Up to 37% off pay-as-you-go (1-3 year commitment) |
| **Spot/Preemptible Instances** | Up to 90% off on-demand (for fault-tolerant workloads) |
| **Serverless** | Eliminates cluster idle costs |
| **Auto-scaling** | Scale to zero when not in use |

---

## 9. Competitive Landscape

### Databricks vs Alternatives for Data Engineering

| Platform | Type | Best For | Typical Cost |
|----------|------|----------|-------------|
| **Databricks Lakeflow** | Managed Spark + Delta Lake | Large-scale ETL, streaming, ML pipelines | $1K-$200K+/mo |
| **Snowflake** | Managed DWH | SQL-centric analytics, data sharing | $1K-$100K+/mo |
| **Apache Spark** (self-hosted) | Open-source engine | Maximum control; strong engineering team | Infra + 4 FTE SREs |
| **Apache Airflow** (self-hosted) | Open-source orchestrator | Multi-system orchestration | $500-$5K/mo infra |
| **dbt** | Transformation framework | SQL-first transformations | Free (Core) / $100+/mo (Cloud) |
| **Fivetran / Airbyte** | Managed ingestion | SaaS connector library | $1-$50K/mo |
| **Google BigQuery** | Managed DWH | Serverless SQL analytics | Pay-per-query |
| **Amazon Redshift** | Managed DWH | AWS-native analytics | $0.25-$13.04/hr |
| **Apache Flink** | Stream processing | Pure real-time stream processing | Self-hosted |
| **Tinybird** | Real-time analytics | Low-latency APIs over streaming data | Free-$599/mo |

### Self-Hosted Open-Source Stack Comparison

| Capability | Databricks | Open-Source Equivalent |
|-----------|-----------|----------------------|
| Spark Engine | Managed + Photon | Apache Spark (self-managed) |
| Delta Lake | Managed + optimized | Delta Lake OSS / Apache Iceberg / Hudi |
| Orchestration | Lakeflow Jobs | Apache Airflow / Dagster / Prefect |
| Ingestion | Lakeflow Connect | Airbyte (open-source) / Singer |
| Data Quality | SDP Expectations | Great Expectations / Soda |
| Governance | Unity Catalog | Apache Atlas / OpenMetadata |
| SQL Analytics | SQL Warehouses | Trino / Presto / DuckDB |
| CDC | APPLY CHANGES API | Debezium + Kafka Connect |

**Trade-off**: Self-hosted costs ~$500-5K/mo in infrastructure but requires 2-4 FTE engineers for management. One team reported: "We ran self-managed Spark thinking we'd save. We ended up with 4 full-time SREs. Total cost exceeded Databricks when you count salaries."

---

## 10. IPAI Stack Parity Analysis

### What Databricks Offers vs What We Have

| Databricks Feature | IPAI Stack Equivalent | Parity | Notes |
|-------------------|----------------------|--------|-------|
| **ETL Pipelines** | n8n + PostgreSQL views + Python scripts | 70% | n8n is integration-focused, not Spark-scale |
| **Streaming** | Supabase Realtime + pg_cron | 40% | No Structured Streaming equivalent |
| **CDC** | Supabase Realtime (Postgres Changes) | 50% | Basic CDC; no SCD Type 2 |
| **Data Quality** | PostgreSQL constraints + CHECK | 30% | No declarative expectations framework |
| **Orchestration** | n8n workflows | 80% | Strong for integrations; weaker for data DAGs |
| **SQL Analytics** | PostgreSQL + Superset | 75% | Good for our scale; no Photon acceleration |
| **Governance** | Supabase RLS + PostgreSQL roles | 60% | No lineage, no data discovery |
| **Ingestion** | n8n connectors + custom scripts | 65% | Fewer pre-built connectors |
| **Medallion Architecture** | PostgreSQL schemas (raw/clean/gold) | 60% | Can implement pattern; no Delta Lake features |

### Do We Need Databricks?

**Short answer: No.**

| Question | Answer |
|----------|--------|
| Do we process petabytes? | No. Our data is in PostgreSQL, manageable at current scale. |
| Do we need real-time streaming at scale? | No. Supabase Realtime + pg_cron covers our needs. |
| Do we run ML training pipelines? | Minimal. scikit-learn on DO droplet suffices. |
| Do we need 60%+ Fortune 500 scale? | No. We're a cost-minimized small team. |
| Budget for $1K-200K/mo? | No. Our entire infra is ~$50-100/mo. |

### What's Actually Useful (Concepts to Borrow)

| Concept | IPAI Implementation | Priority |
|---------|-------------------|----------|
| **Medallion Architecture** | PostgreSQL schemas: `raw.*`, `clean.*`, `gold.*` | P2 |
| **Declarative Data Quality** | PostgreSQL CHECK constraints + `ipai_data_quality` module | P3 |
| **CDC for Odoo** | Supabase Realtime `postgres_changes` on Odoo mirror tables | P2 |
| **Data Lineage** | Lightweight lineage in `ops.data_lineage` table | P3 |
| **Incremental Processing** | PostgreSQL `updated_at` tracking + n8n scheduled flows | P2 |

---

## 11. Verdict & Recommendations

### Verdict: **Do NOT adopt Databricks**

| Criterion | Assessment |
|-----------|-----------|
| **Cost** | $1K-200K+/mo vs our $50-100/mo infrastructure. 10-2000x our budget. |
| **Scale** | Built for petabyte-scale Fortune 500. Our PostgreSQL handles our data fine. |
| **Complexity** | Requires Spark expertise (Python/Scala); steep learning curve |
| **Self-Hosting** | Not self-hostable (managed SaaS only); contradicts our philosophy |
| **Vendor Lock-in** | High (Unity Catalog, Photon, Lakeflow Jobs are proprietary) |
| **Open Source** | Delta Lake and Spark are OSS, but Databricks' value-add is proprietary |

### Recommendations

1. **No action required** -- PostgreSQL + n8n + Superset + Supabase covers our data engineering needs at <0.1% of Databricks cost.

2. **Borrow Medallion Architecture pattern** (P2):
   ```sql
   -- Implement in PostgreSQL
   CREATE SCHEMA IF NOT EXISTS raw;    -- Bronze: raw ingested data
   CREATE SCHEMA IF NOT EXISTS clean;  -- Silver: validated, deduplicated
   CREATE SCHEMA IF NOT EXISTS gold;   -- Gold: aggregated, consumption-ready
   ```

3. **Borrow CDC pattern** (P2) via Supabase:
   ```typescript
   supabase
     .channel('odoo-mirror')
     .on('postgres_changes',
       { event: '*', schema: 'odoo_mirror', table: '*' },
       (payload) => processChange(payload)
     )
     .subscribe()
   ```

4. **Borrow Data Quality pattern** (P3):
   ```sql
   -- Declarative expectations (PostgreSQL-native)
   ALTER TABLE clean.invoices ADD CONSTRAINT expect_positive_amount
     CHECK (amount > 0);
   ALTER TABLE clean.invoices ADD CONSTRAINT expect_valid_partner
     CHECK (partner_id IS NOT NULL);
   ```

5. **If we ever need Spark-scale processing**, evaluate **self-hosted Apache Spark + Airflow + Delta Lake OSS** before considering Databricks. Cost would be ~$500-5K/mo vs $1K-200K+/mo.

### Cost Comparison Summary

| Solution | Monthly Cost | Annual Cost | Notes |
|----------|-------------|-------------|-------|
| **IPAI Stack** (current) | $50-$100 | $600-$1,200 | PostgreSQL + n8n + Superset on DO |
| **Databricks** (small team) | $1,000-$4,000 | $12,000-$48,000 | Plus cloud infra |
| **Databricks** (medium team) | $4,000-$20,000 | $48,000-$240,000 | Plus cloud infra |
| **Self-hosted Spark** | $500-$5,000 | $6,000-$60,000 | Plus 2-4 FTE engineers |

---

## Sources

- [Databricks Lakeflow: Unified Data Engineering](https://www.databricks.com/product/data-engineering)
- [Spark Declarative Pipelines (SDP)](https://www.databricks.com/product/data-engineering/spark-declarative-pipelines)
- [Lakeflow Connect](https://www.databricks.com/product/data-engineering/lakeflow-connect)
- [Delta Live Tables Overview](https://www.databricks.com/resources/demos/videos/data-engineering/delta-live-tables-overview)
- [Getting Started with SDP](https://www.databricks.com/discover/pages/getting-started-with-delta-live-tables)
- [Medallion Architecture](https://www.databricks.com/glossary/medallion-architecture)
- [Medallion Architecture (AWS Docs)](https://docs.databricks.com/aws/en/lakehouse/medallion)
- [Data Ingestion Reference Architecture](https://www.databricks.com/resources/architectures/data-ingestion-reference-architecture)
- [Intelligent Data Warehousing](https://www.databricks.com/resources/architectures/intelligent-data-warehousing-on-databricks)
- [Batch vs Streaming](https://docs.databricks.com/aws/en/data-engineering/batch-vs-streaming)
- [CDC Tutorial](https://docs.databricks.com/aws/en/ldp/tutorial-pipelines)
- [APPLY CHANGES CDC API](https://docs.databricks.com/aws/en/ldp/cdc)
- [Salesforce Connector](https://www.databricks.com/blog/introducing-salesforce-connectors-lakehouse-federation-and-lakeflow-connect)
- [SAP + Salesforce Integration](https://www.databricks.com/blog/sap-and-salesforce-data-integration-supplier-analytics-databricks)
- [Databricks Pricing](https://www.databricks.com/product/pricing)
- [Databricks Pricing Guide 2026 (Mammoth)](https://mammoth.io/blog/databricks-pricing/)
- [Databricks Pricing Guide 2026 (Flexera)](https://www.flexera.com/blog/finops/databricks-pricing-guide/)
- [Databricks Pricing Guide 2026 (CloudForecast)](https://www.cloudforecast.io/guides/databricks-pricing-costs-guide/)
- [Databricks Pricing Guide 2026 (Revefi)](https://www.revefi.com/blog/databricks-pricing-guide)
- [Customer Stories](https://www.databricks.com/customers)
- [100+ Data & AI Use Cases](https://www.databricks.com/blog/data-intelligence-action-100-data-and-ai-use-cases-databricks-customers)
- [Databricks vs Apache Spark](https://build5nines.com/databricks-vs-apache-spark-key-differences-and-when-to-use-each/)
- [Databricks Workflows vs Airflow (Astronomer)](https://www.astronomer.io/blog/comparing-data-orchestration-databricks-workflows-vs-apache-airflow-part-1/)
- [Databricks Alternatives (Tinybird)](https://www.tinybird.co/blog/databricks-alternatives)
- [DLT Best Practices (B EYE)](https://b-eye.com/blog/databricks-delta-live-tables-guide/)
- [DS Stream: Declarative ETL with DLT](https://www.dsstream.com/post/create-declarative-etl-pipelines-in-databricks-with-delta-live-tables)

---

*Review compiled: 2026-03-07*
*Branch: claude/review-signavio-url-HffM8*
*See also: [DATABRICKS_ARCHITECTURES_INDEX.md](./DATABRICKS_ARCHITECTURES_INDEX.md) for reference architectures*
