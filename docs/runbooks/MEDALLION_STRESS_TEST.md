# Runbook: Medallion Pipeline Stress Test

## Purpose

Validates the Bronze-Silver-Gold medallion pipeline using synthetic data with configurable scale, data quality issues (duplicates, nulls, late-arriving facts, schema drift), and automated correctness checks.

## Artifacts

| File | Purpose |
|------|---------|
| `data-intelligence/tests/synthetic/profiles.yaml` | Scale profile definitions |
| `data-intelligence/tests/synthetic/data_generator.py` | Synthetic data generator (5 tables) |
| `data-intelligence/notebooks/tests/seed_synthetic.py` | Databricks notebook: seed Bronze |
| `data-intelligence/notebooks/tests/test_medallion_pipeline.py` | Databricks notebook: Bronze-Silver-Gold transforms |
| `data-intelligence/tests/synthetic/validate_medallion.py` | Validation suite (row counts, schemas, correctness) |
| `data-intelligence/notebooks/tests/cleanup_test_data.py` | Databricks notebook: drop test schemas |
| `data-intelligence/tests/synthetic/results_schema.json` | JSON Schema for test output |

## Environment

| Item | Value |
|------|-------|
| Workspace | `adb-7405610347978231.11.azuredatabricks.net` |
| SQL Warehouse | `e7d89eabce4c330c` (Small, Pro) |
| Catalog | `dbw_ipai_dev` |
| Test schemas | `test_bronze`, `test_silver`, `test_gold` |
| Runtime | Databricks Runtime 15.4+ |

## Scale Profiles

| Profile | Rows/table | Line items | Dup rate | Null rate | Late-arriving | Skew | Drift |
|---------|-----------|------------|----------|-----------|---------------|------|-------|
| `tiny` | 100 | 2/inv | 5% | 2% | 1% | 0.3 | No |
| `small` | 1,000 | 3/inv | 8% | 5% | 3% | 0.5 | Yes |
| `medium` | 10,000 | 4/inv | 10% | 7% | 5% | 0.7 | Yes |
| `large` | 100,000 | 5/inv | 12% | 10% | 8% | 0.9 | Yes |

Approximate total rows (including line items, payments, events):

- **tiny**: ~1,500 rows across all tables
- **small**: ~15,000 rows
- **medium**: ~180,000 rows
- **large**: ~2,000,000 rows

## How to Run

### Step 1: Seed Bronze data

1. Open `notebooks/tests/seed_synthetic.py` in Databricks workspace
2. Set widget `scale_profile` to desired profile (default: `small`)
3. Set widget `seed` to `42` (or any integer for reproducibility)
4. Run all cells
5. Notebook exits with JSON ingestion metrics

### Step 2: Run medallion pipeline

1. Open `notebooks/tests/test_medallion_pipeline.py`
2. Run all cells
3. Observe Bronze-Silver dedup counts, Silver-Gold aggregate creation
4. Notebook exits with full pipeline metrics JSON

### Step 3: Validate

Option A (in notebook):
```python
from tests.synthetic.validate_medallion import MedallionValidator
v = MedallionValidator(spark, catalog="dbw_ipai_dev")
report = v.run_all()
v.print_report(report)
```

Option B (standalone notebook cell):
```python
%run /Workspace/Repos/data-intelligence/tests/synthetic/validate_medallion
```

### Step 4: Cleanup

1. Open `notebooks/tests/cleanup_test_data.py`
2. Run all cells
3. Confirms all `test_*` schemas are dropped

## Expected Outputs

### Seed metrics

```json
{
  "profile": "small",
  "seed": 42,
  "total_rows": 14832,
  "tables": {
    "customers": {"rows_written": 1080},
    "invoices": {"rows_written": 1080},
    "line_items": {"rows_written": 8400},
    "payments": {"rows_written": 810},
    "events": {"rows_written": 5400}
  }
}
```

### Validation report

```
[+] PASS row_count.customers.bronze_gte_silver
         Bronze=1,080 Silver=1,000 (dedup removed 80)
[+] PASS schema.customers.has_customer_id
         present in customers
[+] PASS uniqueness.customers.customer_id
         total=1,000 distinct=1,000 dupes=0
[+] PASS gold_correctness.revenue_total
         gold=4,521,300.50 silver_ref=4,521,300.50 diff=0.00
```

## Validation Checks

| Category | Check | Rule |
|----------|-------|------|
| Row counts | `bronze_gte_silver` | Bronze >= Silver (dedup removes rows) |
| Row counts | `gold_not_empty` | Gold tables have > 0 rows |
| Schema | `has_<column>` | Required columns present in Silver |
| Schema | `<column>_type` | Column types match contract |
| Schema | `no_drift_cols` | No `_drift_*` columns in Silver |
| Uniqueness | `<pk>` | No duplicate primary keys in Silver |
| Correctness | `revenue_total` | Gold revenue = sum(Silver line_total) for posted/paid |
| Correctness | `customer_kpi_count` | Gold KPI rows = Silver customer rows |
| Idempotency | `has_history` | Delta version history exists |

## Guardrails

### Cost control

- **Default to `small` profile** for routine testing
- **`large` profile** generates ~2M rows — use only for stress testing, not daily CI
- All test data lives in `test_*` schemas — never contaminates production schemas
- SQL Warehouse `e7d89eabce4c330c` is Small/Pro — adequate for all profiles
- Always run cleanup after testing to free storage

### Safety

- Test schemas use `test_` prefix — `DROP SCHEMA ... CASCADE` only affects test data
- Cleanup notebook verifies production schemas are untouched
- Seed notebook uses `mode("overwrite")` — idempotent, safe to rerun
- No secrets required — uses workspace-level catalog access

### Time estimates (approximate)

| Profile | Seed | Pipeline | Validate | Total |
|---------|------|----------|----------|-------|
| tiny | <30s | <30s | <15s | ~1 min |
| small | <1 min | <1 min | <30s | ~2 min |
| medium | ~3 min | ~5 min | ~1 min | ~10 min |
| large | ~15 min | ~30 min | ~5 min | ~50 min |

## Local Testing (without Databricks)

The data generator works standalone:

```bash
cd data-intelligence
python -m tests.synthetic.data_generator --profile small --output /tmp/synthetic_data --format csv
```

This produces CSV files for inspection without consuming Databricks compute.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `SCHEMA_NOT_FOUND` | Test schemas not created | Run seed notebook first |
| `TABLE_NOT_FOUND` in validation | Pipeline notebook not run | Run `test_medallion_pipeline` before validation |
| `AnalysisException: cannot resolve` | Schema drift columns | Pipeline drops `_drift_*` columns — verify notebook ran fully |
| Slow `large` profile | Warehouse undersized | Scale warehouse to Medium temporarily |
| Revenue total mismatch | Floating point drift | Check tolerance (0.01 allowed) |
