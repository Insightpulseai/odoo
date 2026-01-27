# Databricks Implementation Guide for odoo-ce

---

**Purpose**: Step-by-step implementation guide following Azure Databricks best practices for data engineering, ML, and production deployment.

**Status**: IMPLEMENTATION READY
**Created**: 2026-01-26
**Based On**: Microsoft Learn Databricks Guides

---

## Implementation Phases Overview

```
Phase 1: Foundation (Weeks 1-4)
├── Workspace setup + Unity Catalog
├── Data discovery (Catalog Explorer)
├── File upload patterns
└── Auto Loader ingestion

Phase 2: ETL Pipeline (Weeks 5-8)
├── Lakeflow DLT pipelines
├── Bronze → Silver → Gold
├── Data quality expectations
└── Incremental processing

Phase 3: ML/AI (Weeks 9-12)
├── Feature engineering
├── MLflow model training
├── AI/BI Genie dashboards
└── Model serving

Phase 4: Production (Weeks 13-16)
├── Lakeflow Jobs orchestration
├── Asset Bundles deployment
├── Unity Catalog governance
└── Monitoring & optimization
```

---

## Phase 1: Foundation Setup

### Week 1: Workspace & Unity Catalog

**Objective**: Set up Databricks workspace with Unity Catalog for data governance

**Tasks**:

**1.1 Create Databricks Workspace**
```bash
# Prerequisites
# - Azure subscription
# - Resource group: odoo-ce-databricks
# - Location: Southeast Asia (Singapore)

# Create workspace via Azure CLI
az databricks workspace create \
  --resource-group odoo-ce-databricks \
  --name odoo-ce-databricks-prod \
  --location southeastasia \
  --sku premium
```

**1.2 Enable Unity Catalog**
```bash
# Unity Catalog provides:
# - Centralized metadata management
# - Fine-grained access control
# - Data lineage tracking
# - Cross-workspace catalog sharing

# Enable Unity Catalog (Azure Portal)
# Databricks Workspace → Configuration → Unity Catalog → Enable
```

**1.3 Create Metastore**
```python
# scripts/databricks/setup_unity_catalog.py
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# Create metastore (one-time setup)
metastore = w.metastores.create(
    name="odoo_ce_metastore",
    storage_root="abfss://unity-catalog@odoocedata.dfs.core.windows.net/",
    region="southeastasia"
)

# Assign metastore to workspace
w.metastores.assign(
    workspace_id="<workspace-id>",
    metastore_id=metastore.metastore_id
)

print(f"Unity Catalog metastore created: {metastore.metastore_id}")
```

**1.4 Create Catalogs**
```sql
-- Create catalogs for medallion architecture
CREATE CATALOG IF NOT EXISTS bronze
COMMENT 'Raw ingested data';

CREATE CATALOG IF NOT EXISTS silver
COMMENT 'Cleaned and validated data';

CREATE CATALOG IF NOT EXISTS gold
COMMENT 'Business-ready aggregated data';

-- Create schemas
CREATE SCHEMA IF NOT EXISTS bronze.scout_transactions;
CREATE SCHEMA IF NOT EXISTS silver.scout_transactions;
CREATE SCHEMA IF NOT EXISTS gold.bir_analytics;
```

**Acceptance Criteria**:
- ✅ Workspace created in Southeast Asia
- ✅ Unity Catalog enabled
- ✅ Metastore configured with Azure Storage
- ✅ 3 catalogs (bronze, silver, gold) created

---

### Week 2: Data Discovery & Catalog Explorer

**Objective**: Explore existing data and understand schema using Catalog Explorer

**Tasks**:

**2.1 Use Catalog Explorer (Web UI)**
```
1. Navigate to Databricks Workspace
2. Sidebar → Catalog
3. Browse catalogs, schemas, tables
4. View metadata:
   - Schema (columns, types)
   - Permissions (who has access)
   - Lineage (upstream/downstream dependencies)
   - History (Delta Lake time travel)
```

**2.2 Programmatic Discovery (Python SDK)**
```python
# scripts/databricks/discover_catalogs.py
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# List all catalogs
for catalog in w.catalogs.list():
    print(f"\nCatalog: {catalog.name}")
    print(f"  Owner: {catalog.owner}")
    print(f"  Created: {catalog.created_at}")

    # List schemas in catalog
    for schema in w.schemas.list(catalog_name=catalog.name):
        print(f"  Schema: {schema.name}")

        # List tables in schema
        for table in w.tables.list(catalog_name=catalog.name, schema_name=schema.name):
            print(f"    Table: {table.name} ({table.table_type})")
```

