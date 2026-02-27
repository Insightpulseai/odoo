# Expense Liquidation Is SSOT

**Date:** 2026-02-27
**Status:** Active canonical module

---

## Decision

`addons/ipai/ipai_hr_expense_liquidation` is the **single source of truth** for:

- TBWA Itemized Expense Report logic
- Cash Advance Liquidation form number (`LIQ/YYYY/####`)
- Expense line categorization (meals / transportation / misc)
- Settlement calculation (advance vs total expenses)
- QWeb report binding (`hr.expense.liquidation` record → PDF)

---

## What this means for future modules

| Scenario | Correct approach |
|---|---|
| Add OCR receipt auto-fill | `ipai_expense_ocr` extends `hr.expense` (already exists) |
| Add policy rules / limits | Create `ipai_expense_policy`, depend on `ipai_hr_expense_liquidation` |
| Add budget check | Same — new sibling addon, `_inherit` only |
| Add new report variant | Add a new `ir.actions.report` in this addon or a sibling |
| Rebuild liquidation in a new addon | ❌ Blocked — creates drift and dual-SSOT |

---

## Field → form mapping

See `addons/ipai/ipai_hr_expense_liquidation/README.md` for the full TBWA form
field → Odoo field mapping table.

---

## Constraints in place (as of 2026-02-27)

1. **LIQ sequence** — `hr.expense.liquidation.name` is auto-assigned, read-only, copy=False
2. **Employee scope** — `hr.expense.cash_advance_liquidation_id` employee must match liquidation employee
3. **Company scope** — same for `company_id`
4. **Single-advance-per-sheet** — `hr.expense.sheet` rejects > 1 distinct liquidation across its expense lines

---

## Related commits

| Commit | Description |
|---|---|
| `0aff4c9ee` | Add liquidation_report_date + hr.expense CA link fields |
| `04ddc51c8` | Update QWeb report with Form No. and Date Prepared bindings |
| `1472125ca` | Add test_form_no tests (date default, related field, sheet constraint) |
