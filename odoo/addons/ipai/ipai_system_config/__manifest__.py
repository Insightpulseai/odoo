{
  "name": "IPAI System Config (SSOT)",
  "version": "19.0.1.0.0",
  "category": "Tools",
  "summary": "Env-backed SSOT for critical Odoo settings (base url, alias domain, SMTP).",
  "license": "LGPL-3",
  "depends": ["base", "mail"],
  "data": [
    "security/ir.model.access.csv",
  ],
  "post_init_hook": "post_init_hook",
  "installable": True,
  "application": False,
}
