# Databricks API Reference for odoo-ce Integration

---

**Purpose**: Complete API reference for all Databricks integrations with odoo-ce stack.

**Status**: REFERENCE GUIDE
**Created**: 2026-01-26
**API Version**: 2.1 (latest recommended)

---

## API Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Databricks API Ecosystem                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  REST API 2.1 (Core)                                             │
│  ├── Workspace API (notebooks, repos)                           │
│  ├── Clusters API (compute management)                          │
│  ├── Jobs API (workflow orchestration)                          │
│  ├── DBFS API (file system)                                     │
│  └── SQL API (analytics queries)                                │
│                                                                  │
│  MLflow API (ML Lifecycle)                                       │
│  ├── Experiments (tracking)                                     │
│  ├── Runs (training metadata)                                   │
│  ├── Model Registry (versioning)                                │
│  └── Model Serving (inference)                                  │
│                                                                  │
│  Unity Catalog API (Governance)                                 │
│  ├── Catalogs, Schemas, Tables                                  │
│  ├── Permissions & Grants                                       │
│  ├── External Locations                                         │
│  └── Service Principals                                         │
│                                                                  │
│  Feature Engineering API (Feature Store)                        │
│  ├── Feature Tables                                             │
│  ├── Online Stores                                              │
│  └── Feature Lookups                                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Authentication

### Methods

**Personal Access Token (PAT)** - Development
```bash
# Generate token: Workspace → User Settings → Access Tokens
export DATABRICKS_TOKEN="dapi1234567890abcdef"
export DATABRICKS_HOST="https://<workspace-id>.azuredatabricks.net"
```

**Service Principal** - Production
```bash
# Azure AD Application
export DATABRICKS_CLIENT_ID="<azure-app-id>"
export DATABRICKS_CLIENT_SECRET="<azure-client-secret>"
export DATABRICKS_TENANT_ID="<azure-tenant-id>"
```

**OAuth M2M** - CI/CD
```bash
# For GitHub Actions
export DATABRICKS_CLIENT_ID="<github-actions-app-id>"
export DATABRICKS_CLIENT_SECRET="${{ secrets.DATABRICKS_CLIENT_SECRET }}"
```

### Request Headers

```bash
# All API requests require Authorization header
curl -X GET \
  "https://<workspace>.azuredatabricks.net/api/2.1/clusters/list" \
  -H "Authorization: Bearer $DATABRICKS_TOKEN" \
  -H "Content-Type: application/json"
```

---

## REST API 2.1 (Core)

### Base URL

```
https://<workspace-id>.azuredatabricks.net/api/2.1
```

### Workspace API

**List Workspace Objects**
```bash
GET /workspace/list
```

```python
# Python SDK
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
for obj in w.workspace.list("/Shared/ETL"):
    print(f"{obj.path} ({obj.object_type})")
```

```bash
# curl
curl -X GET \
  "$DATABRICKS_HOST/api/2.1/workspace/list?path=/Shared/ETL" \
  -H "Authorization: Bearer $DATABRICKS_TOKEN"
```

**Import Notebook**
```bash
POST /workspace/import
```

```json
{
  "path": "/Shared/ETL/bronze_ingestion",
  "format": "SOURCE",
  "language": "PYTHON",
  "content": "<base64-encoded-notebook>",
  "overwrite": true
}
```

```python
# Python SDK
import base64

with open("databricks/src/etl/bronze_ingestion.py", "rb") as f:
    content = base64.b64encode(f.read()).decode()

w.workspace.import_file(
    path="/Shared/ETL/bronze_ingestion",
    format="SOURCE",
    language="PYTHON",
    content=content,
    overwrite=True
)
```

**Export Notebook**
```bash
GET /workspace/export?path=/Shared/ETL/bronze_ingestion&format=SOURCE
```

**Delete Object**
```bash
POST /workspace/delete
```

```json
{
  "path": "/Shared/ETL/old_notebook",
  "recursive": false
}
```

---

### Clusters API

**List Clusters**
```bash
GET /clusters/list
```

```python
# Python SDK
for cluster in w.clusters.list():
    print(f"Cluster: {cluster.cluster_name}")
    print(f"  ID: {cluster.cluster_id}")
    print(f"  State: {cluster.state}")
    print(f"  Spark Version: {cluster.spark_version}")
```

**Create Cluster**
```bash
POST /clusters/create
```

