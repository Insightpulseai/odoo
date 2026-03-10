---
name: expenses
description: Employee expense logging, approval, posting to accounting journals, reimbursement, and reinvoicing to customers.
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# expenses — Odoo 19.0 Skill Reference

## Overview

The Odoo Expenses app manages the full employee expense lifecycle: logging individual expenses (manually, via receipt upload/OCR, drag-and-drop, or email), submitting expense reports for approval, posting approved reports to accounting journals, and reimbursing employees via cash, check, bank transfer, or payslip integration. Expenses can be reinvoiced to customers through sales orders. Physical and virtual expense cards (Stripe Issuing) provide real-time expense tracking with automatic record creation.

## Key Concepts

- **Expense Category**: Product-like records defining expense types (meals, mileage, travel, etc.). Each has a reference code, optional fixed cost, expense account, and tax configuration. Managed at Expenses > Configuration > Expense Categories.
- **Expense Record**: Individual expense entry with description, category, total/quantity, date, employee, paid-by (employee or company), analytic distribution, and optional receipt attachment.
- **Expense Report**: Collection of submitted expense records grouped for approval. Tracks status through Draft > Submitted > Approved > Posted > Done.
- **Expense Digitization (OCR)**: Automatic receipt scanning using IAP credits. Three modes: Do not digitize, Digitize on demand only, Digitize automatically.
- **Expense Card**: Physical or virtual pre-paid debit card (Stripe Issuing) that auto-creates expense records on purchase. Supports spending policies (country, category, per-transaction and periodic limits).
- **Reinvoicing**: Charging expenses back to customers by linking expenses to sales orders. Configured per category (No / At cost / Sales price).
- **Analytic Distribution**: Allocation of expense costs across analytic accounts (projects, departments) with percentage splits.

## Core Workflows

### 1. Log and Submit an Expense

1. Open Expenses app (My Expenses dashboard).
2. Click New. Fill Description, Category, Total/Quantity, Employee, Paid By, Expense Date.
3. Optionally set Account, Customer to Reinvoice (SO), Analytic Distribution.
4. Click Attach Receipt to upload supporting document.
5. From My Expenses list, select draft expenses, click Submit.
6. Status changes to Submitted; report is created and sent for approval.

### 2. Approve an Expense Report

1. Navigate to Expenses > Expense Reports (requires Team Approver rights or higher).
2. Filter by Submitted status.
3. Click individual report, then Approve. Or select multiple reports and click Approve Report.
4. To refuse: open individual report, click Refuse, enter reason.
5. Refused reports can be Reset to Draft for correction and resubmission.

### 3. Post Expenses to Accounting

1. Navigate to Expenses > Expense Reports, filter by Approved status.
2. Click individual report, then Post Journal Entries. Or select multiple and click Post Entries.
3. Requires Accountant/Adviser access rights + Expenses Manager role.
4. Journal Entry smart button appears linking to the posted accounting entry.

### 4. Reimburse Employees

1. Navigate to Expenses > Expense Reports, filter by Posted status.
2. **Individual**: Click report, click Pay. Select Journal (Bank/Cash), Payment Method, verify Amount, set Payment Date, click Create Payment.
3. **Bulk**: Select multiple posted reports, click Pay. Optionally enable Group Payments to consolidate per employee. Click Create Payments.
4. **Via Payslip**: For approved (not yet posted) reports, click Report in Next Payslip. Expense is added to employee's next payroll run.

### 5. Reinvoice Expenses to Customers

1. Configure expense category with Re-Invoice Costs set to At cost or Sales price.
2. When logging expense, select the Sales Order in Customer to Reinvoice field.
3. Set Analytic Distribution to the project account.
4. Submit, approve, and post the expense report.
5. After posting, expenses appear on the linked Sales Order's Order Lines tab.
6. On the SO, click Create Invoice to bill the customer.

## Technical Reference

### Key Models

| Model | Purpose |
|-------|---------|
| `hr.expense` | Individual expense records |
| `hr.expense.sheet` | Expense reports (collections of expenses) |
| `product.product` | Expense categories (stored as products) |
| `hr.expense.card` | Expense card configuration |

### Key Fields on `hr.expense`

- `name`: Description
- `product_id`: Expense category (product reference)
- `total_amount` / `unit_amount` / `quantity`
- `employee_id`: Employee who incurred the expense
- `payment_mode`: `own_account` (employee pays, to reimburse) or `company_account`
- `date`: Expense date
- `account_id`: GL account for posting
- `analytic_distribution`: JSON dict of analytic account allocations
- `sale_order_id`: Sales order for reinvoicing
- `sheet_id`: Link to expense report

### Key Fields on `hr.expense.sheet`

- `state`: `draft`, `submit`, `approve`, `post`, `done`, `cancel`
- `employee_id`, `journal_id`, `company_id`
- `expense_line_ids`: One2many to `hr.expense`
- `account_move_id`: Posted journal entry

### Access Rights

| Role | Capabilities |
|------|-------------|
| Employee | Log own expenses, submit reports |
| Team Approver | View and approve/refuse team expense reports |
| All Approver | View and approve/refuse all expense reports |
| Manager | Full access including posting to journals |
| Accountant/Adviser | Required (in addition to Manager) for posting journal entries |

### Important Settings

- Expenses > Configuration > Settings:
  - **Expense Digitization (OCR)**: Enable receipt scanning
  - **Incoming Emails**: Configure email alias for expense submission
  - **Expense Card**: Enable Stripe Issuing integration
  - **Reimburse in Payslip**: Add expenses to next payroll
  - **Payment Methods**: Configure reimbursement payment options

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

- **Expense Cards**: Full Stripe Issuing integration with physical and virtual cards, spending policies (country/category/limit restrictions), and automatic expense record creation.
- **Demo expense card module**: `Expense Cards: Demo` module for testing without live Stripe account.
- **Auto-post bills per vendor**: Related vendor bill setting (Always / Ask after 3 validations / Never) can affect expense-related vendor workflows.
- **Expense report statuses**: Workflow states are Draft > Submitted > Approved > Posted > Done (with Refused as side state).

## Common Pitfalls

- **OCR requires IAP credits**: Receipt digitization (upload, drag-and-drop, email) consumes In-App Purchase credits. Running out silently disables auto-digitization.
- **Email alias requires domain configuration**: The incoming email feature for expenses needs a configured domain alias before the email address field appears in settings.
- **Reinvoice field locks on approval**: The Customer to Reinvoice field cannot be modified after an expense report is approved. Set it correctly before submission.
- **Expense cards require both Accounting and Invoicing apps** installed. Cards only work in supported EU countries (20 countries listed).
- **Payslip reimbursement only works on Approved status**: Once an expense report is Posted, the Report in Next Payslip option is no longer available. Choose the reimbursement method before posting.
