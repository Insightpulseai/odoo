# Enterprise SaaS ERP - Databricks Architecture Pattern

---

**Purpose**: Analyze how enterprise SaaS ERP platforms structure Databricks projects and GitHub repositories, with recommendations for odoo-ce.

**Status**: ARCHITECTURE GUIDE
**Created**: 2026-01-26
**Reference**: NetSuite, SAP, Workday, Oracle Cloud ERP patterns

---

## Industry Standard Patterns

### Tier 1 SaaS ERPs (Reference Architecture)

**Companies Analyzed**:
- **NetSuite (Oracle)**: Multi-tenant SaaS ERP with analytics platform
- **SAP S/4HANA Cloud**: Enterprise resource planning with data warehouse
- **Workday**: Cloud-native financial/HR platform with Prism Analytics
- **Microsoft Dynamics 365**: ERP/CRM with Power BI and Azure Synapse
- **Oracle Fusion Cloud**: Complete ERP suite with Oracle Analytics Cloud

---

## Repository Structure Patterns

### Pattern 1: Monorepo (Most Common for Enterprise)

**Used By**: NetSuite Analytics, SAP Data Warehouse Cloud, Workday Prism

**Structure**:
```
enterprise-erp-analytics/
├── .github/
│   ├── workflows/
│   │   ├── ci-lint.yml
│   │   ├── ci-test.yml
│   │   ├── cd-dev.yml
│   │   ├── cd-staging.yml
│   │   └── cd-prod.yml
│   └── CODEOWNERS
│
├── databricks/
│   ├── bundles/                          # Asset Bundles (IaC)
│   │   ├── dev/
│   │   │   └── databricks.yml
│   │   ├── staging/
│   │   │   └── databricks.yml
│   │   └── prod/
│   │       └── databricks.yml
│   │
│   ├── notebooks/                        # Databricks notebooks
│   │   ├── etl/
│   │   │   ├── finance/                  # Domain-specific
│   │   │   │   ├── accounts_payable.py
│   │   │   │   ├── accounts_receivable.py
│   │   │   │   └── general_ledger.py
│   │   │   ├── hr/
│   │   │   │   ├── payroll.py
│   │   │   │   └── time_tracking.py
│   │   │   └── supply_chain/
│   │   │       ├── inventory.py
│   │   │       └── procurement.py
│   │   ├── ml/
│   │   │   ├── forecasting/
│   │   │   ├── anomaly_detection/
│   │   │   └── recommendation/
│   │   └── analytics/
│   │       ├── dashboards/
│   │       └── reports/
│   │
│   ├── src/                              # Reusable Python packages
│   │   ├── common/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── logging.py
│   │   │   └── utils.py
│   │   ├── data_quality/
│   │   │   ├── __init__.py
│   │   │   ├── expectations.py
│   │   │   └── validators.py
│   │   ├── feature_engineering/
│   │   │   ├── __init__.py
│   │   │   ├── transformers.py
│   │   │   └── aggregators.py
│   │   └── connectors/
│   │       ├── __init__.py
│   │       ├── erp_connector.py
│   │       ├── crm_connector.py
│   │       └── external_api.py
│   │
│   ├── tests/                            # Unit + integration tests
│   │   ├── unit/
│   │   ├── integration/
│   │   └── fixtures/
│   │
│   └── config/                           # Configuration files
│       ├── clusters/
│       ├── jobs/
│       └── warehouses/
│
├── terraform/                            # Infrastructure as Code
│   ├── modules/
│   │   ├── databricks_workspace/
│   │   ├── unity_catalog/
│   │   └── networking/
│   ├── environments/
│   │   ├── dev/
│   │   ├── staging/
│   │   └── prod/
│   └── shared/
│
├── docker/                               # Local development
│   ├── Dockerfile.databricks
│   └── docker-compose.yml
│
├── scripts/                              # Automation scripts
│   ├── deploy/
│   ├── migrate/
│   └── validate/
│
├── docs/                                 # Documentation
│   ├── architecture/
│   ├── runbooks/
│   └── api/
│
├── requirements.txt                      # Python dependencies
├── pyproject.toml                        # Python project config
├── Makefile                              # Common operations
└── README.md
```

