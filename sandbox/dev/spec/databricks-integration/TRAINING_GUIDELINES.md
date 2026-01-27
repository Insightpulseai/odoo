# Azure Databricks Training Guidelines for Odoo-CE Team

## Purpose

This document outlines the training strategy for onboarding the odoo-ce development team to Azure Databricks, following enterprise SaaS ERP patterns and aligning with the 16-week implementation roadmap.

---

## Learning Paths by Role

### 1. **Data Engineers** (Primary: ETL Pipeline Development)

**Prerequisites**: Python, SQL, basic cloud concepts

**Phase 1 - Foundations (Weeks 1-2)**:
- [ ] **Unity Catalog Basics** (4 hours)
  - Catalogs, schemas, tables hierarchy
  - Managed vs external tables
  - Data lineage and governance
  - Hands-on: Create bronze/silver/gold catalogs

- [ ] **Delta Lake Deep Dive** (4 hours)
  - ACID transactions, time travel, optimize/vacuum
  - Merge operations for incremental updates
  - Change Data Feed (CDF) for CDC patterns
  - Hands-on: Convert Scout export Parquet → Delta tables

- [ ] **Auto Loader** (2 hours)
  - Incremental file ingestion patterns
  - Schema evolution and inference
  - Checkpointing and exactly-once semantics
  - Hands-on: Ingest Google Drive exports

**Phase 2 - Advanced (Weeks 3-4)**:
- [ ] **Lakeflow DLT** (8 hours)
  - Declarative pipeline syntax (`@dlt.table`, `@dlt.view`)
  - Data quality expectations (`@dlt.expect_or_drop`)
  - Pipeline dependencies and DAGs
  - Development vs production modes
  - Hands-on: Build BIR compliance pipeline

- [ ] **Python SDK for Workspace Management** (4 hours)
  - CRUD operations for jobs, notebooks, repos
  - Authentication with service principals
  - Asset Bundles for IaC
  - Hands-on: Automate pipeline deployment

**Certification Target**: Databricks Data Engineer Associate (optional, recommended)

---

### 2. **ML Engineers / Data Scientists** (Primary: Feature Engineering & Predictive Models)

**Prerequisites**: Python, pandas, scikit-learn, basic statistics

**Phase 1 - Foundations (Weeks 1-2)**:
- [ ] **MLflow Tracking** (4 hours)
  - Experiments, runs, parameters, metrics
  - Artifact logging (models, plots, data samples)
  - Autologging for scikit-learn/XGBoost
  - Hands-on: Log BIR forecasting experiment

- [ ] **Feature Engineering API** (4 hours)
  - Feature tables (online + offline)
  - Time-series features with point-in-time correctness
  - Feature lineage and versioning
  - Hands-on: Create 50+ financial ratio features

**Phase 2 - Advanced (Weeks 3-4)**:
- [ ] **Model Registry** (4 hours)
  - Model versioning and stage transitions
  - Model webhooks for CI/CD integration
  - Model aliases and serving endpoints
  - Hands-on: Register and promote BIR tax model

- [ ] **Model Serving** (4 hours)
  - REST API endpoints for real-time inference
  - Batch inference with Spark UDFs
  - A/B testing and canary deployments
  - Hands-on: Serve model via n8n webhook

**Certification Target**: Databricks Machine Learning Associate (optional, recommended)

---

### 3. **Backend Developers** (Primary: Odoo-Databricks Integration)

**Prerequisites**: Python, REST APIs, Docker, CI/CD basics

**Phase 1 - Foundations (Weeks 1-2)**:
- [ ] **REST API 2.1 Essentials** (4 hours)
  - Authentication (PAT, AAD service principals)
  - Workspace, Clusters, Jobs, DBFS endpoints
  - SQL Query API for Delta Lake queries
  - Hands-on: Query gold.finance.bir_monthly_summary

- [ ] **Databricks Connect** (3 hours)
  - Local IDE development with remote execution
  - Debugging Spark jobs from VS Code
  - Integration with pytest for unit tests
  - Hands-on: Run Scout ETL job from local machine

