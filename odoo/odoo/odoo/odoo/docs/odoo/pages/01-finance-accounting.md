# Finance & Accounting Overview – InsightPulseAI Edition

**Module:** `account`, `hr_expense`, `ipai_expense`, `ipai_finance_ppm`
**Domain:** Finance
**Owner Engine:** TE-Cheq (Travel & Expense)
**Last Updated:** 2025-12-07

---

## 1. Overview & Purpose

The Finance workspace in InsightPulseAI provides comprehensive accounting and expense management capabilities built on Odoo 18 CE with OCA enhancements. This module handles:

- **Double-entry bookkeeping** for all financial transactions
- **Customer invoicing** and accounts receivable management
- **Vendor bills** and accounts payable processing
- **Expense management** with TE-Cheq integration
- **Bank reconciliation** with AI-assisted matching
- **Month-end close** workflows

### Key Differentiators from Stock Odoo

| Feature | Stock Odoo | InsightPulseAI Stack |
|---------|------------|----------------------|
| Online Payments | Enterprise (Stripe, PayPal) | External payment providers via n8n |
| Document Management | Enterprise `documents` | Supabase `doc.*` + Notion |
| Approval Workflows | Enterprise `approvals` | n8n workflows + Mattermost |
| Analytics Dashboards | Enterprise Spreadsheet | Apache Superset |
| AI Reconciliation | Not available | E3 Intelligence Engine |
| Multi-tenant | Basic multi-company | Supabase RLS + tenant_id |

---

## 2. Related Domain Engine(s)

| Engine | Role |
|--------|------|
| **TE-Cheq** | Primary owner - expense management, travel requests |
| **E1 Data Intake** | Receipt OCR and document parsing |
| **E3 Intelligence** | AI-assisted bank reconciliation |

---

## 3. Data Models

### 3.1 Core Odoo Models

| Model | Description | Key Fields |
|-------|-------------|------------|
| `account.move` | Journal entries, invoices, bills | `move_type`, `partner_id`, `amount_total`, `state` |
| `account.move.line` | Journal entry lines | `account_id`, `debit`, `credit`, `analytic_account_id` |
| `account.account` | Chart of accounts | `code`, `name`, `account_type`, `reconcile` |
| `account.journal` | Journals (Sales, Purchase, Bank, etc.) | `type`, `code`, `default_account_id` |
| `account.payment` | Payment records | `payment_type`, `partner_type`, `amount` |
| `account.bank.statement` | Bank statements | `date`, `balance_start`, `balance_end_real` |
| `hr.expense` | Individual expenses | `product_id`, `total_amount`, `employee_id`, `sheet_id` |
| `hr.expense.sheet` | Expense reports | `employee_id`, `state`, `total_amount` |

### 3.2 Custom IPAI Models

| Model | Module | Description |
|-------|--------|-------------|
| `ipai.cash.advance` | `ipai_cash_advance` | Cash advance requests and liquidations |
| `ipai.expense.category.ph` | `ipai_expense` | PH-specific expense categories |
| `ipai.monthly.closing` | `ipai_finance_monthly_closing` | Month-end close tracking |

### 3.3 Tenant Isolation

All financial data flows to Supabase with `tenant_id` for multi-tenant isolation:

```sql
-- Supabase table example
CREATE TABLE finance.invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id),
    odoo_id INTEGER NOT NULL,
    move_type VARCHAR(20),
    partner_id UUID,
    amount_total DECIMAL(15,2),
    state VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT unique_tenant_odoo UNIQUE (tenant_id, odoo_id)
);

-- RLS Policy
CREATE POLICY tenant_isolation ON finance.invoices
    FOR ALL USING (tenant_id = core.current_tenant_id());
```

---

## 4. User Roles & Permissions

