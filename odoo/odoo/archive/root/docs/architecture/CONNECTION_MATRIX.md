# Connection Matrix (Canonical)

> Reference for all database and service connection patterns in the InsightPulse AI platform.
> **Status:** Canonical | **Last updated:** 2026-02-23

---

## Quick Decision Guide

```
Client is IPv4-only? (Vercel, GitHub Actions, most SaaS BI tools)
  → Use Supabase Transaction Pooler

Client is IPv6-capable + long-lived? (DO droplet container, persistent service)
  → Direct connection allowed

Need Superset to query Supabase?
  → Transaction Pooler + read-only service role key

Odoo needs to read/write Supabase?
  → ipai_* bridge connector (never raw cross-DB SQL)
```

---

## Supabase Postgres (Primary SSOT)

| Connection Type | IPv4/IPv6 | Lifetime | Use Case |
|----------------|-----------|----------|----------|
| **Transaction Pooler** | IPv4-safe ✅ | Short-lived (serverless, BI) | Vercel, GitHub Actions, Superset, n8n |
| **Direct** | IPv6-first ⚠️ | Long-lived (app servers) | DO droplet services, Odoo bridge connectors |

**Rule:** Any IPv4-only client **MUST** use the Transaction Pooler. Attempting a Direct connection from IPv4-only infra will fail silently or timeout.

**Supabase connection string locations:**
- Transaction Pooler: `postgresql://[user]@[project].pooler.supabase.com:6543/postgres`
- Direct: `postgresql://[user]@db.[project].supabase.co:5432/postgres`

---

## Superset

| Component | Required | Notes |
|-----------|----------|-------|
| Metadata DB | **PostgreSQL** ✅ | Never SQLite |
| Datasources (BI queries) | Transaction Pooler preferred | IPv4-safe; works from DO droplet |
| Datasources (long-lived) | Direct (IPv6 only) | Confirm IPv6 on hosting infra |

---

## DigitalOcean Managed PostgreSQL (Odoo DB)

| Access Type | Policy | Notes |
|-------------|--------|-------|
| Odoo runtime (droplet/VPC) | ✅ Allowlisted | Default approved path |
| GitHub Actions CI | 🟡 Allowlist if needed | For migration runners only |
| External / public internet | ❌ Prohibited | "Open to all inbound" banned |
| Connection mode | SSL required | Enforced at cluster level |

---

## Odoo (System of Record)

| Direction | Allowed Path | Notes |
|-----------|-------------|-------|
| Odoo → Supabase ops/analytics | `ipai_*` bridge connectors | Thin adapters only; no raw cross-DB |
| Supabase → Odoo data | Edge Functions / n8n RPC | Never direct Odoo DB writes from Supabase |
| Odoo → External mail | Zoho Mail SMTP (`ipai_mail_bridge_zoho`) | Port 587 via `smtp.zoho.com` |
| Odoo → n8n webhooks | HTTP callbacks from Odoo base automation | Via `https://n8n.insightpulseai.com` |

---

## n8n

| Connection | Type | Notes |
|-----------|------|-------|
| n8n metadata DB | PostgreSQL (DO managed) | Not SQLite in production |
| n8n → Supabase | Supabase node or HTTP | Use Transaction Pooler for DB queries |
| n8n → Odoo | JSON-RPC (`xmlrpc`) | Via `erp.insightpulseai.com` |

---

## Service Endpoints (Runtime)

> **SSOT for all service URLs:** `docs/architecture/runtime_identifiers.json` (generated)
> Edit source: `infra/dns/subdomain-registry.yaml`

| Service | URL | Notes |
|---------|-----|-------|
| Odoo ERP | `https://erp.insightpulseai.com` | DO droplet 178.128.112.214 |
| n8n | `https://n8n.insightpulseai.com` | Same droplet |
| Supabase | `https://spdtwktxdalcfigzeqrz.supabase.co` | Managed Supabase |
| Superset | `https://superset.insightpulseai.com` | DO App Platform |