**Benefits**:
- ✅ Single source of truth
- ✅ Atomic commits across infrastructure + code
- ✅ Easier dependency management
- ✅ Unified CI/CD pipeline

**Drawbacks**:
- ❌ Large repository size
- ❌ Longer CI/CD times
- ❌ Requires good tooling (Turborepo, Nx)

---

### Pattern 2: Multi-Repo (Used by Oracle, Microsoft)

**Structure**:
```
Organization: acme-corp

Repositories:
├── erp-databricks-platform          # Platform configuration
│   ├── terraform/
│   ├── unity-catalog/
│   └── workspace-config/
│
├── erp-etl-pipelines                 # ETL jobs
│   ├── finance/
│   ├── hr/
│   └── supply-chain/
│
├── erp-ml-models                     # ML models
│   ├── forecasting/
│   ├── anomaly-detection/
│   └── recommendation/
│
├── erp-analytics-dashboards          # BI dashboards
│   ├── executive/
│   ├── finance/
│   └── operations/
│
└── erp-shared-libraries              # Common utilities
    ├── data-quality/
    ├── logging/
    └── connectors/
```

**Benefits**:
- ✅ Clear separation of concerns
- ✅ Independent versioning
- ✅ Team autonomy (finance vs HR)
- ✅ Faster CI/CD per repo

**Drawbacks**:
- ❌ Dependency management complexity
- ❌ Cross-repo changes difficult
- ❌ Version drift risk

---

## Recommended Architecture for odoo-ce

### Hybrid Approach (Monorepo with Domain Separation)

**Rationale**: odoo-ce already has monorepo structure, extend with Databricks as subdirectory.

