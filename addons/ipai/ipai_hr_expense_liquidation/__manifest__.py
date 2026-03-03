# -*- coding: utf-8 -*-
{
    'name': 'IPAI HR Expense Liquidation',
    'version': '19.0.2.0.0',
    'category': 'Human Resources/Expenses',
    'sequence': 85,
    'summary': 'Concur-like cash advance with multi-step approval, policy engine, and monitoring',
    'description': """
Expense Liquidation with Cash Advance Lifecycle
================================================

Features:
---------
* **3 Liquidation Types**:
  - Cash Advance: Track advance amount, expenses, and settlement
  - Reimbursement: Direct employee reimbursement for out-of-pocket expenses
  - Petty Cash: Small-value purchases from petty cash fund

* **8-State Approval Workflow** (Cash Advance):
  - draft -> submitted -> manager_approved -> finance_approved
  - -> released -> in_liquidation -> liquidated -> closed
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

* **Copilot Integration**:
  - 4 tools: create_cash_advance, submit_liquidation, check_policy_compliance, get_overdue_advances

* **Itemized Expenses**:
  - Line-by-line expense entry with dates, categories, amounts
  - Receipt attachment support per line item
  - Automatic bucket categorization (Meals, Transportation, Misc)

* **Cash Advance Settlement**:
  - Advance amount tracking
  - Total expenses calculation
  - Return amount / Additional reimbursement
  - Settlement status tracking

Technical Details:
------------------
* Extends hr.expense module
* Models: hr.expense.liquidation, hr.expense.liquidation.line,
  hr.expense.policy.rule, hr.expense.policy.violation
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
    ],
    'data': [
        # Security
        'security/security.xml',
        'security/ir.model.access.csv',

        # Data
        'data/sequence.xml',
        'data/cron_monitoring.xml',
        'data/copilot_tools.xml',

        # Views
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
