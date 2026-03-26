{
    "name": "Mail Plugin Bridge",
    "version": "19.0.1.0.0",
    "summary": "Bridge endpoints for the InsightPulseAI Gmail add-on",
    "description": """
        Provides JSON-RPC endpoints consumed by the org-owned
        Google Workspace add-on (InsightPulseAI for Gmail).

        Endpoints:
        - /ipai/mail_plugin/session   — authenticate via API key
        - /ipai/mail_plugin/context   — contact + related records lookup
        - /ipai/mail_plugin/actions/* — create lead, ticket, log note
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "category": "Productivity/Mail Plugin",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
        "crm",
        "project",
    ],
    "data": [
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