**2.3 Query Existing Tables**
```sql
-- Explore bronze data
SELECT * FROM bronze.scout_transactions.raw_exports LIMIT 10;

-- Check schema
DESCRIBE TABLE EXTENDED bronze.scout_transactions.raw_exports;

-- View table history (Delta Lake)
DESCRIBE HISTORY bronze.scout_transactions.raw_exports;
```

**Acceptance Criteria**:
- ✅ Catalog Explorer accessible
- ✅ All existing tables documented
- ✅ Schema metadata extracted
- ✅ Lineage visible for key tables

---

### Week 3: File Upload & Initial Data Load

**Objective**: Upload initial Scout transaction data using file upload UI

**Tasks**:

**3.1 Prepare Sample Data**
```bash
# Export sample transactions from Supabase
psql "$POSTGRES_URL" -c "
  COPY (
    SELECT transaction_id, agency, transaction_date, amount, category, vendor_id
    FROM scout.transactions
    WHERE transaction_date >= '2025-01-01'
    LIMIT 10000
  ) TO STDOUT WITH CSV HEADER
" > /tmp/scout_transactions_sample.csv
```

**3.2 Upload via Catalog Explorer UI**
```
1. Catalog Explorer → bronze catalog → scout_transactions schema
2. Click "Create Table" → "Upload File"
3. Select: /tmp/scout_transactions_sample.csv
4. Configure:
   - Table name: raw_exports
   - File format: CSV with header
   - Infer schema: Yes
5. Create table
```

**3.3 Validate Upload (SQL)**
```sql
-- Check row count
SELECT COUNT(*) FROM bronze.scout_transactions.raw_exports;
-- Expected: 10000

-- Validate schema
DESCRIBE bronze.scout_transactions.raw_exports;

-- Sample data
SELECT * FROM bronze.scout_transactions.raw_exports LIMIT 5;
```

**3.4 Create External Table (for production)**
```sql
-- Point to Azure Storage location
CREATE TABLE IF NOT EXISTS bronze.scout_transactions.raw_exports
USING DELTA
LOCATION 'abfss://bronze@odoocedata.dfs.core.windows.net/scout_transactions/raw_exports';
```

**Acceptance Criteria**:
- ✅ 10K sample transactions uploaded
- ✅ Schema correctly inferred
- ✅ External table configured
- ✅ Validation queries successful

---

### Week 4: Auto Loader Setup (Incremental Ingestion)

**Objective**: Configure Auto Loader for incremental file ingestion from Azure Storage

**Tasks**:

**4.1 Configure Azure Storage Connection**
```python
# scripts/databricks/setup_storage_credentials.py
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.catalog import StorageCredentialInfo, AzureServicePrincipal

w = WorkspaceClient()

# Create storage credential (service principal)
credential = w.storage_credentials.create(
    name="odoo_ce_storage_credential",
    azure_service_principal=AzureServicePrincipal(
        directory_id="<azure-tenant-id>",
        application_id="<azure-app-id>",
        client_secret="<azure-client-secret>"
    ),
    comment="Credential for odoo-ce Azure Storage"
)

print(f"Storage credential created: {credential.name}")
```

**4.2 Create External Location**
```python
# Grant access to storage container
w.external_locations.create(
    name="odoo_ce_raw_data",
    url="abfss://raw-data@odoocedata.dfs.core.windows.net/",
    credential_name="odoo_ce_storage_credential",
    comment="Raw data landing zone"
)
```