```json
{
  "cluster_name": "odoo-ce-etl-cluster",
  "spark_version": "14.3.x-scala2.12",
  "node_type_id": "Standard_DS3_v2",
  "autoscale": {
    "min_workers": 2,
    "max_workers": 8
  },
  "autotermination_minutes": 30,
  "spark_conf": {
    "spark.databricks.delta.optimizeWrite.enabled": "true",
    "spark.databricks.delta.autoCompact.enabled": "true"
  },
  "azure_attributes": {
    "availability": "SPOT_WITH_FALLBACK_AZURE",
    "spot_bid_max_price": -1
  }
}
```

```python
# Python SDK
from databricks.sdk.service.compute import ClusterSpec, AutoScale

cluster = w.clusters.create(
    cluster_name="odoo-ce-etl-cluster",
    spark_version="14.3.x-scala2.12",
    node_type_id="Standard_DS3_v2",
    autoscale=AutoScale(min_workers=2, max_workers=8),
    autotermination_minutes=30
)

print(f"Cluster created: {cluster.cluster_id}")
```

**Start Cluster**
```bash
POST /clusters/start
```

```json
{
  "cluster_id": "1234-567890-abc123"
}
```

**Terminate Cluster**
```bash
POST /clusters/terminate
```

```json
{
  "cluster_id": "1234-567890-abc123"
}
```

**Get Cluster Info**
```bash
GET /clusters/get?cluster_id=1234-567890-abc123
```

---

### Jobs API (Recommended: 2.1)

**List Jobs**
```bash
GET /jobs/list
```

```python
# Python SDK
for job in w.jobs.list():
    print(f"Job: {job.settings.name} (ID: {job.job_id})")
```

**Create Job**
```bash
POST /jobs/create
```

```json
{
  "name": "BIR Month-End ETL",
  "tasks": [
    {
      "task_key": "bronze_ingestion",
      "notebook_task": {
        "notebook_path": "/Shared/ETL/bronze_ingestion",
        "base_parameters": {
          "month": "2026-01"
        }
      },
      "new_cluster": {
        "spark_version": "14.3.x-scala2.12",
        "node_type_id": "Standard_DS3_v2",
        "num_workers": 2
      },
      "timeout_seconds": 3600
    },
    {
      "task_key": "silver_cleaning",
      "notebook_task": {
        "notebook_path": "/Shared/ETL/silver_cleaning"
      },
      "depends_on": [
        {
          "task_key": "bronze_ingestion"
        }
      ]
    }
  ],
  "schedule": {
    "quartz_cron_expression": "0 0 2 1 * ?",
    "timezone_id": "Asia/Manila",
    "pause_status": "UNPAUSED"
  },
  "email_notifications": {
    "on_success": ["business@insightpulseai.com"],
    "on_failure": ["business@insightpulseai.com"]
  },
  "max_concurrent_runs": 1
}
```

```python
# Python SDK
from databricks.sdk.service.jobs import Task, NotebookTask, JobCluster

job = w.jobs.create(
    name="BIR Month-End ETL",
    tasks=[
        Task(
            task_key="bronze_ingestion",
            notebook_task=NotebookTask(
                notebook_path="/Shared/ETL/bronze_ingestion",
                base_parameters={"month": "2026-01"}
            ),
            job_cluster_key="main_cluster",
            timeout_seconds=3600
        ),
        Task(
            task_key="silver_cleaning",
            notebook_task=NotebookTask(
                notebook_path="/Shared/ETL/silver_cleaning"
            ),
            depends_on=[{"task_key": "bronze_ingestion"}],
            job_cluster_key="main_cluster"
        )
    ],
    job_clusters=[
        JobCluster(
            job_cluster_key="main_cluster",
            new_cluster={
                "spark_version": "14.3.x-scala2.12",
                "node_type_id": "Standard_DS3_v2",
                "num_workers": 2
            }
        )
    ]
)

print(f"Job created: {job.job_id}")
```

**Run Job Now**
```bash
POST /jobs/run-now
```

```json
{
  "job_id": 123,
  "notebook_params": {
    "month": "2026-02"
  }
}
```

```python
# Python SDK
run = w.jobs.run_now(job_id=123, notebook_params={"month": "2026-02"})
print(f"Job run started: {run.run_id}")
```

**Get Run Status**
```bash
GET /jobs/runs/get?run_id=456
```

