# Edge Infrastructure Runbook: Nginx + Cloudflare

> SSOT: `ssot/edge/nginx_cloudflare_map.yaml`
> Audit: `scripts/edge/audit_nginx_cloudflare.sh`
> DNS SSOT: `infra/dns/subdomain-registry.yaml`

## Architecture Overview

```
Client → Cloudflare (CDN + WAF + TLS termination)
       → Origin nginx (reverse proxy + optional TLS)
       → Upstream service (Odoo, OCR, n8n, etc.)
```

### Local Dev Stack

```
Browser → localhost:80 → ipai-nginx container → odoo:8069 (Odoo)
                                              → odoo:8072 (longpoll/websocket)

Browser → localhost:8088 → superset:8088 (direct, no nginx)
Browser → localhost:5679 → n8n:5678 (direct, no nginx)
Browser → localhost:3333 → mcp_gateway:3333 (direct, no nginx)
```

**Compose files:**

| File | Services | Nginx? |
|------|----------|--------|
| `docker-compose.yml` | db, redis, odoo, **nginx**, pgadmin, mailpit | Yes (port 80) |
| `docker-compose.dev.yml` | + superset, n8n, mcp_gateway | No additional nginx |

**Local nginx config mount:**

| Host Path | Container Path |
|-----------|---------------|
| `ipai-platform/nginx/nginx.conf` | `/etc/nginx/nginx.conf` |
| `ipai-platform/nginx/conf.d/` | `/etc/nginx/conf.d/` |

**Effective local config:** `ipai-platform/nginx/conf.d/default.conf`
- `server_name localhost`
- upstream `odoo:8069` (HTTP), `odoo:8072` (longpoll)
- WebSocket on `/websocket` (Upgrade + Connection headers)
- Longpoll on `/longpolling` (no buffering)
- Static cache on `/web/static/` (24h expires)
- `client_max_body_size 100M`

### Production Stack

```
Client → Cloudflare (proxied, orange cloud)
       → 178.128.112.214:443 (nginx, Let's Encrypt TLS)
       → 127.0.0.1:8069 (Odoo) or :8072 (longpoll) or :8001 (OCR) etc.
```

**Prod nginx vhosts (synced from prod 2026-03-04):**

| Hostname | Repo Config | TLS | Upstream | Prod Path |
|----------|------------|-----|----------|-----------|
| insightpulseai.com | `infra/deploy/nginx/insightpulseai.com.conf` | LE (SAN cert) | 127.0.0.1:8069 / :8072 | sites-enabled |
| ocr.insightpulseai.com | `infra/nginx/ocr.insightpulseai.com.conf` | LE (separate) | 127.0.0.1:8001 | sites-enabled |
| n8n.insightpulseai.com | `infra/nginx/n8n.insightpulseai.com.conf` | LE (74d valid) | 127.0.0.1:5678 | sites-enabled |
| mcp.insightpulseai.com | `infra/nginx/mcp.insightpulseai.com.conf` | LE (74d valid) | 127.0.0.1:8766 | sites-enabled |
| plane.insightpulseai.com | `infra/nginx/plane.insightpulseai.com.conf` | Custom cert (`/etc/ssl/plane/`) | 127.0.0.1:3002 | **conf.d** |
| superset.insightpulseai.com | `infra/nginx/superset.insightpulseai.com.conf` | LE (SAN cert, shared with apex) | 127.0.0.1:8088 | sites-enabled |
| shelf.insightpulseai.com | N/A (placeholder) | None (HTTP only) | None (503) | sites-enabled |

**Prod nginx on droplet:** Mix of `/etc/nginx/sites-enabled/` (symlinks) and `/etc/nginx/conf.d/` (plane)

## Drift Audit

### Run locally (no external access)

```bash
bash scripts/edge/audit_nginx_cloudflare.sh
```

Checks: SSOT shape, local compose nginx, config file existence, upstream targets, proxy headers, WebSocket headers, vhost inventory.

### Run with prod SSH

```bash
SSH_HOST=root@178.128.112.214 bash scripts/edge/audit_nginx_cloudflare.sh
```

