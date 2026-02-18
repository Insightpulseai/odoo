{
    "name": "IPAI BIR Plane Sync",
    "summary": "Bidirectional sync between BIR tax deadlines and Plane issues for OKR tracking",
    "version": "19.0.1.0.0",
    "category": "Accounting/Localizations",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.com",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "base",
        "ipai_bir_tax_compliance",  # BIR core module
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/bir_filing_deadline_views.xml",
        "data/ir_config_parameter.xml",
    ],
    "external_dependencies": {
        "python": ["requests"],
    },
}
