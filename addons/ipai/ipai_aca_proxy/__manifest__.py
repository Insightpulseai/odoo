{
    'name': 'IPAI ACA Proxy Fix',
    'version': '18.0.1.0.0',
    'category': 'Technical',
    'summary': 'Inject X-Forwarded-Host for Azure Container Apps ingress',
    'description': """
Azure Container Apps ingress sends X-Forwarded-Proto and X-Forwarded-For
but does NOT send X-Forwarded-Host. Odoo's ProxyFix activation (http.py)
requires X-Forwarded-Host to be present before it will trust
X-Forwarded-Proto for scheme detection.

This server-wide module injects X-Forwarded-Host from the Host header
when X-Forwarded-Proto is present but X-Forwarded-Host is missing,
allowing ProxyFix to activate and set the correct HTTPS scheme.

Without this fix, Odoo constructs http:// redirect URIs behind ACA,
which breaks Entra ID OAuth (AADSTS50011).
    """,
    'author': 'InsightPulse AI',
    'license': 'LGPL-3',
    'depends': ['base'],
    'post_load': '_aca_proxy_post_load',
    'installable': True,
    'auto_install': False,
}
