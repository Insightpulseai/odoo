# Power BI on Gold

## Purpose

Define the reporting contract from the curated gold layer into Power BI.

---

## Approved source

Power BI connects to the Databricks SQL Warehouse:

- Warehouse ID: `e7d89eabce4c330c`
- Host: `adb-7405610347978231.11.azuredatabricks.net`
- Auth: Entra ID (Azure AD token) or Databricks PAT

---

## Source boundary

Approved report sources must come from a curated serving contract over:

- `dbw_ipai_dev.gold.*`

Reports must not connect directly to:

- Mirrored operational tables (Fabric or OneLake raw mirrors)
- Bronze objects (`dbw_ipai_dev.bronze.*`)
- Silver working tables (`dbw_ipai_dev.silver.*`)
- Experimental gold tables not marked for BI serving
- Federated source tables (`odoo_erp.public.*`)

---

## Serving contract

Not every gold table is a report contract. The serving layer narrows gold to stable, owned, documented objects.

### Recommended naming convention

Choose one and apply consistently:

- `dbw_ipai_dev.gold.bi_*` — BI-designated tables/views
- `dbw_ipai_dev.gold.reporting_*` — reporting-designated
- `dbw_ipai_dev.serving.*` — dedicated serving schema

### Contract requirements

Each approved serving object must define:

| Attribute | Description |
|-----------|-------------|
| Grain | What one row represents (e.g., one invoice line per period) |
| Business owner | Who owns the business definition |
| Refresh expectation | How often the data is refreshed (daily, near real-time, etc.) |
| Canonical measures | Approved aggregations (total revenue, margin %, utilization rate) |
| Conformed dimensions used | Which dim tables join to this fact |
| Exclusions / caveats | What is intentionally excluded or approximate |

---

## Required semantics

Before new dashboards are built, the dataset or semantic model must identify:

- Authoritative measures (which calculations are canonical vs derived)
- Additive vs non-additive behavior (can this measure be summed across all dimensions?)
- Approved join paths (which dimensions join to which facts, at what grain)
- Approved filter dimensions (which dimensions are safe to slice by)

---

## Initial serving objects (Finance PPM)

Based on verified gold layer tables:

| Serving object | Grain | Business entity | Measures |
|---------------|-------|----------------|----------|
| `fact_account_move` | One accounting entry | Financial transactions | Amount, debit, credit |
| `fact_project_task` | One project task | Project execution | Task count, completion |
| `client_revenue` | One client | Revenue by client | Total revenue |
| `ap_ar_cash_summary` | Aggregate | AP/AR cash position | Receivable, payable, net |
| `expense_liquidation_health` | Aggregate | Expense health | Liquidation rate |
| `dim_project` | One project | Project dimension | — |
| `dim_analytic_account` | One analytic account | Cost center dimension | — |
| `dim_task_stage` | One stage | Task stage dimension | — |
| `dim_tag` | One tag | Tag dimension | — |

---

## Delivery rule

Before new dashboards are built:

1. Identify the serving objects needed
2. Verify they exist in gold with documented grain and ownership
3. If they don't exist, create them in `data-intelligence` repo first
4. Publish to Unity Catalog
5. Then build the Power BI dataset/semantic model
6. Then build the report

Do not reverse this order. Reports should never drive table creation.

---

## Anti-patterns

| Anti-pattern | Why it's wrong |
|-------------|---------------|
| Report reads from mirrored PG table | No conformance, no governance, business logic in dashboard |
| Dashboard defines its own calculated measures over raw data | Semantics live in reports instead of the modeled layer |
| Multiple reports define the same measure differently | No single source of truth for business KPIs |
| Gold table exposed without grain/owner documentation | Consumers don't know what one row means |
| Experimental table used in production report | Breaks when the table changes |

---

## Power BI connection setup

### Direct Lake (preferred for Fabric)

Connect Fabric lakehouse/warehouse to Databricks gold via OneLake shortcut:

```text
Finance PPM workspace → Lakehouse → Shortcut → dbw_ipai_dev.gold.*
                                                    ↓
                                           Semantic Model (Direct Lake)
                                                    ↓
                                              Power BI Report
```

### Import/DirectQuery (alternative)

Connect Power BI Desktop directly to Databricks SQL:

```text
Power BI Desktop → Get Data → Azure Databricks
  → Server: adb-7405610347978231.11.azuredatabricks.net
  → HTTP Path: /sql/1.0/warehouses/e7d89eabce4c330c
  → Auth: Azure AD
  → Select: dbw_ipai_dev.gold.* tables
```

---

## Governance

- Serving objects are versioned through the `data-intelligence` repo
- Changes to serving objects require PR review
- Breaking changes (renamed columns, changed grain) require a migration note
- Power BI datasets should pin to specific serving object versions where possible

---

## References

- Benchmark alignment: `docs/architecture/ORG_BENCHMARK_ALIGNMENT.md`
- Finance PPM target state: `docs/architecture/FABRIC_FINANCE_PPM_TARGET_STATE.md`
- Role split: `docs/architecture/DATABRICKS_FABRIC_ROLE_SPLIT.md`
- Databricks SQL Warehouse: `e7d89eabce4c330c`
