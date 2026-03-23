# -*- coding: utf-8 -*-
{
    'name': 'IPAI HR Expense Liquidation',
    'version': '19.0.3.0.0',
    'category': 'Human Resources/Expenses',
    'sequence': 85,
    'summary': 'Cash advance request, multi-step approval, liquidation, policy engine, and monitoring',
    'description': """
Expense Liquidation with Cash Advance Lifecycle
================================================

Features:
---------
* **Cash Advance Request** (pre-spend):
  - Employee requests funds before travel/event
  - Department + Finance approval workflow
  - Auto-calculated liquidation due date (event end + 15 days)
  - Calendar integration for due date reminders
  - Branch awareness via operating.branch

* **3 Liquidation Types** (post-spend):
  - Cash Advance: Track advance amount, expenses, and settlement
  - Reimbursement: Direct employee reimbursement for out-of-pocket expenses
  - Petty Cash: Small-value purchases from petty cash fund

* **Multi-Step Approval Workflow**:
  - Cash Advance Request: draft -> submitted -> dept_approved -> finance_approved
    -> released -> for_liquidation -> liquidated -> closed
  - Liquidation: draft -> submitted -> manager_approved -> finance_approved
    -> released -> in_liquidation -> liquidated -> closed
  - Plus: rejected, cancelled

* **Accounting Entries with Idempotency**:
  - Release: debit advance receivable, credit cash/bank
  - Liquidation: debit expense accounts, credit advance receivable
  - Idempotency keys prevent double-posting

* **Policy Engine**:
  - Configurable rules: amount limits, receipt requirements, category limits, overdue checks
  - Policy violation tracking with warning/blocking severity
  - Violation resolution workflow

* **Monitoring**:
  - Daily cron checks for overdue advances
  - Automatic policy violation creation

* **Itemized Expenses**:
  - Line-by-line expense entry with dates, categories, amounts
  - Sub-amount columns: Meals, Transport, Misc
  - Receipt attachment support per line item
  - Automatic bucket categorization

* **Withholding Tax & Multi-Page**:
  - Gross amount / withholding tax / net paid tracking
  - Multi-page report support with other_pages_total

* **Cash Advance Settlement**:
  - Advance amount tracking
  - Total expenses calculation
  - Amount due to employee / refundable to company
  - Settlement status tracking

Technical Details:
------------------
* Models: cash.advance, cash.advance.line, hr.expense.liquidation,
  hr.expense.liquidation.line, hr.expense.policy.rule, hr.expense.policy.violation
* Extends: hr.expense, hr.expense.sheet
* Multi-currency support
* Chatter integration with state transition notifications

Author: InsightPulse AI
License: LGPL-3
    """,
    'author': 'InsightPulse AI',
    'website': 'https://insightpulseai.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'hr',
        'hr_expense',
        'account',
        'calendar',
        'ipai_branch_profile',
    ],
    'data': [
        # Security
        'security/security.xml',
        'security/ir.model.access.csv',

        # Data
        'data/sequence.xml',
        'data/cron_monitoring.xml',

        # Views
        'views/cash_advance_views.xml',
        'views/expense_liquidation_views.xml',
        'views/expense_policy_views.xml',
        'views/menu.xml',

        # Reports
        'report/expense_liquidation_report.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
