# Azure Databricks Integration - Product Requirements Document

---

**Status**: PROPOSED
**Owner**: Jake Tolentino
**Created**: 2026-01-26
**Target**: Q1 2026

---

## Overview

Integrate Azure Databricks capabilities into odoo-ce stack to enable:
- Advanced ETL pipelines (replacing manual Scout data processing)
- AI/ML-powered financial analytics
- Real-time feature engineering for BIR compliance
- Unified data lakehouse architecture

---

## Strategic Context

### Current State (odoo-ce)

**Data Processing**:
- Manual ETL: Google Drive exports → Supabase Bronze → Silver → Gold
- Limited ML capabilities: OpenAI API calls only
- BIR compliance: Rule-based validation (no predictive analytics)
- Scout transaction analysis: SQL queries in Apache Superset

**Pain Points**:
1. **Scalability**: Supabase PostgreSQL hits limits at >10M transactions
2. **Processing Speed**: ETL jobs take 2-4 hours for monthly close
3. **ML Constraints**: No native feature engineering or model training
4. **Data Quality**: Manual column mapping with 15-20% error rate

### Desired State (with Databricks)

**Data Lakehouse Architecture**:
```
Source Systems (Google Drive, Odoo, n8n)
    ↓
Azure Databricks (Delta Lake)
    ├── Bronze (Raw ingestion)
    ├── Silver (Cleaned, validated)
    ├── Gold (Business logic, aggregates)
    └── Platinum (ML features, predictions)
        ↓
    ╔═══════════════════════════════════╗
    ║  Databricks SQL Warehouse         ║
    ║  - Apache Superset dashboards     ║
    ║  - Tableau integration            ║
    ║  - Direct Odoo queries            ║
    ╚═══════════════════════════════════╝
```

**Benefits**:
1. **10x Scalability**: Handle 100M+ transactions with Delta Lake
2. **5x Speed**: Spark-based ETL completes in 20-30 minutes
3. **ML Native**: Feature store + model registry for BIR predictions
4. **Auto Quality**: ML-based column mapping with 95%+ accuracy

---

## Target Features (Azure Databricks Capabilities)

### Phase 1: Data Engineering (Q1 2026)

**Feature 1.1: Lakeflow Spark Declarative Pipelines (DLT)**
- **Purpose**: Replace manual ETL with declarative pipelines
- **Input**: Google Drive exports (JSON/ZIP), Odoo API, n8n webhooks
- **Output**: Delta Lake tables (Bronze → Silver → Gold)
- **Success Criteria**: ETL runtime <30 minutes, data quality >98%

**Feature 1.2: Databricks Connect**
- **Purpose**: Connect n8n workflows to Databricks compute
- **Integration**: n8n HTTP nodes → Databricks REST API → Spark jobs
- **Success Criteria**: n8n can trigger ETL jobs, query results

**Feature 1.3: Delta Lake Storage**
- **Purpose**: ACID transactions, time travel, schema evolution
- **Migration**: Supabase Bronze/Silver → Delta Lake (parallel run for 1 month)
- **Success Criteria**: Zero data loss, 100% parity with Supabase

### Phase 2: AI/ML Analytics (Q2 2026)

**Feature 2.1: Feature Engineering**
- **Purpose**: Automated feature extraction for BIR compliance
- **Features**: Transaction velocity, category patterns, anomaly scores
- **Success Criteria**: Feature store with 50+ features, <5ms latency

**Feature 2.2: ML Runtimes**
- **Models**: BIR form field prediction, expense category classification
- **Training**: AutoML on historical data (2022-2025)
- **Success Criteria**: 95%+ accuracy, deployed to production

**Feature 2.3: AI/BI Dashboards**
- **Purpose**: Genie conversational analytics for Finance SSC
- **Interface**: Natural language queries in Apache Superset
- **Success Criteria**: Finance team can ask questions in plain English

### Phase 3: Infrastructure Integration (Q3 2026)

**Feature 3.1: Databricks Asset Bundles**
- **Purpose**: IaC for pipeline management (like Terraform for Databricks)
- **Repository**: `odoo-ce/infra/databricks/` with YAML configs
- **Success Criteria**: CI/CD deploys Databricks jobs automatically

