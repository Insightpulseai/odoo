import os
from odoo import api, SUPERUSER_ID

def _env(name, default=None):
    v = os.getenv(name)
    return v if v not in (None, "") else default

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    icp = env["ir.config_parameter"].sudo()
    MailServer = env["ir.mail_server"].sudo()

    # Canonical (no .net): use insightpulseai.com and your production URL
    base_url    = _env("ODOO_BASE_URL")         # e.g. https://erp.insightpulseai.com
    alias_domain= _env("ODOO_ALIAS_DOMAIN")     # e.g. insightpulseai.com

    if base_url:
        icp.set_param("web.base.url", base_url)
        icp.set_param("web.base.url.freeze", "True")

    if alias_domain:
        # Alias domain for mail aliases
        icp.set_param("mail.catchall.domain", alias_domain)

    # SMTP SSOT (Zoho Mail)
    smtp_host = _env("ODOO_SMTP_HOST")
    smtp_port = int(_env("ODOO_SMTP_PORT", "587"))
    smtp_user = _env("ODOO_SMTP_USER")
    smtp_pass = _env("ODOO_SMTP_PASS")
    smtp_tls  = _env("ODOO_SMTP_TLS", "1") == "1"

    if smtp_host and smtp_user and smtp_pass:
        ms = MailServer.search([("name", "=", "SSOT SMTP")], limit=1)
        vals = {
            "name": "SSOT SMTP",
            "smtp_host": smtp_host,
            "smtp_port": smtp_port,
            "smtp_user": smtp_user,
            "smtp_pass": smtp_pass,
            "smtp_encryption": "starttls" if smtp_tls else "none",
            "smtp_authentication": "login",
            "sequence": 1,
            "active": True,
        }
        if ms:
            ms.write(vals)
        else:
            MailServer.create(vals)