```python
# Python SDK
run_status = w.jobs.get_run(run_id=456)
print(f"State: {run_status.state.life_cycle_state}")
print(f"Result: {run_status.state.result_state}")

# Wait for completion
w.jobs.wait_get_run_job_terminated_or_skipped(run_id=456)
```

**Cancel Run**
```bash
POST /jobs/runs/cancel
```

```json
{
  "run_id": 456
}
```

---

### DBFS API (Databricks File System)

**List Files**
```bash
GET /dbfs/list?path=/delta/bronze_transactions
```

```python
# Python SDK
for file in w.dbfs.list("/delta/bronze_transactions"):
    print(f"{file.path} ({file.file_size} bytes)")
```

**Upload File**
```bash
POST /dbfs/put
```

```json
{
  "path": "/raw/sample.csv",
  "contents": "<base64-encoded-file>",
  "overwrite": true
}
```

```python
# Python SDK
import base64

with open("scripts/data/sample.csv", "rb") as f:
    content = base64.b64encode(f.read()).decode()

w.dbfs.put(
    path="/raw/sample.csv",
    contents=content,
    overwrite=True
)
```

**Download File**
```bash
GET /dbfs/read?path=/delta/gold_transactions/_delta_log/00000000000000000000.json
```

**Delete File**
```bash
POST /dbfs/delete
```

```json
{
  "path": "/raw/old_file.csv",
  "recursive": false
}
```

---

### SQL API

**Execute SQL Statement**
```bash
POST /sql/statements
```

```json
{
  "statement": "SELECT agency, SUM(amount) as total FROM gold.bir_transactions WHERE year = 2026 GROUP BY agency",
  "warehouse_id": "abc123def456",
  "wait_timeout": "30s"
}
```

```python
# Python SDK
result = w.sql.execute_statement(
    warehouse_id="abc123def456",
    statement="""
        SELECT agency, SUM(amount) as total
        FROM gold.bir_transactions
        WHERE year = 2026
        GROUP BY agency
    """
)

# Access results
for row in result.result.data_array:
    agency, total = row
    print(f"{agency}: {total}")
```

**Get Statement Status**
```bash
GET /sql/statements/{statement_id}
```

**Cancel Statement**
```bash
POST /sql/statements/{statement_id}/cancel
```

---

## MLflow API

### Base URL

```
https://<workspace-id>.azuredatabricks.net/api/2.0/mlflow
```

### Experiments

**Create Experiment**
```bash
POST /experiments/create
```

```json
{
  "name": "/Shared/Experiments/BIR_Tax_Forecasting",
  "artifact_location": "dbfs:/mlflow/bir_forecasting"
}
```

```python
# Python (MLflow client)
import mlflow

mlflow.set_tracking_uri("databricks")
experiment_id = mlflow.create_experiment(
    name="/Shared/Experiments/BIR_Tax_Forecasting",
    artifact_location="dbfs:/mlflow/bir_forecasting"
)
```

**List Experiments**
```bash
GET /experiments/list
```

---

### Runs

**Create Run**
```bash
POST /runs/create
```

```json
{
  "experiment_id": "123",
  "start_time": 1706227200000,
  "tags": [
    {
      "key": "mlflow.user",
      "value": "jake.tolentino"
    }
  ]
}
```

```python
# Python (MLflow client)
with mlflow.start_run(experiment_id="123"):
    # Training code
    mlflow.log_param("n_estimators", 100)
    mlflow.log_metric("rmse", 1234.56)
    mlflow.sklearn.log_model(model, "model")
```

**Log Metric**
```bash
POST /runs/log-metric
```

```json
{
  "run_id": "abc123def456",
  "key": "rmse",
  "value": 1234.56,
  "timestamp": 1706227200000
}
```

**Log Parameter**
```bash
POST /runs/log-parameter
```

```json
{
  "run_id": "abc123def456",
  "key": "n_estimators",
  "value": "100"
}
```

---

### Model Registry

**Create Registered Model**
```bash
POST /registered-models/create
```

```json
{
  "name": "bir_tax_forecaster",
  "description": "BIR tax forecasting model using Random Forest"
}
```

```python
# Python (MLflow client)
from mlflow.tracking import MlflowClient

client = MlflowClient()
client.create_registered_model(
    name="bir_tax_forecaster",
    description="BIR tax forecasting model using Random Forest"
)
```

