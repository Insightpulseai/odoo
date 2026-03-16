# Odoo configuration guide

Step-by-step configuration for Odoo CE 19 at InsightPulse AI, covering chart of accounts, journals, taxes, finance PPM seed data, cron jobs, and integration testing. All configurations target Philippine regulatory compliance (BIR, SEC, DOLE).

## Configuration phases

| Phase | Scope | Prerequisite |
|-------|-------|-------------|
| 1. Company setup | Legal entity, currency (PHP), fiscal year | Fresh Odoo instance |
| 2. Chart of accounts | Philippine COA (1000-7999) | Company created |
| 3. Journals | Bank, sales, purchase, miscellaneous | COA loaded |
| 4. Tax configuration | VAT, EWT, withholding | Journals created |
| 5. Finance PPM seed data | Period close tasks, SLA definitions | Phases 1-4 complete |
| 6. HR and payroll | Pay structures, contribution tables | Phases 1-4 complete |
| 7. Cron jobs | Automated schedules | All modules installed |
| 8. Integration testing | End-to-end validation | All configuration complete |

## Phase 1: Company setup

Configure in **Settings > General Settings > Companies**.

| Field | Value |
|-------|-------|
| Company name | InsightPulse AI Inc. |
| Currency | PHP (Philippine Peso) |
| Fiscal year | January 1 - December 31 |
| Country | Philippines |
| Tax ID (TIN) | Set via environment variable |
| Address | Registered business address |

## Phase 2: Chart of accounts

The Philippine COA follows a 4-digit structure aligned with SEC and BIR reporting requirements.

| Range | Category | Examples |
|-------|----------|----------|
| 1000-1999 | Assets | 1010 Cash on Hand, 1020 Cash in Bank, 1100 Accounts Receivable, 1200 Inventory, 1500 Fixed Assets |
| 2000-2999 | Liabilities | 2010 Accounts Payable, 2100 Accrued Expenses, 2200 Output VAT, 2300 Withholding Tax Payable, 2500 Loans Payable |
| 3000-3999 | Equity | 3010 Capital Stock, 3100 Retained Earnings, 3200 Current Year Earnings |
| 4000-4999 | Revenue | 4010 Service Revenue, 4020 Product Revenue, 4100 Other Income |
| 5000-5999 | Cost of sales | 5010 Direct Labor, 5020 Direct Materials, 5100 Subcontractor Costs |
| 6000-6999 | Operating expenses | 6010 Salaries, 6100 Rent, 6200 Utilities, 6300 Depreciation, 6400 Professional Fees |
| 7000-7999 | Other expenses | 7010 Interest Expense, 7100 Bank Charges, 7200 Foreign Exchange Loss |

??? note "Loading the COA"
    Load the COA via the `l10n_ph` (Philippine localization) module. Customize additional accounts through `ipai_finance_ppm` seed data.

    ```bash
    # Install Philippine localization
    odoo-bin -d odoo_dev -i l10n_ph --stop-after-init
    ```

## Phase 3: Journal configuration

| Journal | Type | Code | Default debit account | Default credit account |
|---------|------|------|-----------------------|------------------------|
| Bank (BDO) | Bank | BDO | 1021 Cash in Bank - BDO | 1021 Cash in Bank - BDO |
| Bank (BPI) | Bank | BPI | 1022 Cash in Bank - BPI | 1022 Cash in Bank - BPI |
| Customer invoices | Sale | INV | 1100 Accounts Receivable | 4010 Service Revenue |
| Vendor bills | Purchase | BILL | 6000 Expenses | 2010 Accounts Payable |
| Miscellaneous | General | MISC | — | — |
| Payroll | General | PAY | 6010 Salaries Expense | 2010 Accounts Payable |
| Tax adjustments | General | TAX | — | — |
| Exchange difference | General | EXCH | 7200 FX Loss | 4200 FX Gain |

## Phase 4: Tax configuration

### Output VAT

| Tax | Rate | Account | BIR form |
|-----|------|---------|----------|
| Output VAT (Sales) | 12% | 2200 Output VAT | 2550M / 2550Q |
| Output VAT (Services) | 12% | 2200 Output VAT | 2550M / 2550Q |
| VAT-Exempt Sales | 0% | — | 2550M / 2550Q |
| Zero-Rated Sales | 0% | — | 2550M / 2550Q |

### Input VAT

| Tax | Rate | Account | BIR form |
|-----|------|---------|----------|
| Input VAT (Purchases) | 12% | 1300 Input VAT | 2550M / 2550Q |
| Input VAT (Services) | 12% | 1300 Input VAT | 2550M / 2550Q |
| Input VAT (Capital Goods) | 12% | 1301 Input VAT - Capital Goods | 2550M / 2550Q |

### Expanded withholding tax (EWT)

