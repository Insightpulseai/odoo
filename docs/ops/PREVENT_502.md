# Preventing 502 Bad Gateway Errors in Odoo

## Overview

A **502 Bad Gateway** from nginx means nginx is up but the upstream (Odoo) isn't responding correctly. This guide covers the root causes specific to Odoo stacks and how to prevent them with deterministic checks.

---

## Why 502 Errors Happen (Root Causes)

### Cause 1: Odoo Container Down / Crash-Looping

**Symptoms:**
- Container shows "Restarting" status
- Logs show Python exceptions, OOM kills, or module errors
- `docker compose ps` shows unhealthy state

**Common triggers:**
- Bad module upgrade (syntax error, missing dependency)
- Out of memory (OOM) - Odoo workers consuming too much RAM
- Database authentication failure
- Missing Python dependencies
- Corrupted filestore or session data

**Detection:**
```bash
docker compose ps
docker compose logs --tail=200 odoo | grep -E "Error|Exception|Traceback|OOM|Killed"
```

**Prevention:**
- Health checks in docker-compose that fail fast
- Resource limits (memory, CPU)
- Module upgrade testing in staging before prod
- Automated rollback on health check failure

---

### Cause 2: Wrong Upstream Routing (nginx misconfiguration)

**Symptoms:**
- 502 on all routes
- nginx error log shows "upstream prematurely closed connection"
- Odoo container is healthy but nginx can't reach it

**Common triggers:**
- Container name mismatch (nginx points to wrong name)
- Port mismatch (8069 vs 8072)
- Docker network mismatch (containers on different networks)
- Host binding issues (localhost vs 0.0.0.0)

**Detection:**
```bash
# Check nginx error log
tail -100 /var/log/nginx/error.log

# Test upstream directly
curl -I http://127.0.0.1:8069/web/login
curl -I http://127.0.0.1:8072/longpolling/poll

# Check container networking
docker compose exec odoo curl -I http://localhost:8069/web/login
```

**Prevention:**
- Use explicit upstream definitions in nginx
- Test internal connectivity before enabling external traffic
- Use docker-compose service names consistently

---

### Cause 3: Longpolling / WebSocket Misrouted

**Symptoms:**
- 502 specifically on `/longpolling/*` or `/websocket`
- Chat, notifications, and real-time updates fail
- Main application works but feels "stuck"

**Common triggers:**
- Missing `/longpolling` location block in nginx
- Pointing `/longpolling` to port 8069 instead of 8072
- Missing WebSocket upgrade headers

**Detection:**
```bash
# Test longpolling route
curl -I https://erp.insightpulseai.com/longpolling/poll

# Check nginx config
grep -A5 "longpolling" /etc/nginx/sites-enabled/odoo.conf
```

**Prevention:**
Nginx config must include:
```nginx
upstream odoo-longpolling {
    server 127.0.0.1:8072;
}

location /longpolling {
    proxy_pass http://odoo-longpolling;
    proxy_redirect off;
}

location /websocket {
    proxy_pass http://odoo-longpolling;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 86400;
}
```

---

### Cause 4: Timeout Issues

**Symptoms:**
- 502/504 on long-running operations (reports, exports, imports)
- Intermittent 502s under load
- Operations start but never complete

**Common triggers:**
- `proxy_read_timeout` too low (default 60s is not enough)
- `proxy_connect_timeout` too aggressive
- Odoo worker timeout conflicts

**Detection:**
```bash
# Check nginx timeouts
grep -E "timeout|keepalive" /etc/nginx/sites-enabled/odoo.conf

# Check Odoo config
docker compose exec odoo cat /etc/odoo/odoo.conf | grep -E "limit_time|workers"
```

**Prevention:**
Nginx should have:
```nginx
proxy_read_timeout    720s;
proxy_connect_timeout 60s;
proxy_send_timeout    600s;
```

Odoo should have:
```ini
limit_time_cpu = 600
limit_time_real = 1200
```

---

### Cause 5: Database Connection Exhaustion

**Symptoms:**
- Intermittent 502s that correlate with high activity
- "too many connections" in Odoo logs
- PostgreSQL shows max connections reached

**Detection:**
```bash
# Check active connections
docker compose exec db psql -U odoo -d odoo -c "SELECT count(*) FROM pg_stat_activity;"

# Check max connections
docker compose exec db psql -U odoo -c "SHOW max_connections;"

# Check Odoo connection usage
docker compose logs odoo | grep -i "connection"
```

**Prevention:**
- Set appropriate `max_connections` in PostgreSQL (100-200 typical)
- Configure connection pooling (pgbouncer if needed)
- Monitor connection count with alerts
- Ensure idle connections are closed properly

---

### Cause 6: Memory Pressure (OOM)

**Symptoms:**
- Container killed and restarted
- `docker stats` shows high memory usage
- Kernel logs show OOM killer activity

**Detection:**
```bash
# Check memory usage
docker stats --no-stream

# Check for OOM events
dmesg | grep -i "oom\|killed"

# Check container limits
docker compose config | grep -A5 "deploy:"
```

**Prevention:**
- Set memory limits in docker-compose:
```yaml
deploy:
  resources:
    limits:
      memory: 4G
    reservations:
      memory: 1G
```
- Monitor memory usage with alerts
- Tune Odoo workers (`workers = 4` is typical for 8GB RAM)

---

### Cause 7: Proxy Mode / Base URL Mismatch

**Symptoms:**
- Redirect loops (ERR_TOO_MANY_REDIRECTS)
- Mixed content warnings
- OAuth fails with "redirect_uri mismatch"

