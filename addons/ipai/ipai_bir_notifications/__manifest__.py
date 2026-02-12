{
    "name": "IPAI BIR Notifications",
    "summary": "Email digest and urgent alerts for BIR tax filing deadlines",
    "version": "19.0.1.0.0",
    "category": "Accounting/Localizations",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.com",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "base",
        "mail",
        "ipai_bir_tax_compliance",  # BIR core module
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/mail_templates.xml",
        "data/cron_jobs.xml",
        "views/bir_alert_views.xml",
        "views/menus.xml",
    ],
}