**Create Model Version**
```bash
POST /model-versions/create
```

```json
{
  "name": "bir_tax_forecaster",
  "source": "runs:/abc123def456/model",
  "run_id": "abc123def456"
}
```

```python
# Python (MLflow client)
version = client.create_model_version(
    name="bir_tax_forecaster",
    source="runs:/abc123def456/model",
    run_id="abc123def456"
)

print(f"Model version: {version.version}")
```

**Transition Model Stage**
```bash
POST /model-versions/transition-stage
```

```json
{
  "name": "bir_tax_forecaster",
  "version": "1",
  "stage": "Production",
  "archive_existing_versions": true
}
```

```python
# Python (MLflow client)
client.transition_model_version_stage(
    name="bir_tax_forecaster",
    version="1",
    stage="Production",
    archive_existing_versions=True
)
```

---

### Model Serving

**Create Serving Endpoint**
```bash
POST /serving-endpoints
```

```json
{
  "name": "bir-tax-forecaster",
  "config": {
    "served_entities": [
      {
        "entity_name": "bir_tax_forecaster",
        "entity_version": "1",
        "scale_to_zero_enabled": true,
        "workload_size": "Small"
      }
    ]
  }
}
```

```python
# Python SDK
from databricks.sdk.service.serving import EndpointCoreConfigInput, ServedEntityInput

endpoint = w.serving_endpoints.create(
    name="bir-tax-forecaster",
    config=EndpointCoreConfigInput(
        served_entities=[
            ServedEntityInput(
                entity_name="bir_tax_forecaster",
                entity_version="1",
                scale_to_zero_enabled=True,
                workload_size="Small"
            )
        ]
    )
)
```

**Query Serving Endpoint**
```bash
POST /serving-endpoints/bir-tax-forecaster/invocations
```

```json
{
  "dataframe_records": [
    {
      "prev_month_wht": 50000.00,
      "prev_year_wht": 48000.00,
      "rolling_avg_3m": 49500.00,
      "rolling_avg_12m": 47800.00,
      "transaction_velocity": 450,
      "unique_vendors": 85
    }
  ]
}
```

```bash
# curl
curl -X POST \
  "$DATABRICKS_HOST/serving-endpoints/bir-tax-forecaster/invocations" \
  -H "Authorization: Bearer $DATABRICKS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "dataframe_records": [{
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

---

## Unity Catalog API

### Catalogs

**List Catalogs**
```bash
GET /unity-catalog/catalogs
```

```python
# Python SDK
for catalog in w.catalogs.list():
    print(f"Catalog: {catalog.name}")
```

**Create Catalog**
```bash
POST /unity-catalog/catalogs
```

```json
{
  "name": "bronze",
  "comment": "Raw ingested data",
  "properties": {
    "purpose": "landing_zone"
  }
}
```

```python
# Python SDK (or SQL)
spark.sql("CREATE CATALOG IF NOT EXISTS bronze COMMENT 'Raw ingested data'")
```

---

### Schemas

**List Schemas**
```bash
GET /unity-catalog/schemas?catalog_name=bronze
```

**Create Schema**
```bash
POST /unity-catalog/schemas
```

```json
{
  "name": "scout_transactions",
  "catalog_name": "bronze",
  "comment": "Scout transaction data"
}
```

```python
# SQL
spark.sql("""
    CREATE SCHEMA IF NOT EXISTS bronze.scout_transactions
    COMMENT 'Scout transaction data'
""")
```

---

### Tables

**List Tables**
```bash
GET /unity-catalog/tables?catalog_name=bronze&schema_name=scout_transactions
```

**Get Table Info**
```bash
GET /unity-catalog/tables/{full_name}
```

```python
# Python SDK
table_info = w.tables.get(full_name="bronze.scout_transactions.raw_exports")
print(f"Table: {table_info.name}")
print(f"Type: {table_info.table_type}")
print(f"Owner: {table_info.owner}")
```

---

### Permissions

**Grant Permissions**
```bash
PATCH /unity-catalog/permissions/{securable_type}/{full_name}
```

```json
{
  "changes": [
    {
      "add": [
        {
          "principal": "odoo-ce-n8n",
          "privileges": ["SELECT"]
        }
      ]
    }
  ]
}
```

```python
# SQL
spark.sql("""
    GRANT SELECT ON CATALOG gold
    TO SERVICE_PRINCIPAL `odoo-ce-n8n`
""")
```

**Get Permissions**
```bash
GET /unity-catalog/permissions/{securable_type}/{full_name}
```

---

## Feature Engineering API

### Feature Tables

**Create Feature Table**
```python
from databricks.feature_engineering import FeatureEngineeringClient

