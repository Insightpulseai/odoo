{
    "name": "IPAI Social CAPI Bridge",
    "version": "19.0.1.0.0",
    "category": "Marketing",
    "summary": "Bridge CRM events to Meta Conversions API via Azure Function",
    "description": """
Automatically relays Odoo CRM lifecycle events to Meta Conversions API
for server-side attribution tracking.

Events tracked:
- Lead created → Meta Lead event
- Lead qualified (stage change) → Meta Lead (qualified) event
- Opportunity won → Meta Purchase event
- Invoice paid → Meta Purchase event with value

Architecture:
- Odoo → webhook POST → Azure Function (meta-capi-bridge) → Meta Graph API
- All secrets resolved from Azure Key Vault at runtime
- PII hashed (SHA-256) before transmission per Meta CAPI spec
- App Secret Proof (HMAC-SHA256) enforced on all API calls

No direct Odoo-to-Meta API calls. Bridge pattern only.
    """,
    "author": "InsightPulse AI",
    "website": "https://www.insightpulseai.com",
    "license": "LGPL-3",
    "depends": [
        "crm",
        "account",
        "utm",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_config_parameter.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
    "development_status": "Beta",
}
