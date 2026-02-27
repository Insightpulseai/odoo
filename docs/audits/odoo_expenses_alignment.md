# Odoo 19 Expenses Workflow Alignment

**Date:** 2026-02-27
**Status:** Active policy
**Canonical docs:** https://www.odoo.com/documentation/19.0/applications/finance/expenses.html

---

## Decision

IPAI automations **never bypass** Odoo's native expense approval or journal posting workflow.
They extend and assist it. Odoo's approval/posting state model is the authority.

---

## Odoo 19 Expenses canonical workflow

```
Employee logs expense
  → attaches receipt (OCR can pre-fill fields)
  → submits expense report (hr.expense.sheet)
       → Manager approves (Expenses Manager role)
            → Finance posts journal entries (Accounting: Accountant/Adviser)
                 → Payment / reimbursement
```

**References:**
- Log → Submit: https://www.odoo.com/documentation/19.0/applications/finance/expenses.html
- Submit → Approve: https://www.odoo.com/documentation/19.0/applications/finance/expenses/submit_expenses.html
- Approve → Post: https://www.odoo.com/documentation/19.0/applications/finance/expenses/post_expenses.html

---

## Alignment matrix: IPAI modules vs Odoo native flow

| Odoo step | Odoo model / action | IPAI module | IPAI role |
|---|---|---|---|
| Log expense | `hr.expense` create | `ipai_hr_expense_liquidation` | Adds `cash_advance_liquidation_id` link (optional) |
| Attach receipt | `ir.attachment` on `hr.expense` | *(OCR bridge, future)* | Pre-fills fields; does not replace Odoo upload UX |
| Submit report | `hr.expense.sheet` → `action_submit_sheet` | `ipai_hr_expense_liquidation` | Validates single-advance-per-sheet constraint |
| Approve | `hr.expense.sheet` → `action_approve_expense_sheets` | `ipai_agent` | Can assist with audit info; cannot approve without Expenses Manager group |
| Post journal | `hr.expense.sheet` → `action_sheet_move_create` | `ipai_agent` | Any "post" action requires `account.group_account_user` + Expenses Manager — enforced below |
| Reimburse | Payment registration | *(no IPAI override)* | Native only |

---

## What IPAI modules DO NOT do

| Prohibited | Why |
|---|---|
| Call `action_sheet_move_create` from agent without Odoo role check | Would bypass posting permission gate |
| Set `hr.expense.sheet.state = 'post'` directly via SQL / ORM bypass | Skips approval state machine |
| Create journal entries (`account.move`) for expenses outside Odoo posting flow | Dual-accounting risk |
| Auto-approve expense reports without human Expenses Manager action | Violates Odoo's stated access control |

---

## Cash advance / liquidation (not in core Odoo 19 docs)

Odoo 19 Expenses documentation does not describe native cash advance liquidation as a first-class feature.

**IPAI decision:** `ipai_hr_expense_liquidation` is the SSOT for this capability. It:
- Adds `hr.expense.liquidation` model (LIQ/YYYY/#### sequence = Form No.)
- Links `hr.expense` records back to a liquidation form
- Generates the TBWA "Itemized Expense Report" QWeb PDF
- Does **not** replace or shadow the native `hr.expense.sheet` approval/posting flow

---

## IPAI agent + posting tools: group enforcement

Any `ipai.agent.tool` that triggers journal posting or expense approval **must**:

1. Set `allowed_group_ids` to include both:
   - `account.group_account_user` (Accounting: Accountant/Adviser)
   - `hr_expense.group_hr_expense_manager` (Expenses: Manager)
2. Have the governing `ipai.agent.policy` with `require_approval = True`
3. Never call `action_sheet_move_create` directly — always invoke it on behalf of a user who holds the required groups

**Example tool configuration:**

```python
# In Odoo data / setup script (never in Python code — use admin UI or data XML)
tool = env["ipai.agent.tool"].create({
    "name": "Post Expense Report",
    "technical_name": "expense_sheet_post",
    "auth_mode": "service_role",
    "allowed_group_ids": [
        env.ref("account.group_account_user").id,
        env.ref("hr_expense.group_hr_expense_manager").id,
    ],
})
# Policy:
env["ipai.agent.policy"].create({
    "name": "Expense Posting Policy",
    "target_model": "hr.expense.sheet",
    "require_approval": True,
    "allowed_tool_ids": [(4, tool.id)],
})
```

---

## OCR bridge alignment

The OCR pipeline (PaddleOCR-VL → Supabase → Odoo) behaves as a **connector**:

1. Extract: merchant, date, total, tax, category from receipt image
2. Pre-fill: `hr.expense` fields if confidence ≥ threshold
3. Queue for review: low-confidence extractions go to a review list
4. Never create expenses autonomously without employee review

This aligns with Odoo's native "digitalization settings" framework (upload → extract → review).

---

## Acceptance criteria

- [ ] No IPAI code path posts journal entries without checking Odoo posting access groups
- [ ] `ipai_agent` tools for expense posting have `allowed_group_ids` set correctly
- [ ] `require_approval = True` in policy for all expense/posting tools
- [ ] OCR output is always presented for employee review before submitting
- [ ] `docs/audits/expense_liquidation_ssot.md` remains the SSOT for liquidation model decisions
