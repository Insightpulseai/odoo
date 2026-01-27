# Azure Databricks API Acceleration Strategy — EE Parity + Data Platform

---

**Purpose**: Leverage Azure Databricks APIs to accelerate both Enterprise Edition parity and data platform modernization simultaneously.

**Status**: PROPOSED
**Created**: 2026-01-26
**Target**: Q1-Q2 2026 (parallel execution)

---

## Strategic Insight: Two Birds, One Platform

**Key Realization**: Azure Databricks can simultaneously solve two major odoo-ce challenges:

1. **Enterprise Edition Parity**: Backport Odoo EE analytics features to CE using Databricks
2. **Data Platform Modernization**: Replace manual ETL with Databricks lakehouse

**Acceleration Method**: Use Databricks APIs to build features that would normally require Odoo Enterprise subscriptions.

---

## Current State vs. Target State

### Current Limitations (Odoo 18 CE + Manual ETL)

**Enterprise Edition Gaps**:
- ❌ No advanced analytics (Odoo Studio)
- ❌ No forecasting (Odoo Planning)
- ❌ No custom dashboards (limited to Superset)
- ❌ No AI/ML predictions (OpenAI API only)

**Data Platform Gaps**:
- ❌ Manual ETL (2-4 hours)
- ❌ Supabase PostgreSQL limits (10M transactions)
- ❌ No real-time analytics
- ❌ No ML feature store

### Target State (Databricks-Powered CE)

**EE Parity Features** (via Databricks APIs):
- ✅ Advanced analytics dashboards (Databricks SQL)
- ✅ Financial forecasting (MLflow models)
- ✅ Custom reporting (SQL Analytics API)
- ✅ AI predictions (Databricks ML Runtime)

**Data Platform** (Lakehouse):
- ✅ Automated ETL (Lakeflow DLT)
- ✅ 100M+ transactions (Delta Lake)
- ✅ Real-time streaming (Structured Streaming)
- ✅ ML feature store (Feature Engineering API)

---

## Databricks API Categories for Acceleration

### 1. REST API (Core Automation)

**Purpose**: Automate all Databricks operations from Odoo/n8n/Claude Code

**Key Endpoints**:
```python
# Workspace API
POST /api/2.0/workspace/import        # Upload notebooks
GET  /api/2.0/workspace/list          # List notebooks
DELETE /api/2.0/workspace/delete      # Remove notebooks

# Cluster API
POST /api/2.0/clusters/create         # Provision cluster
POST /api/2.0/clusters/start          # Start cluster
POST /api/2.0/clusters/terminate      # Stop cluster

# Jobs API (v2.1 recommended)
POST /api/2.1/jobs/create             # Create ETL job
POST /api/2.1/jobs/run-now            # Trigger job
GET  /api/2.1/jobs/runs/get           # Check status
```

**Integration Points**:
- **n8n workflows**: Trigger ETL jobs from Odoo events
- **MCP Server**: `databricks-mcp-server` exposes APIs to Claude Code
- **Odoo scheduled actions**: Cron jobs trigger Databricks jobs

**Example: Month-End Close Automation**
```python
# n8n workflow: Trigger Databricks ETL at month-end
import requests

DATABRICKS_HOST = "https://<workspace>.azuredatabricks.net"
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN")

# Create job
job_config = {
    "name": "BIR Month-End ETL",
    "tasks": [{
        "task_key": "bir_etl",
        "notebook_task": {
            "notebook_path": "/Shared/BIR/month_end_close",
            "base_parameters": {
                "month": "2026-01",
                "agencies": "RIM,CKVC,BOM,JPAL,JLI,JAP,LAS,RMQB"
            }
        },
        "new_cluster": {
            "spark_version": "14.3.x-scala2.12",
            "node_type_id": "Standard_DS3_v2",
            "num_workers": 2
        }
    }],
    "schedule": {
        "quartz_cron_expression": "0 0 2 1 * ?",  # 2 AM on 1st of month
        "timezone_id": "Asia/Manila"
    }
}

response = requests.post(
    f"{DATABRICKS_HOST}/api/2.1/jobs/create",
    headers={"Authorization": f"Bearer {DATABRICKS_TOKEN}"},
    json=job_config
)

job_id = response.json()["job_id"]
print(f"Created job: {job_id}")
```

---

### 2. SQL Analytics API (EE Parity: Custom Dashboards)

**Purpose**: Replace Odoo Studio/Planning with Databricks SQL dashboards

