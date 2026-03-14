# Monthly close runbook

Step-by-step execution guide for the 5-day monthly close. Follow this sequence day by day. For the full task checklist, see the [month-end task template](month-end-tasks.md).

---

## Pre-close checklist (day -1 to day 0)

Complete before the close period begins.

- [ ] Verify Odoo period is open (`Accounting > Configuration > Settings > Lock Date`)
- [ ] Confirm all users have appropriate access for close activities
- [ ] Retrieve bank statements for all accounts (PDF + OFX/MT940)
- [ ] Confirm AP cut-off communicated — no new vendor invoices for prior period
- [ ] Confirm AR cut-off communicated — all customer invoices posted
- [ ] Verify scheduled actions (depreciation, recurring entries) are enabled
- [ ] Generate preliminary trial balance — flag anomalies early

!!! tip "System readiness check"
    Run the following to verify no draft entries remain from the prior close:

    ```sql
    SELECT COUNT(*) AS draft_entries
    FROM account_move
    WHERE state = 'draft'
      AND date < DATE_TRUNC('month', CURRENT_DATE);
    ```

    If count > 0, investigate and post or cancel before proceeding.

---

## Day 1 — Transaction cut-off and bank reconciliation

### Transaction cut-off

1. Lock AR/AP for the closing period — set the lock date for non-advisers to the period end date.
2. Verify all bank transactions are imported.
3. Post any pending journal entries dated within the period.

### Bank reconciliation

1. **Import statements**: Upload OFX/MT940 files or use automated bank feeds.

    ```
    Accounting > Dashboard > [Bank Journal] > Import
    ```

2. **Auto-reconciliation**: Run the OCA auto-reconciliation engine.

    ```python
    # Trigger via scheduled action or manually:
    env['account.reconcile.model'].search([]).action_reconcile()
    ```

3. **Manual exceptions**: Review unmatched items in the reconciliation widget.

    | Exception type | Action |
    |----------------|--------|
    | Partial match | Split and match remaining amount |
    | No match — known item | Create journal entry and match |
    | No match — unknown item | Flag for investigation, do not write off without approval |
    | Stale items (> 90 days) | Escalate to Accounting Manager for write-off decision |

4. **Write-off approval**: Any write-offs require Accounting Manager sign-off before posting.

5. **Reconciliation report**: Generate and save to working papers.

---

## Day 2 — GL reconciliation

### Balance sheet account reconciliation

Reconcile every balance sheet account to its supporting detail.

| Account group | Source of detail | Tolerance |
|---------------|------------------|-----------|
| Cash and banks | Bank statements | PHP 0 (must tie exactly) |
| Accounts receivable | AR aging report | PHP 0 (sub-ledger must tie to GL) |
| Accounts payable | AP aging report | PHP 0 (sub-ledger must tie to GL) |
| Inventory | Inventory valuation report | 1% of balance |
| Fixed assets | Asset register | PHP 0 |
| Prepayments | Amortization schedule | PHP 0 |
| VAT payable/input | Tax detail report | PHP 1 |
| WHT payable | WHT detail report | PHP 1 |
| Intercompany | Counterparty confirmation | PHP 0 |

### AR/AP aging review

```sql
-- AR aging summary
SELECT
    CASE
        WHEN date_maturity >= CURRENT_DATE THEN 'Current'
        WHEN date_maturity >= CURRENT_DATE - 30 THEN '1-30 days'
        WHEN date_maturity >= CURRENT_DATE - 60 THEN '31-60 days'
        WHEN date_maturity >= CURRENT_DATE - 90 THEN '61-90 days'
        ELSE '90+ days'
    END AS aging_bucket,
    SUM(amount_residual) AS balance
FROM account_move_line
WHERE account_id IN (SELECT id FROM account_account WHERE account_type = 'asset_receivable')
  AND reconciled = FALSE
GROUP BY 1
ORDER BY 1;
```

### VAT and WHT reconciliation

1. Export VAT input and output totals from `account.move.line` filtered by tax group.
2. Reconcile to the VAT returns filed (2550M/2550Q).
3. Export WHT payable totals grouped by ATC (alpha-numeric tax code).
4. Reconcile to 1601-C filed amounts.

---

## Day 3 — Accruals and adjustments

### Expense accruals

Post accrual entries for expenses incurred but not yet invoiced:

- Utilities (electricity, water, telecom)
- Professional services (legal, audit, consulting)
- Rent (if not on straight-line lease)
- Payroll-related (13th month, unused leave)

??? example "Accrual journal entry template"
    ```
    Debit:  6xxxx - [Expense account]      PHP X,XXX.XX
    Credit: 2xxxx - Accrued expenses        PHP X,XXX.XX
    Reference: Accrual - [Vendor/Description] - [Period]
    ```

