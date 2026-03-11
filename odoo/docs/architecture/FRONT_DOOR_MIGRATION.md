# Azure Front Door Migration

Current edge: Cloudflare (DNS + proxy + WAF) + nginx reverse proxy on DO droplet (178.128.112.214).
Target edge: Azure Front Door Premium + Azure Container Apps backends. Cloudflare retains DNS authority but proxying moves to Front Door.

---

## Architecture: Before and After

```
BEFORE (current)
================

  Client
    |
    v
  Cloudflare (orange-cloud proxy)
    |  TLS termination
    |  WAF (managed + page rules)
    |  Cache (page rules + cache rules)
    v
  178.128.112.214 (DO droplet)
    |
    v
  nginx (reverse proxy)
    |--- :8069 --> Odoo CE 19
    |--- :5678 --> n8n
    |--- :8088 --> Superset
    |--- :8001 --> PaddleOCR
    |--- :3002 --> Plane
    |--- :3003 --> Shelf
    |--- :3004 --> CRM
    |--- :8080 --> Auth
    |--- :8766 --> MCP


AFTER (target)
==============

  Client
    |
    v
  Cloudflare (DNS-only, grey-cloud)
    |  CNAME --> *.azurefd.net
    v
  Azure Front Door Premium
    |  TLS termination (Azure-managed certs)
    |  WAF (Front Door WAF policy)
    |  Cache (route-level caching rules)
    |  WebSocket upgrade (/websocket, /longpolling)
    v
  Azure Container Apps (backend pool)
    |--- erp.insightpulseai.com    --> Odoo container
    |--- n8n.insightpulseai.com    --> n8n container
    |--- superset.insightpulseai.com --> Superset container
    |--- ocr.insightpulseai.com    --> PaddleOCR container
    |--- plane.insightpulseai.com  --> Plane container
    |--- shelf.insightpulseai.com  --> Shelf container
    |--- crm.insightpulseai.com    --> CRM container
    |--- auth.insightpulseai.com   --> Auth container
    |--- mcp.insightpulseai.com    --> MCP container
```

---

## WAF Rule Mapping

Each Cloudflare WAF/security rule mapped to its Front Door WAF policy equivalent.

