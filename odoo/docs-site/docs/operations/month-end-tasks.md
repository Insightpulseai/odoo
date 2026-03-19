# Month-end task template

44 tasks across 4 phases, targeting completion in 5 business days. Each task has a defined owner, dependency, and deadline. Use this as the master checklist — copy it into your close tracker each period.

---

## Summary

| Phase | Days | Tasks | Focus |
|-------|------|:-----:|-------|
| 1. Transaction cut-off and reconciliation | 1–2 | 15 | Cut-off, bank/GL reconciliation |
| 2. Adjusting entries and reclassifications | 2–3 | 10 | Accruals, deferrals, corrections |
| 3. Financial reporting and analysis | 3–4 | 10 | Statements, variance analysis |
| 4. Review, approval, and BIR prep | 4–5 | 9 | Sign-off, period lock, BIR forms |

---

## Phase 1 — Transaction cut-off and reconciliation (days 1–2)

| # | Task | Responsible | Dependency | Deadline |
|:-:|------|-------------|------------|----------|
| 1 | Verify AP cut-off — confirm all vendor invoices posted | AP Clerk | None | Day 1 AM |
| 2 | Verify AR cut-off — confirm all customer invoices posted | AR Clerk | None | Day 1 AM |
| 3 | Post pending bank transactions | Treasury | None | Day 1 AM |
| 4 | Import bank statements (all accounts) | Treasury | Task 3 | Day 1 AM |
| 5 | Run auto-reconciliation (`account_reconcile_oca`) | Senior Accountant | Task 4 | Day 1 PM |
| 6 | Resolve bank reconciliation exceptions | Senior Accountant | Task 5 | Day 1 PM |
| 7 | Approve bank write-offs (if any) | Accounting Manager | Task 6 | Day 2 AM |
| 8 | Reconcile AR sub-ledger to GL | AR Clerk | Task 2 | Day 1 PM |
| 9 | Reconcile AP sub-ledger to GL | AP Clerk | Task 1 | Day 1 PM |
| 10 | Reconcile inventory sub-ledger to GL | Cost Accountant | None | Day 2 AM |
| 11 | Reconcile fixed assets register to GL | Fixed Assets Clerk | None | Day 2 AM |
| 12 | Reconcile intercompany balances | Senior Accountant | Tasks 8, 9 | Day 2 AM |
| 13 | Reconcile VAT input/output accounts | Tax Accountant | Tasks 1, 2 | Day 2 PM |
| 14 | Reconcile WHT accounts | Tax Accountant | Tasks 1, 2 | Day 2 PM |
| 15 | Prepare bank reconciliation report | Senior Accountant | Task 7 | Day 2 PM |

## Phase 2 — Adjusting entries and reclassifications (days 2–3)

| # | Task | Responsible | Dependency | Deadline |
|:-:|------|-------------|------------|----------|
| 16 | Post expense accruals (utilities, rent, services) | Senior Accountant | Phase 1 | Day 2 PM |
| 17 | Post revenue accruals (unbilled revenue) | Senior Accountant | Phase 1 | Day 2 PM |
| 18 | Post prepayment amortization entries | Senior Accountant | None | Day 3 AM |
| 19 | Post depreciation entries | Fixed Assets Clerk | Task 11 | Day 3 AM |
| 20 | Post payroll accrual (if payroll not yet final) | Payroll Accountant | None | Day 3 AM |
| 21 | Post FX revaluation entries | Senior Accountant | Phase 1 | Day 3 AM |
| 22 | Reclassify misposted entries | Senior Accountant | Phase 1 | Day 3 PM |
| 23 | Post intercompany elimination entries | Senior Accountant | Task 12 | Day 3 PM |
| 24 | Post tax provision adjustments | Tax Accountant | Tasks 13, 14 | Day 3 PM |
| 25 | Review and approve all adjusting entries | Accounting Manager | Tasks 16–24 | Day 3 PM |

## Phase 3 — Financial reporting and analysis (days 3–4)