**Repository Structure**:
```
odoo-ce/                                  # Main repository
├── addons/                               # Odoo modules (existing)
│   └── ipai/
│       ├── ipai_finance_ppm/
│       ├── ipai_workspace_core/
│       └── ...
│
├── databricks/                           # NEW: Databricks integration
│   ├── bundles/                          # Asset Bundles (IaC)
│   │   ├── databricks.yml                # Root bundle config
│   │   ├── resources/
│   │   │   ├── clusters.yml
│   │   │   ├── jobs.yml
│   │   │   ├── pipelines.yml
│   │   │   ├── warehouses.yml
│   │   │   └── mlflow.yml
│   │   └── targets/
│   │       ├── dev.yml
│   │       ├── staging.yml
│   │       └── prod.yml
│   │
│   ├── notebooks/                        # Databricks notebooks
│   │   ├── etl/
│   │   │   ├── finance/
│   │   │   │   ├── bir_compliance/
│   │   │   │   │   ├── 1601c_ingestion.py
│   │   │   │   │   ├── 2550q_aggregation.py
│   │   │   │   │   └── month_end_close.py
│   │   │   │   ├── accounts_payable/
│   │   │   │   └── general_ledger/
│   │   │   ├── scout/
│   │   │   │   ├── transaction_ingestion.py
│   │   │   │   ├── expense_categorization.py
│   │   │   │   └── vendor_enrichment.py
│   │   │   └── shared/
│   │   │       ├── bronze_to_silver.py
│   │   │       └── silver_to_gold.py
│   │   ├── ml/
│   │   │   ├── forecasting/
│   │   │   │   ├── bir_tax_predictor/
│   │   │   │   │   ├── train.py
│   │   │   │   │   ├── evaluate.py
│   │   │   │   │   └── deploy.py
│   │   │   │   └── expense_predictor/
│   │   │   ├── classification/
│   │   │   │   └── expense_categorization/
│   │   │   └── anomaly_detection/
│   │   │       └── fraud_detection/
│   │   └── analytics/
│   │       ├── bir_dashboards/
│   │       ├── scout_reports/
│   │       └── executive_summary/
│   │
│   ├── src/                              # Reusable Python packages
│   │   ├── odoo_databricks/              # Main package
│   │   │   ├── __init__.py
│   │   │   ├── common/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── config.py
│   │   │   │   ├── logging.py
│   │   │   │   └── spark_utils.py
│   │   │   ├── connectors/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── odoo_connector.py
│   │   │   │   ├── supabase_connector.py
│   │   │   │   ├── n8n_connector.py
│   │   │   │   └── mattermost_connector.py
│   │   │   ├── data_quality/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── expectations.py
│   │   │   │   ├── validators.py
│   │   │   │   └── bir_rules.py
│   │   │   ├── feature_engineering/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── transformers.py
│   │   │   │   ├── aggregators.py
│   │   │   │   └── financial_features.py
│   │   │   └── ml/
│   │   │       ├── __init__.py
│   │   │       ├── models.py
│   │   │       ├── training.py
│   │   │       └── serving.py
│   │   └── setup.py
│   │
│   ├── tests/                            # Tests
│   │   ├── unit/
│   │   │   ├── test_connectors.py
│   │   │   ├── test_data_quality.py
│   │   │   └── test_features.py
│   │   ├── integration/
│   │   │   ├── test_etl_pipeline.py
│   │   │   ├── test_ml_training.py
│   │   │   └── test_odoo_integration.py
│   │   └── fixtures/
│   │       ├── sample_transactions.json
│   │       └── sample_bir_forms.json
│   │
│   ├── config/                           # Configuration templates
│   │   ├── clusters/
│   │   │   ├── etl_cluster.json
│   │   │   └── ml_cluster.json
│   │   ├── jobs/
│   │   │   ├── bir_monthly_close.json
│   │   │   └── scout_daily_sync.json
│   │   └── warehouses/
│   │       └── analytics_warehouse.json
│   │
│   ├── migrations/                       # Data migrations
│   │   ├── 001_initial_schema.sql
│   │   ├── 002_add_bir_tables.sql
│   │   └── ...
│   │
│   └── docs/                             # Databricks-specific docs
│       ├── architecture.md
│       ├── deployment.md
│       └── troubleshooting.md
│
├── mcp/                                  # MCP servers (existing)
│   └── servers/
│       ├── databricks-mcp-server/        # NEW: Databricks MCP
│       │   ├── src/
│       │   │   ├── index.ts
│       │   │   ├── tools/
│       │   │   │   ├── execute_sql.ts
│       │   │   │   ├── run_job.ts
│       │   │   │   └── predict.ts
│       │   │   └── utils/
│       │   ├── package.json
│       │   └── tsconfig.json
│       └── ...
│
├── .github/
│   └── workflows/
│       ├── databricks-ci.yml             # NEW: Databricks CI
│       ├── databricks-deploy-dev.yml     # NEW: Deploy dev
│       ├── databricks-deploy-prod.yml    # NEW: Deploy prod
│       └── ... (existing workflows)
│
├── terraform/                            # Infrastructure (existing)
│   ├── databricks/                       # NEW: Databricks IaC
│   │   ├── main.tf
│   │   ├── workspace.tf
│   │   ├── unity_catalog.tf
│   │   ├── networking.tf
│   │   └── variables.tf
│   └── ...
│
├── docs/
│   ├── databricks/                       # NEW: Databricks docs
│   │   ├── GETTING_STARTED.md
│   │   ├── ARCHITECTURE.md
│   │   ├── API_REFERENCE.md
│   │   └── RUNBOOKS.md
│   └── ...
│
└── CLAUDE.md                             # Updated with Databricks rules
```

---

## Unity Catalog Structure (Enterprise Standard)

### Catalog Organization Pattern

