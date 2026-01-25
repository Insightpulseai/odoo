# Databricks Data Science Platform

Collaborative data science at scale for the InsightPulseAI stack.

## Overview

The Databricks Data Science Platform provides a unified environment for end-to-end data science workflows - from data preparation to modeling to sharing insights. Built on an open lakehouse foundation, it offers:

- Quick access to clean and reliable data
- Preconfigured compute resources
- IDE integration and multi-language support
- Built-in advanced visualization tools
- Maximum flexibility for data analytics teams

## Capabilities

### Collaborative Notebooks

Write code in **Python**, **R**, **Scala**, and **SQL** in a single notebook environment:

| Language | Use Case | Example |
|----------|----------|---------|
| Python | ML/AI, data manipulation | pandas, sklearn, pytorch |
| R | Statistical analysis | tidyverse, ggplot2 |
| Scala | Big data processing | Spark native |
| SQL | Data queries, aggregations | Standard SQL + Delta extensions |

**Collaboration Features:**

- **Coauthoring**: Multiple users edit notebooks simultaneously
- **Commenting**: Inline comments for code review and discussion
- **Automatic versioning**: Every save creates a version checkpoint
- **Git integration**: Native support for Git repos
- **Role-based access controls**: Granular permissions (viewer, editor, admin)

### Scalable Compute

Move beyond laptop limitations with cloud-scale compute:

| Feature | Description |
|---------|-------------|
| Personal compute | Dedicated single-user clusters for exploration |
| Auto-managed clusters | Databricks handles provisioning and scaling |
| Shared clusters | Cost-effective for team workloads |
| Serverless SQL | Pay-per-query for ad-hoc analytics |

**Migration Path:**

```
Local Environment → Databricks
    │
    ├── Connect notebooks to personal compute
    ├── Access auto-managed clusters
    └── Scale to any data volume
```

### IDE Integrations

Use your preferred development environment with Databricks compute:

| IDE | Integration Type | Features |
|-----|-----------------|----------|
| **VS Code** | Extension | Remote execution, debugging, notebook sync |
| **PyCharm** | Databricks Connect | Run local code on remote clusters |
| **RStudio** | Hosted in Databricks | Full RStudio experience with lakehouse data |
| **JupyterLab** | Hosted in Databricks | Familiar Jupyter UI with Databricks compute |
| **IntelliJ** | Databricks Connect | Scala/Java development |

**Setup Example (VS Code):**

```bash
# Install Databricks extension
code --install-extension databricks.databricks

# Configure workspace
databricks configure --profile DEFAULT

# Connect and run notebooks remotely
```

### Data Preparation

Get data ready for analysis with Delta Lake and Unity Catalog:

**Data Readiness Features:**

| Feature | Benefit |
|---------|---------|
| Delta Lake | ACID transactions, time travel, schema enforcement |
| Unity Catalog | Centralized governance and discovery |
| Auto quality checks | Validate data meets expectations on ingestion |
| Data versioning | Roll back to any previous version for compliance |
| Schema evolution | Handle changing data structures gracefully |

**Medallion Architecture Integration:**

```
┌─────────────────────────────────────────────────────────────────┐
│                      Data Preparation Layer                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐           │
│  │   Bronze    │──▶│   Silver    │──▶│    Gold     │           │
│  │ (Raw Data)  │   │ (Cleaned)   │   │ (Curated)   │           │
│  └─────────────┘   └─────────────┘   └─────────────┘           │
│        │                  │                  │                   │
│   Quality Checks    Transformations    Business Logic            │
│   Schema Enforce    Deduplication      Aggregations              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Low-Code Visual Tools

Visual tools for data exploration directly within notebooks:

| Tool | Purpose |
|------|---------|
| **Data Profile** | Automatic column statistics, distributions, nulls |
| **Visual Query Builder** | Drag-and-drop query construction |
| **Chart Builder** | Interactive visualization creation |
| **Schema Browser** | Explore tables, columns, and relationships |

**Benefits:**

- Enable teams across expertise levels to work with data
- Generate code from visual operations (transparency)
- Reduce boilerplate code writing
- Focus on high-value analysis work

**Example Workflow:**

```
1. Load data visually (no code)
2. Apply transformations via UI
3. Generate visualization
4. Click "Show Code" to see Python/SQL
5. Export generated code for automation
```

### Insights & Dashboards

Share analysis results with dynamic dashboards:

| Feature | Description |
|---------|-------------|
| **AI Dashboards** | AI-generated from natural language prompts |
| **Classic Dashboards** | Drag-and-drop dashboard builder |
| **Embedded Queries** | Dashboards run live queries |
| **Export Formats** | HTML, IPython Notebook, PDF |
| **Role-based Sharing** | Control who sees what |

**Dashboard Types:**

```
┌─────────────────────────────────────────────────────────────────┐
│                        Dashboard Options                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────┐    ┌────────────────┐    ┌────────────────┐ │
│  │  AI Dashboard  │    │ Classic Dash   │    │ Notebook Share │ │
│  │                │    │                │    │                │ │
│  │  "Show me top  │    │  Drag & drop   │    │  Export cells  │ │
│  │   customers"   │    │  widgets       │    │  or full nb    │ │
│  └────────────────┘    └────────────────┘    └────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Integration with InsightPulseAI Stack

### Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                   InsightPulseAI Data Science                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Odoo ERP ──────┐                                               │
│                 │                                                │
│  Supabase ──────┼──▶ Delta Lake ──▶ Notebooks ──▶ Dashboards   │
│                 │        │               │              │        │
│  n8n Workflows ─┘        │               ▼              ▼        │
│                          │         Data Science    Superset BI   │
│                          │           Agent                       │
│                          │               │                       │
│                          ▼               ▼                       │
│                     Unity Catalog   MLflow Models                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Use Case Mapping

| InsightPulseAI Domain | Databricks Capability | Output |
|-----------------------|----------------------|--------|
| Odoo ERP Analytics | Notebooks + SQL | Revenue dashboards |
| Finance/PPM | Data Science Agent | Forecasting models |
| BIR Tax Compliance | Quality checks + DLT | Compliance reports |
| Infrastructure | Streaming + notebooks | Health dashboards |
| Marketing Agency | Visual tools + ML | Campaign analytics |

## Best Practices

### Notebook Organization

```
/Workspace/
├── Shared/
│   ├── Libraries/          # Reusable code modules
│   ├── Templates/          # Notebook templates
│   └── Data Quality/       # Quality check notebooks
├── Projects/
│   ├── finance_ppm/        # Project-specific notebooks
│   ├── marketing_analytics/
│   └── compliance_reports/
└── Scratch/                # Exploratory work
```

### Collaboration Guidelines

| Practice | Description |
|----------|-------------|
| Use branches | Create feature branches for significant changes |
| Comment code | Document complex logic inline |
| Version control | Commit notebooks to Git regularly |
| Review PRs | Use notebook diffs for code review |
| Share read-only | Share results without edit permissions |

### Performance Optimization

```python
# Use Delta caching for repeated queries
spark.conf.set("spark.databricks.io.cache.enabled", "true")

# Partition data appropriately
df.write.partitionBy("date").format("delta").save(path)

# Use Z-ordering for query optimization
spark.sql("OPTIMIZE table_name ZORDER BY (column_name)")
```

## Migration Guide

### From Local Jupyter

```bash
# 1. Export local notebooks
jupyter nbconvert --to script *.ipynb

# 2. Upload to Databricks Repos
git add . && git commit -m "migrate notebooks"
git push origin main

# 3. Import in Databricks
# Repos > Add Repo > paste Git URL

# 4. Update imports for Databricks
# Replace local paths with Unity Catalog references
```

### From Hadoop/Spark

| Hadoop Component | Databricks Equivalent |
|-----------------|----------------------|
| HDFS | Delta Lake on cloud storage |
| Hive Metastore | Unity Catalog |
| YARN | Databricks clusters |
| Oozie | Databricks Jobs |
| Jupyter on cluster | Databricks Notebooks |

## Related Documentation

- [Data Science Agent Guide](./DATA_SCIENCE_AGENT.md) - AI-powered notebook assistant
- [Unity Catalog OSS](./UNITY_CATALOG_OSS.md) - Open-source governance
- [Training Guidelines](../infra/DATABRICKS_TRAINING_GUIDELINES.md) - Agent development
- [DAB Workbench](../../infra/databricks/README.md) - Infrastructure setup

## References

- [Databricks Data Science](https://www.databricks.com/product/data-science)
- [Notebooks Documentation](https://docs.databricks.com/notebooks/index.html)
- [Unity Catalog](https://docs.databricks.com/data-governance/unity-catalog/index.html)
- [Delta Lake](https://docs.databricks.com/delta/index.html)

---

*Last updated: 2026-01-25*
