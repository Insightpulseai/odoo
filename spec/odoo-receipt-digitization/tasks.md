# Tasks — Odoo Receipt Digitization

**Spec bundle**: `spec/odoo-receipt-digitization/`
**Tracks**: `plan.md` phases

---

## Phase 1: Lane A — OCR Digitization (no new infra)

All tasks within `addons/ipai/ipai_expense_ocr/`.

| # | Task | Files | Verify command |
|---|------|-------|----------------|
| 1.1 | Create `utils/__init__.py` (empty) | NEW | `python3 -c "import importlib; importlib.import_module('utils')"` (from module dir) |
| 1.2 | Create `utils/ocr_client.py` — move `OCRResult`, regex patterns, `normalize_amount`, `parse_text` from `ocr_extract.py`; add `fetch_image_text()` | NEW | `python3 -c "from addons.ipai.ipai_expense_ocr.utils.ocr_client import fetch_image_text, parse_text; print('ok')"` |
| 1.3 | Edit `scripts/ocr_extract.py` — replace local definitions with `from ..utils.ocr_client import OCRResult, parse_text`; keep `main()` CLI intact | EDIT | `python3 scripts/ocr_extract.py --in test.txt --out /tmp/r.json && cat /tmp/r.json` |
| 1.4 | Create `models/hr_expense_mixin.py` — `_inherit = "hr.expense"`, computed fields `ocr_run_count` / `ocr_confidence`, `action_digitize_receipt()`, `action_open_ocr_runs()` | NEW | Odoo shell: `'action_digitize_receipt' in dir(env['hr.expense'])` |
| 1.5 | Edit `models/__init__.py` — add `from . import hr_expense_mixin` | EDIT | Module install no traceback |
| 1.6 | Create `views/hr_expense_views.xml` — inherit `hr_expense.hr_expense_view_form`; add Digitize button in header + OCR scan stat button | NEW | Odoo: form view loads without error |
| 1.7 | Edit `__manifest__.py` — add `views/hr_expense_views.xml` to `data[]` before `views/menu.xml` | EDIT | `grep hr_expense_views __manifest__.py` returns match |
| 1.8 | Update module: `odoo -d odoo_dev -c odoo.conf -u ipai_expense_ocr --stop-after-init` | — | Exit 0, no Python traceback in log |
| 1.9 | E2E manual test: upload JPEG → click Digitize → verify fields + audit record | — | `env["ipai.expense.ocr.run"].search([("status","=","ok")], limit=1).confidence > 0` |
| 1.10 | Add `tests/test_digitize.py` — mock `requests.post` to return fixture JSON → assert fields filled + run record created | NEW | `pytest addons/ipai/ipai_expense_ocr/tests/ -v` passes |

---

## Phase 2: Lane B — Supabase ETL CDC (new infra)

| # | Task | Files | Verify command |
|---|------|-------|----------------|
| 2.1 | SSH to DO droplet → check `wal_level` | — | `psql -c "SHOW wal_level;"` → must be `logical` |
| 2.2 | If `wal_level != logical`: `ALTER SYSTEM SET wal_level = 'logical';` → restart Postgres | DO droplet SSH | Re-run `SHOW wal_level;` → `logical` |
| 2.3 | Create read-only replication user: `CREATE ROLE odoo_cdc REPLICATION LOGIN PASSWORD '...';` + grant SELECT on expense tables | SQL | `\du odoo_cdc` shows REPLICATION |
| 2.4 | Create publication: `CREATE PUBLICATION odoo_expense_pub FOR TABLE hr_expense, hr_expense_sheet, ir_attachment, ipai_expense_ocr_run;` | SQL | `\dRp` lists `odoo_expense_pub` |
| 2.5 | Create `infra/supabase-etl/odoo-expense.toml` | NEW | `supabase-etl validate infra/supabase-etl/odoo-expense.toml` exits 0 |
| 2.6 | Add GitHub Actions secrets: `ODOO_PG_CDC_URL`, `ICEBERG_CATALOG_URI`, `ICEBERG_WAREHOUSE`, `ICEBERG_NAMESPACE`, `ICEBERG_S3_ENDPOINT`, `ICEBERG_REGION`, `ICEBERG_ACCESS_KEY_ID`, `ICEBERG_SECRET_ACCESS_KEY`, `ICEBERG_S3_PATH_STYLE` | GitHub UI | `gh secret list \| grep ICEBERG_CATALOG_URI` |
| 2.7 | Create `.github/workflows/supabase-etl-expense.yml` — deploys ETL worker on DO App Platform | NEW | Workflow runs, worker starts |
| 2.8 | Integration test: insert test expense in `odoo_dev` → confirm Iceberg snapshot advances and row is queryable within 60s | — | `SELECT * FROM odoo_ops.expense ORDER BY id DESC LIMIT 1` via Iceberg query engine returns inserted row; snapshot ID has incremented |

---

## Commit Order

```bash
# Phase 1
git add addons/ipai/ipai_expense_ocr/utils/ \
        addons/ipai/ipai_expense_ocr/scripts/ocr_extract.py
git commit -m "feat(expense): extract OCR utils module — ocr_client.py"

git add addons/ipai/ipai_expense_ocr/models/hr_expense_mixin.py \
        addons/ipai/ipai_expense_ocr/models/__init__.py \
        addons/ipai/ipai_expense_ocr/views/hr_expense_views.xml \
        addons/ipai/ipai_expense_ocr/__manifest__.py
git commit -m "feat(expense): add action_digitize_receipt to hr.expense + form button"

git add addons/ipai/ipai_expense_ocr/tests/test_digitize.py
git commit -m "test(expense): digitize receipt E2E with mocked OCR endpoint"

# Spec
git add spec/odoo-receipt-digitization/
git commit -m "docs(spec): add odoo-receipt-digitization spec bundle"

# Phase 2
git add infra/supabase-etl/
git commit -m "feat(infra): add Supabase ETL config for odoo-expense CDC publication"

git add .github/workflows/supabase-etl-expense.yml
git commit -m "feat(ci): add supabase-etl-expense workflow for CDC worker deploy"
```