fe = FeatureEngineeringClient()

fe.create_table(
    name="gold.ml_features.bir_forecasting",
    primary_keys=["agency", "year", "month"],
    schema="""
        agency STRING,
        year INT,
        month INT,
        prev_month_wht DECIMAL(15,2),
        prev_year_wht DECIMAL(15,2),
        update_timestamp TIMESTAMP
    """,
    description="Feature table for BIR tax forecasting"
)
```

**Write to Feature Table**
```python
# Compute features
features_df = spark.sql("""
    SELECT
        agency,
        year,
        month,
        LAG(withholding_tax, 1) OVER (PARTITION BY agency ORDER BY year, month) as prev_month_wht,
        LAG(withholding_tax, 12) OVER (PARTITION BY agency ORDER BY year, month) as prev_year_wht,
        CURRENT_TIMESTAMP() as update_timestamp
    FROM silver.gold_bir_monthly
""")

# Write to feature store
fe.write_table(
    name="gold.ml_features.bir_forecasting",
    df=features_df,
    mode="merge"
)
```

**Read from Feature Table**
```python
# Read features for training
features_df = fe.read_table(name="gold.ml_features.bir_forecasting")
```

---

## Integration Patterns

### n8n Workflow Integration

**HTTP Request Node Configuration**:
```json
{
  "name": "Trigger Databricks Job",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "url": "={{ $env.DATABRICKS_HOST }}/api/2.1/jobs/run-now",
    "authentication": "headerAuth",
    "headerAuth": {
      "name": "Authorization",
      "value": "Bearer {{ $env.DATABRICKS_TOKEN }}"
    },
    "sendBody": true,
    "bodyParameters": {
      "parameters": [
        {
          "name": "job_id",
          "value": "={{ $json.job_id }}"
        },
        {
          "name": "notebook_params",
          "value": "={{ { \"month\": $json.month } }}"
        }
      ]
    },
    "options": {
      "timeout": 30000
    }
  }
}
```

---

### Odoo Integration (Python)

**Execute SQL Query from Odoo**:
```python
# addons/ipai/ipai_finance_ppm/models/bir_schedule.py
import requests
import os

class BIRSchedule(models.Model):
    _inherit = 'ipai.finance.bir_schedule'

    def _query_databricks(self, query):
        """Execute SQL query on Databricks SQL Warehouse"""
        databricks_host = os.getenv("DATABRICKS_HOST")
        databricks_token = os.getenv("DATABRICKS_TOKEN")
        warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID")

        response = requests.post(
            f"{databricks_host}/api/2.0/sql/statements",
            headers={
                "Authorization": f"Bearer {databricks_token}",
                "Content-Type": "application/json"
            },
            json={
                "statement": query,
                "warehouse_id": warehouse_id,
                "wait_timeout": "30s"
            },
            timeout=35
        )

        response.raise_for_status()
        result = response.json()

        # Extract data
        if result.get("status", {}).get("state") == "SUCCEEDED":
            return result["result"]["data_array"]
        else:
            raise Exception(f"Query failed: {result}")

    def action_fetch_databricks_data(self):
        """Fetch BIR data from Databricks"""
        query = f"""
            SELECT
                agency,
                SUM(withholding_tax) as total_wht,
                SUM(income_tax) as total_income_tax,
                SUM(vat) as total_vat
            FROM gold.bir_monthly
            WHERE year = {self.year} AND month = {self.month}
            GROUP BY agency
        """

        results = self._query_databricks(query)

        # Update Odoo records
        for row in results:
            agency, wht, income, vat = row
            # ... update Odoo fields
```

**Get MLflow Prediction**:
```python
def _get_prediction(self, features):
    """Get prediction from Databricks MLflow endpoint"""
    databricks_host = os.getenv("DATABRICKS_HOST")
    databricks_token = os.getenv("DATABRICKS_TOKEN")

    response = requests.post(
        f"{databricks_host}/serving-endpoints/bir-tax-forecaster/invocations",
        headers={
            "Authorization": f"Bearer {databricks_token}",
            "Content-Type": "application/json"
        },
        json={"dataframe_records": [features]},
        timeout=5
    )

    response.raise_for_status()
    return response.json()["predictions"][0]