**Phase 2 - Integration (Weeks 3-4)**:
- [ ] **n8n Workflow Integration** (4 hours)
  - HTTP Request nodes for Databricks APIs
  - Webhook triggers from Odoo events
  - Error handling and retry logic
  - Hands-on: Build "Expense Approved → Trigger ETL" workflow

- [ ] **MCP Server Development** (6 hours)
  - TypeScript MCP server architecture
  - Tool definitions for Claude Code integration
  - Rate limiting and error handling
  - Hands-on: Implement `databricks_execute_sql` tool

**Certification Target**: None (internal competency assessment via code review)

---

### 4. **DevOps Engineers** (Primary: CI/CD, Infrastructure, Cost Optimization)

**Prerequisites**: GitHub Actions, Docker, IaC tools (Terraform optional)

**Phase 1 - Foundations (Weeks 1-2)**:
- [ ] **Databricks Asset Bundles** (6 hours)
  - `databricks.yml` structure
  - Jobs, pipelines, notebooks as code
  - Multi-environment deployments (dev/staging/prod)
  - Hands-on: Bundle BIR pipeline for prod deployment

- [ ] **CLI and CI/CD** (4 hours)
  - `databricks bundle validate/deploy`
  - GitHub Actions workflow integration
  - Secrets management with GitHub Secrets
  - Hands-on: Automated bundle deployment via PR merge

**Phase 2 - Operations (Weeks 3-4)**:
- [ ] **Cluster Policies and Cost Optimization** (4 hours)
  - Serverless compute vs classic clusters
  - Spot instance configurations
  - Autoscaling policies
  - Monitoring compute costs
  - Hands-on: Implement spot instance policy

- [ ] **RBAC and Governance** (4 hours)
  - Service principals for app authentication
  - User groups and workspace permissions
  - Unity Catalog GRANT statements
  - Audit logs and compliance
  - Hands-on: Configure least-privilege access

**Certification Target**: Databricks Platform Administrator (optional, recommended)

---

### 5. **Finance SSC Team** (Primary: Dashboards, Ad-hoc Analysis)

**Prerequisites**: SQL, basic business analytics concepts

**Phase 1 - Foundations (Weeks 1-2)**:
- [ ] **Databricks SQL Essentials** (3 hours)
  - Query Editor and SQL Warehouse
  - Querying Delta Lake tables
  - Joins, aggregations, window functions
  - Hands-on: Query BIR compliance metrics

- [ ] **Dashboards and Visualizations** (3 hours)
  - Lakeview dashboards (successor to Databricks SQL Dashboards)
  - Chart types and best practices
  - Parameterized queries and filters
  - Hands-on: Build Finance PPM dashboard

**Phase 2 - Advanced (Weeks 3-4)**:
- [ ] **Genie (AI/BI Assistant)** (2 hours)
  - Natural language queries
  - Suggested insights and anomaly detection
  - Custom instructions for domain context
  - Hands-on: Ask "Which agencies are over budget this quarter?"

- [ ] **Data Export and Reporting** (2 hours)
  - Scheduled dashboard refreshes
  - Email alerts on threshold breaches
  - CSV/Excel export for offline analysis
  - Hands-on: Schedule weekly BIR filing status report

**Certification Target**: None (self-service analytics focus)

---

## Recommended Training Resources

### Microsoft Learn (Free)
- **Data Engineering with Databricks**: https://learn.microsoft.com/en-us/azure/databricks/getting-started/data-engineering
- **Machine Learning with Databricks**: https://learn.microsoft.com/en-us/azure/databricks/machine-learning/
- **Unity Catalog**: https://learn.microsoft.com/en-us/azure/databricks/data-governance/unity-catalog/

### Databricks Academy (Free + Paid)
- **Free On-Demand Courses**:
  - Lakehouse Fundamentals (2 hours)
  - Apache Spark Programming with Databricks (8 hours)
  - Delta Lake Deep Dive (4 hours)

- **Paid Instructor-Led Training** (optional, ~$1,500 per course):
  - Databricks Data Engineer Learning Plan (3 days)
  - Databricks Machine Learning Learning Plan (2 days)

