{
    "name": "IPAI DocFlow Manual Review (Odoo 19)",
    "version": "19.0.1.0.0",
    "category": "Accounting",
    "summary": "Manual review queue for OCR+LLM extracted expenses and vendor bills",
    "depends": [
        "base",
        "mail",
        "account",
        "hr_expense",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "data/sla_cron.xml",
        "views/docflow_document_views.xml",
        "views/docflow_routing_rule_views.xml",
        "data/docflow_routing_rule_menu.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