**Odoo Enterprise Feature**: Custom dashboards (requires Studio subscription)
**Databricks Alternative**: SQL Analytics + REST API

**Implementation**:
```python
# Create custom BIR compliance dashboard
import requests

dashboard_config = {
    "name": "BIR Compliance Dashboard",
    "queries": [
        {
            "name": "Monthly Withholding Tax",
            "query": """
                SELECT
                    agency,
                    month,
                    SUM(withholding_tax) as total_wht,
                    COUNT(DISTINCT transaction_id) as txn_count
                FROM gold.bir_transactions
                WHERE year = 2026
                GROUP BY agency, month
                ORDER BY month DESC, total_wht DESC
            """
        },
        {
            "name": "Filing Status by Form",
            "query": """
                SELECT
                    form_type,
                    filing_status,
                    COUNT(*) as count
                FROM gold.bir_filings
                WHERE filing_deadline >= CURRENT_DATE - INTERVAL 90 DAYS
                GROUP BY form_type, filing_status
            """
        }
    ],
    "visualizations": [
        {"type": "bar", "query_id": 0},
        {"type": "pie", "query_id": 1}
    ]
}

# Databricks SQL API
response = requests.post(
    f"{DATABRICKS_HOST}/api/2.0/preview/sql/dashboards",
    headers={"Authorization": f"Bearer {DATABRICKS_TOKEN}"},
    json=dashboard_config
)
```

**Embed in Odoo**:
```xml
<!-- addons/ipai/ipai_finance_ppm/views/bir_dashboard.xml -->
<record id="view_bir_dashboard_iframe" model="ir.ui.view">
    <field name="name">BIR Dashboard</field>
    <field name="model">ipai.finance.bir_schedule</field>
    <field name="arch" type="xml">
        <form>
            <sheet>
                <div class="o_dashboard_container">
                    <iframe
                        src="https://<workspace>.azuredatabricks.net/sql/dashboards/<dashboard_id>?embed=true"
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

**Benefits**:
- ✅ No Odoo Studio subscription needed
- ✅ Unlimited custom dashboards
- ✅ Real-time data updates
- ✅ Advanced visualizations (Databricks UI)

---

### 3. MLflow API (EE Parity: Forecasting)

**Purpose**: Replace Odoo Planning forecasting with MLflow models

**Odoo Enterprise Feature**: Financial forecasting (requires Planning app)
**Databricks Alternative**: MLflow Model Registry + Serving

**Implementation**:
```python
# Train BIR tax forecasting model
import mlflow
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

mlflow.set_tracking_uri("databricks")
mlflow.set_experiment("/Shared/BIR/tax_forecasting")

with mlflow.start_run():
    # Load historical data
    df = spark.sql("""
        SELECT
            month,
            agency,
            withholding_tax,
            income_tax,
            vat,
            LAG(withholding_tax, 1) OVER (PARTITION BY agency ORDER BY month) as prev_month_wht,
            LAG(withholding_tax, 12) OVER (PARTITION BY agency ORDER BY month) as prev_year_wht
        FROM gold.bir_transactions
        WHERE year BETWEEN 2022 AND 2025
    """).toPandas()

    # Train model
    X = df[['prev_month_wht', 'prev_year_wht', 'income_tax', 'vat']]
    y = df['withholding_tax']

    model = RandomForestRegressor(n_estimators=100)
    model.fit(X, y)

    # Log model
    mlflow.sklearn.log_model(model, "bir_tax_forecaster")
    mlflow.log_metric("rmse", 0.05)  # Example metric

# Register model
client = mlflow.tracking.MlflowClient()
client.create_model_version(
    name="bir_tax_forecaster",
    source=f"runs:/{run.info.run_id}/model",
    run_id=run.info.run_id
)

# Serve predictions via API
# GET https://<workspace>.azuredatabricks.net/model/bir_tax_forecaster/1/invocations
```

**Integrate with Odoo**:
```python
# addons/ipai/ipai_finance_ppm/models/bir_schedule.py
import requests

