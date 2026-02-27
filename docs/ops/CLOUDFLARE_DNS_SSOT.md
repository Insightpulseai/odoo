# Cloudflare DNS SSOT — insightpulseai.com

> **SSOT for all DNS records managed via Cloudflare.**
> Edit the YAML file. Never edit Cloudflare UI directly.

---

## SSOT location

| File | Purpose |
|------|---------|
| `infra/cloudflare/insightpulseai.com.records.yaml` | All zone records (A, MX, TXT) |
| `infra/dns/subdomain-registry.yaml` | Subdomain service mapping + health checks |
| `infra/dns/zoho_mail_dns.yaml` | Email records (mirrors records.yaml for Zoho-specific context) |

**Workflow**: edit YAML → commit → CI validates drift → apply via Terraform or Cloudflare API.

---

## Zone identifiers

| Property | Value |
|----------|-------|
| **Zone name** | `insightpulseai.com` |
| **Zone ID** | `73f587aee652fc24fd643aec00dcca81` |
| **Account ID** | `dadf50a41a8bb4c0d0bbbb15681a53af` |

---

## Proxy vs DNS-only rules

| Record type | Proxy setting | Reason |
|-------------|--------------|--------|
| A (`@`, `www`, `erp`, `n8n`, `mcp`, `superset`) | **Proxied** (orange cloud) | HTTP/HTTPS apps; Cloudflare edge termination |
| MX (`@`) | **DNS-only** | SMTP is not proxied by Cloudflare |
| TXT (SPF, DKIM, DMARC, `_dmarc`) | **DNS-only** | Email auth records; must resolve directly |
| CNAME (future app subdomains) | Check per-case | Platform apps (DO) typically DNS-only; Vercel apps typically DNS-only (Vercel handles TLS) |

---

## App-specific caveats for proxied subdomains

### Odoo (`erp.insightpulseai.com`)

Odoo must run behind a reverse proxy. Required config in `odoo.conf`:

```ini
proxy_mode = True
```

Odoo reads `X-Forwarded-For` and `X-Forwarded-Proto` headers set by Cloudflare.
Without `proxy_mode = True`, session cookies and redirect URLs break.

### n8n (`n8n.insightpulseai.com`)

n8n uses **WebSockets** for real-time UI updates. Cloudflare handles WebSocket proxying
automatically — no special config needed, but ensure your Cloudflare SSL mode is
**Full (Strict)** (not Flexible) to avoid mixed-content or auth loop issues.

### Odoo bus / longpolling

Odoo 19 uses HTTP/2 long-polling for the bus (notifications). Cloudflare proxies HTTP/2
transparently. If you see bus timeouts, check:
- Cloudflare SSL mode is Full (Strict)
- nginx/Caddy `proxy_read_timeout` is high enough (≥ 300 s)

---

## SSL mode recommendation

Set Cloudflare SSL/TLS mode to **Full (Strict)** for all proxied subdomains.

| Mode | Risk |
|------|------|
| Flexible | Cloudflare ↔ origin is HTTP; exposes plaintext between CF and DO droplet |
| Full | Cloudflare accepts any origin cert (including self-signed) — do not use |
| **Full (Strict)** | Origin must have a valid cert (Let's Encrypt or Cloudflare Origin CA) ✅ |

---

## How to update records

1. Edit `infra/cloudflare/insightpulseai.com.records.yaml`.
2. Commit + push (PR or directly to `main` for infra changes).
3. CI drift check runs — fails if live DNS differs from YAML.
4. Apply change:
   - **Via Terraform**: `cd infra/terraform && terraform apply -target=cloudflare_record.*`
   - **Via API**: `scripts/ci/verify_cloudflare_dns_drift.py --apply` (if implemented with write mode)
   - **Manual API call** (last resort): use Cloudflare API with `CF_API_TOKEN` from GitHub Secrets.

---

## Drift checker

`scripts/ci/verify_cloudflare_dns_drift.py` reads the SSOT YAML and compares against
live Cloudflare API records. Fails with a clear diff if any record differs.

Required env var: `CF_API_TOKEN` — read-only DNS token scoped to `insightpulseai.com` zone.

CI gate: `.github/workflows/cloudflare-dns-drift.yml` — runs on PRs that change
`infra/cloudflare/**` or `infra/dns/**`.

---

## Email posture

Current: `p=quarantine` (DMARC).

**Next hardening step (when ready):** ramp to `p=reject` using `pct=` incrementally:

```
1. p=quarantine; pct=25  (1 week — monitor reports)
2. p=quarantine; pct=100 (1 week — stable)
3. p=reject; pct=10      (gradual ramp)
4. p=reject; pct=100     (full enforcement)
```

Only proceed after confirming all legitimate senders are DKIM-aligned in DMARC reports.

---

## Optional hardening records (not yet implemented)

| Record | Purpose |
|--------|---------|
| CAA | Restrict which CAs can issue certs for this domain |
| `_mta-sts` TXT + HTTPS policy | MTA-STS: enforce TLS for inbound SMTP |
| `_smtp._tls` TXT | TLS-RPT: reporting for SMTP TLS failures |

---

## Related

| File | Purpose |
|------|---------|
| `infra/cloudflare/insightpulseai.com.records.yaml` | Zone record SSOT |
| `scripts/ci/verify_cloudflare_dns_drift.py` | Drift checker |
| `.github/workflows/cloudflare-dns-drift.yml` | CI gate |
| `infra/dns/subdomain-registry.yaml` | Subdomain service registry |
| `infra/dns/zoho_mail_dns.yaml` | Email-specific DNS context |
