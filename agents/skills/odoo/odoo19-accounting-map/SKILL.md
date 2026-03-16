# Skill: Odoo 19 Accounting — Full Feature Map

## Metadata

| Field | Value |
|-------|-------|
| **id** | `odoo19-accounting-map` |
| **domain** | `odoo_ce` |
| **source** | https://www.odoo.com/documentation/19.0/applications/finance/accounting.html |
| **extracted** | 2026-03-15 |
| **applies_to** | odoo, agents |
| **tags** | accounting, finance, tax, invoicing, bank, reconciliation, reporting, budget |

---

## Documentation Structure (76 pages)

### 1. Get Started (7 pages)

| Page | Path | IPAI Relevance |
|------|------|---------------|
| Cheat sheet | `get_started/cheat_sheet.html` | Reference for agent prompts |
| Chart of accounts | `get_started/chart_of_accounts.html` | **Critical** — PH CoA setup |
| Consolidation | `get_started/consolidation.html` | Multi-company |
| Journals | `get_started/journals.html` | **Critical** — journal config |
| Multi-currency | `get_started/multi_currency.html` | PHP + USD handling |
| Avg price on returns | `get_started/avg_price_valuation.html` | Inventory costing |
| Tax units | `get_started/tax_units.html` | BIR tax unit mapping |

### 2. Taxes (10 pages)

| Page | Path | IPAI Relevance |
|------|------|---------------|
| Tax overview | `taxes.html` | **Critical** — BIR tax setup |
| Cash basis taxes | `taxes/cash_basis.html` | PH cash basis requirement |
| Tax computation | `taxes/tax_computation.html` | VAT/withholding calculation |
| **Withholding taxes** | `taxes/retention.html` | **Critical** — BIR EWT/FWT |
| VAT verification (VIES) | `taxes/vat_verification.html` | EU only — skip |
| Fiscal positions | `taxes/fiscal_positions.html` | **Critical** — PH tax mapping |
| AvaTax | `taxes/avatax.html` | US only — skip |
| EU distance selling | `taxes/eu_distance_selling.html` | EU only — skip |
| B2B/B2C pricing | `taxes/B2B_B2C.html` | Tax-inclusive pricing |

### 3. Customer Invoices (14 pages)

| Page | Path | IPAI Relevance |
|------|------|---------------|
| Invoicing processes | `customer_invoices/overview.html` | **Critical** — AR workflow |
| Payment terms | `customer_invoices/payment_terms.html` | **Critical** — PH terms |
| Credit notes/refunds | `customer_invoices/credit_notes.html` | Return processing |
| Cash discounts | `customer_invoices/cash_discounts.html` | Early payment discount |
| Deferred revenues | `customer_invoices/deferred_revenues.html` | Revenue recognition |
| **Electronic invoicing** | `customer_invoices/electronic_invoicing.html` | BIR e-invoicing compliance |
| Invoice sequence | `customer_invoices/sequence.html` | BIR numbering rules |
| Cash rounding | `customer_invoices/cash_rounding.html` | PH centavo rounding |
| Delivery/invoice addresses | `customer_invoices/customer_addresses.html` | Multi-address |
| Terms & conditions | `customer_invoices/terms_conditions.html` | Standard terms |
| Incoterms | `customer_invoices/incoterms.html` | Import/export |
| EPC QR codes | `customer_invoices/epc_qr_code.html` | Payment QR |
| Snailmail | `customer_invoices/snailmail.html` | Physical mail — skip |

### 4. Vendor Bills (4 pages)

| Page | Path | IPAI Relevance |
|------|------|---------------|
| Vendor bills overview | `vendor_bills.html` | **Critical** — AP workflow |
| **Document digitization** | `vendor_bills/invoice_digitization.html` | IAP OCR → replace with ADE/DI |
| Fixed assets | `vendor_bills/assets.html` | Asset management |
| Deferred expenses | `vendor_bills/deferred_expenses.html` | Prepaid expenses |

### 5. Payments (9 pages)

| Page | Path | IPAI Relevance |
|------|------|---------------|
| Payments overview | `payments.html` | **Critical** — payment workflow |
| Online payments | `payments/online.html` | Payment gateway |
| Batch payments | `payments/batch.html` | **Critical** — bulk vendor payment |
| SEPA Direct Debit | `payments/batch_sdd.html` | EU only — skip |
| **Follow-up on invoices** | `payments/follow_up.html` | **Critical** — AR collection |
| Pay with SEPA | `payments/pay_sepa.html` | EU only — skip |
| Pay by checks | `payments/pay_checks.html` | Check printing |
| Forecast bills | `payments/forecast.html` | Cash flow forecast |
| Trusted accounts | `payments/trusted_accounts.html` | Wire transfer security |

### 6. Bank & Cash (8 pages)

