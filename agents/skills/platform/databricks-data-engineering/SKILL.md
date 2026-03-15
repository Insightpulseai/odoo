# Skill: Databricks Data Engineering

source: databricks.com/product/data-engineering
extracted: 2026-03-15
applies-to: lakehouse, automations

## Core primitives

| Primitive | Use for |
|---|---|
| Delta Live Tables (DLT) | Declarative medallion pipelines (Bronze→Silver→Gold) |
| Lakeflow Jobs | Orchestrated multi-task workflows (cron, trigger, dependency) |
| Lakeflow Connect | Managed connectors (Salesforce, SharePoint, JDBC, Kafka) |
| Streaming (Spark Structured) | Real-time ingestion from Kafka/Event Hubs/Kinesis |
| DBSQL | Serverless SQL warehouse for analytics + transformations |
| Delta Sharing | Zero-copy data sharing to external consumers |

## DLT pipeline skeleton (standard for IPAI)

```python
import dlt
from pyspark.sql.functions import *

@dlt.table(
  name="silver_odoo_journal_entries",
  comment="Validated Odoo journal entries from Bronze",
  table_properties={"quality": "silver"}
)
@dlt.expect_all({
  "valid_amount": "amount IS NOT NULL AND amount != 0",
  "valid_date": "date >= '2020-01-01'",
  "valid_company": "company_id IS NOT NULL"
})
def silver_journal_entries():
  return (
    dlt.read_stream("bronze_odoo_journal_entries")
      .withColumn("ingested_at", current_timestamp())
      .dropDuplicates(["odoo_id", "company_id"])
  )
```

## Key 2025-2026 features for IPAI
- SQL Stored Procedures: encapsulate BIR report logic in SQL
- Recursive CTEs: org hierarchy + account tree traversals
- Spatial SQL 80+ functions: geospatial for Project Scout / retail
- Lakehouse Federation GA: query Supabase PG directly from Databricks (zero-copy)
- Multi-statement transactions (upcoming): atomic updates across tables