### Hands-On Labs (Databricks Community Edition)
- Free tier: https://community.cloud.databricks.com/
- Limited compute (15GB cluster RAM)
- Sufficient for learning DLT, MLflow, Unity Catalog basics
- Use odoo-ce Azure subscription for production-scale labs

---

## Training Timeline (Aligned with 16-Week Implementation)

### Weeks 1-4 (Phase 1: Foundation)
**Who**: Data Engineers, DevOps Engineers
**Focus**: Unity Catalog setup, Auto Loader, Asset Bundles
**Training Hours**: 20 hours/person (4 hours/week)
**Format**: Self-paced Microsoft Learn + weekly team sync

### Weeks 5-8 (Phase 2: ETL Pipelines)
**Who**: Data Engineers, Backend Developers
**Focus**: Lakeflow DLT, Python SDK, n8n integration
**Training Hours**: 16 hours/person (4 hours/week)
**Format**: Pair programming on real BIR pipeline

### Weeks 9-12 (Phase 3: ML/AI)
**Who**: ML Engineers, Finance SSC Team
**Focus**: MLflow, Feature Store, Genie dashboards
**Training Hours**: 16 hours/person (4 hours/week)
**Format**: Real-world model development + dashboard workshops

### Weeks 13-16 (Phase 4: Production)
**Who**: DevOps Engineers, Backend Developers
**Focus**: CI/CD, RBAC, cost optimization, monitoring
**Training Hours**: 12 hours/person (3 hours/week)
**Format**: Production deployment rehearsal + incident response drills

---

## Assessment and Competency Gates

### Data Engineer Competency (Required to ship production pipelines)
- [ ] Can write DLT pipeline with data quality expectations
- [ ] Can debug failed pipeline runs via Event Logs
- [ ] Can optimize Delta table with Z-ordering and file compaction
- [ ] Can configure Auto Loader for new data source
- [ ] **Acceptance**: Code review approval from Tech Lead

### ML Engineer Competency (Required to ship production models)
- [ ] Can log experiments with MLflow Tracking
- [ ] Can create feature table with point-in-time correctness
- [ ] Can register and promote model to Production stage
- [ ] Can deploy model to serving endpoint
- [ ] **Acceptance**: Model accuracy ≥95% on hold-out test set

### Backend Developer Competency (Required to ship Odoo integration)
- [ ] Can query Delta Lake via REST API
- [ ] Can trigger Databricks job from n8n workflow
- [ ] Can implement MCP tool with error handling
- [ ] Can write unit tests for Databricks connector
- [ ] **Acceptance**: Integration test passing in CI/CD

### DevOps Competency (Required to manage production infra)
- [ ] Can deploy Asset Bundle to prod environment
- [ ] Can configure service principal with least-privilege access
- [ ] Can monitor compute costs and optimize cluster policies
- [ ] Can respond to pipeline failure alerts
- [ ] **Acceptance**: Successful zero-downtime deployment to prod

### Finance SSC Competency (Required for self-service analytics)
- [ ] Can write SQL query for BIR compliance metrics
- [ ] Can create Lakeview dashboard with filters
- [ ] Can use Genie to ask natural language questions
- [ ] Can schedule and export dashboard for offline review
- [ ] **Acceptance**: Dashboard used in weekly Finance PPM meeting

---

## Knowledge Sharing and Documentation

### Internal Wiki (Notion / Odoo Wiki)
- [ ] **Databricks 101**: Getting Started Guide
- [ ] **Common Queries**: SQL snippets for BIR, Scout, Finance marts
- [ ] **Troubleshooting**: Known issues and resolutions
- [ ] **Runbook**: Incident response for pipeline failures

### Code Review Guidelines
- [ ] DLT pipelines must include data quality expectations
- [ ] MLflow experiments must log hyperparameters and metrics
- [ ] Asset Bundles must pass `databricks bundle validate`
- [ ] MCP tools must implement rate limiting and retries

### Weekly Team Sync (30 minutes)
- Demo recent Databricks feature implementations
- Share learnings from Microsoft Learn courses
- Review production incidents and post-mortems
- Plan next sprint priorities

---

## Budget Allocation

