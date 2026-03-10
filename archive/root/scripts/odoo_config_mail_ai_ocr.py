import os
import sys

def env_var(name, default=None, required=False):
  v = os.getenv(name, default)
  if required and (v is None or v == "" or v == "__SET_ME__"):
    raise SystemExit(f"Missing required env var: {name}")
  return v

SMTP_HOST = env_var("ODOO_SMTP_HOST", required=True)
SMTP_PORT = int(env_var("ODOO_SMTP_PORT", "587"))
SMTP_USER = env_var("ODOO_SMTP_USER", required=True)
SMTP_PASS = env_var("ODOO_SMTP_PASS", required=True)
SMTP_TLS  = env_var("ODOO_SMTP_TLS", "true").lower() in ("1","true","yes","y")

IMAP_HOST = env_var("ODOO_IMAP_HOST", required=True)
IMAP_PORT = int(env_var("ODOO_IMAP_PORT", "993"))
IMAP_USER = env_var("ODOO_IMAP_USER", required=True)
IMAP_PASS = env_var("ODOO_IMAP_PASS", required=True)
IMAP_SSL  = env_var("ODOO_IMAP_SSL", "true").lower() in ("1","true","yes","y")

AI_ENDPOINT = env_var("IPAI_AI_ENDPOINT_URL", required=True)
AI_API_KEY  = env_var("IPAI_AI_API_KEY", required=True)

OCR_ENDPOINT = env_var("IPAI_OCR_ENDPOINT_URL", required=True)
OCR_API_KEY  = env_var("IPAI_OCR_API_KEY", "")

# --- Odoo runtime is injected by odoo-bin shell: provides `env` (Odoo Environment) ---
# We deliberately avoid importing odoo; use the already-bootstrapped env object.

def upsert_param(key, value):
  ICP = env["ir.config_parameter"].sudo()
  existing = ICP.get_param(key)
  if existing != value:
    ICP.set_param(key, value)

def upsert_ir_mail_server():
  MailServer = env["ir.mail_server"].sudo()
  domain = [("smtp_host","=",SMTP_HOST), ("smtp_user","=",SMTP_USER)]
  rec = MailServer.search(domain, limit=1)
  vals = {
    "name": f"Zoho SMTP ({SMTP_USER})",
    "smtp_host": SMTP_HOST,
    "smtp_port": SMTP_PORT,
    "smtp_user": SMTP_USER,
    "smtp_pass": SMTP_PASS,
    "smtp_encryption": "starttls" if SMTP_TLS else "none",
    "sequence": 10,
    "active": True,
  }
  if rec:
    rec.write(vals)
  else:
    MailServer.create(vals)

def upsert_fetchmail_imap():
  # Requires fetchmail module installed
  Fetch = env["fetchmail.server"].sudo()
  domain = [("server","=",IMAP_HOST), ("user","=",IMAP_USER)]
  rec = Fetch.search(domain, limit=1)
  vals = {
    "name": f"Zoho IMAP ({IMAP_USER})",
    "server": IMAP_HOST,
    "port": IMAP_PORT,
    "type": "imap",
    "is_ssl": IMAP_SSL,
    "user": IMAP_USER,
    "password": IMAP_PASS,
    "state": "draft",   # we'll start it explicitly after validation
    "active": True,
    # action_id: optional routing; leave default to "Incoming Mail" processing
  }
  if rec:
    rec.write(vals)
  else:
    Fetch.create(vals)

def ensure_modules():
  # Install minimal modules needed for incoming/outgoing mail routing + fetchmail
  # NOTE: module names can vary by Odoo version; these are typical.
  mods = ["mail", "fetchmail"]
  Module = env["ir.module.module"].sudo()
  to_install = Module.search([("name","in",mods), ("state","not in",["installed","to install"])])
  if to_install:
    to_install.button_install()

def apply_agent_params():
  # These keys are intentionally namespaced; update to match your ipai_* modules if they expect different keys.
  upsert_param("ipai.ai.endpoint_url", AI_ENDPOINT)
  upsert_param("ipai.ai.api_key", AI_API_KEY)
  upsert_param("ipai.ocr.endpoint_url", OCR_ENDPOINT)
  upsert_param("ipai.ocr.api_key", OCR_API_KEY or "")

def main():
  ensure_modules()
  # After ensure_modules(), in a fresh DB you may need a second run once modules finish installing.
  upsert_ir_mail_server()
  upsert_fetchmail_imap()
  apply_agent_params()
  env.cr.commit()
  print("OK: configured SMTP, IMAP fetchmail (draft), and ipai.ai/ipai.ocr params")

main()
