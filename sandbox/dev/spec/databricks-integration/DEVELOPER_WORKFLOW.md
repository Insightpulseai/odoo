# Databricks Developer Workflow for odoo-ce

---

**Purpose**: Define the complete developer workflow for integrating Azure Databricks with odoo-ce using modern developer tools, SDKs, and CI/CD patterns.

**Status**: IMPLEMENTATION READY
**Created**: 2026-01-26
**Target**: Local development + CI/CD automation

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                   Developer Workflow Architecture                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Local Development                     CI/CD Pipeline            │
│  ├── VS Code + Extension              ├── GitHub Actions        │
│  ├── Databricks Connect               ├── Databricks Asset      │
│  ├── Python SDK                       │   Bundles               │
│  └── Local debugging                  └── Terraform (optional)  │
│       ↓                                     ↓                    │
│   Azure Databricks Workspace                                    │
│   ├── Delta Lake (data storage)                                 │
│   ├── Spark Clusters (compute)                                  │
│   ├── MLflow (ML lifecycle)                                     │
│   └── SQL Warehouse (analytics)                                 │
│       ↓                                     ↓                    │
│   odoo-ce Integration                                           │
│   ├── MCP Server (Claude Code)                                  │
│   ├── n8n Workflows (automation)                                │
│   ├── Odoo Modules (UI/business logic)                          │
│   └── Apache Superset (dashboards)                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Developer Tooling Setup

### 1. VS Code Extension (Recommended)

**Installation**:
```bash
# Install VS Code extension
code --install-extension databricks.databricks

# Or search "Databricks" in VS Code Extensions marketplace
```

**Configuration** (`.vscode/settings.json`):
```json
{
  "databricks.workspace.url": "https://<workspace-id>.azuredatabricks.net",
  "databricks.workspace.token": "${env:DATABRICKS_TOKEN}",
  "databricks.workspace.profile": "DEFAULT",
  "databricks.python.envFile": "${workspaceFolder}/.env",
  "databricks.sync.enabled": true,
  "databricks.sync.path": "/Shared/odoo-ce-integration"
}
```

**Usage**:
```bash
# Authenticate
# VS Code Command Palette (Cmd+Shift+P):
# > Databricks: Configure Databricks

# Sync notebooks
# Right-click notebook → Databricks: Sync to Workspace

# Run on cluster
# Open Python file → Databricks: Run File on Cluster
```

**Benefits**:
- ✅ Easy configuration UI
- ✅ Notebook sync (local ↔ workspace)
- ✅ Run files directly on Databricks clusters
- ✅ Integrated debugging

---

### 2. Databricks Connect (Multi-IDE Support)

**Installation**:
```bash
# Install Databricks Connect
pip install databricks-connect

# Configure cluster connection
databricks-connect configure --profile DEFAULT
# Prompts for:
# - Workspace URL
# - Token
# - Cluster ID
```

**Configuration** (`~/.databrickscfg`):
```ini
[DEFAULT]
host = https://<workspace-id>.azuredatabricks.net
token = dapi123456789abcdef
cluster_id = 1234-567890-abc123
```

**Local Development** (Python):
```python
# scripts/databricks/local_etl_test.py
from pyspark.sql import SparkSession

# Databricks Connect automatically uses cluster
spark = SparkSession.builder.appName("LocalETLTest").getOrCreate()

# Test ETL logic locally, runs on Databricks cluster
df = spark.read.format("delta").load("dbfs:/delta/bronze_transactions")
df_cleaned = df.filter("amount > 0").select("transaction_id", "amount", "agency")
df_cleaned.write.format("delta").mode("overwrite").save("dbfs:/delta/silver_transactions")

print(f"Processed {df_cleaned.count()} transactions")
spark.stop()
```

**Run Locally**:
```bash
# Execute on Databricks cluster from local terminal
python scripts/databricks/local_etl_test.py
# Output: "Processed 1234567 transactions"
```

**Benefits**:
- ✅ Local debugging with remote execution
- ✅ Works with PyCharm, IntelliJ, Eclipse, RStudio, JupyterLab
- ✅ Test Spark code without deploying to workspace
- ✅ Faster iteration (no notebook upload required)

---

### 3. Python SDK (Workspace Management)

**Installation**:
```bash
pip install databricks-sdk
```

**Usage Examples**:

**Create Job Programmatically**:
```python
# scripts/databricks/create_bir_etl_job.py
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.jobs import Task, NotebookTask, JobCluster

w = WorkspaceClient()

# Create BIR month-end ETL job
job = w.jobs.create(
    name="BIR Month-End ETL",
    tasks=[
        Task(
            task_key="bronze_ingestion",
            notebook_task=NotebookTask(
                notebook_path="/Shared/ETL/bronze_ingestion",
                base_parameters={"month": "2026-01"}
            ),
            job_cluster_key="main_cluster"
        ),
        Task(
            task_key="silver_cleaning",
            notebook_task=NotebookTask(
                notebook_path="/Shared/ETL/silver_cleaning"
            ),
            depends_on=[{"task_key": "bronze_ingestion"}],
            job_cluster_key="main_cluster"
        ),
        Task(
            task_key="gold_aggregation",
            notebook_task=NotebookTask(
                notebook_path="/Shared/ETL/gold_aggregation"
            ),
            depends_on=[{"task_key": "silver_cleaning"}],
            job_cluster_key="main_cluster"
        )
    ],
    job_clusters=[
        JobCluster(
            job_cluster_key="main_cluster",
            new_cluster={
                "spark_version": "14.3.x-scala2.12",
                "node_type_id": "Standard_DS3_v2",
                "num_workers": 2,
                "spark_conf": {
                    "spark.databricks.delta.optimizeWrite.enabled": "true"
                }
            }
        )
    ]
)

print(f"Created job: {job.job_id}")
```

**List Clusters**:
```python
# scripts/databricks/list_clusters.py
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

for cluster in w.clusters.list():
    print(f"Cluster: {cluster.cluster_name} (ID: {cluster.cluster_id})")
    print(f"  State: {cluster.state}")
    print(f"  Spark Version: {cluster.spark_version}")
```

**Execute SQL Query**:
```python
# scripts/databricks/query_delta_lake.py
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# Execute query on SQL warehouse
result = w.sql.execute_statement(
    warehouse_id="abc123def456",
    statement="""
        SELECT agency, SUM(withholding_tax) as total_wht
        FROM gold.bir_transactions
        WHERE year = 2026 AND month = 1
        GROUP BY agency
    """
)

for row in result.result.data_array:
    print(f"Agency: {row[0]}, Total WHT: {row[1]}")
```

**Benefits**:
- ✅ Full workspace automation (Python)
- ✅ Type-safe SDK (better than raw REST API)
- ✅ Supports all Databricks services (Jobs, Clusters, SQL, MLflow)
- ✅ Integrates with existing Python tooling

---

### 4. Databricks CLI (Terminal Operations)

**Installation**:
```bash
# Via pip
pip install databricks-cli

# Via Homebrew (macOS)
brew install databricks-cli

# Configure
databricks configure --token
# Prompts for workspace URL and token
```

**Common Commands**:

**Workspace Management**:
```bash
# List notebooks
databricks workspace ls /Shared/ETL

# Import notebook
databricks workspace import --language PYTHON \
  --file scripts/databricks/bronze_ingestion.py \
  --path /Shared/ETL/bronze_ingestion

# Export notebook
databricks workspace export --format SOURCE \
  --path /Shared/ETL/gold_aggregation \
  --file scripts/databricks/gold_aggregation.py
```

**Job Management**:
```bash
# List jobs
databricks jobs list

# Run job
databricks jobs run-now --job-id 123

# Get run status
databricks jobs get-run --run-id 456
```

**Cluster Management**:
```bash
# List clusters
databricks clusters list

# Start cluster
databricks clusters start --cluster-id abc123

# Get cluster info
databricks clusters get --cluster-id abc123
```

**DBFS (Databricks File System)**:
```bash
# List files
databricks fs ls dbfs:/delta/

# Upload file
databricks fs cp scripts/data/sample.csv dbfs:/raw/sample.csv

# Download file
databricks fs cp dbfs:/delta/gold_transactions/_delta_log/00000000000000000000.json ./logs/
```

**Benefits**:
- ✅ Quick operations from terminal
- ✅ Scriptable (Bash automation)
- ✅ CI/CD integration (GitHub Actions)
- ✅ Remote workspace terminal access

---

## CI/CD Integration (Databricks Asset Bundles)

### Asset Bundle Structure

