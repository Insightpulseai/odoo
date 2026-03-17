Fetch = env["fetchmail.server"].sudo()
servers = Fetch.search([("active","=",True), ("type","=","imap")])
for s in servers:
  s.write({"state":"done"})   # marks as running/active in many versions
env.cr.commit()
print(f"OK: enabled {len(servers)} IMAP fetchmail servers")
