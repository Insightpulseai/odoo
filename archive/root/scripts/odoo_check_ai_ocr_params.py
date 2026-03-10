ICP = env["ir.config_parameter"].sudo()
keys = ["ipai.ai.endpoint_url","ipai.ai.api_key","ipai.ocr.endpoint_url","ipai.ocr.api_key"]
print({k: ("***" if "key" in k else ICP.get_param(k)) for k in keys})