**Multi-Tenant Pattern** (NetSuite, Workday):
```
Unity Catalog Metastore
├── bronze                                # Raw ingested data
│   ├── external_sources/
│   │   ├── google_drive_exports/
│   │   ├── odoo_api_sync/
│   │   └── n8n_webhooks/
│   └── scout/
│       └── transactions/
│
├── silver                                # Cleaned and validated
│   ├── finance/
│   │   ├── bir_transactions/
│   │   ├── accounts_payable/
│   │   └── general_ledger/
│   ├── scout/
│   │   ├── transactions_clean/
│   │   └── expense_categories/
│   └── shared/
│       └── reference_data/
│
├── gold                                  # Business-ready aggregates
│   ├── finance/
│   │   ├── bir_monthly/
│   │   ├── bir_quarterly/
│   │   ├── month_end_close/
│   │   └── executive_dashboard/
│   ├── scout/
│   │   ├── agency_summary/
│   │   └── vendor_analysis/
│   └── ml_features/
│       ├── bir_forecasting/
│       └── expense_prediction/
│
├── platinum                              # ML models + predictions
│   ├── models/
│   │   ├── bir_tax_forecaster/
│   │   └── expense_classifier/
│   └── predictions/
│       ├── bir_monthly_forecast/
│       └── expense_anomalies/
│
└── sandbox                               # Development/testing
    ├── dev_finance/
    ├── dev_ml/
    └── feature_testing/
```

**Benefits**:
- ✅ Clear data lifecycle (bronze → silver → gold → platinum)
- ✅ Domain isolation (finance, scout, shared)
- ✅ Development safety (sandbox catalog)
- ✅ Consistent naming conventions

---

## Access Control Patterns (Enterprise)

### Role-Based Access Control (RBAC)

**Service Principals** (Application Access):
```sql
-- n8n automation service
CREATE SERVICE PRINCIPAL 'odoo-ce-n8n';
GRANT SELECT ON CATALOG silver TO SERVICE_PRINCIPAL `odoo-ce-n8n`;
GRANT SELECT ON CATALOG gold TO SERVICE_PRINCIPAL `odoo-ce-n8n`;
GRANT ALL PRIVILEGES ON CATALOG bronze TO SERVICE_PRINCIPAL `odoo-ce-n8n`;

-- Odoo application
CREATE SERVICE PRINCIPAL 'odoo-ce-app';
GRANT SELECT ON CATALOG gold TO SERVICE_PRINCIPAL `odoo-ce-app`;
GRANT EXECUTE ON FUNCTION gold.ml_features.get_bir_forecast TO SERVICE_PRINCIPAL `odoo-ce-app`;

-- CI/CD pipeline
CREATE SERVICE PRINCIPAL 'odoo-ce-cicd';
GRANT ALL PRIVILEGES ON CATALOG sandbox TO SERVICE_PRINCIPAL `odoo-ce-cicd`;
GRANT SELECT ON CATALOG silver TO SERVICE_PRINCIPAL `odoo-ce-cicd`;

-- MCP Server (Claude Code)
CREATE SERVICE PRINCIPAL 'odoo-ce-mcp';
GRANT SELECT ON CATALOG gold TO SERVICE_PRINCIPAL `odoo-ce-mcp`;
GRANT EXECUTE ON FUNCTION gold.ml_features.get_bir_forecast TO SERVICE_PRINCIPAL `odoo-ce-mcp`;
```

**User Groups** (Human Access):
```sql
-- Finance team
CREATE GROUP finance_analysts;
GRANT SELECT ON CATALOG silver.finance TO GROUP `finance_analysts`;
GRANT SELECT ON CATALOG gold.finance TO GROUP `finance_analysts`;

-- Data scientists
CREATE GROUP data_scientists;
GRANT ALL PRIVILEGES ON CATALOG sandbox TO GROUP `data_scientists`;
GRANT SELECT ON CATALOG silver TO GROUP `data_scientists`;
GRANT SELECT ON CATALOG gold TO GROUP `data_scientists`;

-- Executives
CREATE GROUP executives;
GRANT SELECT ON CATALOG gold.finance.executive_dashboard TO GROUP `executives`;

-- Admins
CREATE GROUP databricks_admins;
GRANT ALL PRIVILEGES ON METASTORE TO GROUP `databricks_admins`;
```