**Repository Layout**:
```
odoo-ce/
├── databricks/                    # Databricks Asset Bundles
│   ├── databricks.yml             # Bundle configuration
│   ├── resources/
│   │   ├── jobs.yml               # Job definitions
│   │   ├── pipelines.yml          # DLT pipelines
│   │   └── mlflow.yml             # MLflow experiments
│   └── src/
│       ├── etl/
│       │   ├── bronze_ingestion.py
│       │   ├── silver_cleaning.py
│       │   └── gold_aggregation.py
│       └── ml/
│           ├── train_bir_model.py
│           └── feature_engineering.py
├── .github/workflows/
│   └── databricks-deploy.yml     # CI/CD workflow
└── ...
```

**Bundle Configuration** (`databricks/databricks.yml`):
```yaml
bundle:
  name: odoo-ce-databricks

resources:
  jobs:
    bir_etl:
      name: "BIR Month-End ETL"
      tasks:
        - task_key: bronze_ingestion
          notebook_task:
            notebook_path: ./src/etl/bronze_ingestion.py
          new_cluster:
            spark_version: "14.3.x-scala2.12"
            node_type_id: "Standard_DS3_v2"
            num_workers: 2
        - task_key: silver_cleaning
          notebook_task:
            notebook_path: ./src/etl/silver_cleaning.py
          depends_on:
            - task_key: bronze_ingestion
        - task_key: gold_aggregation
          notebook_task:
            notebook_path: ./src/etl/gold_aggregation.py
          depends_on:
            - task_key: silver_cleaning
      schedule:
        quartz_cron_expression: "0 0 2 1 * ?"  # 2 AM on 1st of month
        timezone_id: "Asia/Manila"

  pipelines:
    scout_dlt:
      name: "Scout Transaction DLT"
      storage: "dbfs:/pipelines/scout_etl"
      target: "gold"
      libraries:
        - notebook:
            path: ./src/etl/dlt_pipeline.py
      clusters:
        - label: "default"
          autoscale:
            min_workers: 1
            max_workers: 5

targets:
  dev:
    workspace:
      host: "https://<workspace-dev>.azuredatabricks.net"
  prod:
    workspace:
      host: "https://<workspace-prod>.azuredatabricks.net"
```

**GitHub Actions Workflow** (`.github/workflows/databricks-deploy.yml`):
```yaml
name: Databricks Deploy

on:
  push:
    branches: [main]
    paths:
      - 'databricks/**'
  pull_request:
    paths:
      - 'databricks/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install Databricks CLI
        run: pip install databricks-cli databricks-sdk

      - name: Configure Databricks CLI
        env:
          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}
          DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}
        run: |
          echo "$DATABRICKS_HOST" > ~/.databrickscfg
          echo "$DATABRICKS_TOKEN" >> ~/.databrickscfg

      - name: Validate Bundle
        run: databricks bundle validate -t prod
        working-directory: databricks

      - name: Deploy Bundle (Prod)
        if: github.ref == 'refs/heads/main'
        run: databricks bundle deploy -t prod
        working-directory: databricks

      - name: Run Tests
        if: github.ref == 'refs/heads/main'
        run: databricks bundle run bir_etl -t prod
        working-directory: databricks
```

**Benefits**:
- ✅ Infrastructure as Code (IaC) for Databricks
- ✅ Git-based version control for notebooks
- ✅ Automated deployments via CI/CD
- ✅ Environment separation (dev/staging/prod)
- ✅ Rollback capability (Git revert)

---

## Local Development Workflow (Step-by-Step)

### Workflow 1: Develop ETL Pipeline Locally

**Step 1: Clone Repository**
```bash
cd ~/Documents/GitHub/odoo-ce
git checkout -b feat/databricks-bir-etl
```

**Step 2: Create Local Notebook**
```bash
mkdir -p databricks/src/etl
cat > databricks/src/etl/bronze_ingestion.py << 'EOF'
# Databricks notebook source
# MAGIC %md
# MAGIC # Bronze Ingestion: Google Drive → Delta Lake

from pyspark.sql import functions as F

# Read raw files from DBFS
df_raw = spark.read.json("dbfs:/raw/scout_transactions/*.json")

# Basic schema validation
df_bronze = df_raw.select(
    "transaction_id",
    "agency",
    "transaction_date",
    "amount",
    "category",
    "vendor_id"
)

# Write to Delta Lake Bronze
df_bronze.write.format("delta").mode("overwrite").save("dbfs:/delta/bronze_transactions")

print(f"Ingested {df_bronze.count()} transactions to Bronze")
EOF
```

