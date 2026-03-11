# Databricks Data Science Agent

Integration guide for using the Data Science Agent within the InsightPulseAI stack.

> **See also**: [Data Science Platform](./DATA_SCIENCE_PLATFORM.md) for the broader platform capabilities including collaborative notebooks, IDE integrations, and visual tools.

## Overview

The Data Science Agent is an AI-powered assistant in Databricks notebooks and SQL Editor that can:

- Plan multi-step data science workflows
- Generate and execute code autonomously
- Fix errors automatically
- Interpret outputs and iterate

## Prerequisites

- Partner-powered AI features enabled (account + workspace)
- Databricks Assistant Agent Mode preview enabled
- Unity Catalog permissions for target tables

## Lakeflow Architecture

Lakeflow is Databricks' end-to-end data engineering solution with three pipeline layers:

| Layer | Automation | Customization | Use Case |
|-------|------------|---------------|----------|
| **Fully-managed connectors** | High | Low | Fast ingestion from popular sources |
| **Lakeflow Spark Declarative Pipelines** | Medium | Medium | Reliable ETL with some customization |
| **Structured Streaming** | Low | High | Advanced custom streaming solutions |

### Available Lakeflow Connect Sources

**Databricks Native Connectors:**
- Amazon S3
- Salesforce
- Google Analytics Raw Data
- SAP Business Data Cloud
- Workday Reports
- ServiceNow
- Dynamics 365 (Preview)
- Jira (Preview)
- Confluence (Preview)