**Detection:**
```bash
# Check Odoo config
docker compose exec odoo cat /etc/odoo/odoo.conf | grep proxy_mode

# Check system parameters
docker compose exec odoo odoo shell -d odoo -c "print(env['ir.config_parameter'].get_param('web.base.url'))"
```

**Prevention:**
- Set `proxy_mode = True` in odoo.conf
- Set correct `web.base.url` system parameter
- Ensure `X-Forwarded-Proto: https` header is passed
- Ensure `X-Forwarded-Host` header is set

---

## Deterministic Health Gates

To prevent 502s from reaching production, enforce these gates:

### Pre-Deploy Gate

```bash
#!/bin/bash
set -e

# Gate 1: Container starts successfully
docker compose up -d
sleep 30

# Gate 2: Internal health check
HEALTH=$(docker compose exec -T odoo curl -sS -o /dev/null -w '%{http_code}' http://localhost:8069/web/health)
if [ "$HEALTH" != "200" ]; then
    echo "FAIL: Health check returned $HEALTH"
    exit 1
fi

# Gate 3: Login page accessible
LOGIN=$(docker compose exec -T odoo curl -sS -o /dev/null -w '%{http_code}' http://localhost:8069/web/login)
if [ "$LOGIN" != "200" ] && [ "$LOGIN" != "303" ]; then
    echo "FAIL: Login page returned $LOGIN"
    exit 1
fi

# Gate 4: Assets compile successfully
ASSETS=$(docker compose exec -T odoo curl -sS -o /dev/null -w '%{http_code}' http://localhost:8069/web/assets/debug/web.assets_backend.js)
if [ "$ASSETS" != "200" ]; then
    echo "FAIL: Assets returned $ASSETS"
    exit 1
fi

# Gate 5: DB connectivity
docker compose exec -T db pg_isready -U odoo -d odoo

# Gate 6: No crash loop (stable for 60s)
sleep 60
RESTARTS=$(docker inspect --format='{{.RestartCount}}' odoo-ce)
if [ "$RESTARTS" -gt "0" ]; then
    echo "FAIL: Container restarted $RESTARTS times"
    exit 1
fi

echo "All health gates passed"
```

### Post-Deploy Verification

```bash
#!/bin/bash
set -e

BASE_URL="${1:-https://erp.insightpulseai.com}"

# External checks
curl -fsS -o /dev/null -w '%{http_code}' "$BASE_URL/web/login"
curl -fsS -o /dev/null -w '%{http_code}' "$BASE_URL/web/health"
curl -fsS -o /dev/null -w '%{http_code}' "$BASE_URL/longpolling/poll" || true  # 400 is OK

echo "External verification passed"
```

---

## Rollback Procedure

If 502s occur after deployment:

### Immediate (Same Image)

```bash
# Force module registry rebuild
docker compose exec odoo odoo -d odoo -u base,web --stop-after-init
docker compose restart odoo
```

### Full Rollback (Previous Tag)

```bash
# 1. Note current state
docker compose images odoo

# 2. Update to previous tag
# Edit .env: APP_IMAGE_VERSION=previous-tag

# 3. Deploy previous version
docker compose pull odoo
docker compose up -d odoo

# 4. Verify
./scripts/deploy/verify_prod.sh
```

### Database Rollback (Last Resort)

```bash
# 1. Stop services
docker compose down

# 2. Restore database
docker compose up -d db
docker compose exec -T db psql -U odoo -d postgres -c "DROP DATABASE IF EXISTS odoo;"
docker compose exec -T db psql -U odoo -d postgres -c "CREATE DATABASE odoo OWNER odoo;"
docker compose exec -T db psql -U odoo -d odoo < backup.sql

# 3. Restart all
docker compose up -d

# 4. Verify
./scripts/deploy/verify_prod.sh
```

---

## Monitoring Checklist

Set up alerts for:

| Metric | Threshold | Severity |
|--------|-----------|----------|
| HTTP 502 count | > 5 in 5 minutes | Critical |
| Container restart count | > 3 in 10 minutes | Critical |
| Response time p95 | > 10s | Warning |
| DB connection count | > 80% max | Warning |
| Memory usage | > 85% | Warning |
| Queue backlog | > 100 jobs | Warning |

---

## Quick Reference: nginx Config

Complete config that prevents most 502s:

```nginx
upstream odoo {
    server 127.0.0.1:8069;
}

upstream odoo-longpolling {
    server 127.0.0.1:8072;
}

server {
    listen 443 ssl http2;
    server_name erp.insightpulseai.com;

    # SSL
    ssl_certificate     /etc/letsencrypt/live/erp.insightpulseai.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/erp.insightpulseai.com/privkey.pem;

    # Timeouts (CRITICAL)
    proxy_read_timeout    720s;
    proxy_connect_timeout 60s;
    proxy_send_timeout    600s;

    # Headers (CRITICAL for proxy_mode)
    proxy_set_header Host              $host;
    proxy_set_header X-Real-IP         $remote_addr;
    proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto https;
    proxy_set_header X-Forwarded-Host  $host;

    client_max_body_size 64m;

    location / {
        proxy_pass http://odoo;
        proxy_redirect off;
    }

    # CRITICAL: Separate longpolling upstream
    location /longpolling {
        proxy_pass http://odoo-longpolling;
        proxy_redirect off;
    }

    # WebSocket support
    location /websocket {
        proxy_pass http://odoo-longpolling;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
```

---

*Last updated: 2026-01-08*