**Step 3: Test Locally with Databricks Connect**
```bash
# Ensure Databricks Connect configured
databricks-connect test

# Run notebook locally (executes on Databricks cluster)
python databricks/src/etl/bronze_ingestion.py
# Output: "Ingested 1234567 transactions to Bronze"
```

**Step 4: Debug in VS Code**
```bash
# Open in VS Code
code databricks/src/etl/bronze_ingestion.py

# Set breakpoints in VS Code
# Run with Databricks Connect debugger
# F5 → Debug on Databricks cluster
```

**Step 5: Add to Asset Bundle**
```yaml
# databricks/databricks.yml
resources:
  jobs:
    bir_etl:
      tasks:
        - task_key: bronze_ingestion
          notebook_task:
            notebook_path: ./src/etl/bronze_ingestion.py
```

**Step 6: Deploy via CI/CD**
```bash
# Commit and push
git add databricks/
git commit -m "feat(databricks): add BIR ETL bronze ingestion"
git push origin feat/databricks-bir-etl

# GitHub Actions automatically deploys to Databricks
# Check workflow: https://github.com/jgtolentino/odoo-ce/actions
```

---

### Workflow 2: Train ML Model Locally

**Step 1: Create Training Script**
```python
# databricks/src/ml/train_bir_model.py
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# Set tracking URI (Databricks workspace)
mlflow.set_tracking_uri("databricks")
mlflow.set_experiment("/Shared/Experiments/BIR_Tax_Forecasting")

# Load data from Delta Lake
df = spark.sql("""
    SELECT
        withholding_tax,
        prev_month_wht,
        prev_year_wht,
        income_tax,
        vat
    FROM gold.bir_features
    WHERE year BETWEEN 2022 AND 2025
""").toPandas()

X = df[['prev_month_wht', 'prev_year_wht', 'income_tax', 'vat']]
y = df['withholding_tax']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
with mlflow.start_run():
    model = RandomForestRegressor(n_estimators=100, max_depth=10)
    model.fit(X_train, y_train)

    # Log metrics
    score = model.score(X_test, y_test)
    mlflow.log_metric("r2_score", score)
    mlflow.log_param("n_estimators", 100)

    # Log model
    mlflow.sklearn.log_model(model, "bir_tax_forecaster")

    print(f"Model R² score: {score:.4f}")
    print(f"Run ID: {mlflow.active_run().info.run_id}")
```

**Step 2: Run Locally**
```bash
# Execute on Databricks cluster from local machine
python databricks/src/ml/train_bir_model.py
# Output:
# Model R² score: 0.9523
# Run ID: abc123def456
```

**Step 3: Register Model**
```python
# databricks/src/ml/register_model.py
import mlflow
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Register best model
client.create_registered_model(name="bir_tax_forecaster")
client.create_model_version(
    name="bir_tax_forecaster",
    source="runs:/abc123def456/model",
    run_id="abc123def456"
)

print("Model registered: bir_tax_forecaster version 1")
```

**Step 4: Deploy via Asset Bundle**
```yaml
# databricks/resources/mlflow.yml
resources:
  mlflow_experiments:
    bir_forecasting:
      name: "/Shared/Experiments/BIR_Tax_Forecasting"
      artifact_location: "dbfs:/mlflow/bir_forecasting"
```

---

## Integration with odoo-ce

### MCP Server Development

**Local Development**:
```bash
cd mcp/servers/databricks-mcp-server

# Install dependencies
npm install

# Build
npm run build

# Test locally
npm run dev
```

**Test with Claude Code**:
```bash
# Configure MCP server in .claude/mcp-servers.json
# (already documented in ACCELERATION_STRATEGY.md)

# Test in Claude Code
claude code

# Prompt: "Use Databricks to query gold.bir_transactions"
# MCP server handles API call
```

### n8n Workflow Integration

**n8n Node: Trigger Databricks Job**
```json
{
  "nodes": [
    {
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
            }
          ]
        }
      },
      "name": "Trigger Databricks Job",
      "type": "n8n-nodes-base.httpRequest"
    }
  ]
}
```

### Odoo Computed Field Integration

