# Fabric Finance PPM — Target State

## Purpose

`Finance PPM` is the first **business-facing Fabric workspace** for modeled analytics, semantic serving, and reporting.

It is NOT a raw replica destination. It consumes **curated business data** from the governed medallion pipeline.

---

## Workspace role

| Function | Description |
|----------|-------------|
| Finance/project reporting | Portfolio health, budget vs actual, margin, utilization |
| Semantic model publishing | Single governed semantic model for all Finance PPM reports |
| Executive dashboards | Power BI reports over gold data |
| Governed self-service | Analysts query gold via SQL analytics endpoint |

---

## Internal structure

```text
Finance PPM (Fabric workspace)
├── bronze
│   ├── raw_odoo_projects
│   ├── raw_odoo_tasks
│   ├── raw_odoo_timesheets
│   ├── raw_odoo_purchase_lines
│   ├── raw_odoo_invoice_lines
│   └── raw_odoo_budget_inputs
│
├── silver
│   ├── project_conformed
│   ├── task_conformed
│   ├── timesheet_conformed
│   ├── cost_actuals_conformed
│   ├── revenue_conformed
│   ├── vendor_spend_conformed
│   └── date / org / customer / owner dimensions
│
├── gold
│   ├── fact_project_finance
│   ├── fact_project_progress
│   ├── fact_budget_vs_actual
│   ├── fact_utilization
│   ├── dim_project
│   ├── dim_customer
│   ├── dim_period
│   ├── dim_owner
│   └── dim_cost_center
│
├── semantic
│   └── finance_ppm_semantic_model (published Power BI semantic model)
│
└── reports
    ├── exec_portfolio_dashboard
    ├── project_margin_dashboard
    └── budget_vs_actual_dashboard
```

---

## Layer definitions

### Bronze — raw landing

- Raw data from operational sources (Odoo PG, mirroring, federation)
- Retained for reconciliation, auditability, engineering
- NOT the reporting contract
- Schema matches source with minimal transformation (timestamp, source tag)

### Silver — conformed entities

- Cleansed, typed, joined business entities
- Conformed to standard naming and grain
- Deduplication and consolidation applied
- Business keys established
- Date/org/customer dimensions conformed

### Gold — business-ready marts

- Dimensional or aggregated models ready for consumption
- Fact and dimension tables with clear grain
- Business definitions owned here, not in dashboards
- This is the **reporting contract**

### Semantic — published model

- Power BI semantic model published over gold tables
- Single source of truth for all reports in this workspace
- Relationships, measures, hierarchies, display names defined here
- Connected via Direct Lake or Databricks SQL endpoint

### Reports — dashboards

- Built exclusively on the semantic model
- Never read directly from bronze, silver, or raw mirrored tables
- Cover specific business questions, not generic table explorers

---

## Hard rules

### 1. No reporting on raw mirrors

Mirrored or ingested operational tables are for retention, reconciliation, auditability, and engineering. They are NOT the reporting contract.

### 2. Gold is the contract

- Bronze = raw retention/auditability
- Silver = cleansed/joined data
- Gold = business-ready, dimensional or aggregated
- Reports consume gold through a semantic model

### 3. Semantic model sits above gold

Fabric reports read from a published semantic model, not directly from bronze/silver and not from raw ERP schemas.

### 4. Transactional truth stays separate

Odoo/Postgres remains the transactional SoR. Fabric is the modeled analytics/consumption plane. They serve different audiences and have different update frequencies.

### 5. One semantic model before report sprawl

Publish `finance_ppm_semantic_model` before creating multiple reports. All reports in this workspace must share the same semantic model.

---

## Source lanes

| Database | Role | Allowed for reporting? |
|----------|------|----------------------|
| `odoo_prod` | Production reporting source | Yes — only acceptable production lane |
| `odoo_staging` | Validation/test | No — staging only |
| `odoo` | Dev/sandbox | No — dev only |
| `postgres` | System database | Never |

---

## Data flow options

### Option A: Databricks-first (preferred)

```text
Odoo PG → Lakehouse Federation → Databricks Bronze → Silver → Gold
                                                            ↓
                                              Fabric (via shortcut or Direct Lake)
                                                            ↓
                                              Semantic Model → Power BI Reports
```

Gold tables already exist in `dbw_ipai_dev.gold.*` (26 tables verified). Fabric connects to Databricks SQL Warehouse for consumption.

### Option B: Fabric-native medallion

```text
Odoo PG → Fabric Mirroring → Bronze (OneLake)
                                  ↓
                              Silver (Fabric notebook/dataflow)
                                  ↓
                              Gold (Fabric warehouse/lakehouse)
                                  ↓
                              Semantic Model → Power BI Reports
```

Use only when Databricks is not in the data path for a specific domain.

### Option C: Hybrid

```text
Odoo PG → Fabric Mirroring → Bronze (OneLake, tactical)
Odoo PG → Databricks Federation → Bronze → Silver → Gold (governed)
                                                       ↓
                                         Fabric Gold (shortcut to Databricks)
                                                       ↓
                                         Semantic Model → Reports
```

Mirroring provides low-latency operational visibility. Databricks provides governed curated analytics. Reports always consume gold.

**Recommended: Option A (Databricks-first) with Option C (hybrid) for tactical operational dashboards.**

---

## Existing gold layer (from Databricks)

These tables are already verified and populated in `dbw_ipai_dev.gold`:

| Table | Business entity | Rows |
|-------|----------------|------|
| `fact_account_move` | Financial transactions | 12 |
| `fact_project_task` | Project execution | Verified |
| `client_revenue` | Revenue by client | 5 |
| `dim_project` | Project dimension | Verified |
| `dim_tag` | Tag dimension | Verified |
| `dim_task_stage` | Task stage dimension | Verified |
| `dim_analytic_account` | Analytic account dimension | Verified |
| `expense_liquidation_health` | Expense health metric | Verified |
| `ap_ar_cash_summary` | AP/AR cash position | Verified |

These can be exposed to Fabric via Databricks SQL endpoint or OneLake shortcut immediately.

---

## Sprint plan

### Phase 1: Wire gold to Fabric

- Create shortcut or Direct Lake connection from Finance PPM to `dbw_ipai_dev.gold.*`
- Validate table visibility in Fabric SQL analytics endpoint
- No new modeling needed — gold already exists

### Phase 2: Publish semantic model

- Create `finance_ppm_semantic_model` in Fabric
- Define relationships between fact and dimension tables
- Add business measures (total revenue, margin %, utilization rate, budget variance)
- Publish to workspace

### Phase 3: Ship canonical reports

- **Portfolio Health Dashboard** — project status, task completion, milestone tracking
- **Budget vs Actual Dashboard** — planned vs actual spend by project/period
- **Margin & Utilization Dashboard** — revenue, cost, margin by client/project

---

## References

- Role split: `docs/architecture/DATABRICKS_FABRIC_ROLE_SPLIT.md`
- Benchmark alignment: `docs/architecture/ORG_BENCHMARK_ALIGNMENT.md`
- Microsoft reference: [Data Intelligence E2E with Databricks and Fabric](https://techcommunity.microsoft.com/blog/azurearchitectureblog/data-intelligence-end-to-end-with-azure-databricks-and-microsoft-fabric/4232621)
- Data platform audit: `docs/audits/data-platform/20260328/`