**4.3 Implement Auto Loader Notebook**
```python
# databricks/src/etl/autoloader_ingestion.py
# Databricks notebook source

from pyspark.sql.functions import current_timestamp, input_file_name

# Auto Loader configuration
source_path = "abfss://raw-data@odoocedata.dfs.core.windows.net/scout_transactions/"
checkpoint_path = "dbfs:/checkpoints/scout_autoloader"
target_table = "bronze.scout_transactions.raw_exports"

# Read streaming data with Auto Loader
df = (
    spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "json")  # or "csv"
    .option("cloudFiles.schemaLocation", checkpoint_path + "/schema")
    .option("cloudFiles.inferColumnTypes", "true")
    .option("cloudFiles.schemaEvolutionMode", "addNewColumns")
    .load(source_path)
)

# Add metadata columns
df_enriched = (
    df
    .withColumn("_ingestion_timestamp", current_timestamp())
    .withColumn("_source_file", input_file_name())
)

# Write to Delta Lake (streaming)
query = (
    df_enriched.writeStream
    .format("delta")
    .option("checkpointLocation", checkpoint_path)
    .option("mergeSchema", "true")
    .trigger(availableNow=True)  # Process all available files once
    .toTable(target_table)
)

query.awaitTermination()
print(f"Auto Loader ingestion complete: {target_table}")
```

**4.4 Schedule Auto Loader Job**
```yaml
# databricks/resources/jobs.yml
resources:
  jobs:
    autoloader_ingestion:
      name: "Auto Loader - Scout Transactions"
      tasks:
        - task_key: ingest
          notebook_task:
            notebook_path: ./src/etl/autoloader_ingestion.py
          new_cluster:
            spark_version: "14.3.x-scala2.12"
            node_type_id: "Standard_DS3_v2"
            num_workers: 2
      schedule:
        quartz_cron_expression: "0 */15 * * * ?"  # Every 15 minutes
        timezone_id: "Asia/Manila"
```

**Acceptance Criteria**:
- ✅ Storage credential configured
- ✅ External location accessible
- ✅ Auto Loader notebook tested
- ✅ Job scheduled (every 15 minutes)
- ✅ Schema evolution enabled

---

## Phase 2: ETL Pipeline (Lakeflow DLT)

### Week 5: Lakeflow DLT - Bronze to Silver

**Objective**: Build declarative DLT pipeline for data cleaning and validation

**Tasks**:

**5.1 Create DLT Pipeline Notebook**
```python
# databricks/src/etl/dlt_bronze_to_silver.py
# Databricks notebook source

import dlt
from pyspark.sql import functions as F

# Define expectations (data quality rules)
@dlt.table(
    name="silver_transactions",
    comment="Cleaned Scout transactions with quality checks",
    table_properties={
        "quality": "silver",
        "pipelines.autoOptimize.managed": "true"
    }
)
@dlt.expect_or_drop("valid_amount", "amount > 0")
@dlt.expect_or_drop("valid_date", "transaction_date IS NOT NULL")
@dlt.expect_or_drop("valid_agency", "agency IN ('RIM', 'CKVC', 'BOM', 'JPAL', 'JLI', 'JAP', 'LAS', 'RMQB')")
@dlt.expect_or_fail("unique_transaction_id", "COUNT(*) = COUNT(DISTINCT transaction_id)")
def silver_transactions():
    """Bronze → Silver: Clean and validate transactions"""
    return (
        dlt.read("bronze.scout_transactions.raw_exports")
        # Data type corrections
        .withColumn("amount", F.col("amount").cast("decimal(15,2)"))
        .withColumn("transaction_date", F.to_date("transaction_date", "yyyy-MM-dd"))
        # Null handling
        .withColumn("category", F.when(F.col("category").isNull(), "UNCATEGORIZED").otherwise(F.col("category")))
        # Deduplication (keep latest by timestamp)
        .withColumn("row_number", F.row_number().over(
            Window.partitionBy("transaction_id").orderBy(F.col("_ingestion_timestamp").desc())
        ))
        .filter(F.col("row_number") == 1)
        .drop("row_number")
        # Select final columns
        .select(
            "transaction_id",
            "agency",
            "transaction_date",
            "amount",
            "category",
            "vendor_id",
            "_ingestion_timestamp"
        )
    )
```

**5.2 Create DLT Pipeline Configuration**
```yaml
# databricks/resources/pipelines.yml
resources:
  pipelines:
    scout_etl:
      name: "Scout ETL Pipeline"
      storage: "dbfs:/pipelines/scout_etl"
      target: "silver"
      configuration:
        "pipelines.enableAutoOptimize": "true"
      libraries:
        - notebook:
            path: ./src/etl/dlt_bronze_to_silver.py
      clusters:
        - label: "default"
          autoscale:
            min_workers: 2
            max_workers: 8
          spark_conf:
            "spark.databricks.delta.optimizeWrite.enabled": "true"
      development: false
      continuous: false  # Triggered mode
      channel: "CURRENT"
```