---

## CI/CD Pipeline Pattern (Enterprise)

### GitHub Actions Workflow

**Multi-Environment Deployment**:
```yaml
# .github/workflows/databricks-deploy.yml
name: Databricks Deploy

on:
  push:
    branches: [main, develop]
    paths:
      - 'databricks/**'
  pull_request:
    paths:
      - 'databricks/**'

env:
  DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install black flake8 mypy pytest
          pip install -r databricks/requirements.txt
      - name: Lint code
        run: |
          black --check databricks/src databricks/notebooks
          flake8 databricks/src databricks/notebooks
          mypy databricks/src

  test:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r databricks/requirements.txt
      - name: Run unit tests
        run: pytest databricks/tests/unit --cov=databricks/src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml

  validate-bundle:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4
      - name: Install Databricks CLI
        run: pip install databricks-cli
      - name: Configure Databricks
        env:
          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN_DEV }}
        run: |
          echo "$DATABRICKS_HOST" > ~/.databrickscfg
          echo "$DATABRICKS_TOKEN" >> ~/.databrickscfg
      - name: Validate bundle (dev)
        run: databricks bundle validate -t dev
        working-directory: databricks

  deploy-dev:
    runs-on: ubuntu-latest
    needs: validate-bundle
    if: github.ref == 'refs/heads/develop'
    environment: dev
    steps:
      - uses: actions/checkout@v4
      - name: Install Databricks CLI
        run: pip install databricks-cli
      - name: Deploy to dev
        env:
          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN_DEV }}
        run: |
          databricks bundle deploy -t dev
          databricks bundle run bir_etl -t dev
        working-directory: databricks

  deploy-staging:
    runs-on: ubuntu-latest
    needs: validate-bundle
    if: github.ref == 'refs/heads/main'
    environment: staging
    steps:
      - uses: actions/checkout@v4
      - name: Install Databricks CLI
        run: pip install databricks-cli
      - name: Deploy to staging
        env:
          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN_STAGING }}
        run: databricks bundle deploy -t staging
        working-directory: databricks
      - name: Run integration tests
        run: databricks bundle run integration_tests -t staging
        working-directory: databricks

  deploy-prod:
    runs-on: ubuntu-latest
    needs: deploy-staging
    if: github.ref == 'refs/heads/main'
    environment: production
    steps:
      - uses: actions/checkout@v4
      - name: Install Databricks CLI
        run: pip install databricks-cli
      - name: Deploy to production
        env:
          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN_PROD }}
        run: databricks bundle deploy -t prod
        working-directory: databricks
      - name: Smoke test
        run: databricks bundle run smoke_tests -t prod
        working-directory: databricks
      - name: Notify Mattermost
        uses: mattermost/action-mattermost-notify@master
        with:
          MATTERMOST_WEBHOOK_URL: ${{ secrets.MATTERMOST_WEBHOOK_URL }}
          TEXT: "✅ Databricks deployed to production (commit: ${{ github.sha }})"
```

---

## Configuration Management Pattern

### Environment-Specific Configs

**Asset Bundle Targets**:
```yaml
# databricks/bundles/databricks.yml
bundle:
  name: odoo-ce-databricks

include:
  - resources/*.yml

variables:
  catalog:
    description: "Unity Catalog name"
  warehouse_id:
    description: "SQL Warehouse ID"
  notification_email:
    description: "Notification email"

targets:
  dev:
    mode: development
    workspace:
      host: https://odoo-ce-dev.azuredatabricks.net
    variables:
      catalog: sandbox
      warehouse_id: ${var.dev_warehouse_id}
      notification_email: dev-team@insightpulseai.com

  staging:
    mode: production
    workspace:
      host: https://odoo-ce-staging.azuredatabricks.net
    variables:
      catalog: silver
      warehouse_id: ${var.staging_warehouse_id}
      notification_email: qa-team@insightpulseai.com

  prod:
    mode: production
    workspace:
      host: https://odoo-ce-prod.azuredatabricks.net
    variables:
      catalog: gold
      warehouse_id: ${var.prod_warehouse_id}
      notification_email: business@insightpulseai.com
    permissions:
      - level: CAN_VIEW
        group_name: all_users
```