```

---

### MCP Server Integration

**MCP Server Tool Implementation**:
```typescript
// mcp/servers/databricks-mcp-server/src/tools/execute_sql.ts
import { Tool } from "@modelcontextprotocol/sdk/types.js";

export const executeSqlTool: Tool = {
  name: "databricks_execute_sql",
  description: "Execute SQL query on Databricks SQL Warehouse",
  inputSchema: {
    type: "object",
    properties: {
      query: {
        type: "string",
        description: "SQL query to execute"
      },
      warehouse_id: {
        type: "string",
        description: "SQL Warehouse ID (optional, uses default if not provided)"
      }
    },
    required: ["query"]
  }
};

export async function handleExecuteSql(args: any): Promise<any> {
  const { query, warehouse_id = process.env.DATABRICKS_WAREHOUSE_ID } = args;

  const response = await fetch(
    `${process.env.DATABRICKS_HOST}/api/2.0/sql/statements`,
    {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${process.env.DATABRICKS_TOKEN}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        statement: query,
        warehouse_id
      })
    }
  );

  const result = await response.json();

  if (result.status?.state === "SUCCEEDED") {
    return {
      content: [{
        type: "text",
        text: JSON.stringify(result.result.data_array, null, 2)
      }]
    };
  } else {
    throw new Error(`Query failed: ${JSON.stringify(result)}`);
  }
}
```

---

## Error Handling

### Common Errors

**401 Unauthorized**:
```json
{
  "error_code": "UNAUTHENTICATED",
  "message": "Invalid authentication credentials"
}
```
**Fix**: Check token validity, regenerate if expired

**403 Forbidden**:
```json
{
  "error_code": "PERMISSION_DENIED",
  "message": "User does not have permission to access resource"
}
```
**Fix**: Grant appropriate Unity Catalog permissions

**429 Rate Limit**:
```json
{
  "error_code": "RESOURCE_EXHAUSTED",
  "message": "Too many requests"
}
```
**Fix**: Implement exponential backoff, reduce request rate

**500 Internal Server Error**:
```json
{
  "error_code": "INTERNAL_ERROR",
  "message": "Internal server error"
}
```
**Fix**: Retry with exponential backoff, contact support if persists

### Retry Pattern

```python
import time
from requests.exceptions import RequestException

def databricks_request_with_retry(method, url, max_retries=3, **kwargs):
    """Make Databricks API request with exponential backoff"""
    for attempt in range(max_retries):
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt  # Exponential backoff
            time.sleep(wait_time)
```

---

## Rate Limits

**API Rate Limits**:
- REST API: 30 requests/second per workspace
- SQL API: 10 concurrent queries per warehouse
- MLflow API: 100 requests/minute per workspace

**Best Practices**:
- Batch operations when possible
- Use async/await for parallel requests
- Implement exponential backoff
- Cache results when appropriate

---

## SDK Quick Reference

### Python SDK Installation

```bash
pip install databricks-sdk
```

### Python SDK Examples

```python
from databricks.sdk import WorkspaceClient

# Initialize (uses environment variables)
w = WorkspaceClient()

# Clusters
clusters = w.clusters.list()
cluster = w.clusters.create(...)
w.clusters.start(cluster_id="...")

# Jobs
jobs = w.jobs.list()
job = w.jobs.create(...)
run = w.jobs.run_now(job_id=123)

# SQL
result = w.sql.execute_statement(
    warehouse_id="...",
    statement="SELECT * FROM table"
)

# Unity Catalog
catalogs = w.catalogs.list()
tables = w.tables.list(catalog_name="bronze", schema_name="scout")
```

---

## Related Documentation

- **Databricks REST API**: https://docs.databricks.com/api/azure/workspace/introduction
- **MLflow API**: https://mlflow.org/docs/latest/rest-api.html
- **Unity Catalog API**: https://docs.databricks.com/api/azure/workspace/unitycatalog
- **Python SDK**: https://databricks-sdk-py.readthedocs.io/

---

**Status**: REFERENCE GUIDE
**Last Updated**: 2026-01-26
**API Version**: 2.1 (latest)
