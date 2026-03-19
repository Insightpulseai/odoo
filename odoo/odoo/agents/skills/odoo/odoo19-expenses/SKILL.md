# Skill: Odoo 19 Expenses — Feature Map + Automation Plan

## Metadata

| Field | Value |
|-------|-------|
| **id** | `odoo19-expenses` |
| **domain** | `odoo_ce` |
| **source** | https://www.odoo.com/app/expenses |
| **extracted** | 2026-03-15 |
| **applies_to** | odoo, agents, automations |
| **tags** | expenses, hr-expense, receipt, ocr, reimbursement, reinvoice, approval |

---

## Native Capabilities (Odoo CE `hr_expense`)

### Submission Methods

| Method | How It Works | CE Available |
|--------|-------------|-------------|
| **Email submission** | Send email with expense code → auto-creates expense | Yes |
| **Receipt scan** | Upload photo → OCR extracts amount + date | Yes (IAP OCR) |
| **Drag-and-drop** | Drop receipt file on dashboard | Yes |
| **Manual entry** | Fill form with category, amount, date | Yes |
| **Mobile app** | All methods available on mobile | Yes |

### Workflow

```
Employee creates expense(s)
    ↓
Employee groups into expense report (one click)
    ↓
Submit for approval
    ↓
Manager approves/refuses (with chat discussion)
    ↓
Route: Reimbursement OR Reinvoice
    ├── Reimbursement → Accounting posts to journal → payment to employee
    └── Reinvoice → Updates sales order → invoiced to customer
```

### Features

| Feature | Description | CE? |
|---------|-------------|-----|
| Pre-configured categories | Ready-to-use expense types | Yes |
| Expense reports | Group multiple expenses into one report | Yes |
| Approval workflows | Role-based manager approval | Yes |
| Chat on expenses | Discussion thread for transparency | Yes |
| Reinvoice to customer | Auto-add to sales order on approval | Yes |
| Reimbursement tracking | Track payment status | Yes |
| Dashboard | All expenses with status filters | Yes |
| Customizable reporting | Filters, groups, pivot, graph views | Yes |
| Mobile app | Full functionality on mobile | Yes |

### OCR (Document Digitization)

Odoo's built-in OCR uses **odoo.com IAP** (paid credits). Per IPAI doctrine: **CE-only, no IAP**.

**IPAI replacement**: ADE (LandingAI) or Azure Document Intelligence for receipt OCR.

## OCA Modules for Expenses

| Module | Repo | Purpose | Status |
|--------|------|---------|--------|
| `hr_expense_sequence` | `hr-expense` | Auto-numbering for expense reports | Check 19.0 |
| `hr_expense_cancel` | `hr-expense` | Allow cancellation of posted expenses | Check 19.0 |
| `hr_expense_payment` | `hr-expense` | Payment registration from expense | Check 19.0 |
| `hr_expense_advance_clearing` | `hr-expense` | Cash advance + clearing workflow | Check 19.0 |
| `hr_expense_fleet` | `hr-expense` | Link expenses to fleet vehicles | Check 19.0 |
| `hr_expense_tier_validation` | `hr-expense` | Multi-level approval tiers | Check 19.0 |

## Automation Pipeline (IPAI)

### Receipt → Expense (ExpenseIt Equivalent)

```
Receipt photo (mobile upload / email / webhook)
    ↓
n8n webhook receives file
    ↓
ADE parse + extract (Pydantic schema):
    - merchant_name: str
    - date: str
    - items: list[dict]
    - subtotal: float
    - tax_amount: float
    - total: float
    - payment_method: str
    ↓
n8n → Odoo XML-RPC:
    hr.expense.create({
        'name': f"{merchant_name} - {date}",
        'product_id': <category_id>,  # auto-map by merchant type
        'total_amount': total,
        'date': date,
        'employee_id': <from_context>,
        'payment_mode': 'own_account',  # employee paid
    })
    ↓
Attach original receipt image to expense record
    ↓
Notify employee via Slack: "Expense created: {name} - {total}"
    ↓
Record in ops.run_events (Supabase SSOT)
```

### Expense Report Auto-Submit

```
Weekly cron (Friday 5PM):
    ↓
Query: hr.expense WHERE state='draft' AND employee_id=<employee>
    ↓
If count > 0:
    hr.expense.sheet.create({
        'expense_line_ids': [(6, 0, expense_ids)],
        'employee_id': employee_id,
        'name': f"Week {week_number} Expenses",
    })
    ↓
    Auto-submit for approval
    ↓
    Notify manager via Slack
```

### Expense Audit Agent (Concur Detect Equivalent)

```
On expense_report.submit trigger:
    ↓
Agent reviews all line items:
    1. Check against policy rules:
       - Max amount per category
       - Weekend/holiday spending
       - Duplicate detection (same amount+date+merchant)
       - Missing receipts for amounts > threshold
    2. LLM reasoning for anomalies:
       - Unusual merchant for role
       - Pattern deviation from employee history
    ↓
Result:
    - PASS → proceed to manager approval
    - FLAG → add note with findings, require manager review
    - BLOCK → reject with explanation, notify compliance
    ↓
Record audit result in ops.run_events
```

## Concur Parity Impact

| Concur Feature | IPAI Implementation | Parity After |
|---------------|---------------------|-------------|
| ExpenseIt (receipt OCR) | ADE + n8n → hr.expense | Full |
| Concur Detect (fraud) | Expense audit agent | Full |
| Budget tracking | MIS Builder + hr.expense analytics | Full |
| Mobile submission | Odoo mobile app + email submission | Full |
| Reinvoice to customer | Native Odoo CE | Full |
| Bank card feeds | OCA bank statement import | Partial |
| Mileage tracking | Odoo fleet + distance calc | Partial |

**Expense parity after implementation: 58% → 85%**
