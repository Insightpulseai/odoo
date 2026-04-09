# Domain Primer: Finance & Accounting

## One-paragraph summary

Finance & Accounting is the backbone of enterprise ERP. Every business transaction eventually becomes a financial posting. The discipline encompasses general ledger management, accounts payable/receivable, bank reconciliation, fixed assets, tax compliance, and financial reporting. In SAP terms, this maps to FI (Financial Accounting) and CO (Controlling). In Odoo, the `account` module family handles most of this, extended by OCA modules for enterprise-grade features.

## Key Concepts

| Concept | Definition | Odoo Model |
|---------|-----------|------------|
| Double-entry bookkeeping | Every transaction has equal debits and credits | account.move.line |
| Chart of accounts | Hierarchical list of GL accounts | account.account |
| Journal | Categorized posting book (sales, purchase, bank, misc) | account.journal |
| Fiscal year/period | Reporting time boundaries | date_range (OCA) |
| Reconciliation | Matching transactions to clear open items | account.reconcile.model |
| Analytic accounting | Cost/revenue tracking by business dimension | account.analytic.account |

## Core Processes

1. **Record-to-Report (R2R)**: Transaction → posting → reconciliation → period close → financial statements
2. **Procure-to-Pay (P2P)**: Requisition → PO → receipt → vendor bill → payment
3. **Order-to-Cash (O2C)**: Quote → sales order → delivery → customer invoice → payment collection

## SAP-to-Odoo Quick Map

| SAP | Odoo |
|-----|------|
| Company Code (BUKRS) | res.company |
| GL Account (SKA1) | account.account |
| Document Type | account.journal |
| FI Document (BKPF) | account.move |
| Cost Center | account.analytic.account (with plan) |
| Profit Center | account.analytic.account (with plan) |

## OCA Modules to Know

- `account_financial_report`: Trial balance, BS, P&L, aged partner balance
- `account_payment_order`: Batch payment processing
- `account_payment_mode`: Payment method configuration
- `mis_builder`: Management Information System reporting
- `account_asset_management`: Fixed asset lifecycle
- `account_reconcile_*`: Enhanced reconciliation

## What "SAP-grade" Means Here

- Real-time posting (no batch delays)
- Period controls (lock dates enforced)
- Multi-company with intercompany elimination
- Audit trail on every financial record
- Automated reconciliation with exception handling
- Regulatory reporting ready (BIR for PH)
