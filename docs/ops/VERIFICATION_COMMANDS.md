# Verification Commands Reference

## Overview

Copy/paste commands for verifying Odoo 18 CE deployments. All commands assume you're in the repo root (`/opt/odoo-ce` or equivalent).

---

## 1. Container Health

### Check Container Status

```bash
# All containers
docker compose -f deploy/docker-compose.prod.yml ps

# Specific container details
docker compose -f deploy/docker-compose.prod.yml ps odoo
docker compose -f deploy/docker-compose.prod.yml ps db
```

### View Logs

```bash
# Odoo logs (last 200 lines)
docker compose -f deploy/docker-compose.prod.yml logs --tail=200 odoo

# Follow logs in real-time
docker compose -f deploy/docker-compose.prod.yml logs -f odoo

# All services
docker compose -f deploy/docker-compose.prod.yml logs --tail=100

# Filter for errors
docker compose -f deploy/docker-compose.prod.yml logs odoo 2>&1 | grep -iE "error|exception|traceback" | tail -50
```

### Resource Usage

```bash
# Current resource usage
docker stats --no-stream

# Container details
docker inspect odoo-ce --format='{{json .State}}' | jq
```

### Restart Counts

```bash
# Check for crash loops
docker inspect --format='{{.RestartCount}}' odoo-ce
```

---

## 2. nginx / Traefik Routing

### Test nginx Configuration

```bash
# Syntax check
nginx -t

# View current config
cat /etc/nginx/sites-enabled/odoo.conf
```

### Test Internal Connectivity

```bash
# Main Odoo
curl -I http://127.0.0.1:8069/web/login

# Longpolling
curl -I http://127.0.0.1:8072/longpolling/poll

# Health endpoint
curl -sS http://127.0.0.1:8069/web/health
```

### Test External Connectivity

```bash
# Replace with your domain
BASE_URL="https://erp.insightpulseai.com"

# Login page
curl -sS -o /dev/null -w '%{http_code}\n' "$BASE_URL/web/login"

# Health endpoint
curl -sS -o /dev/null -w '%{http_code}\n' "$BASE_URL/web/health"

# Longpolling (400 is acceptable)
curl -sS -o /dev/null -w '%{http_code}\n' "$BASE_URL/longpolling/poll"

# Full response with timing
curl -w "@-" -o /dev/null -sS "$BASE_URL/web/login" <<'EOF'
     time_namelookup:  %{time_namelookup}s\n
        time_connect:  %{time_connect}s\n
     time_appconnect:  %{time_appconnect}s\n
    time_pretransfer:  %{time_pretransfer}s\n
       time_redirect:  %{time_redirect}s\n
  time_starttransfer:  %{time_starttransfer}s\n
                     ----------\n
          time_total:  %{time_total}s\n
EOF
```

### nginx Error Logs

```bash
# Recent errors
tail -100 /var/log/nginx/error.log

# Odoo-specific log
tail -100 /var/log/nginx/odoo.error.log

# Search for 502 errors
grep "502" /var/log/nginx/access.log | tail -20
```

---

## 3. Odoo Application

### Internal Health Check (from container)

```bash
# Health endpoint
docker compose -f deploy/docker-compose.prod.yml exec -T odoo \
  curl -sS -o /dev/null -w '%{http_code}' http://localhost:8069/web/health

# Login page
docker compose -f deploy/docker-compose.prod.yml exec -T odoo \
  curl -sS -o /dev/null -w '%{http_code}' http://localhost:8069/web/login

# Assets
docker compose -f deploy/docker-compose.prod.yml exec -T odoo \
  curl -sS -o /dev/null -w '%{http_code}' http://localhost:8069/web/assets/debug/web.assets_backend.js
```

### Odoo Shell Commands

```bash
# Enter Odoo shell
docker compose -f deploy/docker-compose.prod.yml exec odoo odoo shell -d odoo

# One-liner: Check installed modules
docker compose -f deploy/docker-compose.prod.yml exec -T odoo \
  odoo shell -d odoo --no-http <<'EOF'
modules = env['ir.module.module'].search([('state', '=', 'installed')])
print(f"Installed modules: {len(modules)}")
for m in modules.filtered(lambda x: x.name.startswith('ipai')):
    print(f"  {m.name}: {m.installed_version}")
EOF

# Check base URL
docker compose -f deploy/docker-compose.prod.yml exec -T odoo \
  odoo shell -d odoo --no-http <<'EOF'
url = env['ir.config_parameter'].get_param('web.base.url')
print(f"Base URL: {url}")
EOF
```

### Odoo Config

```bash
# View odoo.conf
docker compose -f deploy/docker-compose.prod.yml exec odoo cat /etc/odoo/odoo.conf

# Key settings
docker compose -f deploy/docker-compose.prod.yml exec odoo \
  grep -E "proxy_mode|workers|limit_time|db_" /etc/odoo/odoo.conf
```

---

## 4. Database Connectivity

### PostgreSQL Health

```bash
# Check if accepting connections
docker compose -f deploy/docker-compose.prod.yml exec -T db \
  pg_isready -U odoo -d odoo

# Simple query test
docker compose -f deploy/docker-compose.prod.yml exec -T db \
  psql -U odoo -d odoo -c "SELECT 1;"

# Database size
docker compose -f deploy/docker-compose.prod.yml exec -T db \
  psql -U odoo -d odoo -c "SELECT pg_size_pretty(pg_database_size('odoo'));"
```