**Jobs Configuration**:
```yaml
# databricks/bundles/resources/jobs.yml
resources:
  jobs:
    bir_etl:
      name: "BIR ETL - ${bundle.target}"
      tasks:
        - task_key: bronze_ingestion
          notebook_task:
            notebook_path: ${workspace.file_path}/notebooks/etl/finance/bir_compliance/1601c_ingestion.py
            base_parameters:
              catalog: ${var.catalog}
          new_cluster:
            spark_version: "14.3.x-scala2.12"
            node_type_id: "Standard_DS3_v2"
            num_workers: 2
            spark_conf:
              spark.databricks.delta.optimizeWrite.enabled: "true"

      email_notifications:
        on_success: [${var.notification_email}]
        on_failure: [${var.notification_email}]

      # Dev: manual trigger only
      # Staging/Prod: scheduled
      schedule:
        quartz_cron_expression: ${bundle.target == "dev" ? "" : "0 0 2 1 * ?"}
        timezone_id: "Asia/Manila"
        pause_status: ${bundle.target == "dev" ? "PAUSED" : "UNPAUSED"}
```

---

## Data Quality Framework (Enterprise)

### Great Expectations Integration

**Structure**:
```
databricks/
├── src/
│   └── odoo_databricks/
│       └── data_quality/
│           ├── __init__.py
│           ├── expectations.py
│           ├── checkpoints.py
│           └── suites/
│               ├── bronze_expectations.json
│               ├── silver_expectations.json
│               └── gold_expectations.json
```

**Implementation**:
```python
# databricks/src/odoo_databricks/data_quality/expectations.py
import great_expectations as ge
from great_expectations.dataset import SparkDFDataset

class BIRDataQuality:
    """Data quality expectations for BIR transactions"""

    @staticmethod
    def validate_bronze(df):
        """Validate bronze layer expectations"""
        ge_df = SparkDFDataset(df)

        # Completeness
        ge_df.expect_column_values_to_not_be_null("transaction_id")
        ge_df.expect_column_values_to_not_be_null("transaction_date")
        ge_df.expect_column_values_to_not_be_null("amount")

        # Validity
        ge_df.expect_column_values_to_be_between("amount", min_value=0, max_value=10000000)
        ge_df.expect_column_values_to_be_in_set("agency", ["RIM", "CKVC", "BOM", "JPAL", "JLI", "JAP", "LAS", "RMQB"])

        # Uniqueness
        ge_df.expect_column_values_to_be_unique("transaction_id")

        results = ge_df.validate()
        return results.success, results

    @staticmethod
    def validate_silver(df):
        """Validate silver layer expectations"""
        ge_df = SparkDFDataset(df)

        # Type checks
        ge_df.expect_column_values_to_be_of_type("amount", "DecimalType")
        ge_df.expect_column_values_to_be_of_type("transaction_date", "DateType")

        # Business rules
        ge_df.expect_column_values_to_match_regex("transaction_id", r"^TXN\d{10}$")

        results = ge_df.validate()
        return results.success, results
```

**Usage in Notebooks**:
```python
# databricks/notebooks/etl/finance/bir_compliance/1601c_ingestion.py
from odoo_databricks.data_quality import BIRDataQuality

# After ingestion
df_bronze = spark.read.format("delta").load("dbfs:/bronze/bir_transactions")

# Validate
success, results = BIRDataQuality.validate_bronze(df_bronze)

if not success:
    # Log failures
    for check in results.results:
        if not check.success:
            print(f"❌ Failed: {check.expectation_config['expectation_type']}")
    raise Exception("Data quality checks failed")
else:
    print(f"✅ Data quality checks passed ({results.statistics['successful_expectations']}/{results.statistics['evaluated_expectations']})")
```