class BIRSchedule(models.Model):
    _inherit = 'ipai.finance.bir_schedule'

    predicted_amount = fields.Float("Predicted Tax Amount", compute='_compute_predicted_amount')

    def _compute_predicted_amount(self):
        """Get prediction from Databricks MLflow model"""
        for record in self:
            # Prepare features
            features = {
                'prev_month_wht': record.prev_month_withholding_tax,
                'prev_year_wht': record.prev_year_withholding_tax,
                'income_tax': record.income_tax,
                'vat': record.vat
            }

            # Call MLflow model API
            response = requests.post(
                f"{DATABRICKS_HOST}/model/bir_tax_forecaster/1/invocations",
                headers={"Authorization": f"Bearer {DATABRICKS_TOKEN}"},
                json={"dataframe_records": [features]}
            )

            record.predicted_amount = response.json()['predictions'][0]
```

**Benefits**:
- ✅ No Odoo Planning subscription needed
- ✅ ML-powered forecasts (better than linear projections)
- ✅ Automatic retraining pipeline
- ✅ A/B testing with multiple models

---

### 4. Feature Engineering API (EE Parity: Advanced Analytics)

**Purpose**: Create reusable feature store for financial analytics

**Odoo Enterprise Feature**: Advanced analytics (requires Enterprise Analytics addon)
**Databricks Alternative**: Feature Engineering API + Feature Store

**Implementation**:
```python
# Create feature store
from databricks.feature_engineering import FeatureEngineeringClient

fe = FeatureEngineeringClient()

# Define feature table
fe.create_table(
    name="bir_features.transaction_features",
    primary_keys=["transaction_id"],
    schema="""
        transaction_id STRING,
        transaction_velocity_7d DOUBLE,
        category_frequency_30d INT,
        anomaly_score DOUBLE,
        vendor_risk_score DOUBLE,
        update_time TIMESTAMP
    """,
    description="Financial transaction features for BIR compliance"
)

# Populate features (Spark job)
from pyspark.sql import functions as F
from pyspark.sql.window import Window

# Calculate transaction velocity (7-day rolling)
window_7d = Window.partitionBy("agency").orderBy("transaction_date").rowsBetween(-6, 0)

features_df = spark.sql("""
    SELECT
        transaction_id,
        agency,
        transaction_date,
        amount,
        category,
        vendor_id
    FROM gold.bir_transactions
""").withColumn(
    "transaction_velocity_7d",
    F.count("*").over(window_7d)
).withColumn(
    "category_frequency_30d",
    F.count("category").over(Window.partitionBy("agency", "category").orderBy("transaction_date").rangeBetween(-30, 0))
)

# Write to feature store
fe.write_table(
    name="bir_features.transaction_features",
    df=features_df,
    mode="merge"
)
```

**Use in Odoo**:
```python
# Odoo computed field using features
def _compute_risk_score(self):
    """Get risk score from Databricks feature store"""
    for record in self:
        # Query feature store via SQL API
        query = f"""
            SELECT anomaly_score, vendor_risk_score
            FROM bir_features.transaction_features
            WHERE transaction_id = '{record.transaction_id}'
        """

        result = self._execute_databricks_query(query)
        record.risk_score = result['anomaly_score'] * result['vendor_risk_score']
```

**Benefits**:
- ✅ Centralized feature definitions (no code duplication)
- ✅ Real-time feature serving (<5ms latency)
- ✅ Feature lineage tracking (know how features are computed)
- ✅ Point-in-time correctness (avoid data leakage)

---

### 5. Lakeflow API (Data Platform Modernization)

**Purpose**: Automate ETL pipelines with declarative DLT

**Current Manual ETL**: 2-4 hours, 15-20% error rate
**Databricks DLT**: 20-30 minutes, 98%+ accuracy

**Implementation**:
```python
# Create DLT pipeline via API
pipeline_config = {
    "name": "Scout Transaction ETL",
    "storage": "dbfs:/pipelines/scout_etl",
    "target": "gold",
    "libraries": [
        {"notebook": {"path": "/Shared/ETL/scout_bronze_to_silver"}},
        {"notebook": {"path": "/Shared/ETL/scout_silver_to_gold"}}
    ],
    "clusters": [{
        "label": "default",
        "autoscale": {"min_workers": 1, "max_workers": 5}
    }],
    "development": False,
    "continuous": False,
    "channel": "CURRENT"
}

response = requests.post(
    f"{DATABRICKS_HOST}/api/2.0/pipelines",
    headers={"Authorization": f"Bearer {DATABRICKS_TOKEN}"},
    json=pipeline_config
)

pipeline_id = response.json()["pipeline_id"]

