# -*- coding: utf-8 -*-
{
    'name': 'IPAI HR Expense Liquidation',
    'version': '19.0.1.0.0',
    'category': 'Human Resources/Expenses',
    'sequence': 85,
    'summary': 'Cash advance tracking with itemized expense liquidation and bucket totals',
    'description': """
Expense Liquidation with Cash Advance Tracking
================================================

Features:
---------
* **3 Liquidation Types**:
  - Cash Advance: Track advance amount, expenses, and settlement
  - Reimbursement: Direct employee reimbursement for out-of-pocket expenses
  - Petty Cash: Small-value purchases from petty cash fund

* **Itemized Expenses**:
  - Line-by-line expense entry with dates, categories, amounts
  - Receipt attachment support per line item
  - Automatic bucket categorization

* **Bucket Totals**:
  - Meals & Entertainment
  - Transportation & Travel
  - Miscellaneous
  - Auto-calculated totals per bucket

* **Cash Advance Settlement**:
  - Advance amount tracking
  - Total expenses calculation
  - Return amount (if expenses < advance)
  - Additional reimbursement (if expenses > advance)
  - Settlement status tracking

* **Professional Report**:
  - QWeb-based expense liquidation report
  - Bucket total summary
  - Settlement calculation display
  - Signature blocks for employee and approver

Technical Details:
------------------
* Extends hr.expense module
* Adds hr.expense.liquidation model with line items
* Bucket-based expense categorization
* Automated settlement calculations
* Multi-currency support

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

        # Views
        'views/expense_liquidation_views.xml',
        'views/menu.xml',

        # Reports
        'report/expense_liquidation_report.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
