{
    "name": "IPAI Auth OIDC + MFA",
    "version": "19.0.1.0.0",
    "category": "Authentication",
    "summary": "OpenID Connect SSO + TOTP MFA for InsightPulse AI",
    "description": """
        Integrates OpenID Connect (OIDC) authentication and TOTP-based
        multi-factor authentication for the IPAI stack.

        Depends on OCA auth_oidc for the OIDC protocol layer and Odoo's
        built-in auth_totp for MFA. This module provides:
        - Default OAuth provider data template (Google/Keycloak)
        - Provider credentials are injected via environment variables
        - MFA enforcement for admin group users

        Azure WAF Parity: Closes Security pillar gaps (SSO + MFA).
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": [
        "base",
        "auth_totp",
    ],
    "external_dependencies": {
        "python": [],
    },
    "data": [
        "data/auth_provider_data.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}