### Training Costs (16 Weeks)
| Item | Cost | Justification |
|------|------|---------------|
| **Microsoft Learn** | Free | Primary learning resource |
| **Databricks Community Edition** | Free | Hands-on lab environment |
| **Databricks Academy (optional)** | $3,000 (2 courses for Tech Lead) | Accelerate ramp-up |
| **Certification Exams (optional)** | $400 (2 exams) | Data Engineer + ML Associate |
| **Team Training Time** | 64 hours/person × 6 people = 384 hours | Billable time for learning |
| **Total Direct Costs** | $3,400 | **ROI**: $70K/year savings = 5 weeks payback |

---

## Success Metrics

### Week 4 (Foundation Complete)
- ✅ Unity Catalog catalogs created (bronze/silver/gold/platinum)
- ✅ Auto Loader ingesting Scout exports
- ✅ 100% of team completed "Lakehouse Fundamentals" course

### Week 8 (ETL Pipelines in Production)
- ✅ BIR compliance pipeline running in prod
- ✅ Data quality expectations passing (99%+ success rate)
- ✅ n8n workflows triggering Databricks jobs

### Week 12 (ML Models in Production)
- ✅ BIR tax forecaster model deployed to serving endpoint
- ✅ Odoo computed field calling MLflow API
- ✅ Genie dashboard live for Finance SSC team

### Week 16 (Production-Ready Operations)
- ✅ CI/CD pipeline deploying to prod via GitHub Actions
- ✅ RBAC policies enforced (service principals configured)
- ✅ Compute costs <$500/month (spot instances, serverless)
- ✅ 100% of team passed competency assessments

---

## Continuous Learning (Post-Implementation)

### Quarterly Deep Dives (4 hours)
- Advanced Unity Catalog features (row filters, column masks)
- Delta Sharing for external partner data exchange
- Lakehouse Monitoring for drift detection
- Vector Search for RAG applications (future: LLM integration)

### Annual Recertification (optional)
- Databricks certifications valid for 2 years
- Recommend recertification to stay current with platform updates

### Conference Attendance (optional, $2,000/person)
- **Data + AI Summit** (annual, June)
- Networking with enterprise SaaS ERP peers
- Hands-on labs with Databricks engineers

---

## Appendix: Quick Reference Cards

### A. Common DLT Patterns
```python
# Pattern 1: Bronze → Silver with data quality
@dlt.table(name="silver_transactions")
@dlt.expect_or_drop("valid_amount", "amount > 0")
def silver_transactions():
    return dlt.read("bronze.scout.raw_exports").select(...)

# Pattern 2: Silver → Gold with aggregation
@dlt.table(name="gold_bir_monthly")
def gold_bir_monthly():
    return dlt.read("silver.finance.transactions").groupBy(...)
```

### B. Common MLflow Patterns
```python
# Pattern 1: Log experiment
with mlflow.start_run():
    mlflow.log_params({"alpha": 0.5, "l1_ratio": 0.1})
    mlflow.log_metrics({"rmse": 0.15, "r2": 0.93})
    mlflow.sklearn.log_model(model, "model")

# Pattern 2: Load production model
model_uri = "models:/bir_tax_forecaster/Production"
model = mlflow.pyfunc.load_model(model_uri)
```

### C. Common n8n Integration Patterns
```javascript
// Pattern 1: Trigger Databricks job
{
  "method": "POST",
  "url": "https://<workspace>.azuredatabricks.net/api/2.1/jobs/run-now",
  "headers": { "Authorization": "Bearer {{ $env.DATABRICKS_TOKEN }}" },
  "body": { "job_id": 123, "notebook_params": { "date": "{{ $now }}" } }
}

// Pattern 2: Query Delta Lake
{
  "method": "POST",
  "url": "https://<workspace>.azuredatabricks.net/api/2.0/sql/statements",
  "body": {
    "warehouse_id": "abc123def456",
    "statement": "SELECT * FROM gold.finance.bir_monthly WHERE year = 2026"
  }
}
```

---

**Document Version**: 1.0.0
**Last Updated**: 2026-01-26
**Owner**: Tech Lead (Jake Tolentino)
**Next Review**: Week 8 of implementation (mid-point checkpoint)