---

## Monitoring & Observability (Enterprise)

### Logging Pattern

**Structured Logging**:
```python
# databricks/src/odoo_databricks/common/logging.py
import logging
import json
from datetime import datetime

class StructuredLogger:
    """Enterprise-grade structured logging"""

    def __init__(self, name, environment):
        self.logger = logging.getLogger(name)
        self.environment = environment

    def log(self, level, event, **kwargs):
        """Log structured event"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "environment": self.environment,
            "event": event,
            "level": level,
            **kwargs
        }

        self.logger.log(getattr(logging, level), json.dumps(log_entry))

    def info(self, event, **kwargs):
        self.log("INFO", event, **kwargs)

    def error(self, event, error=None, **kwargs):
        if error:
            kwargs["error"] = str(error)
            kwargs["error_type"] = type(error).__name__
        self.log("ERROR", event, **kwargs)

# Usage
logger = StructuredLogger("bir_etl", environment="prod")
logger.info("etl_started", job_id="123", catalog="gold")
logger.error("validation_failed", error=e, table="gold.bir_monthly")
```

### Metrics Collection

**Custom Metrics**:
```python
# databricks/src/odoo_databricks/common/metrics.py
from datetime import datetime

class MetricsCollector:
    """Collect and publish metrics to Databricks system tables"""

    def __init__(self, spark):
        self.spark = spark
        self.metrics = []

    def record(self, metric_name, value, tags=None):
        """Record a metric"""
        self.metrics.append({
            "timestamp": datetime.utcnow(),
            "metric_name": metric_name,
            "value": value,
            "tags": tags or {}
        })

    def publish(self):
        """Publish metrics to Delta table"""
        df = self.spark.createDataFrame(self.metrics)
        df.write.format("delta").mode("append").saveAsTable("system.metrics.custom_metrics")

# Usage
metrics = MetricsCollector(spark)
metrics.record("etl_runtime_seconds", 1234.56, tags={"job": "bir_etl", "stage": "bronze_to_silver"})
metrics.record("rows_processed", 1000000, tags={"table": "gold.bir_monthly"})
metrics.publish()
```

---

## Cost Optimization Patterns (Enterprise)

### Cluster Policies

**Cost-Optimized Policy**:
```json
{
  "name": "Cost-Optimized ETL",
  "definition": {
    "spark_version": {
      "type": "fixed",
      "value": "14.3.x-scala2.12"
    },
    "node_type_id": {
      "type": "allowlist",
      "values": ["Standard_DS3_v2", "Standard_DS4_v2"]
    },
    "autoscale": {
      "type": "fixed",
      "value": {
        "min_workers": 2,
        "max_workers": 8
      }
    },
    "autotermination_minutes": {
      "type": "fixed",
      "value": 30
    },
    "azure_attributes": {
      "type": "fixed",
      "value": {
        "availability": "SPOT_WITH_FALLBACK_AZURE",
        "spot_bid_max_price": -1
      }
    }
  }
}
```

**ML Training Policy**:
```json
{
  "name": "ML Training - GPU",
  "definition": {
    "node_type_id": {
      "type": "allowlist",
      "values": ["Standard_NC6s_v3", "Standard_NC12s_v3"]
    },
    "runtime_engine": {
      "type": "fixed",
      "value": "PHOTON"
    },
    "autotermination_minutes": {
      "type": "fixed",
      "value": 60
    }
  }
}
```

---

## Recommended Implementation Plan

### Phase 1: Repository Structure (Week 1)

