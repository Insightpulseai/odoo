{
    "name": "Expense OCR (IPAI)",
    "summary": "Deterministic OCR ingestion for receipts into hr.expense",
    "version": "18.0.1.0.0",
    "category": "Human Resources/Expenses",
    "license": "AGPL-3",
    "author": "IPAI",
    "website": "https://github.com/jgtolentino/odoo-ce",
    "depends": ["base", "mail", "hr_expense"],
    "data": [
        "security/ir.model.access.csv",
        "views/menu.xml",
    ],
    "installable": True,
    "application": False,
}
