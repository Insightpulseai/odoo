{
    "name": "ipai_<module_name>",
    "version": "18.0.1.0.0",
    "summary": "<One-line summary>",
    "description": """
    One-paragraph description. See README.md and docs/MODULE_INTROSPECTION.md
    for the full justification.

    Module type: <bridge | overlay | adapter | extension>
    """,
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "category": "InsightPulseAI/<category>",
    "depends": [
        "base",
        # CE modules
        # OCA modules (cite explicitly — required per doctrine)
    ],
    "data": [
        "security/ir.model.access.csv",
        # "data/parameter.xml",
        # "views/<view>.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