```bash
# 1. Create Databricks directory structure
cd ~/Documents/GitHub/odoo-ce
mkdir -p databricks/{bundles,notebooks,src,tests,config,migrations,docs}
mkdir -p databricks/notebooks/{etl,ml,analytics}
mkdir -p databricks/src/odoo_databricks/{common,connectors,data_quality,feature_engineering,ml}
mkdir -p databricks/tests/{unit,integration,fixtures}

# 2. Initialize Python package
cat > databricks/src/setup.py << 'EOF'
from setuptools import setup, find_packages

setup(
    name="odoo-databricks",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pyspark",
        "delta-spark",
        "mlflow",
        "databricks-sdk",
        "great-expectations"
    ]
)
EOF

# 3. Create bundle config
cat > databricks/bundles/databricks.yml << 'EOF'
bundle:
  name: odoo-ce-databricks

include:
  - resources/*.yml

targets:
  dev:
    workspace:
      host: https://<workspace-dev>.azuredatabricks.net
  prod:
    workspace:
      host: https://<workspace-prod>.azuredatabricks.net
EOF
```

### Phase 2: Unity Catalog Setup (Week 2)

```sql
-- Create catalogs
CREATE CATALOG IF NOT EXISTS bronze COMMENT 'Raw ingested data';
CREATE CATALOG IF NOT EXISTS silver COMMENT 'Cleaned and validated';
CREATE CATALOG IF NOT EXISTS gold COMMENT 'Business-ready aggregates';
CREATE CATALOG IF NOT EXISTS platinum COMMENT 'ML models and predictions';
CREATE CATALOG IF NOT EXISTS sandbox COMMENT 'Development testing';

-- Create schemas
CREATE SCHEMA IF NOT EXISTS bronze.scout;
CREATE SCHEMA IF NOT EXISTS silver.finance;
CREATE SCHEMA IF NOT EXISTS silver.scout;
CREATE SCHEMA IF NOT EXISTS gold.finance;
CREATE SCHEMA IF NOT EXISTS gold.ml_features;
CREATE SCHEMA IF NOT EXISTS platinum.models;
```

### Phase 3: CI/CD Pipeline (Week 3)

```bash
# Create GitHub Actions workflow
mkdir -p .github/workflows
cp spec/databricks-integration/ENTERPRISE_ARCHITECTURE.md .github/workflows/databricks-deploy.yml
# (Use workflow YAML from CI/CD Pipeline Pattern section)
```

### Phase 4: Access Control (Week 4)

```sql
-- Service principals
CREATE SERVICE PRINCIPAL 'odoo-ce-n8n';
CREATE SERVICE PRINCIPAL 'odoo-ce-app';
CREATE SERVICE PRINCIPAL 'odoo-ce-cicd';

-- Grant permissions
GRANT SELECT ON CATALOG gold TO SERVICE_PRINCIPAL `odoo-ce-app`;
GRANT ALL PRIVILEGES ON CATALOG bronze TO SERVICE_PRINCIPAL `odoo-ce-n8n`;
```

---

## Acceptance Criteria

**Repository Structure**:
- ✅ Databricks directory follows enterprise pattern
- ✅ Python package structure with setup.py
- ✅ Asset bundles configured for dev/staging/prod
- ✅ Tests organized (unit/integration)

**Unity Catalog**:
- ✅ 5 catalogs (bronze/silver/gold/platinum/sandbox)
- ✅ Domain-specific schemas (finance, scout, ml_features)
- ✅ Service principals configured
- ✅ RBAC policies enforced

**CI/CD**:
- ✅ Lint + test + deploy pipeline
- ✅ Environment-specific deployments
- ✅ Integration tests in staging
- ✅ Smoke tests in production

**Monitoring**:
- ✅ Structured logging implemented
- ✅ Custom metrics collected
- ✅ Alerts configured
- ✅ Cost tracking enabled

---

**Status**: ARCHITECTURE GUIDE
**Pattern**: Hybrid Monorepo (Enterprise Standard)
**Timeline**: 4 weeks setup + ongoing maintenance