Additional: captures `nginx -T` from prod, compares server_name directives against expected hostnames.

### Run with Cloudflare API

```bash
CF_API_TOKEN=xxx CF_ZONE_ID=yyy bash scripts/edge/audit_nginx_cloudflare.sh
```

Additional: fetches DNS records, compares record types (A/CNAME) and proxy status against SSOT, checks SSL mode.

### Full audit

```bash
SSH_HOST=root@178.128.112.214 \
CF_API_TOKEN=xxx \
CF_ZONE_ID=yyy \
bash scripts/edge/audit_nginx_cloudflare.sh
```

### Output

| File | Format | Purpose |
|------|--------|---------|
| `docs/evidence/edge_drift_<ts>.md` | Markdown | Human-readable evidence |
| `ssot/edge/drift_report.json` | JSON | Machine-readable for CI/agents |

## Log Collection

### Where to find logs

| Source | Local | Production |
|--------|-------|------------|
| nginx access | `docker compose logs nginx` | `/var/log/nginx/<hostname>.access.log` |
| nginx error | `docker compose logs nginx` | `/var/log/nginx/<hostname>.error.log` |
| Odoo app | `docker compose logs odoo` | `docker logs odoo-erp-prod` |
| Cloudflare | N/A | Cloudflare dashboard → Analytics → Ray ID |
| TLS/cert | N/A | `certbot certificates` on droplet |

### Incident evidence pack (collect all of these)

For any edge-related incident, gather:

```bash
# 1. Cloudflare Ray ID (from response headers)
curl -sI https://hostname | grep -i cf-ray

# 2. Response headers (status, server, encoding)
curl -sIv https://hostname 2>&1 | head -30

# 3. nginx access log (last 50 lines for hostname)
ssh root@178.128.112.214 "tail -50 /var/log/nginx/hostname.access.log"

# 4. nginx error log (last 20 lines)
ssh root@178.128.112.214 "tail -20 /var/log/nginx/hostname.error.log"

# 5. Odoo logs around request time
ssh root@178.128.112.214 "docker logs --since=5m odoo-erp-prod 2>&1 | tail -50"

# 6. DNS resolution check
dig +short hostname
dig +short hostname @8.8.8.8

# 7. Origin direct check (bypass Cloudflare)
curl -sI --resolve hostname:443:178.128.112.214 https://hostname
```

## Failure Mode Catalog

### FM-NGINX-CSS-404: CSS/JS assets return 404

**Symptoms:** Odoo UI unstyled, browser console shows 404 for `/web/assets/web.assets_*.min.css`

**Triage:**
```bash
# Check if Odoo serves assets directly
curl -sI http://127.0.0.1:8069/web/assets/web.assets_frontend.min.css

# Check if nginx proxies correctly
curl -sI http://localhost/web/assets/web.assets_frontend.min.css

# Check via Cloudflare
curl -sI https://insightpulseai.com/web/assets/web.assets_frontend.min.css
```

**Likely causes:**
1. `location /web/assets` not proxied to Odoo upstream → fix nginx config
2. Odoo asset bundle not compiled → restart Odoo: `docker compose restart odoo`
3. `proxy_cache` serving stale 404 → purge cache or disable caching temporarily
4. Cloudflare serving cached 404 → purge Cloudflare cache for the URL
5. `gzip_types` missing `text/css` or `application/javascript` → add to nginx http block

**Resolution:** Check each layer from origin outward. Odoo → nginx → Cloudflare.

### FM-CF-SSL-LOOP: ERR_TOO_MANY_REDIRECTS

**Symptoms:** Browser infinite redirect loop, `curl -L` shows 301 chain

**Triage:**
```bash
# Check redirect chain
curl -sIL https://insightpulseai.com 2>&1 | grep -E 'HTTP|Location'

# Check what origin returns for HTTP
curl -sI http://127.0.0.1:8069/ | grep Location

# Check X-Forwarded-Proto handling
curl -sI -H 'X-Forwarded-Proto: https' http://127.0.0.1:8069/
```

**Likely causes:**
1. CF SSL mode "Flexible" + nginx HTTP→HTTPS redirect = loop
   → Fix: Set CF SSL to "Full (strict)"