**Feature 3.2: SQL Connectors**
- **Purpose**: Direct Odoo → Databricks queries
- **Integration**: Odoo external database connector + Databricks SQL
- **Success Criteria**: Odoo can read Delta Lake tables as views

**Feature 3.3: Serverless Compute**
- **Purpose**: Auto-scaling for month-end close spikes
- **Cost Optimization**: Pay-per-use instead of always-on clusters
- **Success Criteria**: 40% cost reduction vs. dedicated clusters

---

## Technical Architecture

### Component Integration

**Existing Stack (odoo-ce)**:
```
DigitalOcean App Platform (services)
    ↓
Supabase PostgreSQL (transactional)
    ↓
Apache Superset (BI dashboards)
    ↓
Vercel (frontend)
```

**With Databricks** (new):
```
DigitalOcean App Platform (services)
    ↓
Azure Databricks (analytical workloads)
    ├── Delta Lake (data lakehouse)
    ├── Spark (ETL processing)
    ├── MLflow (model registry)
    └── SQL Warehouse (BI queries)
        ↓
    Supabase PostgreSQL (transactional only)
        ↓
    Apache Superset (dashboards from Databricks + Supabase)
        ↓
    Vercel (frontend)
```

### Data Flow

**ETL Pipeline** (Databricks replaces manual process):
```python
# Current (manual): 2-4 hours
# 1. Download from Google Drive
# 2. Parse JSON/Excel
# 3. Fuzzy column matching
# 4. Insert to Supabase Bronze
# 5. Transform to Silver/Gold (SQL)

# With Databricks: 20-30 minutes
# 1. Auto-ingest from Google Drive (Databricks Connect)
# 2. Parse with Spark (parallel processing)
# 3. ML column matching (95%+ accuracy)
# 4. Write to Delta Lake Bronze (ACID)
# 5. DLT pipeline Bronze → Silver → Gold (declarative)
# 6. Sync Gold → Supabase (for Odoo transactions)
```

**ML Prediction Pipeline** (new capability):
```python
# BIR form auto-fill
# 1. User uploads expense receipt (Odoo)
# 2. OCR extraction (existing PaddleOCR-VL)
# 3. Feature engineering (Databricks)
#    - vendor_category, amount_pattern, tax_code
# 4. Model prediction (Databricks ML)
#    - predicted_bir_form, confidence_score
# 5. Auto-populate Odoo fields
# 6. User reviews + submits
```

---

## MCP Server Integration

**New MCP Server**: `mcp/servers/databricks-mcp-server/`

**Capabilities**:
1. **Cluster Management**: Start, stop, scale Databricks clusters
2. **Job Orchestration**: Trigger ETL jobs, monitor status
3. **SQL Queries**: Execute Databricks SQL, fetch results
4. **Model Serving**: Invoke MLflow models, get predictions
5. **Delta Lake Access**: Read/write Delta tables

**Configuration** (`.claude/mcp-servers.json`):
```json
{
  "databricks": {
    "command": "node",
    "args": ["mcp/servers/databricks-mcp-server/dist/index.js"],
    "env": {
      "DATABRICKS_HOST": "https://<workspace-id>.azuredatabricks.net",
      "DATABRICKS_TOKEN": "${DATABRICKS_ACCESS_TOKEN}",
      "DATABRICKS_CLUSTER_ID": "${DATABRICKS_CLUSTER_ID}"
    }
  }
}
```

**Agent Integration**:
- **bi_architect**: Query Databricks SQL for dashboards
- **finance_ssc_expert**: Trigger BIR ETL jobs
- **devops_engineer**: Manage Databricks infrastructure
- **analyzer**: Run ML predictions, analyze feature importance

---

## Acceptance Criteria

### Phase 1 (Data Engineering)

**ETL Pipeline**:
- ✅ DLT pipeline processes 1M transactions in <30 minutes
- ✅ Data quality checks pass (>98% accuracy)
- ✅ Delta Lake has time travel (can restore any snapshot)
- ✅ n8n workflows trigger Databricks jobs successfully

**Integration**:
- ✅ Apache Superset queries Databricks SQL Warehouse
- ✅ Odoo reads Delta Lake Gold tables as external views
- ✅ MCP server responds to Claude Code commands

### Phase 2 (AI/ML)

**Feature Store**:
- ✅ 50+ financial features available (transaction velocity, category patterns, etc.)
- ✅ Feature freshness <5 minutes (real-time updates)
- ✅ Feature lineage tracked (know how features are computed)

