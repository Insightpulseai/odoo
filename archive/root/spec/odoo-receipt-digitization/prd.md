# PRD — Odoo Receipt Digitization

**Spec bundle**: `spec/odoo-receipt-digitization/`
**Status**: Draft
**Module**: `ipai_expense_ocr` (extends existing)
**Lanes**: A (OCR auto-fill) + B (Supabase ETL CDC)

---

## Problem

Odoo CE has receipt attachment (upload + store) but no automated field extraction.
Odoo Enterprise provides OCR via IAP (cloud, paid). This spec replaces IAP with the
existing PaddleOCR service at `ocr.insightpulseai.com`.

---

## User Stories

| ID | Story |
|----|-------|
| US-01 | As an employee, I upload a receipt image to a draft expense and click "Digitize" so that merchant, date, and amount fill automatically. |
| US-02 | As a manager, I see an OCR confidence badge on the expense so I know if extraction was reliable before I approve. |
| US-03 | As an analyst, expense and OCR events stream to the data warehouse in real time so dashboards stay current without export scripts. |
| US-04 | As a developer, if the OCR service is down I see a clear error and an audit record — expense data is never silently corrupted or overwritten. |

---

## Scope

### In scope
- "Digitize Receipt" button on `hr.expense` form (draft + reported states)
- POST image attachment to PaddleOCR → parse merchant / date / total
- Write extracted values back to blank expense fields only
- `ipai.expense.ocr.run` audit record on every attempt (success or error)
- Smart badge showing OCR scan count + last confidence score
- Supabase ETL CDC replication of expense + OCR tables to analytics destination

### Out of scope
- Email alias → auto-create expense from forwarded receipt
- Mobile camera capture
- Multi-attachment batch wizard
- VAT / line-item extraction (ML model required)
- Supabase ETL destination setup (BigQuery / Iceberg — separate infra spec)

---

## Extraction Schema (Lane A output)

```json
{
  "merchant":      "string | null",
  "receipt_date":  "YYYY-MM-DD | null",
  "total":         "float | null",
  "currency":      "PHP | USD | null",
  "confidence":    "0.0 – 1.0",
  "raw_text":      "string"
}
```

---

## Write-back Rules

| Extracted field | Writes to | Condition |
|-----------------|-----------|-----------|
| `merchant` | `hr.expense.name` (max 100 chars) | Only if field is blank |
| `total` | `hr.expense.unit_amount` | Only if field is 0 or blank |
| `receipt_date` | `hr.expense.date` | Only if field is blank |

**Never overwrite user-entered data.** All writes are conditional on blank target.

---

## Error States

| State | Behaviour |
|-------|-----------|
| No image attachment found | `UserError`: "No image attachment found. Upload a receipt image first." |
| `IPAI_OCR_ENDPOINT_URL` not set | `UserError`: "OCR endpoint not configured. Run scripts/odoo_config_mail_ai_ocr.py." |
| OCR service timeout (30s) | `UserError`: "OCR service error: \<reason\>" + error audit record created |
| OCR service HTTP 5xx | `UserError`: "OCR service error: \<reason\>" + error audit record created |
| Confidence < 0.4 | Fields fill, but notification shows low-confidence warning (not an error) |
| All target fields already populated | No write, notification: "Fields already populated — no changes made." |

---

## Acceptance Criteria

1. Upload JPEG receipt to draft `hr.expense` → click "Digitize" → `name`, `unit_amount`, `date` filled
2. Smart badge appears showing "1 OCR Scan" → click → shows audit record with confidence
3. Second "Digitize" on already-filled expense → fields unchanged, notification shown
4. OCR service offline → `UserError` displayed, error audit record created, expense unchanged
5. `ipai.expense.ocr.run` record exists for every button click (success or error)
6. Button absent on posted/paid expenses (state `posted`, `done`)

---

## CDC Replication Tables (Lane B)

| Odoo table | Destination name | Events |
|------------|------------------|--------|
| `hr_expense` | `expense` | INSERT, UPDATE, DELETE |
| `hr_expense_sheet` | `expense_sheet` | INSERT, UPDATE |
| `ir_attachment` | `expense_attachment` | INSERT (metadata only, no binary) |
| `ipai_expense_ocr_run` | `expense_ocr_run` | INSERT |

Delivery: at-least-once, resumable via replication slot. Lag target: < 60 seconds.

---

### Supabase / Infrastructure Acceptance Criteria

- [ ] No plaintext secrets in `infra/supabase-etl/odoo-expense.toml` or any spec doc — env var references only
- [ ] Lane B ETL config references Vault or env var names; values never in git
- [ ] Any new `ops.*` table created for this feature has RLS enabled + policies defined
- [ ] CDC is at-least-once + replayable (slot persists across restarts; no data loss on worker restart)
- [ ] `ir_attachment.datas` binary column excluded from all Iceberg schema definitions