| Role | Odoo Group | Supabase Role | Permissions |
|------|------------|---------------|-------------|
| Finance Director | `account.group_account_manager` | `finance_director` | Full accounting access, close periods |
| Accountant | `account.group_account_user` | `teq_approver` | Post entries, approve expenses |
| Invoice Clerk | `account.group_account_invoice` | `teq_employee` | Create/edit invoices only |
| Employee | `hr_expense.group_hr_expense_user` | `teq_employee` | Submit own expenses |
| Auditor | `account.group_account_readonly` | `readonly` | View-only access |

---

## 5. Key Workflows

### 5.1 Customer Invoicing Workflow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  1. Create  │────▶│  2. Confirm │────▶│  3. Send    │────▶│  4. Payment │
│   Invoice   │     │   (Post)    │     │   to Cust   │     │   Received  │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
     Draft            Posted            Invoiced           Paid
```

**Step-by-Step:**

1. **Create Invoice** (Odoo)
   - Navigate to: Accounting > Customers > Invoices > Create
   - Select customer (`res.partner`)
   - Add invoice lines with products/services
   - Set payment terms
   - Save as draft

2. **Confirm Invoice** (Odoo)
   - Click "Confirm" to post the journal entry
   - System auto-generates:
     - Debit: Accounts Receivable
     - Credit: Revenue account(s)
   - **Triggers:** `wf_invoice_sync` (n8n → Supabase)

3. **Send to Customer** (Odoo + n8n)
   - Click "Send by Email" or "Print"
   - n8n can trigger additional notifications via Mattermost

4. **Register Payment** (Odoo)
   - Click "Register Payment"
   - Select payment method and journal
   - System auto-reconciles with invoice
   - **Triggers:** `wf_payment_sync` (n8n → Supabase)

### 5.2 Expense Report Workflow (TE-Cheq)

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  1. Create  │────▶│  2. Submit  │────▶│  3. Approve │────▶│  4. Post    │────▶│  5. Pay     │
│  Expenses   │     │   Report    │     │   (Mgr)     │     │  (Finance)  │     │   Employee  │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
     Draft            Submitted          Approved           Posted            Done
```

**Step-by-Step:**

1. **Create Expense Lines** (Odoo Mobile/Web)
   - Navigate to: Expenses > My Expenses > Create
   - Upload receipt (OCR via E1 Data Intake)
   - Select category, enter amount
   - Attach to project (analytic account) if applicable

2. **Submit Report** (Odoo)
   - Click "Create Report" from expense lines
   - Add description and submit
   - **Triggers:** `wf_expense_submitted` (n8n)
   - **Notification:** Manager notified via Mattermost

3. **Manager Approval** (n8n + Mattermost)
   - Manager receives approval request in Mattermost
   - Can approve/reject with comment
   - n8n updates Odoo via API
   - **Triggers:** `wf_expense_approval`

4. **Finance Posting** (Odoo)
   - Finance team reviews approved reports
   - Posts to journal (creates `account.move`)
   - **Triggers:** `wf_expense_posted` (n8n → Supabase)

5. **Payment** (Odoo)
   - Create payment batch for approved expenses
   - Mark as paid
   - **Triggers:** `wf_expense_paid`

### 5.3 Bank Reconciliation Workflow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  1. Import  │────▶│  2. AI Match│────▶│  3. Manual  │────▶│  4. Validate│
│  Statement  │     │             │     │   Review    │     │             │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

**Step-by-Step:**

1. **Import Bank Statement** (Odoo)
   - Navigate to: Accounting > Dashboard > Bank Journal
   - Click "Import Statement" (CSV, OFX, CAMT)
   - Or use `wf_bank_statement_import` for automated feeds

2. **AI-Assisted Matching** (E3 Intelligence)
   - System auto-matches based on:
     - Amount matching
     - Partner reference
     - Historical patterns
   - AI suggests matches for ambiguous items
   - **Confidence scores** displayed for each suggestion

3. **Manual Review** (Odoo)
   - Review AI suggestions
   - Manually match/create entries as needed
   - Flag items for investigation

