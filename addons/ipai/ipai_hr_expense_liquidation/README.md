# ipai_hr_expense_liquidation

**Canonical implementation of TBWA Itemized Expense Report + Cash Advance Liquidation.**

This module is the **SSOT** for all expense liquidation logic. Do not duplicate its model
or report in another addon. Extend via `_inherit` only.

---

## TBWA Form Field Mapping

The following table maps printed labels on the TBWA "Itemized Expense Report" form to
their Odoo model fields. This is the authoritative binding — no other addon should
re-implement these fields.

| Printed label on form | Odoo field | Model | Notes |
|---|---|---|---|
| **If Cash Advance Liquidation, Form No.** | `name` | `hr.expense.liquidation` | Auto-assigned sequence `LIQ/YYYY/####` on create |
| **Date Prepared** | `liquidation_report_date` | `hr.expense.liquidation` | Default: record creation date |
| **Liquidation Date** | `date` | `hr.expense.liquidation` | Transaction date |
| **Employee** | `employee_id.name` | `hr.expense.liquidation` | Required |
| **Department** | `department_id.name` | `hr.expense.liquidation` | Related from employee |
| **Period** | `period_start` / `period_end` | `hr.expense.liquidation` | Optional date range |
| **Advance Amount** | `advance_amount` | `hr.expense.liquidation` | Cash advance type only |
| **Advance Reference** | `advance_reference` | `hr.expense.liquidation` | Advance voucher number |
| **Line: Date** | `line_ids.date` | `hr.expense.liquidation.line` | Per-receipt date |
| **Line: Description** | `line_ids.description` | `hr.expense.liquidation.line` | Required |
| **Line: Category** | `line_ids.bucket` | `hr.expense.liquidation.line` | meals/transportation/miscellaneous |
| **Line: Amount** | `line_ids.amount` | `hr.expense.liquidation.line` | Monetary |
| **Meals & Entertainment total** | `total_meals` | `hr.expense.liquidation` | Computed |
| **Transportation & Travel total** | `total_transportation` | `hr.expense.liquidation` | Computed |
| **Miscellaneous total** | `total_miscellaneous` | `hr.expense.liquidation` | Computed |
| **Total Expenses** | `total_expenses` | `hr.expense.liquidation` | Computed |
| **Settlement Amount** | `settlement_amount` | `hr.expense.liquidation` | advance - total_expenses |
| **Employee Signature / Name** | `employee_id.name` | `hr.expense.liquidation` | Printed in sig block |
| **Approver Signature / Name** | `approver_id.name` | `hr.expense.liquidation` | Printed after approval |

---

## Report binding

The QWeb report action (`action_report_expense_liquidation`) binds to **`hr.expense.liquidation`**
records directly — **not** to `hr.expense` or `hr.expense.sheet`. One liquidation record
= one printed form = one `LIQ/YYYY/####` Form No.

```
ir.actions.report  →  model: hr.expense.liquidation
                   →  template: report_expense_liquidation_document
                   →  paperformat: base.paperformat_us
```

---

## Linking expenses to a liquidation

`hr.expense` records may optionally reference a liquidation via:

```python
cash_advance_liquidation_id = fields.Many2one("hr.expense.liquidation", ...)
cash_advance_form_no        = fields.Char(related="cash_advance_liquidation_id.name", store=True)
```

Constraints enforced:
- An expense's `employee_id` and `company_id` must match the linked liquidation's.
- An `hr.expense.sheet` may not contain expenses referencing more than one distinct
  liquidation (hard `ValidationError` on save).

---

## Scope constraints (prevents cross-entity drift)

| Rule | Where enforced | Error |
|---|---|---|
| Expense employee must match liquidation employee | `hr.expense` `@constrains` | `ValidationError` |
| Expense company must match liquidation company | `hr.expense` `@constrains` | `ValidationError` |
| All linked expenses on a sheet share one liquidation | `hr.expense.sheet` `@constrains` | `ValidationError` |

---

## Extension guide (for future addons)

```
✅ Do:   _inherit = "hr.expense.liquidation"  — add fields via inheritance
✅ Do:   _inherit = "hr.expense.liquidation.line"  — same
✅ Do:   Create a sibling addon (e.g. ipai_expense_policy) that depends on this one
❌ Don't: Duplicate hr.expense.liquidation in another addon
❌ Don't: Re-implement the LIQ/YYYY/#### sequence elsewhere
❌ Don't: Create ipai_expense_e2e — it does not exist and is not needed
```

---

## Sequence

| Key | Pattern | Example |
|---|---|---|
| `hr.expense.liquidation` | `LIQ/%(year)s/%(seq)04d` | `LIQ/2026/0001` |

Defined in `data/sequence.xml`.

---

## Security groups

| Group | XML ID | Permissions |
|---|---|---|
| Expense Liquidation User | `group_expense_liquidation_user` | read, write, create |
| Expense Liquidation Approver | `group_expense_liquidation_approver` | read, write, create, delete |