**5.3 Deploy Pipeline via Asset Bundle**
```bash
# Deploy DLT pipeline
cd databricks
databricks bundle deploy -t prod

# Trigger pipeline run
databricks pipelines update scout_etl --full-refresh false
```

**5.4 Monitor Data Quality**
```sql
-- Check expectations summary
SELECT
    dataset,
    expectation,
    SUM(passed_records) as passed,
    SUM(failed_records) as failed,
    ROUND(100.0 * SUM(passed_records) / (SUM(passed_records) + SUM(failed_records)), 2) as pass_rate_pct
FROM event_log('scout_etl')
WHERE details:flow_progress.metrics IS NOT NULL
GROUP BY dataset, expectation
ORDER BY pass_rate_pct ASC;
```

**Acceptance Criteria**:
- ✅ DLT pipeline created and deployed
- ✅ Data quality expectations defined
- ✅ Pass rate >98% for all expectations
- ✅ Event log accessible for monitoring

---

### Week 6: Lakeflow DLT - Silver to Gold

**Objective**: Create business-ready gold tables with aggregations

**Tasks**:

**6.1 Define Gold Tables**
```python
# databricks/src/etl/dlt_silver_to_gold.py
# Databricks notebook source

import dlt
from pyspark.sql import functions as F

# Gold: BIR Monthly Aggregation
@dlt.table(
    name="gold_bir_monthly",
    comment="Monthly BIR tax aggregations by agency"
)
def gold_bir_monthly():
    """Silver → Gold: Monthly tax aggregations"""
    return (
        dlt.read("silver_transactions")
        .withColumn("year", F.year("transaction_date"))
        .withColumn("month", F.month("transaction_date"))
        .groupBy("agency", "year", "month")
        .agg(
            F.sum("amount").alias("total_amount"),
            F.count("transaction_id").alias("transaction_count"),
            F.countDistinct("vendor_id").alias("unique_vendors"),
            # BIR tax calculations
            F.sum(F.when(F.col("category") == "WITHHOLDING_TAX", F.col("amount")).otherwise(0)).alias("withholding_tax"),
            F.sum(F.when(F.col("category") == "INCOME_TAX", F.col("amount")).otherwise(0)).alias("income_tax"),
            F.sum(F.when(F.col("category") == "VAT", F.col("amount")).otherwise(0)).alias("vat")
        )
    )

# Gold: Category Analysis
@dlt.table(
    name="gold_category_analysis",
    comment="Transaction patterns by category"
)
def gold_category_analysis():
    """Silver → Gold: Category-level analytics"""
    return (
        dlt.read("silver_transactions")
        .groupBy("agency", "category")
        .agg(
            F.sum("amount").alias("total_amount"),
            F.count("transaction_id").alias("transaction_count"),
            F.avg("amount").alias("avg_amount"),
            F.min("transaction_date").alias("first_transaction"),
            F.max("transaction_date").alias("last_transaction")
        )
    )
```

**6.2 Update Pipeline Configuration**
```yaml
# Add gold transformations to pipeline
resources:
  pipelines:
    scout_etl:
      libraries:
        - notebook:
            path: ./src/etl/dlt_bronze_to_silver.py
        - notebook:
            path: ./src/etl/dlt_silver_to_gold.py  # New
```

**6.3 Query Gold Tables**
```sql
-- BIR monthly summary
SELECT
    agency,
    year,
    month,
    total_amount,
    withholding_tax,
    income_tax,
    vat
FROM silver.gold_bir_monthly
WHERE year = 2026
ORDER BY year DESC, month DESC, total_amount DESC;

-- Category analysis
SELECT
    agency,
    category,
    total_amount,
    transaction_count,
    avg_amount
FROM silver.gold_category_analysis
ORDER BY total_amount DESC
LIMIT 20;
```

**Acceptance Criteria**:
- ✅ 2+ gold tables created
- ✅ Business logic validated
- ✅ Query performance <5 seconds
- ✅ Data freshness <1 hour

---

### Weeks 7-8: Incremental Processing & Optimization