# Trigger pipeline
requests.post(
    f"{DATABRICKS_HOST}/api/2.0/pipelines/{pipeline_id}/updates",
    headers={"Authorization": f"Bearer {DATABRICKS_TOKEN}"},
    json={"full_refresh": False}
)
```

**DLT Notebook** (`/Shared/ETL/scout_bronze_to_silver.py`):
```python
import dlt
from pyspark.sql import functions as F

@dlt.table(
    name="silver_transactions",
    comment="Cleaned Scout transactions with ML column mapping"
)
@dlt.expect_or_drop("valid_amount", "amount > 0")
@dlt.expect_or_drop("valid_date", "transaction_date IS NOT NULL")
def silver_transactions():
    """Bronze → Silver: Clean and validate transactions"""
    return (
        dlt.read("bronze_transactions")
        .withColumn("amount", F.col("amount").cast("decimal(15,2)"))
        .withColumn("transaction_date", F.to_date("transaction_date", "yyyy-MM-dd"))
        .withColumn("category", F.when(F.col("category").isNull(), "UNCATEGORIZED").otherwise(F.col("category")))
        .select("transaction_id", "agency", "transaction_date", "amount", "category", "vendor_id")
    )
```

**Benefits**:
- ✅ 5x faster ETL (2-4 hours → 30 minutes)
- ✅ Declarative syntax (no manual Airflow DAGs)
- ✅ Automatic data quality checks
- ✅ Incremental processing (only new data)

---

## MCP Server: Databricks Integration

**New MCP Server**: `mcp/servers/databricks-mcp-server/`

**Capabilities** (via Databricks APIs):

```typescript
// mcp/servers/databricks-mcp-server/src/index.ts
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const server = new Server({
  name: "databricks-mcp-server",
  version: "1.0.0"
});