**Use Databricks Predictions in Odoo**:
```python
# addons/ipai/ipai_finance_ppm/models/bir_schedule.py
import requests
import os

class BIRSchedule(models.Model):
    _inherit = 'ipai.finance.bir_schedule'

    predicted_tax = fields.Float(
        string="Predicted Tax Amount",
        compute='_compute_predicted_tax',
        help="ML prediction from Databricks"
    )

    def _compute_predicted_tax(self):
        """Get prediction from Databricks MLflow model"""
        databricks_host = os.getenv("DATABRICKS_HOST")
        databricks_token = os.getenv("DATABRICKS_TOKEN")

        for record in self:
            # Prepare features
            features = {
                "prev_month_wht": record.prev_month_withholding_tax or 0,
                "prev_year_wht": record.prev_year_withholding_tax or 0,
                "income_tax": record.income_tax or 0,
                "vat": record.vat or 0
            }

            # Call MLflow model API
            try:
                response = requests.post(
                    f"{databricks_host}/model/bir_tax_forecaster/1/invocations",
                    headers={"Authorization": f"Bearer {databricks_token}"},
                    json={"dataframe_records": [features]},
                    timeout=5
                )
                response.raise_for_status()
                record.predicted_tax = response.json()['predictions'][0]
            except Exception as e:
                _logger.error(f"Databricks prediction failed: {e}")
                record.predicted_tax = 0.0
```

---

## Testing Strategy

### Unit Tests (Local)

**Test ETL Logic**:
```python
# databricks/tests/test_bronze_ingestion.py
import pytest
from pyspark.sql import SparkSession

@pytest.fixture
def spark():
    return SparkSession.builder.appName("UnitTest").getOrCreate()

def test_bronze_schema(spark):
    """Test bronze ingestion schema validation"""
    from databricks.src.etl.bronze_ingestion import validate_schema

    test_data = [
        ("txn001", "RIM", "2026-01-15", 10000.0, "EXPENSE", "vendor001")
    ]
    df = spark.createDataFrame(test_data, ["transaction_id", "agency", "transaction_date", "amount", "category", "vendor_id"])

    result = validate_schema(df)
    assert result.count() == 1
    assert "transaction_id" in result.columns
```

**Run Tests**:
```bash
pytest databricks/tests/
```

### Integration Tests (CI/CD)

**GitHub Actions Test Job**:
```yaml
# .github/workflows/databricks-test.yml
jobs:
  integration-test:
    runs-on: ubuntu-latest
    steps:
      - name: Run BIR ETL (Test)
        run: |
          databricks jobs run-now --job-id ${{ secrets.TEST_JOB_ID }}
          # Wait for completion and check status
```

---

## Best Practices

### 1. Version Control

**What to Commit**:
- ✅ Asset Bundle configs (`databricks.yml`)
- ✅ Python notebooks (`databricks/src/**/*.py`)
- ✅ ML training scripts
- ✅ Tests

**What to .gitignore**:
- ❌ Databricks CLI cache (`~/.databrickscfg`)
- ❌ Credentials (use environment variables)
- ❌ Local Spark metadata (`metastore_db/`, `spark-warehouse/`)

### 2. Security

**Token Management**:
```bash
# Store in environment (not in code)
export DATABRICKS_TOKEN=$(security find-generic-password -s "databricks-token" -w)

# Use in scripts
# Python SDK auto-detects DATABRICKS_TOKEN env var
```

**Role-Based Access**:
- Dev workspace: Full access
- Prod workspace: Read-only (except CI/CD service account)

### 3. Performance

**Cluster Auto-Scaling**:
```yaml
# databricks.yml
new_cluster:
  autoscale:
    min_workers: 1
    max_workers: 10
  autotermination_minutes: 30
```

**Delta Lake Optimization**:
```python
# Optimize tables regularly
spark.sql("OPTIMIZE gold.bir_transactions")
spark.sql("VACUUM gold.bir_transactions RETAIN 168 HOURS")
```

---

## Next Steps

1. ✅ Document developer workflow (this file)
2. ⏳ Set up VS Code extension + Databricks Connect
3. ⏳ Create first Asset Bundle (`databricks/databricks.yml`)
4. ⏳ Implement Bronze ingestion notebook
5. ⏳ Configure CI/CD pipeline (GitHub Actions)
6. ⏳ Train first ML model (BIR forecasting)
7. ⏳ Deploy MCP server integration

---

**Status**: IMPLEMENTATION READY
**Owner**: Jake Tolentino
**Tools**: VS Code, Databricks Connect, Python SDK, Asset Bundles