| # | Cloudflare Rule | Cloudflare Config | Front Door Equivalent | Front Door Config |
|---|----------------|-------------------|----------------------|-------------------|
| 1 | XML-RPC managed challenge | Page rule: `*insightpulseai.com/xmlrpc/*` security_level=high | Custom WAF rate limit rule | Match: `RequestUri contains /xmlrpc/`. Action: rate limit (100 req/min per IP), then block. Priority 10. |
| 2 | Block AI crawlers | WAF managed rule (verified bots) | Custom WAF rule on User-Agent | Match: `RequestHeader["User-Agent"] contains "GPTBot" OR "CCBot" OR "anthropic-ai" OR "ClaudeBot" OR "Google-Extended"`. Action: Block. Priority 20. |
| 3 | Health check WAF bypass | No explicit rule (Cloudflare skips managed rules for known monitors) | WAF exclusion for health paths | Exclusion rule: `RequestUri in {"/web/health", "/web/login", "/healthz", "/health", "/healthcheck", "/api/health"}`. Action: Allow (bypass WAF). Priority 1. |
| 4 | Browser integrity check | Zone setting: `browser_check=on` | Bot protection (Front Door Premium) | Enable bot protection managed rule set. Mode: Prevention. |
| 5 | TLS minimum 1.2 | Zone setting: `min_tls_version=1.2` | Front Door TLS policy | `minimumTlsVersion: "1.2"` on custom domain configuration. |
| 6 | Security headers | Transform rule: X-Content-Type-Options, X-Frame-Options, Referrer-Policy | Rules Engine response headers | Rules Engine rule: add response headers `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, `Referrer-Policy: strict-origin-when-cross-origin`. |

Source for current Cloudflare rules: `infra/cloudflare/cloudflare-cache-rules.json`.

---

## Cache Rule Mapping

| # | Cloudflare/nginx Rule | Path Pattern | TTL | Front Door Equivalent | Front Door TTL |
|---|----------------------|--------------|-----|----------------------|----------------|
| 1 | Cache Odoo static assets | `/web/static/*`, `/web/image/*`, `*.js`, `*.css`, `*.woff2`, etc. | Edge: 1d, Browser: 1h | Route-level caching rule | `cacheDuration: P30D`, `queryStringCachingBehavior: IgnoreQueryString` |
| 2 | Cache content/images | `/web/content/*` (page rule) | Edge: 7d, Browser: 1d | Route-level caching rule | `cacheDuration: P7D`, `queryStringCachingBehavior: UseQueryString`, vary on `Cookie` header |
| 3 | Dynamic bypass | `/web/login`, `/web/session`, `/web/webclient`, `/web/action`, `/web/dataset`, `/longpolling/*`, `/xmlrpc/*`, `/jsonrpc` | No cache | Disable caching | `enableCaching: false` on matching route |
| 4 | nginx static fallback | `location ~* \.(js|css|png|jpg|woff2)$` with `expires 30d` | 30d | Covered by rule 1 above | Included in P30D static rule |

Source: `infra/cloudflare/cloudflare-cache-rules.json`, nginx vhost configs in `infra/deploy/nginx/`.

---

## TLS Certificate Strategy

Azure Front Door manages TLS certificates automatically for custom domains.

| Item | Configuration |
|------|--------------|
| Certificate type | Azure-managed (Front Door managed) |
| CA | DigiCert (via Microsoft) |
| Validation | CNAME-based domain validation (TXT record `_dnsauth.<hostname>`) |
| Auto-renewal | Yes, handled by Front Door |
| Minimum TLS | 1.2 |
| Cipher suites | Front Door default (TLS 1.2+ with AEAD ciphers) |

Process per hostname:
1. Add custom domain in Front Door profile.
2. Front Door generates a `_dnsauth.<hostname>` TXT validation record.
3. Create TXT record in Cloudflare DNS (grey-cloud, DNS-only).
4. Front Door validates ownership and provisions certificate.
5. Certificate auto-renews before expiry.

No manual cert management, no Let's Encrypt, no certbot.

---

## WebSocket Support

Odoo uses long-polling and WebSocket connections for real-time bus notifications.

| Path | Protocol | Current (nginx) | Front Door Config |
|------|----------|-----------------|-------------------|
| `/websocket` | WebSocket (wss://) | `proxy_pass` with `Upgrade` headers | Enable WebSocket on the route. Front Door supports WebSocket natively on Premium SKU. Set `originResponseTimeoutSeconds: 240`. |
| `/longpolling/poll` | HTTP long-poll | `proxy_pass` to `:8072` (gevent) | Route to dedicated backend pool (Odoo longpoll container). Set `originResponseTimeoutSeconds: 120`. Disable caching. |

Front Door Premium supports WebSocket without additional configuration beyond enabling it on the route. The key constraint is the origin response timeout: Odoo long-poll connections can hold for 50-60 seconds, so the timeout must exceed this.

---

## Cutover Sequence

Hostnames are cut over in waves to limit blast radius. The wave definitions and per-hostname checklist live in `ssot/azure/hostname-cutover-checklist.yaml`.

### Wave Approach

| Wave | Hostnames | Criteria | Rollback Window |
|------|-----------|----------|-----------------|
| wave0-canary | One low-risk hostname (e.g., `shelf.insightpulseai.com`) | Validate Front Door routing, TLS, headers | 24h |
| wave1-core | `erp`, `n8n`, `auth` | Core business services, validated in wave0 | 4h |
| wave2-support | `superset`, `ocr`, `plane`, `crm`, `mcp` | Supporting services | 24h |
| wave3-edge | `ops`, `agent`, `cdn`, staging hostnames | Edge/non-critical | 48h |

### Per-Hostname Cutover Steps

1. **Pre-flight**: Container Apps backend is healthy, Front Door origin group configured.
2. **DNS switch**: In Cloudflare, change record from A (178.128.112.214) to CNAME (`<profile>.azurefd.net`). Disable orange-cloud proxy (set to DNS-only/grey-cloud).
3. **Validation**: Run `scripts/azure/validate-front-door-cutover.sh --hostname <hostname>`.
4. **Monitor**: Watch Azure Monitor for 4xx/5xx spike, latency anomalies for the rollback window duration.
5. **Confirm**: Mark hostname as `status: cutover_complete` in `ssot/azure/hostname-cutover-checklist.yaml`.

---

## Rollback Procedure

Any hostname can be rolled back independently by repointing DNS.

### Steps

1. In Cloudflare DNS, change the hostname record:
   - **From**: CNAME to `<profile>.azurefd.net` (DNS-only)
   - **To**: A record to `178.128.112.214` (orange-cloud proxy on)
2. DNS propagation: typically < 5 minutes with Cloudflare TTL.
3. Verify: `dig +short <hostname>` returns `178.128.112.214`.
4. Verify: `curl -sI https://<hostname>/ | grep server` shows nginx, not Front Door.
5. Update `ssot/azure/hostname-cutover-checklist.yaml`: set `status: rolled_back` with timestamp and reason.
6. Commit evidence to `docs/evidence/<YYYYMMDD-HHMM>/front-door-rollback/`.

### Rollback does NOT require

- Any Azure-side changes (Front Door config stays intact).
- Any Container Apps changes (containers keep running).
- Any nginx changes on the DO droplet (nginx config is unchanged during cutover).

The DO droplet + nginx stack remains fully operational throughout the migration as a warm standby.

---

## DNS Transition

Cloudflare remains the authoritative DNS provider. The change is in how records point to the backend.

### Before (current state)

```
erp.insightpulseai.com  -->  A  178.128.112.214  (proxied, orange-cloud)
```

Cloudflare terminates TLS, applies WAF, caches, then forwards to origin IP.

### After (target state)

```
erp.insightpulseai.com  -->  CNAME  ipai-fd.azurefd.net  (DNS-only, grey-cloud)
```

Front Door terminates TLS, applies WAF, caches, then forwards to Container Apps backend.

### Key DNS Rules

1. **Disable Cloudflare proxy** (grey-cloud) for all Front Door hostnames. Double-proxying (Cloudflare -> Front Door) causes TLS and header conflicts.
2. **CNAME flattening**: Cloudflare CNAME flattening at apex (`insightpulseai.com`) is supported but Front Door requires explicit CNAME validation. Use a subdomain CNAME where possible.
3. **TTL**: Set Cloudflare DNS TTL to 60s during cutover window. Revert to 300s after confirmation.
4. **TXT validation records**: `_dnsauth.<hostname>.insightpulseai.com` TXT records for Front Door domain validation. These persist indefinitely alongside the CNAME.

### SSOT Updates

All DNS changes follow the existing workflow:
1. Edit `infra/dns/subdomain-registry.yaml` (update target, set `cloudflare_proxied: false`).
2. Run `scripts/dns/generate-dns-artifacts.sh`.
3. Commit generated artifacts.
4. CI applies via Terraform on merge to main.

---

## Monitoring

### Azure Monitor Metrics (Front Door)

| Metric | Alert Threshold | Action |
|--------|----------------|--------|
| `RequestCount` by HTTP status | 5xx rate > 1% over 5 min | Page on-call |
| `OriginLatency` (p95) | > 5000ms over 5 min | Investigate backend |
| `WebApplicationFirewallRequestCount` by action=Block | > 50 blocks/min (sudden spike) | Review WAF logs for false positives |
| `OriginHealthPercent` | < 80% | Check Container Apps health |
| `TotalLatency` (p50) | > 2000ms sustained | Check Front Door POP routing |

### Application Insights

Each Container Apps backend sends telemetry to a shared Application Insights instance.

| Signal | Source | Purpose |
|--------|--------|---------|
| Request traces | Odoo, n8n, auth | End-to-end transaction correlation |
| Dependency calls | Odoo -> PostgreSQL | Database latency tracking |
| Exceptions | All backends | Error rate monitoring |
| Custom events | Cutover script | Track cutover/rollback events |

### Validation Script

Run the automated cutover validation:

```bash
# Validate all hostnames
./scripts/azure/validate-front-door-cutover.sh

# Validate specific hostname
./scripts/azure/validate-front-door-cutover.sh --hostname erp.insightpulseai.com

# Validate a wave
./scripts/azure/validate-front-door-cutover.sh --wave wave1-core

# Dry run (show what would be checked)
./scripts/azure/validate-front-door-cutover.sh --dry-run
```

Script source: `scripts/azure/validate-front-door-cutover.sh`.
Checklist SSOT: `ssot/azure/hostname-cutover-checklist.yaml`.

---

## Related Files

| File | Purpose |
|------|---------|
| `ssot/azure/hostname-cutover-checklist.yaml` | Per-hostname cutover status and wave assignment |
| `ssot/azure/target-state.yaml` | Azure platform target state |
| `ssot/azure/service-matrix.yaml` | Service inventory with endpoints |
| `ssot/azure/dns-migration-plan.yaml` | DNS record migration tracking |
| `infra/dns/subdomain-registry.yaml` | Canonical DNS SSOT |
| `infra/cloudflare/cloudflare-cache-rules.json` | Current Cloudflare cache/WAF rules |
| `scripts/azure/validate-front-door-cutover.sh` | Automated cutover validation |