**7.1 Implement Incremental Load**
```python
# Update silver transformation for incremental processing
@dlt.table(
    name="silver_transactions",
    partition_cols=["transaction_date"]
)
@dlt.expect_or_drop("valid_amount", "amount > 0")
def silver_transactions():
    """Incremental load with watermark"""
    return (
        dlt.read_stream("bronze.scout_transactions.raw_exports")  # Streaming read
        .withWatermark("_ingestion_timestamp", "1 hour")  # Handle late data
        .dropDuplicates(["transaction_id"])
        # ... rest of transformation
    )
```

**7.2 Optimize Delta Tables**
```sql
-- Optimize gold tables (weekly maintenance)
OPTIMIZE silver.gold_bir_monthly
ZORDER BY (agency, year, month);

OPTIMIZE silver.gold_category_analysis
ZORDER BY (agency, category);

-- Vacuum old versions (retain 7 days)
VACUUM silver.gold_bir_monthly RETAIN 168 HOURS;
```

**Acceptance Criteria**:
- ✅ Incremental processing working
- ✅ Late data handled correctly
- ✅ Tables optimized (Z-ordering)
- ✅ Vacuum scheduled (weekly)

---

## Phase 3: ML/AI Integration

### Week 9: Feature Engineering

**Objective**: Create feature store for BIR tax forecasting

**Tasks**:

**9.1 Create Feature Table**
```python
# databricks/src/ml/create_feature_table.py
from databricks.feature_engineering import FeatureEngineeringClient
from pyspark.sql import functions as F
from pyspark.sql.window import Window

fe = FeatureEngineeringClient()

# Create feature table definition
fe.create_table(
    name="gold.ml_features.bir_forecasting",
    primary_keys=["agency", "year", "month"],
    schema="""
        agency STRING,
        year INT,
        month INT,
        prev_month_wht DECIMAL(15,2),
        prev_year_wht DECIMAL(15,2),
        rolling_avg_3m DECIMAL(15,2),
        rolling_avg_12m DECIMAL(15,2),
        transaction_velocity BIGINT,
        unique_vendors INT,
        update_timestamp TIMESTAMP
    """,
    description="Feature table for BIR tax forecasting"
)

# Compute features
df = spark.sql("""
    SELECT
        agency,
        year,
        month,
        withholding_tax,
        transaction_count,
        unique_vendors
    FROM silver.gold_bir_monthly
""")

# Add lag features
window_spec = Window.partitionBy("agency").orderBy("year", "month")

df_features = (
    df
    .withColumn("prev_month_wht", F.lag("withholding_tax", 1).over(window_spec))
    .withColumn("prev_year_wht", F.lag("withholding_tax", 12).over(window_spec))
    .withColumn("rolling_avg_3m", F.avg("withholding_tax").over(
        window_spec.rowsBetween(-2, 0)
    ))
    .withColumn("rolling_avg_12m", F.avg("withholding_tax").over(
        window_spec.rowsBetween(-11, 0)
    ))
    .withColumn("transaction_velocity", F.col("transaction_count"))
    .withColumn("update_timestamp", F.current_timestamp())
    .select(
        "agency", "year", "month",
        "prev_month_wht", "prev_year_wht",
        "rolling_avg_3m", "rolling_avg_12m",
        "transaction_velocity", "unique_vendors",
        "update_timestamp"
    )
)

# Write to feature store
fe.write_table(
    name="gold.ml_features.bir_forecasting",
    df=df_features,
    mode="merge"
)

print("Feature table populated")
```

**Acceptance Criteria**:
- ✅ Feature table created
- ✅ 8+ features computed
- ✅ Update timestamp tracked
- ✅ Features available for training

---

### Week 10: MLflow Model Training

**Objective**: Train and register BIR tax forecasting model

**Tasks**:

**10.1 Train Model with Feature Store**
```python
# databricks/src/ml/train_bir_forecaster.py
import mlflow
import mlflow.sklearn
from databricks.feature_engineering import FeatureEngineeringClient
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

mlflow.set_tracking_uri("databricks")
mlflow.set_experiment("/Shared/Experiments/BIR_Tax_Forecasting")

fe = FeatureEngineeringClient()

# Load training data from feature store
training_df = fe.read_table(name="gold.ml_features.bir_forecasting")

# Also load targets (actual withholding tax)
targets_df = spark.sql("""
    SELECT agency, year, month, withholding_tax as target
    FROM silver.gold_bir_monthly
    WHERE year >= 2022
""").toPandas()

# Merge features and targets
df_combined = training_df.toPandas().merge(
    targets_df,
    on=["agency", "year", "month"],
    how="inner"
)

# Prepare training data
feature_cols = ["prev_month_wht", "prev_year_wht", "rolling_avg_3m", "rolling_avg_12m", "transaction_velocity", "unique_vendors"]
X = df_combined[feature_cols].fillna(0)
y = df_combined["target"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model with MLflow tracking
with mlflow.start_run(run_name="RandomForest_v1"):
    # Model training
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        random_state=42
    )
    model.fit(X_train, y_train)

    # Predictions
    y_pred = model.predict(X_test)

    # Metrics
    rmse = mean_squared_error(y_test, y_pred, squared=False)
    r2 = r2_score(y_test, y_pred)

    # Log to MLflow
    mlflow.log_param("n_estimators", 100)
    mlflow.log_param("max_depth", 10)
    mlflow.log_metric("rmse", rmse)
    mlflow.log_metric("r2_score", r2)

    # Log model with feature store metadata
    fe.log_model(
        model=model,
        artifact_path="model",
        flavor=mlflow.sklearn,
        training_set=fe.create_training_set(
            df=spark.createDataFrame(df_combined),
            feature_lookups=[
                fe.FeatureLookup(
                    table_name="gold.ml_features.bir_forecasting",
                    lookup_key=["agency", "year", "month"]
                )
            ],
            label="target"
        )
    )

    print(f"Model trained: RMSE={rmse:.2f}, R²={r2:.4f}")
    print(f"Run ID: {mlflow.active_run().info.run_id}")
```

**10.2 Register Model**
```python
# Register best model
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Register model
model_name = "bir_tax_forecaster"
run_id = "<run-id-from-training>"

model_version = client.create_model_version(
    name=model_name,
    source=f"runs:/{run_id}/model",
    run_id=run_id
)

# Promote to production
client.transition_model_version_stage(
    name=model_name,
    version=model_version.version,
    stage="Production"
)

print(f"Model registered: {model_name} v{model_version.version}")
```

**Acceptance Criteria**:
- ✅ Model trained with R² >0.90
- ✅ Feature store integration working
- ✅ Model registered in MLflow
- ✅ Production version promoted

---

### Week 11: AI/BI Genie Dashboards

**Objective**: Create natural language dashboards for Finance team

**Tasks**:

**11.1 Create Genie Space**
```
1. Databricks Workspace → AI/BI
2. Create new Genie space: "BIR Compliance Dashboard"
3. Add data sources:
   - silver.gold_bir_monthly
   - silver.gold_category_analysis
4. Define business context:
   - "This dashboard tracks BIR tax filings for 8 agencies (RIM, CKVC, etc.)"
   - "Users can ask about monthly trends, agency comparisons, and forecasts"
```

**11.2 Configure Natural Language Queries**
```
Example queries Finance team can ask:
- "What is the total withholding tax for RIM in January 2026?"
- "Compare income tax across all agencies for Q1 2026"
- "Show me the top 3 agencies by VAT payments"
- "What's the trend for CKVC's withholding tax over the past 6 months?"
```

**11.3 Embed in Odoo**
```xml
<!-- addons/ipai/ipai_finance_ppm/views/genie_dashboard.xml -->
<record id="view_genie_dashboard" model="ir.ui.view">
    <field name="name">BIR Genie Dashboard</field>
    <field name="model">ipai.finance.bir_schedule</field>
    <field name="arch" type="xml">
        <form>
            <sheet>
                <div class="o_dashboard_container">
                    <iframe
                        src="https://<workspace>.azuredatabricks.net/genie/<space-id>?embed=true"
                        width="100%"
                        height="800px"
                        frameborder="0">
                    </iframe>
                </div>
            </sheet>
        </form>
    </field>
</record>
```

**Acceptance Criteria**:
- ✅ Genie space created
- ✅ Data sources connected
- ✅ Natural language queries working
- ✅ Embedded in Odoo UI

---

### Week 12: Model Serving Integration

**Objective**: Serve predictions via REST API and integrate with Odoo

**Tasks**:

**12.1 Enable Model Serving**
```python
# Enable model serving endpoint
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import EndpointCoreConfigInput, ServedEntityInput

w = WorkspaceClient()

# Create serving endpoint
endpoint = w.serving_endpoints.create(
    name="bir-tax-forecaster",
    config=EndpointCoreConfigInput(
        served_entities=[
            ServedEntityInput(
                entity_name="bir_tax_forecaster",
                entity_version="1",  # Production version
                scale_to_zero_enabled=True,
                workload_size="Small"
            )
        ]
    )
)

print(f"Serving endpoint created: {endpoint.name}")
print(f"URL: https://<workspace>.azuredatabricks.net/serving-endpoints/bir-tax-forecaster/invocations")
```

**12.2 Test Prediction API**
```bash
curl -X POST \
  "https://<workspace>.azuredatabricks.net/serving-endpoints/bir-tax-forecaster/invocations" \
  -H "Authorization: Bearer $DATABRICKS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "dataframe_records": [{
      "agency": "RIM",
      "year": 2026,
      "month": 2,
      "prev_month_wht": 50000.00,
      "prev_year_wht": 48000.00,
      "rolling_avg_3m": 49500.00,
      "rolling_avg_12m": 47800.00,
      "transaction_velocity": 450,
      "unique_vendors": 85
    }]
  }'

# Response: {"predictions": [51200.50]}
```

**12.3 Integrate with Odoo** (already documented in ACCELERATION_STRATEGY.md)

**Acceptance Criteria**:
- ✅ Serving endpoint deployed
- ✅ API responding in <200ms
- ✅ Odoo integration working
- ✅ Predictions visible in UI

---

## Phase 4: Production Deployment

### Week 13: Lakeflow Jobs Orchestration

**Objective**: Orchestrate complete ETL + ML workflow

**Tasks**:

**13.1 Create Master Workflow**
```yaml
# databricks/resources/jobs.yml
resources:
  jobs:
    bir_monthly_orchestration:
      name: "BIR Monthly Orchestration"
      tasks:
        - task_key: autoloader_ingestion
          notebook_task:
            notebook_path: ./src/etl/autoloader_ingestion.py
          new_cluster:
            spark_version: "14.3.x-scala2.12"
            node_type_id: "Standard_DS3_v2"
            num_workers: 2

        - task_key: dlt_pipeline
          pipeline_task:
            pipeline_id: scout_etl
          depends_on:
            - task_key: autoloader_ingestion

        - task_key: feature_engineering
          notebook_task:
            notebook_path: ./src/ml/create_feature_table.py
          depends_on:
            - task_key: dlt_pipeline

        - task_key: model_training
          notebook_task:
            notebook_path: ./src/ml/train_bir_forecaster.py
          depends_on:
            - task_key: feature_engineering

        - task_key: notify_completion
          notebook_task:
            notebook_path: ./src/utils/notify_mattermost.py
            base_parameters:
              message: "BIR monthly orchestration complete"
          depends_on:
            - task_key: model_training

      schedule:
        quartz_cron_expression: "0 0 2 1 * ?"  # 2 AM on 1st of month
        timezone_id: "Asia/Manila"

      email_notifications:
        on_success: ["business@insightpulseai.com"]
        on_failure: ["business@insightpulseai.com"]
```

**Acceptance Criteria**:
- ✅ Master workflow created
- ✅ Task dependencies configured
- ✅ Monthly schedule working
- ✅ Email notifications enabled

---

### Week 14: Asset Bundles CI/CD

**Objective**: Automate deployment via GitHub Actions

**Tasks**:

**14.1 GitHub Actions Workflow** (already documented in DEVELOPER_WORKFLOW.md)

**14.2 Environment Separation**
```yaml
# databricks/databricks.yml
targets:
  dev:
    workspace:
      host: "https://odoo-ce-dev.azuredatabricks.net"
    resources:
      jobs:
        bir_monthly_orchestration:
          schedule:
            pause_status: PAUSED  # Don't run in dev

  prod:
    workspace:
      host: "https://odoo-ce-prod.azuredatabricks.net"
    resources:
      jobs:
        bir_monthly_orchestration:
          schedule:
            pause_status: UNPAUSED  # Run in prod
```

**Acceptance Criteria**:
- ✅ CI/CD pipeline working
- ✅ Dev/prod environments separated
- ✅ Automated tests passing
- ✅ Rollback capability tested

---

### Week 15: Unity Catalog Governance

**Objective**: Configure fine-grained access control

**Tasks**:

