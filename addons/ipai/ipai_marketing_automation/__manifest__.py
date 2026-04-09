{
    "name": "IPAI Marketing Automation",
    "version": "18.0.1.0.0",
    "category": "Marketing",
    "summary": "Multi-step campaign automation with timed triggers and conditions",
    "author": "InsightPulse AI, Odoo Community Association (OCA)",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": [
        "mass_mailing",
        "mail",
        "queue_job",
        "crm",
    ],
    "data": [
        "security/ipai_marketing_automation_groups.xml",
        "security/ir.model.access.csv",
        "views/ipai_campaign_views.xml",
        "data/ir_cron.xml",
    ],
    "installable": True,
    "application": True,
    "development_status": "Beta",
}
