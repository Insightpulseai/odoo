# Edge Prod Sync — Evidence Pack
**Date**: 2026-03-04T01:27+08:00
**Scope**: Sync repo nginx configs to prod reality, update SSOT, clean stale configs

---

## Summary

| Metric | Value |
|--------|-------|
| Audit result | **36 pass, 0 warn, 0 fail, 1 skip** |
| Hostnames validated (prod SSH) | 6/6 |
| External HTTPS checks | 4/4 responding |
| Stale configs removed | 1 (`conf.d/superset.conf` — deprecated .net) |
| SSOT version | 2 → 3 |

---

## Prod Discoveries (nginx -T + certbot certificates)

### Port Corrections
| Hostname | Repo (before) | Prod (actual) | Action |
|----------|---------------|---------------|--------|
| mcp.insightpulseai.com | 8000 (unconfirmed) | **8766** | Repo updated |
| n8n.insightpulseai.com | 5678 | 5678 | Confirmed, timeouts updated (300s→3600s) |

### TLS Corrections
| Hostname | Repo (before) | Prod (actual) | Action |
|----------|---------------|---------------|--------|
| plane.insightpulseai.com | LE cert assumed | **Custom cert** at `/etc/ssl/plane/` | Repo updated |
| superset.insightpulseai.com | Own LE cert assumed | **SAN cert** (shared `insightpulseai.com`) | Repo updated |
| n8n.insightpulseai.com | HTTP-only in repo | Already HTTPS with LE cert (74d valid) | Repo synced |
| mcp.insightpulseai.com | HTTP-only in repo | Already HTTPS with LE cert (74d valid) | Repo synced |

### Config Layout Corrections
| Hostname | Repo (before) | Prod (actual) | Action |
|----------|---------------|---------------|--------|
| plane.insightpulseai.com | sites-enabled | **conf.d/plane.conf** | Repo updated |
| superset.insightpulseai.com | sites-enabled | sites-enabled (correct) + stale conf.d | Stale removed |

### New Discovery
| Hostname | Status | Action |
|----------|--------|--------|
| shelf.insightpulseai.com | HTTP-only placeholder, 503 | Added to SSOT as known placeholder |

---

## Prod Cleanup

### Removed: `/etc/nginx/conf.d/superset.conf`
- **Reason**: Used deprecated `superset.insightpulseai.net` domain
- **Action**: Moved to `.bak.20260304`, nginx -t passed, nginx reloaded
- **Verification**: `nginx -t` → syntax ok, test successful

---

## External Validation (curl -sI)

| Hostname | HTTP Status | Meaning |
|----------|-------------|---------|
| https://n8n.insightpulseai.com | **200** | n8n UI serving |
| https://mcp.insightpulseai.com | **404** | MCP service alive (no route on /) |
| https://plane.insightpulseai.com | **200** | Plane UI serving |
| https://superset.insightpulseai.com | **302** → /superset/welcome/ | Superset redirect (expected) |

---

## Certbot Certificate State (prod)

| Certificate | Domains | Expiry | Valid Days |
|-------------|---------|--------|------------|
| insightpulseai.com | insightpulseai.com, erp, superset, www | 2026-05-12 | 69 |
| n8n.insightpulseai.com | n8n.insightpulseai.com | 2026-05-17 | 74 |
| mcp.insightpulseai.com | mcp.insightpulseai.com | 2026-05-17 | 74 |
| ocr.insightpulseai.com | ocr.insightpulseai.com | 2026-05-29 | 86 |
| plane.insightpulseai.com | N/A — custom cert at /etc/ssl/plane/ | Unknown | — |

---

## DNS SSOT Fix: MCP A Record

**Discovery**: DNS SSOT (`infra/dns/subdomain-registry.yaml`) defined MCP as `CNAME → pulse-hub-web-an645.ondigitalocean.app`, but prod nginx -T showed MCP runs on the droplet at `127.0.0.1:8766`. Cloudflare's A record (178.128.112.214) was **correct all along**.

**Fix**: Updated DNS SSOT from `type: CNAME` to `type: A` with `origin_port: 443`. Updated edge SSOT to close DRIFT-MCP-DNS-TYPE.

## All Drift Items — Resolved

| ID | Status |
|----|--------|
| DRIFT-N8N-HTTPS | Resolved |
| DRIFT-MCP-HTTPS | Resolved |
| DRIFT-MCP-PORT | Resolved |
| DRIFT-MCP-DNS-TYPE | Resolved |
| DRIFT-PLANE-VHOST | Resolved |
| DRIFT-SUPERSET-VHOST | Resolved |
| DRIFT-SUPERSET-STALE-CONFD | Resolved |

**Zero open drift items remain.**

---

## Files Changed (repo)

| File | Change |
|------|--------|
| `infra/nginx/n8n.insightpulseai.com.conf` | Synced to prod: port 5678, timeout 3600s, proxy_buffering off, security headers |
| `infra/nginx/mcp.insightpulseai.com.conf` | Synced to prod: port 8766, no WS headers, proxy_buffering off, security headers |
| `infra/nginx/plane.insightpulseai.com.conf` | Synced to prod: custom cert, upstream group plane_proxy, conf.d deployment |
| `infra/nginx/superset.insightpulseai.com.conf` | Synced to prod: SAN cert (insightpulseai.com), HSTS header |
| `ssot/edge/nginx_cloudflare_map.yaml` | v2→v3: all corrections, shelf added, drift items resolved |

---

## Audit Evidence

- **Drift report**: `ssot/edge/drift_report.json`
- **Evidence markdown**: `docs/evidence/edge_drift_20260304-0127+0800.md`
- **Prod nginx -T capture**: `docs/evidence/nginx_T_prod_20260304-0127+0800.txt`
