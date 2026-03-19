# Checklist — odoo-shell-debug

- [ ] Session purpose documented before connecting
- [ ] Connected via `az containerapp exec` (not Odoo.sh web shell)
- [ ] Odoo process state verified (running, PID, workers)
- [ ] Module installation state inspected for target module
- [ ] Database connectivity confirmed
- [ ] Container filesystem inspected (addons path, config, logs)
- [ ] No production data modified during session
- [ ] No modules installed/uninstalled via shell on production
- [ ] Secrets redacted from all diagnostic output
- [ ] Session disconnected cleanly
- [ ] Evidence captured in `docs/evidence/{stamp}/odoo-delivery/odoo-shell-debug/`