**Fivetran Connectors (via Partner Connect):**
- OneDrive
- Google Drive
- GitHub
- Webhooks
- Adjust
- [See all Fivetran connectors](https://fivetran.com/connectors)

### Connector Selection Guide

| Data Source | Recommended Connector | Notes |
|-------------|----------------------|-------|
| Odoo PostgreSQL | S3 export / Custom | Export to S3 or use Structured Streaming |
| Salesforce CRM | Salesforce (native) | Fully managed, CDC support |
| Google Analytics | GA Raw Data (native) | Automated schema handling |
| HR Data | Workday Reports (native) | Scheduled sync |
| ITSM Data | ServiceNow (native) | Incident/change feeds |
| Dev Metrics | Jira + GitHub (Fivetran) | Issue + PR correlation |
| Documentation | Confluence (native) | Knowledge base sync |

## Integration with InsightPulseAI Stack

### Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│              Lakeflow Connect (Fully-Managed Connectors)         │
├─────────────────────────────────────────────────────────────────┤
│  ┌────────┐ ┌──────────┐ ┌─────────┐ ┌─────────┐ ┌───────────┐ │
│  │   S3   │ │Salesforce│ │ GA Raw  │ │ Workday │ │ServiceNow │ │
│  └────┬───┘ └────┬─────┘ └────┬────┘ └────┬────┘ └─────┬─────┘ │
│       │          │            │           │            │        │
│       └──────────┴─────┬──────┴───────────┴────────────┘        │
│                        ▼                                         │
├─────────────────────────────────────────────────────────────────┤
│         Lakeflow Spark Declarative Pipelines (ETL)               │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐            │
│  │   Bronze    │──▶│   Silver    │──▶│    Gold     │            │
│  │ (Raw Data)  │   │ (Cleaned)   │   │ (Curated)   │            │
│  └─────────────┘   └─────────────┘   └─────────────┘            │
│                        │                                         │
│                        ▼                                         │
├─────────────────────────────────────────────────────────────────┤
│              Data Science Agent (Analysis Layer)                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Notebook + SQL Editor                                    │  │
│  │  • Auto-generate analysis code                            │  │
│  │  • Execute & iterate                                      │  │
│  │  • Interpret results                                      │  │
│  └───────────────────────────────────────────────────────────┘  │
│                        │                                         │
│              ┌─────────┴─────────┐                              │
│              ▼                   ▼                              │
│       SQL Dashboards      Curated Marts                         │
│              │                   │                              │
│              ▼                   ▼                              │
│        Superset BI         Supabase/Odoo                        │
└─────────────────────────────────────────────────────────────────┘
```

### Use Cases for InsightPulseAI

#### 1. Odoo ERP Analytics

```
# Prompt for Agent Mode
"Analyze @odoo_sales_orders to identify:
1. Top 10 customers by revenue (last 90 days)
2. Product category trends
3. Seasonal patterns in order volume
Create visualizations and export summary to a Delta table."
```

#### 2. Finance/PPM Reporting

```
# Prompt for Agent Mode
"Using @finance_ppm_monthly, build a forecast of monthly expenses
for the next 6 months. Compare actuals vs budget and highlight
variances > 10%. Create an executive summary."
```

#### 3. BIR Tax Compliance

```
# Prompt for Agent Mode
"Analyze @bir_tax_filings to validate:
1. All required forms are submitted on time
2. Amounts reconcile with @odoo_accounting
3. Flag any discrepancies for review
Export findings to @compliance_audit_log."
```

#### 4. Infrastructure Monitoring

```
# Prompt for Agent Mode
"Query @infra_metrics to identify:
1. Services with >95th percentile latency
2. Error rate trends (last 7 days)
3. Capacity planning recommendations
Create alerts threshold suggestions."
```

#### 5. GitHub/Jira Integration Analysis

```
# Prompt for Agent Mode
"Correlate @jira_issues with @github_prs to measure:
1. Average time from issue creation to PR merge
2. PRs without linked issues
3. Stale issues (no activity >30 days)
Build a developer productivity dashboard."
```

## Prompt Templates

### Exploratory Data Analysis

```
Describe the @{table_name} dataset. Perform EDA including:
1. Column statistics (null counts, cardinality, distributions)
2. Correlation analysis for numeric columns
3. Visualize distributions and outliers
4. Identify data quality issues
Think like a data scientist.
```

### Forecasting

```
Using @{table_name}, build a forecast of {metric} for the next {period}.
Include:
1. Trend decomposition
2. Seasonality detection
3. Confidence intervals
4. Interactive visualization
Export predictions to @{output_table}.
```

### Machine Learning

```
Train a {model_type} model on @{table_name} to predict {target}.
Steps:
1. Feature engineering (handle nulls, encode categoricals)
2. Train/test split (80/20)
3. Hyperparameter tuning
4. Evaluate with {metrics}
5. Log model to MLflow
6. Generate feature importance report
```

### Data Quality

```
Audit @{table_name} for data quality:
1. Check for duplicate records
2. Validate referential integrity with @{related_table}
3. Identify schema drift from expected types
4. Flag records failing business rules
Create a quality scorecard.
```

## Best Practices

### Context References

Always use `@table_name` syntax to provide context:

```
# Good
"Analyze @sales_transactions to find top products"

# Better (more context)
"Analyze @sales_transactions joined with @product_catalog
to find top products by category for Q4 2025"
```

### Iterative Refinement

1. Start with broad analysis
2. Review agent's plan before execution
3. Refine with follow-up prompts
4. Export final results to Delta tables

### Safety Guardrails

- Agent respects Unity Catalog permissions
- Always review generated code before "Allow"
- Use "Allow in this thread" for trusted operations
- Click "Stop" if agent takes unexpected actions

## Integration with MCP Jobs

Route agent-generated insights to MCP Jobs for downstream processing:

```python
# In notebook cell after agent analysis
import requests

# Push analysis results to MCP Jobs queue
result = spark.sql("SELECT * FROM agent_analysis_output")
payload = result.toPandas().to_dict(orient='records')

requests.post(
    "https://v0-open-in-v0-aw4uzb0sw-tbwa.vercel.app/api/jobs/enqueue",
    json={
        "source": "databricks",
        "jobType": "analytics_sync",
        "payload": {"table": "agent_analysis_output", "row_count": len(payload)}
    }
)
```

## Automation via Databricks Jobs

Schedule agent-assisted notebooks as Databricks Jobs:

```yaml
# job_config.yml
name: weekly_analytics_report
tasks:
  - task_key: eda_analysis
    notebook_task:
      notebook_path: /Shared/analytics/weekly_eda
    cluster_id: ${CLUSTER_ID}

schedule:
  quartz_cron_expression: "0 0 8 ? * MON"
  timezone_id: "America/New_York"
```

## Metrics to Track

| Metric | Source | Target |
|--------|--------|--------|
| Agent prompts/week | Workspace logs | Growing adoption |
| Code execution success rate | Notebook runs | >90% |
| Time saved per analysis | Manual comparison | >50% reduction |
| Tables analyzed | Unity Catalog | Comprehensive coverage |

## Platform Context

The Data Science Agent operates within the broader Databricks Data Science Platform:

| Platform Feature | Agent Integration |
|-----------------|-------------------|
| Collaborative Notebooks | Agent generates code in shared notebooks |
| Unity Catalog | Agent respects catalog permissions and references tables via `@table` |
| Delta Lake | Agent reads/writes Delta tables with ACID guarantees |
| MLflow | Agent can log models and experiments automatically |
| Dashboards | Agent-generated insights can be exported to dashboards |

For complete platform capabilities including IDE integrations, visual tools, and collaboration features, see [Data Science Platform](./DATA_SCIENCE_PLATFORM.md).

## Related Documentation

- [Data Science Platform](./DATA_SCIENCE_PLATFORM.md) - Full platform capabilities
- [Databricks Data Science Agent](https://docs.databricks.com/notebooks/use-data-science-agent.html)
- [Unity Catalog Permissions](https://docs.databricks.com/data-governance/unity-catalog/index.html)
- [MLflow Integration](https://docs.databricks.com/mlflow/index.html)