// Tool 1: Execute SQL query
server.setRequestHandler("tools/call", async (request) => {
  if (request.params.name === "databricks_execute_sql") {
    const { query } = request.params.arguments;

    // Call Databricks SQL API
    const response = await fetch(
      `${DATABRICKS_HOST}/api/2.0/sql/statements`,
      {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${DATABRICKS_TOKEN}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          statement: query,
          warehouse_id: DATABRICKS_WAREHOUSE_ID
        })
      }
    );

    const result = await response.json();
    return { content: [{ type: "text", text: JSON.stringify(result.result) }] };
  }

  // Tool 2: Trigger ETL job
  if (request.params.name === "databricks_run_job") {
    const { job_id } = request.params.arguments;

    const response = await fetch(
      `${DATABRICKS_HOST}/api/2.1/jobs/run-now`,
      {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${DATABRICKS_TOKEN}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ job_id })
      }
    );

    const result = await response.json();
    return { content: [{ type: "text", text: `Job triggered: run_id=${result.run_id}` }] };
  }

  // Tool 3: Get MLflow prediction
  if (request.params.name === "databricks_predict") {
    const { model_name, version, features } = request.params.arguments;

    const response = await fetch(
      `${DATABRICKS_HOST}/model/${model_name}/${version}/invocations`,
      {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${DATABRICKS_TOKEN}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ dataframe_records: [features] })
      }
    );

    const result = await response.json();
    return { content: [{ type: "text", text: `Prediction: ${result.predictions[0]}` }] };
  }
});
```

**Configuration** (`.claude/mcp-servers.json`):
```json
{
  "mcpServers": {
    "databricks": {
      "command": "node",
      "args": ["mcp/servers/databricks-mcp-server/dist/index.js"],
      "env": {
        "DATABRICKS_HOST": "https://<workspace-id>.azuredatabricks.net",
        "DATABRICKS_TOKEN": "${DATABRICKS_ACCESS_TOKEN}",
        "DATABRICKS_WAREHOUSE_ID": "${DATABRICKS_WAREHOUSE_ID}"
      }
    }
  }
}
```

---

## Acceleration Timeline (Parallel Execution)

### Phase 1: Foundation (Weeks 1-4)

**EE Parity Track**:
- ✅ Week 1: Set up Databricks workspace + REST API access
- ✅ Week 2: Create `databricks-mcp-server` with SQL Analytics API
- ✅ Week 3: Build custom BIR dashboard (replace Odoo Studio)
- ✅ Week 4: Embed dashboards in Odoo views

**Data Platform Track**:
- ✅ Week 1: Set up Delta Lake storage (Bronze/Silver/Gold)
- ✅ Week 2: Create Lakeflow DLT pipeline (Scout transactions)
- ✅ Week 3: Migrate Supabase Bronze → Databricks Delta Lake
- ✅ Week 4: Validate parity (parallel run)

### Phase 2: ML Capabilities (Weeks 5-8)

**EE Parity Track**:
- ✅ Week 5: Train BIR tax forecasting model (MLflow)
- ✅ Week 6: Deploy model to production (Model Registry)
- ✅ Week 7: Integrate predictions in Odoo (computed fields)
- ✅ Week 8: A/B test vs. current manual forecasts

**Data Platform Track**:
- ✅ Week 5: Create Feature Engineering pipeline
- ✅ Week 6: Build feature store (50+ financial features)
- ✅ Week 7: Integrate feature store with Odoo
- ✅ Week 8: Validate feature freshness (<5 minutes)

### Phase 3: Production (Weeks 9-12)

**Combined Deployment**:
- ✅ Week 9: CI/CD pipelines for Databricks Asset Bundles
- ✅ Week 10: Production cutover (Supabase → Databricks for analytics)
- ✅ Week 11: Monitor performance, rollback plan ready
- ✅ Week 12: Post-launch audit, optimize costs

**Total Timeline**: 12 weeks (3 months)

---

## Cost-Benefit Analysis

### Investment

**Infrastructure**:
- Databricks workspace: $500-800/month (serverless compute)
- Azure Storage (Delta Lake): $100/month
- Data transfer: $50/month
- **Total**: ~$700/month

**Development**:
- MCP server development: 40 hours
- Dashboard creation: 20 hours
- ML model training: 30 hours
- Integration testing: 30 hours
- **Total**: 120 hours (~3 weeks for 1 developer)

### Savings

**Enterprise Edition Subscriptions (Avoided)**:
- Odoo Studio: $30/user/month × 8 users = $240/month
- Odoo Planning: $25/user/month × 8 users = $200/month
- Odoo Enterprise Analytics: $50/user/month × 8 users = $400/month
- **Total**: $840/month saved

**Labor Savings**:
- Manual ETL: 40 hours/month → 5 hours/month (automated)
- BIR forecasting: 10 hours/month → 1 hour/month (ML-powered)
- Dashboard creation: 15 hours/month → 2 hours/month (reusable)
- **Total**: 57 hours/month saved = $5,700/month (at $100/hour)

### ROI

**Monthly**:
- Savings: $840 (subscriptions) + $5,700 (labor) = $6,540
- Costs: $700 (infrastructure)
- **Net**: $5,840/month positive

**Break-even**: Immediate (positive cash flow from month 1)

**Annual ROI**: $5,840 × 12 = $70,080/year

---

## Acceptance Criteria

### EE Parity (Databricks-Powered Features)

**Custom Dashboards**:
- ✅ 5+ Databricks SQL dashboards embedded in Odoo
- ✅ Real-time data updates (<5 minutes)
- ✅ No Odoo Studio subscription required
- ✅ User satisfaction ≥90% (survey)

**Forecasting**:
- ✅ BIR tax predictions ≥95% accuracy
- ✅ MLflow model registry operational
- ✅ Predictions exposed in Odoo computed fields
- ✅ A/B test shows ML > manual forecasts

**Advanced Analytics**:
- ✅ Feature store with 50+ features
- ✅ Feature freshness <5 minutes
- ✅ Feature lineage documented
- ✅ Risk scores computed in real-time

### Data Platform (Lakehouse)

**ETL Performance**:
- ✅ ETL runtime: 2-4 hours → <30 minutes
- ✅ Data quality: 80-85% → >98%
- ✅ Processing capacity: 10M → 100M transactions
- ✅ Cost per transaction: 50% reduction

**Integration**:
- ✅ Odoo queries Databricks via SQL API
- ✅ n8n triggers Databricks jobs
- ✅ MCP server responds to Claude Code
- ✅ Apache Superset queries Delta Lake

---

## Next Steps

1. ✅ Document acceleration strategy (this file)
2. ⏳ Review with stakeholders (technical + finance)
3. ⏳ Approve Azure subscription + budget
4. ⏳ Create Databricks workspace
5. ⏳ Build `databricks-mcp-server` prototype
6. ⏳ Parallel execution: EE Parity + Data Platform tracks

---

**Status**: PROPOSED - Awaiting approval to proceed
**Owner**: Jake Tolentino
**Timeline**: 12 weeks (3 months) parallel execution
**ROI**: $70,080/year positive cash flow