| Tax code | Description | Rate | Account | BIR form |
|----------|-------------|------|---------|----------|
| WC010 | Professional fees (individual) | 5% / 10% | 2310 EWT Payable | 1601-EQ |
| WC020 | Professional fees (corporate) | 10% / 15% | 2310 EWT Payable | 1601-EQ |
| WC100 | Rental - real property | 5% | 2310 EWT Payable | 1601-EQ |
| WC120 | Rental - personal property | 2% | 2310 EWT Payable | 1601-EQ |
| WC140 | Contractor services | 2% | 2310 EWT Payable | 1601-EQ |
| WC160 | Purchase of goods | 1% | 2310 EWT Payable | 1601-EQ |

!!! info "EWT rate selection"
    The applicable EWT rate depends on the vendor's income threshold. Configure vendor-level default taxes in the partner record for automation.

## Phase 5: Finance PPM seed data

The `ipai_finance_ppm` module provides seed data for period close management.

### Close task templates

| Task | Department | SLA (business days) | Sequence |
|------|-----------|---------------------|----------|
| AP cutoff and accrual | Finance | Day 2 | 10 |
| AR cutoff and reconciliation | Finance | Day 2 | 20 |
| Bank reconciliation | Finance | Day 3 | 30 |
| Payroll posting | HR / Finance | Day 3 | 40 |
| Fixed asset depreciation | Finance | Day 3 | 50 |
| Intercompany reconciliation | Finance | Day 5 | 60 |
| Tax provision computation | Tax | Day 7 | 70 |
| Adjusting journal entries | Finance | Day 8 | 80 |
| Trial balance review | Finance Manager | Day 9 | 90 |
| Financial statement generation | Finance Manager | Day 10 | 100 |

### SLA definitions

| Priority | Response time | Resolution time | Escalation |
|----------|-------------|-----------------|------------|
| Critical (SLA breach) | Immediate | 4 hours | Finance Director |
| High (at risk) | 2 hours | 1 business day | Finance Manager |
| Normal | 4 hours | 2 business days | Team lead |

## Phase 6: HR and payroll

See [HR processes](../hr-processes/index.md) for detailed payroll configuration including:

- Pay structures and salary rules
- Government contribution tables (SSS, PhilHealth, Pag-IBIG)
- BIR withholding tax tables
- 13th month pay computation

## Phase 7: Cron jobs

| Cron job | Model | Interval | Time | Purpose |
|----------|-------|----------|------|---------|
| Bank statement import | `account.bank.statement.import` | Daily | 06:00 | Fetch bank transactions |
| Payment reminder | `account.move` | Daily | 09:00 | Send overdue payment reminders |
| Leave accrual | `hr.leave.allocation` | Monthly | Day 1, 01:00 | Accrue monthly leave credits |
| Depreciation posting | `account.asset` | Monthly | Day 1, 02:00 | Post depreciation entries |
| VAT computation | `account.tax.report` | Monthly | Day 5, 03:00 | Compute monthly VAT |
| Clearance SLA check | `hr.clearance` | Daily | 08:00 | Alert on approaching SLA breach |
| PPM task generation | `finance.close.period` | Monthly | Day 1, 00:00 | Generate month-end close tasks |

## Phase 8: Integration testing

### Test cases

| # | Test case | Steps | Expected result |
|---|-----------|-------|-----------------|
| 1 | Customer invoice with VAT | Create invoice, validate, check tax lines | 12% Output VAT line created, correct account |
| 2 | Vendor bill with EWT | Create bill, apply EWT, validate | EWT withheld, net payable correct |
| 3 | Payment with bank reconciliation | Record payment, import statement, reconcile | Payment matched, zero balance |
| 4 | Payroll run | Process payslip, validate, post to journal | Salary expense and liability entries correct |
| 5 | Month-end close | Run all close tasks, generate trial balance | All tasks complete, TB balanced |
| 6 | BIR 2550M generation | Run VAT report for month | Output - Input VAT = Net VAT payable |
| 7 | Final pay computation | Process separation, compute final pay | All components computed per formula |
| 8 | Asset depreciation | Create asset, run monthly depreciation | Depreciation entry posted, NBV updated |

## Troubleshooting

### Installation issues

| Problem | Cause | Solution |
|---------|-------|----------|
| `l10n_ph` not found | Module not in addons path | Verify `addons_path` in `odoo.conf` includes the localization directory |
| `ipai_finance_ppm` dependency error | Missing OCA modules | Install OCA dependencies first: `account_fiscal_month`, `account_fiscal_year` |
| Database migration error | Version mismatch | Run with `--update` flag: `odoo-bin -d odoo_dev -u ipai_finance_ppm --stop-after-init` |

### Configuration issues

| Problem | Cause | Solution |
|---------|-------|----------|
| Tax not applied on invoice | Tax not set on product or partner | Configure default taxes on product category or partner record |
| Wrong EWT rate | Vendor threshold not configured | Set vendor income threshold in partner form |
| Journal entry imbalance | Rounding on multi-currency | Enable automatic rounding in currency settings |

### Performance issues

| Problem | Cause | Solution |
|---------|-------|----------|
| Slow report generation | Large dataset without indexing | Add database indexes on `account_move_line.date` and `account_move_line.account_id` |
| Payroll batch timeout | Too many employees in single batch | Split into department-level batches |
| Bank reconciliation slow | Unreconciled items accumulation | Run reconciliation monthly, do not let items accumulate |