**15.1 Create Service Principals**
```python
# Service principal for n8n workflows
w.service_principals.create(
    display_name="odoo-ce-n8n",
    application_id="<azure-app-id>"
)

# Service principal for Odoo
w.service_principals.create(
    display_name="odoo-ce-app",
    application_id="<azure-app-id>"
)
```

**15.2 Grant Permissions**
```sql
-- n8n: Can read silver/gold, write to bronze
GRANT SELECT ON CATALOG silver TO SERVICE_PRINCIPAL `odoo-ce-n8n`;
GRANT SELECT ON CATALOG gold TO SERVICE_PRINCIPAL `odoo-ce-n8n`;
GRANT ALL PRIVILEGES ON CATALOG bronze TO SERVICE_PRINCIPAL `odoo-ce-n8n`;

-- Odoo: Read-only on gold
GRANT SELECT ON CATALOG gold TO SERVICE_PRINCIPAL `odoo-ce-app`;

-- Data Scientists: Full access to dev, read-only on prod
GRANT ALL PRIVILEGES ON CATALOG dev TO GROUP `data_scientists`;
GRANT SELECT ON CATALOG gold TO GROUP `data_scientists`;
```

**15.3 Audit Access**
```sql
-- View permissions
SHOW GRANTS ON CATALOG gold;

-- Audit log
SELECT
    user_identity,
    request_params.catalog_name,
    request_params.table_name,
    action_name,
    event_time
FROM system.access.audit
WHERE action_name IN ('createTable', 'deleteTable', 'read', 'write')
ORDER BY event_time DESC
LIMIT 100;
```

**Acceptance Criteria**:
- ✅ Service principals created
- ✅ Least privilege permissions
- ✅ Audit log accessible
- ✅ Compliance documentation

---

### Week 16: Monitoring & Optimization

**Objective**: Set up monitoring and optimize costs

**Tasks**:

**16.1 Configure Alerts**
```python
# scripts/databricks/setup_alerts.py
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# Alert: DLT pipeline failure
w.alerts.create(
    name="DLT Pipeline Failure",
    query_id="<query-id>",
    condition={
        "op": "GREATER_THAN",
        "operand": {
            "column": {
                "name": "failed_count"
            }
        },
        "threshold": {
            "value": 0
        }
    },
    rearm=3600  # 1 hour
)
```

**16.2 Optimize Costs**
```yaml
# Use serverless compute for ad-hoc queries
resources:
  sql_warehouses:
    analytics:
      name: "Analytics Warehouse"
      warehouse_type: "SERVERLESS"
      cluster_size: "Small"
      auto_stop_mins: 10

# Use spot instances for non-critical jobs
resources:
  jobs:
    non_critical_etl:
      new_cluster:
        azure_attributes:
          spot_bid_max_price: -1  # Use spot instances
```

**16.3 Performance Monitoring**
```sql
-- Query performance
SELECT
    query_text,
    execution_time_ms,
    rows_produced,
    bytes_scanned
FROM system.query.history
WHERE start_time >= CURRENT_DATE - INTERVAL 7 DAYS
ORDER BY execution_time_ms DESC
LIMIT 20;

-- Job runtime trends
SELECT
    job_name,
    AVG(runtime_seconds) as avg_runtime,
    MAX(runtime_seconds) as max_runtime
FROM system.lakeflow.job_runs
WHERE start_time >= CURRENT_DATE - INTERVAL 30 DAYS
GROUP BY job_name
ORDER BY avg_runtime DESC;
```

**Acceptance Criteria**:
- ✅ Alerts configured (failures, costs)
- ✅ Serverless compute enabled
- ✅ Spot instances used where appropriate
- ✅ Performance baselines established

---

## Success Metrics

**Technical**:
- ✅ ETL runtime: <30 minutes (vs. 2-4 hours manual)
- ✅ Data quality: >98% pass rate
- ✅ ML model R²: >0.90
- ✅ API latency: <200ms (p95)
- ✅ Query performance: <5 seconds (p95)

**Business**:
- ✅ $840/month subscription savings (EE parity)
- ✅ 57 hours/month labor savings
- ✅ 100M transaction capacity (10x current)
- ✅ Real-time forecasting (vs. manual estimates)

---

**Status**: IMPLEMENTATION READY
**Timeline**: 16 weeks (4 months)
**Owner**: Jake Tolentino
**Next**: Review with stakeholders, approve budget, start Week 1