2. nginx always redirects to HTTPS + CF always sends HTTP to origin = loop
   → Fix: Use `X-Forwarded-Proto` to detect CF-terminated HTTPS
3. Odoo `proxy_mode = True` not set → Odoo ignores X-Forwarded-Proto
   → Fix: Ensure `proxy_mode = True` in odoo.conf

**Resolution:** CF SSL must be "Full" or "Full (strict)". Origin must either serve HTTPS or correctly interpret X-Forwarded-Proto.

### FM-WEBSOCKET-BUS-BREAK: Longpolling/bus not working

**Symptoms:** Odoo Discuss messages delayed, notifications not real-time, console WS errors

**Triage:**
```bash
# Test longpoll endpoint directly
curl -sI http://127.0.0.1:8072/longpolling/poll

# Test WebSocket upgrade
curl -sI -H 'Upgrade: websocket' -H 'Connection: Upgrade' http://127.0.0.1:8072/

# Check nginx config for /longpolling
grep -A5 'longpolling' /etc/nginx/sites-enabled/insightpulseai.com
```

**Likely causes:**
1. nginx missing `proxy_http_version 1.1` on /longpolling
2. nginx missing `Upgrade` and `Connection "upgrade"` headers
3. Odoo gevent worker not running on port 8072
4. `proxy_buffering on` for longpoll location (must be off)
5. Cloudflare WebSocket not enabled (check CF dashboard → Network → WebSockets)

**Resolution:** Ensure nginx /longpolling location has all WebSocket headers. Verify Odoo `--workers` > 0 and gevent process listens on 8072.

### FM-UPLOAD-413: File upload rejected (413)

**Symptoms:** Large file upload fails, OCR image upload rejected

**Triage:**
```bash
# Check nginx body size limit
grep client_max_body_size /etc/nginx/sites-enabled/*

# Check Cloudflare plan upload limit (100MB free, 500MB pro)
# Check in CF dashboard → Rules → Upload limit

# Test with known size
dd if=/dev/zero bs=1M count=50 | curl -X POST -d @- http://127.0.0.1:8069/web/binary/upload
```

**Likely causes:**
1. nginx `client_max_body_size` too low (default 1M) → set to 100M
2. Cloudflare upload limit (100MB on free plan)
3. Odoo `limit_memory_hard` too low for large file processing

### FM-ORIGIN-502: Bad Gateway

**Symptoms:** 502 from nginx (or CF 502 page if proxied)

**Triage:**
```bash
# Is Odoo running?
docker compose ps
curl -sI http://127.0.0.1:8069/web/health

# Check Odoo logs for crashes
docker compose logs --tail=50 odoo

# Check for OOM kills
dmesg | tail -20 | grep -i oom
docker inspect odoo-core --format '{{.State.OOMKilled}}'

# Check nginx error log
tail -20 /var/log/nginx/insightpulseai.com.error.log
```

**Likely causes:**
1. Odoo container crashed or not running
2. Odoo OOM killed (increase `--limit-memory-hard` or container memory)
3. Port mismatch (nginx expects 8069 but Odoo bound elsewhere)
4. All Odoo workers busy (increase `--workers`)

### FM-NGINX-VHOST-MISSING: Subdomain shows default page

**Symptoms:** Subdomain shows nginx default "Welcome" page or wrong site

**Triage:**
```bash
# What does nginx serve for this hostname?
curl -sI -H "Host: plane.insightpulseai.com" http://127.0.0.1/

# Is there a vhost?
ls /etc/nginx/sites-enabled/ | grep plane
nginx -T | grep 'server_name.*plane'
```

**Likely causes:**
1. No vhost config created for this subdomain
2. Config exists in sites-available but not symlinked to sites-enabled
3. nginx not reloaded after adding config (`nginx -t && systemctl reload nginx`)

### FM-DNS-TYPE-DRIFT: Record type mismatch

**Symptoms:** SSOT says CNAME but Cloudflare has A (or vice versa)