### Connection Stats

```bash
# Active connections
docker compose -f deploy/docker-compose.prod.yml exec -T db \
  psql -U odoo -d odoo -c "SELECT count(*) FROM pg_stat_activity;"

# Connection details
docker compose -f deploy/docker-compose.prod.yml exec -T db \
  psql -U odoo -d odoo -c "SELECT usename, application_name, client_addr, state FROM pg_stat_activity WHERE datname='odoo';"

# Max connections
docker compose -f deploy/docker-compose.prod.yml exec -T db \
  psql -U odoo -c "SHOW max_connections;"
```

### Module State

```bash
# Installed IPAI modules
docker compose -f deploy/docker-compose.prod.yml exec -T db \
  psql -U odoo -d odoo -c "SELECT name, state, latest_version FROM ir_module_module WHERE name LIKE 'ipai%' ORDER BY name;"

# Ship bundle modules specifically
docker compose -f deploy/docker-compose.prod.yml exec -T db \
  psql -U odoo -d odoo -c "SELECT name, state FROM ir_module_module WHERE name IN ('ipai_theme_aiux', 'ipai_aiux_chat', 'ipai_ask_ai', 'ipai_document_ai', 'ipai_expense_ocr');"

# Count installed vs total
docker compose -f deploy/docker-compose.prod.yml exec -T db \
  psql -U odoo -d odoo -c "SELECT state, count(*) FROM ir_module_module GROUP BY state ORDER BY count DESC;"
```

---

## 5. Cron / Job Queue Status

### Check Cron Jobs

```bash
# Active cron jobs
docker compose -f deploy/docker-compose.prod.yml exec -T db \
  psql -U odoo -d odoo -c "SELECT name, active, interval_number, interval_type, nextcall FROM ir_cron WHERE active=true ORDER BY nextcall LIMIT 20;"

# Cron execution history (if logged)
docker compose -f deploy/docker-compose.prod.yml logs odoo | grep -i cron | tail -20
```

### Queue Job Status (if using OCA queue_job)

```bash
# Pending jobs
docker compose -f deploy/docker-compose.prod.yml exec -T db \
  psql -U odoo -d odoo -c "SELECT state, count(*) FROM queue_job GROUP BY state;" 2>/dev/null || echo "queue_job not installed"

# Failed jobs
docker compose -f deploy/docker-compose.prod.yml exec -T db \
  psql -U odoo -d odoo -c "SELECT id, name, state, exc_info FROM queue_job WHERE state='failed' LIMIT 10;" 2>/dev/null
```

### OCR Queue Status (ipai_expense_ocr)

```bash
# OCR processing state
docker compose -f deploy/docker-compose.prod.yml exec -T db \
  psql -U odoo -d odoo -c "SELECT ocr_state, count(*) FROM hr_expense WHERE ocr_state IS NOT NULL GROUP BY ocr_state;" 2>/dev/null || echo "OCR fields not present"
```

---

## 6. Integration Tests

### Email (Mailgun)

```bash
# Test SMTP from container
docker compose -f deploy/docker-compose.prod.yml exec -T odoo python3 <<'EOF'
import smtplib
import os
try:
    s = smtplib.SMTP('smtp.mailgun.org', 587, timeout=10)
    s.starttls()
    s.login(os.getenv('MAILGUN_SMTP_LOGIN', 'test'), os.getenv('MAILGUN_SMTP_PASSWORD', 'test'))
    s.quit()
    print("SMTP OK")
except Exception as e:
    print(f"SMTP FAIL: {e}")
EOF
```

### OCR Service

```bash
# Health check
docker compose -f deploy/docker-compose.prod.yml exec -T odoo \
  curl -sS -o /dev/null -w '%{http_code}' "${OCR_SERVICE_URL:-http://localhost:8080}/health"
```

---

## 7. Full Verification Script

Run the complete verification:

```bash
# Using repo scripts
./scripts/deploy/verify_prod.sh
./scripts/aiux/verify_install.sh
./scripts/aiux/verify_assets.sh
```

---

## 8. Quick Diagnostic One-Liner

Run this for a quick health summary:

```bash
echo "=== Container Status ===" && \
docker compose -f deploy/docker-compose.prod.yml ps && \
echo -e "\n=== Health Checks ===" && \
echo -n "Login: " && curl -sS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8069/web/login && \
echo -n "Health: " && curl -sS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8069/web/health && \
echo -e "\n=== DB Connection ===" && \
docker compose -f deploy/docker-compose.prod.yml exec -T db pg_isready -U odoo -d odoo && \
echo -e "\n=== Ship Modules ===" && \
docker compose -f deploy/docker-compose.prod.yml exec -T db psql -U odoo -d odoo -t -c "SELECT name || ': ' || state FROM ir_module_module WHERE name IN ('ipai_theme_aiux', 'ipai_aiux_chat', 'ipai_ask_ai', 'ipai_document_ai', 'ipai_expense_ocr');"
```

---

## 9. Environment Information

Capture this for support/debugging:

```bash
echo "=== System Info ===" && \
uname -a && \
echo -e "\n=== Docker Version ===" && \
docker --version && \
docker compose version && \
echo -e "\n=== Git Info ===" && \
git rev-parse HEAD && \
git describe --tags --always && \
echo -e "\n=== Container Versions ===" && \
docker compose -f deploy/docker-compose.prod.yml images
```

---

*Last updated: 2026-01-08*
