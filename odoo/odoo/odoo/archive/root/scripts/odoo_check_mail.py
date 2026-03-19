ms = env["ir.mail_server"].sudo().search([], limit=5)
print("ir.mail_server:", [(r.name, r.smtp_host, r.smtp_user, r.smtp_encryption) for r in ms])

fm = env["fetchmail.server"].sudo().search([], limit=5)
print("fetchmail.server:", [(r.name, r.server, r.user, r.type, r.is_ssl, r.state) for r in fm])
