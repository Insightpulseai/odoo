{
    "name": "IPAI Tax Intelligence",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "summary": "Reverse AvaTax — Odoo-native pre-posting tax validation, exception review, and BIR compliance pack",
    "description": """
        IPAI Tax Intelligence for Odoo 18 CE.

        Implements the Reverse AvaTax architecture:
        - Pre-posting tax validation for invoices, vendor bills, and expenses
        - Tax exception model with review state machine
        - Explainability output (rationale, inputs, confidence, policy reference)
        - PH BIR compliance pack (withholding, VAT 12%, percentage tax, EWT)
        - Audit trail for all tax computation and review actions
        - Approval-aware blocking on open exceptions

        Architecture:
        - Odoo owns all tax/accounting truth (Constitution Principle 1)
        - No parallel ledger (Constitution Principle 4)
        - Compliance is pack-based (Constitution Principle 5)
        - Draft-first: no direct posting from external systems (Constitution Principle 6)
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": ["account", "base"],
    "data": [
        "security/tax_intelligence_security.xml",
        "security/ir.model.access.csv",
        "data/tax_exception_data.xml",
        "data/tax_compliance_pack_ph.xml",
        "views/tax_validation_rule_views.xml",
        "views/tax_exception_views.xml",
        "views/tax_compliance_pack_views.xml",
        "views/tax_audit_log_views.xml",
        "views/account_move_views.xml",
        "views/tax_menu.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