### Revenue accruals

Post accrual entries for revenue earned but not yet invoiced (unbilled revenue).

### Prepayment deferrals

Run the prepayment amortization scheduled action or manually post:

1. Review prepayment schedules for the period.
2. Post amortization entries (debit expense, credit prepaid asset).
3. Verify remaining prepaid balance matches the schedule.

### Depreciation

1. Verify the depreciation scheduled action ran for the period.
2. Spot-check 3–5 assets to confirm correct calculation.
3. Verify accumulated depreciation ties to the asset register.

```python
# Verify depreciation was computed for the period
moves = env['account.move'].search([
    ('asset_id', '!=', False),
    ('date', '>=', '2026-03-01'),
    ('date', '<=', '2026-03-31'),
    ('state', '=', 'posted'),
])
print(f"Depreciation entries posted: {len(moves)}")
```

### FX revaluation

If the company holds foreign currency balances, post FX revaluation using the month-end exchange rate from BSP (Bangko Sentral ng Pilipinas).

---

## Day 4 — Review and approval

### Trial balance validation

1. Generate the trial balance as of period end.
2. Compare to prior month — flag lines with variance > 5% or > PHP 100,000.
3. Document explanations for all flagged variances.

| Variance threshold | Action required |
|--------------------|-----------------|
| < 5% and < PHP 100,000 | No explanation needed |
| 5–10% or PHP 100,000–500,000 | Brief explanation in close notes |
| > 10% or > PHP 500,000 | Detailed explanation + supporting evidence |

### Approval workflow

1. Senior Accountant signs off on reconciliations (Gate 1).
2. Accounting Manager signs off on journal entries (Gate 2).
3. Controller/CFO signs off on financial statements (Gate 3).
4. Tax Manager signs off on BIR forms (Gate 4).

!!! warning "Do not proceed to period lock without all 4 gate approvals."

---

## Day 5 — Period lock

### Pre-lock validation

- [ ] All reconciliation exceptions resolved or documented
- [ ] All adjusting entries posted and approved
- [ ] Trial balance ties to financial statements
- [ ] BIR forms prepared and validated
- [ ] No draft journal entries remain in the period

### Lock execution

1. Set the lock date for all users:

    ```
    Accounting > Configuration > Settings > Fiscal Period Lock Date
    ```

2. Set the tax lock date (prevents modification of tax-affecting entries):

    ```
    Accounting > Configuration > Settings > Tax Lock Date
    ```

3. Verify the lock is effective — attempt to post a test entry (it should be rejected).

### Archive and backup

1. Export the trial balance, financial statements, and reconciliation reports as PDF.
2. Save to the period folder: `finance/close/YYYY-MM/`.
3. Back up the Odoo database.

    ```bash
    pg_dump -Fc odoo > /backups/odoo_close_$(date +%Y%m).dump
    ```

---

## Post-close

### Stakeholder notification

Send the financial close package to:

- CFO and executive team
- Department heads (with departmental P&L)
- Board (quarterly/annually)

### Lessons learned

Document in the close tracker:

1. What delayed the close?
2. What manual steps can be automated next cycle?
3. Were any reconciliation tolerances exceeded?

---

## Troubleshooting

??? warning "Bank reconciliation does not balance"
    **Symptoms**: Bank statement balance does not match Odoo bank GL balance.

    **Check**:

    1. Verify all bank statements for the period are imported.
    2. Check for duplicate imports (`account.bank.statement` with overlapping dates).
    3. Look for unposted bank statement lines.
    4. Verify opening balance matches prior period closing balance.

    ```sql
    SELECT statement_date, balance_start, balance_end_real
    FROM account_bank_statement
    WHERE journal_id = [BANK_JOURNAL_ID]
    ORDER BY statement_date DESC
    LIMIT 5;
    ```

??? warning "Trial balance does not tie to sub-ledgers"
    **Symptoms**: GL balance for AR/AP differs from aging report totals.

    **Check**:

    1. Look for journal entries posted directly to the receivable/payable account (bypassing the invoice workflow).
    2. Check for partially reconciled items.
    3. Verify no entries are posted to the account after the reporting date.

??? warning "Period lock date not working"
    **Symptoms**: Users can still post entries in a locked period.

    **Check**:

    1. Verify the user does not have the "Adviser" role (advisers bypass non-adviser lock dates).
    2. Check that both the fiscal lock date and tax lock date are set.
    3. Verify the lock date is set to the last day of the period (not the first day of the next period).

??? warning "Depreciation entries missing"
    **Symptoms**: No depreciation journal entries for the period.

    **Check**:

    1. Verify the depreciation scheduled action (`ir.cron`) is active.
    2. Check that assets have the correct depreciation method and start date.
    3. Run depreciation manually: `Asset > Compute Depreciation`.
