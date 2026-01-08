# Production Recovery Runbook

This guide covers recovery from critical failures:
1.  **502 Bad Gateway** (Container Crashes / Nginx Issues)
2.  **500 Internal Server Error** (Asset Compilation Failures)

---

# Scenario 1: 502 Bad Gateway (Crash Diagnosis)
**Symptoms:** `502 Bad Gateway` on public URL, or intermittent crashes.
**Cause:** Odoo container is down, not listening on host port `8069`, or Nginx config mismatch.

## 1. Droplet: Confirm Nginx Wiring

```bash
# Check status and logs
sudo systemctl status nginx --no-pager
sudo nginx -t
sudo journalctl -u nginx --since "30 min ago" --no-pager | tail -200

# Verify Upstream Configuration
sudo grep -RIn --color=always -E "proxy_pass|upstream|8069|8072|odoo" /etc/nginx/sites-enabled /etc/nginx/conf.d | tail -200
```
*Target typically `127.0.0.1:8069`.*

## 2. Docker: Confirm Stack Running

```bash
cd /opt/odoo-ce || cd ~/odoo-ce

# Check Container Status
docker compose -f docker-compose.prod.yml ps
# Verify Port Mapping
docker compose -f docker-compose.prod.yml port odoo 8069 || true
# Check recent logs
docker compose -f docker-compose.prod.yml logs --tail=200 odoo
docker compose -f docker-compose.prod.yml logs --tail=200 db
```

## 3. Host-Level Reachability (Bypass Nginx)

Test if Odoo is accessible locally on the host.

```bash
# If running on 8069
curl -sS -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8069/web/login || true

# Check listening ports
ss -lntp | grep -E ":8069|:8072|:80|:443" || true
```
*If this returns 200/303, Nginx is the issue. If it fails, Odoo is the issue.*

## 4. Fast Recovery (Restart)

Most common fix for stuck containers.

```bash
cd /opt/odoo-ce || cd ~/odoo-ce

docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml restart odoo
docker compose -f docker-compose.prod.yml logs -f --tail=200 odoo
```

## 5. Fail-Fast Boot (Debug Crash)

If Odoo keeps crashing (Boot Loop), run deterministically to see the traceback.

```bash
# Stop background container
docker compose -f docker-compose.prod.yml stop odoo

# Run in foreground (Stop after Init) to capture Error
docker compose -f docker-compose.prod.yml run --rm odoo bash -lc \
  "odoo -d odoo_core --stop-after-init --log-level=info"
```
**Look for:** `Traceback`, `ImportError`, `XMLSyntaxError`.

---

# Scenario 2: 500 Internal Server Error (Assets)
**Symptoms:** `/web/login` works, but styles are broken or `/web/assets/...` returns 500.
**Cause:** Corrupted Odoo asset bundles (JS/CSS), often after module updates or file permission issues.

## 1. Quick Fix (Regenerate Assets)
Clears the `ir.attachment` records for compiled assets and forces regeneration.

```bash
cd /opt/odoo-ce || cd ~/odoo-ce

# Execute deletion inside the container
docker compose -f docker-compose.prod.yml exec odoo odoo -d odoo --no-http --stop-after-init shell << 'EOF'
env['ir.attachment'].search([('name', 'like', 'web.assets_%'), ('res_model', '=', 'ir.ui.view')]).unlink()
env['ir.qweb'].clear_caches()
env.cr.commit()
print("Assets cleared.")
EOF

# Restart to rebuild
docker compose -f docker-compose.prod.yml restart odoo
```

## 2. Check Permissions (Corrupt Filestore)

If the quick fix fails, ensure volume permissions are correct.

```bash
# Fix ownership of the var/lib/odoo directory inside container (run as root)
docker compose -f docker-compose.prod.yml exec -u root odoo chown -R odoo:odoo /var/lib/odoo
```

## 3. Database Cleanup (Nuclear Option)
Use this only if the Quick Fix doesn't work. It deletes *all* compiled assets and QWeb cache.

```bash
# Backup first!
docker compose -f docker-compose.prod.yml exec db pg_dump -U odoo odoo > backup_assets_500.sql

# Connect to DB and wipe assets
docker compose -f docker-compose.prod.yml exec db psql -U odoo -d odoo << 'SQL'
DELETE FROM ir_attachment WHERE name LIKE '/web/%';
DELETE FROM ir_attachment WHERE name LIKE 'web.assets%';
DELETE FROM ir_attachment WHERE url LIKE '/web/assets/%';
DELETE FROM ir_attachment WHERE name LIKE '%assets_bundle%';
TRUNCATE ir_qweb;
SQL

# Clear filestore cache from disk
docker compose -f docker-compose.prod.yml exec odoo rm -rf /var/lib/odoo/.local/share/Odoo/filestore/odoo/web/

# Regenerate
docker compose -f docker-compose.prod.yml exec odoo odoo -d odoo -u web --stop-after-init

# Restart
docker compose -f docker-compose.prod.yml restart odoo
```

## 4. Identify Broken Module
If assets still fail, a specific module might be pushing bad SCSS/JS.

```bash
# Check recent installs
docker compose -f docker-compose.prod.yml exec db psql -U odoo -d odoo -c \
"SELECT name, state, write_date FROM ir_module_module WHERE state = 'installed' ORDER BY write_date DESC LIMIT 10;"

# Uninstall suspect module (e.g., ipai_theme_aiux if recent)
docker compose -f docker-compose.prod.yml exec odoo odoo -d odoo -u ipai_theme_aiux --stop-after-init
```