**ML Models**:
- ✅ BIR form prediction accuracy >95%
- ✅ Expense category classification >90%
- ✅ Models deployed to production with A/B testing
- ✅ Model performance monitored in MLflow

### Phase 3 (Infrastructure)

**IaC**:
- ✅ Databricks Asset Bundles deploy pipelines via CI/CD
- ✅ All infrastructure changes tracked in Git
- ✅ Rollback capability (restore previous bundle version)

**Cost Optimization**:
- ✅ Serverless compute reduces costs by 40%
- ✅ Auto-scaling works during month-end close spikes
- ✅ Cost alerts trigger if budget exceeded

---

## Non-Goals (Out of Scope)

**Not Included**:
- ❌ Real-time streaming (use Supabase Edge Functions instead)
- ❌ Graph analytics (not needed for financial data)
- ❌ Geospatial queries (no location-based use cases)
- ❌ Databricks Unity Catalog (use Supabase metadata instead)

---

## Dependencies

**External Services**:
- Azure subscription with Databricks workspace
- Databricks Access Token (personal or service principal)
- Azure Storage (for Delta Lake files)
- Network connectivity: DigitalOcean → Azure (private link?)

**Internal Changes**:
- Update `CLAUDE.md` to allow Azure services
- Create `infra/databricks/` directory with Terraform/Asset Bundles
- Add Databricks credentials to secret management
- Update CI/CD pipelines for Databricks deployments

---

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Azure costs exceed budget | High | Medium | Use serverless compute, set cost alerts, monitor daily |
| Data migration data loss | Critical | Low | Parallel run Supabase + Databricks for 1 month, validate parity |
| ML model accuracy below 95% | Medium | Medium | Start with simple models, iterate, keep human-in-the-loop validation |
| Databricks outage breaks ETL | High | Low | Maintain Supabase as fallback, cache Gold data locally |
| Team lacks Databricks expertise | Medium | High | Training program, hire consultant for initial setup |

---

## Timeline

**Q1 2026 (Phase 1)**:
- Week 1-2: Azure subscription, Databricks workspace setup
- Week 3-4: MCP server development
- Week 5-8: DLT pipeline implementation
- Week 9-12: Parallel run Supabase + Databricks, validate parity

**Q2 2026 (Phase 2)**:
- Week 1-4: Feature engineering setup
- Week 5-8: ML model training (BIR, expense classification)
- Week 9-12: Production deployment, A/B testing

**Q3 2026 (Phase 3)**:
- Week 1-4: Databricks Asset Bundles IaC
- Week 5-8: SQL connectors for Odoo
- Week 9-12: Serverless compute migration

---

## Success Metrics

**Operational**:
- ETL runtime: 2-4 hours → <30 minutes (5x improvement)
- Data quality: 80-85% → >98% (15% improvement)
- Processing capacity: 10M → 100M transactions (10x scalability)

**Cost**:
- Infrastructure costs: +$500/month (Azure Databricks)
- Labor savings: -40 hours/month (automated ETL)
- ROI: Break-even at 6 months

**Quality**:
- BIR form accuracy: 85% → 95% (ML-powered)
- Manual intervention: 15% → 5% (3x reduction)
- Audit compliance: 100% (no change, but faster)

---

## Related Documentation

- **Architecture**: `docs/architecture/DATABRICKS_INTEGRATION.md` (to be created)
- **MCP Server**: `mcp/servers/databricks-mcp-server/README.md` (to be created)
- **IaC**: `infra/databricks/README.md` (to be created)
- **Runbooks**: `docs/runbooks/DATABRICKS_OPERATIONS.md` (to be created)

---

**Next Steps**:
1. ✅ Create this PRD
2. ⏳ Update `CLAUDE.md` to allow Azure services (requires approval)
3. ⏳ Create spec bundle: `constitution.md`, `plan.md`, `tasks.md`
4. ⏳ Estimate costs: Azure Databricks pricing calculator
5. ⏳ Prototype MCP server: Validate Databricks API connectivity

---

**Status**: PROPOSED - Awaiting stakeholder review and budget approval

**Approvers**:
- Jake Tolentino (Technical Owner)
- Finance Director (Budget Approval)
- DevOps Lead (Infrastructure Approval)