4. **Validate** (Odoo)
   - Click "Validate" to confirm all matches
   - Creates reconciliation entries
   - **Triggers:** `wf_reconciliation_complete`

### 5.4 Month-End Close Workflow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  1. Checklist│────▶│  2. Accrue │────▶│  3. Review  │────▶│  4. Close   │
│   Review    │     │  & Adjust   │     │   Reports   │     │   Period    │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

**Automated via n8n:** `wf_month_end_checklist`

**Checklist Items:**
- [ ] All bank statements reconciled
- [ ] All expense reports posted
- [ ] All invoices for period created
- [ ] Accruals and adjustments posted
- [ ] Trial balance reviewed
- [ ] P&L and Balance Sheet generated
- [ ] Period closed (lock date set)

---

## 6. Integrations

### 6.1 Supabase Tables/Views

| Supabase Table | Source Odoo Model | Sync Direction | Frequency |
|----------------|-------------------|----------------|-----------|
| `finance.invoices` | `account.move` (out_invoice) | Odoo → Supabase | Real-time |
| `finance.vendor_bills` | `account.move` (in_invoice) | Odoo → Supabase | Real-time |
| `finance.payments` | `account.payment` | Odoo → Supabase | Real-time |
| `finance.journal_entries` | `account.move.line` | Odoo → Supabase | Nightly |
| `finance.chart_of_accounts` | `account.account` | Odoo → Supabase | On change |
| `expense.expense_reports` | `hr.expense.sheet` | Odoo → Supabase | Real-time |
| `expense.expenses` | `hr.expense` | Odoo → Supabase | Real-time |
| `expense.cash_advances` | `ipai.cash.advance` | Odoo → Supabase | Real-time |

### 6.2 n8n Workflows

| Workflow ID | Trigger | Action | Target |
|-------------|---------|--------|--------|
| `wf_invoice_sync` | Invoice posted | Sync to Supabase | `finance.invoices` |
| `wf_payment_sync` | Payment registered | Sync to Supabase | `finance.payments` |
| `wf_expense_submitted` | Report submitted | Notify manager | Mattermost |
| `wf_expense_approval` | Mattermost action | Update Odoo state | `hr.expense.sheet` |
| `wf_expense_posted` | Report posted | Sync to Supabase | `expense.*` |
| `wf_bank_statement_import` | Daily 6am | Import bank feeds | Odoo bank journal |
| `wf_reconciliation_assist` | Statement imported | AI matching | E3 Intelligence |
| `wf_month_end_checklist` | 1st of month | Generate checklist | Mattermost |
| `wf_fx_rate_update` | Daily 8am | Update FX rates | `res.currency.rate` |

### 6.3 AI Agents/Tools

| Agent | Capability | Use Case |
|-------|------------|----------|
| **Finance Coach** | Query financial data | "What's our AR aging?" |
| **Reconciliation Assistant** | AI matching suggestions | Bank statement reconciliation |
| **Expense Validator** | Policy compliance check | Flag out-of-policy expenses |
| **Close Assistant** | Month-end guidance | "What's left to close November?" |

---

## 7. Configuration Guide

### 7.1 Chart of Accounts Setup

1. **Access**: Accounting > Configuration > Chart of Accounts
2. **PH Localization**: Install `l10n_ph` module for Philippine chart
3. **Customize**:
   - Add accounts for specific needs
   - Set reconcile flag on bank/receivable/payable accounts
   - Configure analytic accounts for project tracking

### 7.2 Journal Configuration

| Journal | Type | Code | Default Account |
|---------|------|------|-----------------|
| Customer Invoices | Sale | INV | 400000 Revenue |
| Vendor Bills | Purchase | BILL | 500000 Expenses |
| Bank (BDO) | Bank | BDO | 101001 BDO Checking |
| Cash | Cash | CSH | 100100 Petty Cash |
| Miscellaneous | General | MISC | - |

### 7.3 Payment Terms