| Page | Path | IPAI Relevance |
|------|------|---------------|
| Bank overview | `bank.html` | **Critical** — bank config |
| Bank synchronization | `bank/bank_synchronization.html` | Auto bank feeds |
| Ponto integration | `bank/bank_synchronization/ponto.html` | EU only — skip |
| Transactions | `bank/transactions.html` | Transaction management |
| **Bank reconciliation** | `bank/reconciliation.html` | **Critical** — daily recon |
| Reconciliation models | `bank/reconciliation_models.html` | Auto-match rules |
| Internal transfers | `bank/internal_transfers.html` | Inter-account transfers |
| Foreign currency | `bank/foreign_currency.html` | PHP/USD accounts |
| Loans | `bank/loans.html` | Loan tracking |

### 7. Reporting (10 pages)

| Page | Path | IPAI Relevance |
|------|------|---------------|
| Reporting overview | `reporting.html` | **Critical** — financial reports |
| **Tax return (VAT)** | `reporting/tax_returns.html` | **Critical** — BIR VAT return |
| Tax carryover | `reporting/tax_carryover.html` | Tax loss carryforward |
| **Analytic accounting** | `reporting/analytic_accounting.html` | **Critical** — cost centers |
| **Budget** | `reporting/budget.html` | **Critical** — budget management |
| Intrastat | `reporting/intrastat.html` | EU only — skip |
| Data inalterability | `reporting/data_inalterability.html` | Audit trail |
| Silverfin | `reporting/silverfin.html` | External integration — skip |
| Custom reports | `reporting/customize.html` | Report builder |
| **Year-end closing** | `reporting/year_end.html` | **Critical** — annual close |

## Priority Pages for Agent Knowledge

The following 20 pages are **critical** for IPAI's Odoo accounting agent:

```
1.  get_started/chart_of_accounts.html      # PH chart of accounts
2.  get_started/journals.html               # Journal configuration
3.  taxes.html                              # Tax system overview
4.  taxes/retention.html                    # Withholding taxes (BIR EWT/FWT)
5.  taxes/fiscal_positions.html             # Tax mapping per vendor/customer type
6.  customer_invoices/overview.html         # AR invoicing workflow
7.  customer_invoices/payment_terms.html    # Payment term setup
8.  customer_invoices/electronic_invoicing.html  # BIR e-invoicing
9.  vendor_bills.html                       # AP vendor bill workflow
10. vendor_bills/invoice_digitization.html  # OCR → vendor bill (replace IAP)
11. payments.html                           # Payment processing
12. payments/batch.html                     # Bulk vendor payments
13. payments/follow_up.html                 # AR collections
14. bank.html                               # Bank account setup
15. bank/reconciliation.html                # Daily bank reconciliation
16. bank/reconciliation_models.html         # Auto-match rules
17. reporting/tax_returns.html              # BIR VAT return
18. reporting/analytic_accounting.html      # Cost center tracking
19. reporting/budget.html                   # Budget vs actual
20. reporting/year_end.html                 # Annual closing procedure
```

## OCA Modules for Accounting (Must-Have)

| Module | Repo | Purpose | Manifest Tier |
|--------|------|---------|---------------|
| `account_reconcile_oca` | account-reconcile | Reconciliation engine | 0 |
| `account_financial_report` | account-financial-reporting | Financial statements | 0 |
| `mis_builder` | mis-builder | Management reporting | 0 |
| `account_asset_management` | account-financial-tools | Fixed assets | 0 |
| `account_move_budget` | account-financial-tools | Budget entries | 1 |
| `account_move_fiscal_year_closing` | account-financial-tools | Year-end close | 1 |
| `account_tax_balance` | account-financial-reporting | Tax balance report | 1 |
| `account_journal_lock_date` | account-financial-tools | Period locking | 1 |
| `account_move_name_sequence` | account-financial-tools | Invoice numbering | 1 |
| `account_payment_partner` | account-payment | Partner payment info | 1 |
| `account_invoice_refund_link` | account-invoicing | Credit note linking | 2 |
| `account_lock_date_update` | account-financial-tools | Lock date management | 2 |
| `account_spread_cost_revenue` | account-financial-tools | Amortization | 2 |
| `currency_rate_update` | account-financial-tools | Auto FX rates | 0 |

## Automation Opportunities

| Process | Current | Target | Tool |
|---------|---------|--------|------|
| Vendor bill entry | Manual | ADE/DI OCR → `account.move` | n8n + ADE |
| Bank reconciliation | Manual matching | Auto-match with reconciliation models | OCA module config |
| AR follow-up | Manual emails | Automated follow-up levels | Odoo native + n8n |
| Month-end close | Manual checklist | Agent-driven close workflow | Close agent skill |
| Tax filing | Manual BIR forms | ADE extract + auto-file | BIR automation skill |
| Budget monitoring | Periodic review | Real-time Superset dashboard | MIS Builder + ETL |

## Agent Knowledge Ingestion Plan

To make the Odoo copilot effective on accounting topics:

1. **Index the 20 critical pages** into Azure AI Search (Foundry IQ knowledge source)
2. **Add PH-specific context**: BIR rules, withholding tax rates, VAT thresholds
3. **Include OCA module docs**: For each must-have module, index README + usage guide
4. **Train eval dataset**: 20 accounting questions with ground truth answers
5. **Run cloud eval**: Task adherence + groundedness against indexed knowledge