**Triage:**
```bash
# Check actual DNS
dig +short mcp.insightpulseai.com
dig +short mcp.insightpulseai.com @1.1.1.1

# Check SSOT
grep -A10 'mcp' ssot/edge/nginx_cloudflare_map.yaml | grep dns_type

# Run drift audit
bash scripts/edge/audit_nginx_cloudflare.sh
```

**Resolution:** Either update SSOT to match reality, or run Terraform apply to fix Cloudflare.

### FM-MAIL-SPLIT-BRAIN: Dual Mailgun + Zoho routing

**Symptoms:** Some emails via Mailgun, others via Zoho; SPF alignment failures

**Triage:**
```bash
# Check Odoo outgoing mail server config
docker compose exec odoo odoo shell -c \
  "for s in self.env['ir.mail_server'].search([]): print(s.name, s.smtp_host)"

# Check which DNS records exist
dig TXT mg.insightpulseai.com +short
dig MX insightpulseai.com +short
```

**Current state:** Mailgun deprecated in intent (2026-02-01) but E2E verified live (2026-02-26). Zoho MX active. Both SPF includes present. Remove Mailgun DNS only after `ipai_mail_bridge_zoho` handles all send paths.

## Cloudflare Configuration

### Zone-level settings (expected)

| Setting | Expected Value | Notes |
|---------|---------------|-------|
| SSL/TLS | Full (strict) | Origin must serve valid TLS |
| Always Use HTTPS | On | Redirects HTTP→HTTPS at edge |
| HTTP/2 | On | Default for proxied zones |
| WebSockets | On | Required for Odoo bus |
| Minimum TLS | 1.2 | Block TLS 1.0/1.1 |
| HSTS | On | Via nginx header, not CF |

### Per-hostname proxy status

| Hostname | Proxied (orange cloud) | DNS-only (gray) |
|----------|----------------------|-----------------|
| insightpulseai.com | Orange | |
| www | Orange | |
| erp | Orange | |
| n8n | Orange | |
| ocr | Orange | |
| plane | Orange | |
| superset | Orange | |
| mcp | Orange | |
| mail | | Gray (DNS-only, no proxy) |
| agent | | Gray (CNAME to DO AI) |

### Known drift items

| Item | Tracking | Resolution | Date |
|------|----------|------------|------|
| mcp DNS type | DRIFT-MCP-DNS-TYPE | A record is correct (MCP on droplet, not DO App Platform). DNS SSOT updated. | 2026-03-04 |
| n8n origin TLS | DRIFT-N8N-HTTPS | Prod already had LE cert. Repo synced to match. | 2026-03-04 |
| mcp origin TLS | DRIFT-MCP-HTTPS | Prod already had LE cert. Repo synced to match. | 2026-03-04 |
| mcp port | DRIFT-MCP-PORT | Port confirmed as 8766 (not 8000). Repo updated. | 2026-03-04 |
| plane vhost | DRIFT-PLANE-VHOST | Prod had vhost in conf.d with custom cert. Repo synced. | 2026-03-04 |
| superset vhost | DRIFT-SUPERSET-VHOST | Prod had vhost in sites-enabled with SAN cert. Repo synced. | 2026-03-04 |
| superset stale conf.d | DRIFT-SUPERSET-STALE-CONFD | Stale .net config removed from prod. | 2026-03-04 |

**All drift items resolved.** No open items remain.

### Training data generation

```bash
# Generate agent troubleshooting training data from latest drift report
bash scripts/edge/generate_training_data.sh
# Output: datasets/agent_troubleshoot/edge/<timestamp>.json
```

## Quick Commands

```bash
# Local: start stack
make up

# Local: check nginx
docker compose exec nginx nginx -T

# Local: test Odoo through nginx
curl -sI http://localhost/web/health

# Prod: check nginx config
ssh root@178.128.112.214 "nginx -T | grep server_name"

# Prod: reload nginx after config change
ssh root@178.128.112.214 "nginx -t && systemctl reload nginx"

# Prod: check certbot certs
ssh root@178.128.112.214 "certbot certificates"

# Prod: renew certs
ssh root@178.128.112.214 "certbot renew --dry-run"

# Full drift audit
bash scripts/edge/audit_nginx_cloudflare.sh
```
