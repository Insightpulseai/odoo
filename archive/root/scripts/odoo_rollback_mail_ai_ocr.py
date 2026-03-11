# Disable mail servers + fetchmail and wipe ipai params
env["ir.mail_server"].sudo().search([]).write({"active": False})
env["fetchmail.server"].sudo().search([]).write({"active": False})

ICP = env["ir.config_parameter"].sudo()
for k in ["ipai.ai.endpoint_url","ipai.ai.api_key","ipai.ocr.endpoint_url","ipai.ocr.api_key"]:
  ICP.set_param(k, "")

env.cr.commit()
print("OK: disabled mail/fetchmail + cleared ipai ai/ocr params")