| # | Task | Responsible | Dependency | Deadline |
|:-:|------|-------------|------------|----------|
| 26 | Generate trial balance | Senior Accountant | Task 25 | Day 3 PM |
| 27 | Generate income statement (P&L) | Senior Accountant | Task 26 | Day 4 AM |
| 28 | Generate balance sheet | Senior Accountant | Task 26 | Day 4 AM |
| 29 | Generate cash flow statement | Senior Accountant | Task 26 | Day 4 AM |
| 30 | Perform P&L variance analysis (vs. budget) | Financial Analyst | Task 27 | Day 4 AM |
| 31 | Perform P&L variance analysis (vs. prior period) | Financial Analyst | Task 27 | Day 4 AM |
| 32 | Perform balance sheet flux analysis | Financial Analyst | Task 28 | Day 4 PM |
| 33 | Prepare management commentary / highlights | Controller | Tasks 30–32 | Day 4 PM |
| 34 | Prepare departmental P&L breakdowns | Financial Analyst | Task 27 | Day 4 PM |
| 35 | Compile financial close package | Controller | Tasks 27–34 | Day 4 PM |

## Phase 4 — Review, approval, and BIR prep (days 4–5)

| # | Task | Responsible | Dependency | Deadline |
|:-:|------|-------------|------------|----------|
| 36 | Controller review of financial package | Controller | Task 35 | Day 5 AM |
| 37 | CFO review and approval | CFO | Task 36 | Day 5 AM |
| 38 | Reconcile WHT to 1601-C form | Tax Accountant | Task 14 | Day 5 AM |
| 39 | Prepare BIR 1601-C (monthly WHT return) | Tax Accountant | Task 38 | Day 5 AM |
| 40 | Prepare BIR 0619-E (expanded WHT remittance) | Tax Accountant | Task 14 | Day 5 PM |
| 41 | Cross-check BIR forms to GL totals | Tax Accountant | Tasks 39, 40 | Day 5 PM |
| 42 | Obtain BIR form approval | Tax Manager | Task 41 | Day 5 PM |
| 43 | Lock accounting period in Odoo | Accounting Manager | Task 37 | Day 5 PM |
| 44 | Archive working papers and distribute reports | Senior Accountant | Task 43 | Day 5 PM |

---

## Approval gates

| Gate | Point in workflow | Approver | Pass criteria |
|------|-------------------|----------|---------------|
| **Reconciliation gate** | After Phase 1 | Senior Accountant | All BS accounts reconciled within tolerance |
| **Journal entry gate** | After Task 25 | Accounting Manager | All adjusting entries have supporting documentation |
| **Financial statement gate** | After Task 37 | CFO | TB ties to statements, variances explained |
| **BIR compliance gate** | After Task 42 | Tax Manager | Form totals match GL, filing deadlines met |

---

## BIR-specific tasks detail

??? info "WHT reconciliation (Task 38)"
    Reconcile the WHT payable accounts in Odoo to the amounts that will appear on BIR Form 1601-C:

    1. Export WHT journal entries for the period from `account.move.line` where tax group = WHT.
    2. Group by tax code (WI010, WI100, WI110, etc.).
    3. Compare totals to the 1601-C worksheet.
    4. Investigate and resolve differences > PHP 1.

    ```sql
    SELECT
        tax.name AS tax_code,
        SUM(aml.credit) AS total_wht
    FROM account_move_line aml
    JOIN account_tax tax ON aml.tax_line_id = tax.id
    WHERE aml.date BETWEEN '2026-03-01' AND '2026-03-31'
      AND tax.tax_group_id = (SELECT id FROM account_tax_group WHERE name = 'WHT')
    GROUP BY tax.name
    ORDER BY tax.name;
    ```

??? info "1601-C preparation (Task 39)"
    1. Pull WHT summary by payee and tax code from Odoo.
    2. Map Odoo tax codes to BIR alpha-numeric tax codes (ATC).
    3. Populate the 1601-C form via eBIRForms or the `ipai_bir_filing` module.
    4. Validate: total remittance = sum of all WHT lines.
    5. Generate BIR 2307 certificates for payees.
