# Edge Local Context — Discovery Summary

> Generated: 2026-03-03
> Agent: Claude Code edge infrastructure audit

## Discovered Files and Roles

### Docker Compose (nginx service)

| File | Role | Nginx Service |
|------|------|---------------|
| `docker-compose.yml` | SSOT compose (project: ipai) | `nginx` (port 80, image nginx:1.27-alpine) |
| `docker-compose.dev.yml` | Dev overlay (includes SSOT) | No additional nginx |
| `.devcontainer/docker-compose.devcontainer.yml` | DevContainer overlay | No nginx changes |

### Local Nginx Config

| Host Path | Container Path | Purpose |
|-----------|---------------|---------|
| `ipai-platform/nginx/nginx.conf` | `/etc/nginx/nginx.conf` | Main config (worker, gzip, includes) |
| `ipai-platform/nginx/conf.d/default.conf` | `/etc/nginx/conf.d/default.conf` | Odoo reverse proxy (localhost:80) |
| `ipai-platform/nginx/conf.d/sites/odoo-prod.conf.disabled` | N/A | Disabled prod-like config |

### Local nginx effective config summary

```
nginx.conf:
  worker_processes auto
  worker_connections 4096
  gzip on (level 6, text/plain text/css application/json application/javascript)
  server_tokens off
  include /etc/nginx/conf.d/*.conf

default.conf:
  listen 80
  server_name localhost
  upstream odoo_backend → odoo:8069 (keepalive 32)
  upstream odoo_longpolling → odoo:8072 (keepalive 16)
  /              → proxy_pass http://odoo_backend
  /longpolling   → proxy_pass http://odoo_longpolling (no buffering)
  /websocket     → proxy_pass http://odoo_longpolling (WS upgrade headers)
  /web/static/   → proxy_pass http://odoo_backend (24h expires)
  /nginx-health  → return 200 "healthy"
  client_max_body_size 100M
  proxy timeouts: 720s (connect, send, read)
  headers: Host, X-Real-IP, X-Forwarded-For, X-Forwarded-Proto, X-Forwarded-Host
```

### Production Nginx Configs (in repo)

| File | Hostname | HTTPS | Upstream | Status |
|------|----------|-------|----------|--------|
| `infra/deploy/nginx/insightpulseai.com.conf` | insightpulseai.com, www, erp | Let's Encrypt (443 ssl http2) | 127.0.0.1:8069 / :8072 | Complete |
| `infra/nginx/ocr.insightpulseai.com.conf` | ocr.insightpulseai.com | Let's Encrypt (separate cert) | 127.0.0.1:8001 | Complete |
| `infra/nginx/n8n.insightpulseai.com.conf` | n8n.insightpulseai.com | Let's Encrypt (certbot pending on prod) | localhost:5678 | Complete (repo) |
| `infra/nginx/mcp.insightpulseai.com.conf` | mcp.insightpulseai.com | Let's Encrypt (certbot pending on prod) | localhost:8000 (TODO) | Complete (repo) |
| `infra/nginx/plane.insightpulseai.com.conf` | plane.insightpulseai.com | Let's Encrypt (certbot pending on prod) | 127.0.0.1:3002 | Complete (repo) |
| `infra/nginx/superset.insightpulseai.com.conf` | superset.insightpulseai.com | Let's Encrypt (certbot pending on prod) | 127.0.0.1:8088 | Complete (repo) |
| `infra/deploy/nginx/erp.insightpulseai.net.conf` | erp.insightpulseai.net | Deprecated (.net domain) | N/A | Deprecated |

### Cloudflare SSOT Tooling (existing)

| File | Purpose |
|------|---------|
| `infra/dns/subdomain-registry.yaml` | DNS record SSOT (21+ entries) |
| `infra/cloudflare/envs/prod/main.tf` | Terraform for Cloudflare DNS |
| `scripts/generate-dns-artifacts.sh` | Generates Terraform + JSON from SSOT |
| `.github/workflows/dns-sync-check.yml` | CI gate for DNS artifact sync |

### New Edge SSOT Files (this session)

| File | Purpose |
|------|---------|
| `ssot/edge/nginx_cloudflare_map.yaml` | Nginx + Cloudflare per-hostname SSOT |
| `scripts/edge/audit_nginx_cloudflare.sh` | Drift audit (local + optional SSH + CF API) |
| `scripts/edge/generate_training_data.sh` | Convert drift report to agent training data |
| `docs/runbooks/EDGE_NGINX_CLOUDFLARE.md` | Failure mode catalog + log collection |
| `docs/evidence/EDGE_LOCAL_CONTEXT.md` | This file |
| `datasets/agent_troubleshoot/edge/*.json` | Generated training data (per audit run) |

## Key Findings

1. **Local dev nginx** is well-configured: proper upstreams, WebSocket support, proxy headers, body limits
2. **Prod nginx** has 6 complete vhost configs in repo (apex/erp, OCR, n8n, mcp, plane, superset)
3. **n8n, mcp, plane, superset** have HTTPS blocks in repo but require `certbot` on prod to activate
4. **MCP** has DNS type drift (A in CF, should be CNAME per SSOT) — open item
5. **Mailgun** is deprecated in intent but operationally live — 4 DNS records must remain until Zoho cutover complete
6. **Audit script** reports 0 FAIL in local mode (all vhosts present with HTTPS)