| Term | Description | Days |
|------|-------------|------|
| Immediate | Due on receipt | 0 |
| Net 15 | Due in 15 days | 15 |
| Net 30 | Due in 30 days | 30 |
| 50% Now, 50% Net 30 | Split payment | 0/30 |

### 7.4 Expense Categories (PH-Specific)

| Category | Account | Tax | Notes |
|----------|---------|-----|-------|
| Meals - Local | 620100 | VAT 12% | P150 daily limit |
| Transportation - Local | 620200 | VAT 12% | Receipt required > P25 |
| Transportation - Grab | 620200 | VAT 12% | e-Receipt auto-capture |
| Accommodation | 620300 | VAT 12% | Pre-approval required |
| Communication | 620400 | VAT 12% | Monthly cap P1,500 |
| Office Supplies | 620500 | VAT 12% | Standard |
| Professional Services | 620600 | EWT 10% | Withholding tax |

---

## 8. Reports & Analytics

### 8.1 Standard Odoo Reports

- Trial Balance
- General Ledger
- Aged Receivable
- Aged Payable
- P&L Statement
- Balance Sheet
- Cash Flow Statement

### 8.2 Superset Dashboards

| Dashboard | Location | Key Metrics |
|-----------|----------|-------------|
| Finance Overview | `/superset/dashboard/finance-overview` | Revenue, AR, AP, Cash |
| Expense Analytics | `/superset/dashboard/teq-expenses` | Spend by category, employee, project |
| Budget vs Actual | `/superset/dashboard/budget-variance` | Monthly variance analysis |
| Cash Flow Forecast | `/superset/dashboard/cash-forecast` | 90-day projection |

---

## 9. Delta from Official Odoo Docs

| Topic | Official Odoo Docs | InsightPulseAI Differences |
|-------|-------------------|---------------------------|
| Online Payments | Configure Stripe/PayPal (Enterprise) | Use external payment providers; webhook via n8n |
| Documents | Link via Documents app (Enterprise) | Store in Supabase `doc.*`; use Notion for KB |
| Approval Routing | Configure Approvals app (Enterprise) | Use n8n workflows + Mattermost |
| Spreadsheet | Use Odoo Spreadsheet (Enterprise) | Export to Superset; no Odoo BI |
| AI Features | Not available | E3 Intelligence Engine for reconciliation |
| Multi-company | Basic Odoo multi-company | Supabase RLS with tenant_id for full isolation |
| Bank Feeds | Odoo.sh bank sync (SaaS) | Custom import via `wf_bank_statement_import` |

---

## 10. Known Limitations & Phase 2+ Items

### Current Limitations

- **No automatic bank feeds**: Manual import or n8n-scheduled import
- **Limited mobile expense capture**: Web-based only; mobile app planned
- **No integrated e-signatures**: Use external DocuSign

### Phase 2 Roadmap

- [ ] Mobile expense capture app (Flutter)
- [ ] PH bank API integration (BDO, BPI, Metrobank)
- [ ] Automated BIR form generation (2307, 2306, 2316)
- [ ] Real-time cash flow forecasting with AI
- [ ] Credit card feed integration

---

> **InsightPulseAI Integration:**
> - **Data flows to:** `finance.*`, `expense.*`, `doc.*`
> - **Used by engines:** TE-Cheq, E1 Data Intake, E3 Intelligence
> - **Triggered automations:** `wf_invoice_sync`, `wf_expense_*`, `wf_reconciliation_*`
> - **AI agents:** Finance Coach, Reconciliation Assistant, Expense Validator

---

## References

- [Odoo 18 Accounting Documentation](https://www.odoo.com/documentation/18.0/applications/finance/accounting.html)
- [OCA account-financial-tools](https://github.com/OCA/account-financial-tools)
- [OCA hr-expense](https://github.com/OCA/hr-expense)
- [InsightPulseAI CE/OCA Mapping](../ODOO18_ENTERPRISE_TO_CE_OCA_MAPPING.md)
