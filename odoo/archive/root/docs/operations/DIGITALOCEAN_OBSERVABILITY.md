# DigitalOcean Observability — ops-console

> **Runbook** for embedding DigitalOcean monitoring surfaces in the ops-console.
> All DO API calls are server-only. The `DIGITALOCEAN_API_TOKEN` never reaches the browser.

---

## Architecture

```
ops-console (browser)
  → /api/observability/do/*  (Next.js route, server-only)
    → api.digitalocean.com/v2/*  (DO API)
      ← droplet metrics, alerts, project status
```

The ops-console has **no direct access to the DO API**. All calls are proxied through
server routes that strip the token before returning JSON to the client.

---

## DO resources monitored

| Resource | DO API path | Metric |
|----------|-------------|--------|
| Droplets | `GET /v2/droplets` | name, status, region, vcpus, memory, disk |
| Droplet health | `GET /v2/monitoring/metrics/droplet/cpu` | CPU %, per droplet |
| Memory | `GET /v2/monitoring/metrics/droplet/memory_utilization_percent` | Memory % |
| Disk | `GET /v2/monitoring/metrics/droplet/disk_utilization_percent` | Disk % |
| Bandwidth | `GET /v2/monitoring/metrics/droplet/public_outbound_bandwidth` | Outbound Mbps |
| Alerts | `GET /v2/monitoring/alerts` | Alert policies and trigger status |

**Primary droplet**: `odoo-production` at `178.128.112.214` (SGP1)

---

## DO API token (server-only)

`DIGITALOCEAN_API_TOKEN` — read-only scopes: `read:droplet`, `read:monitoring`.
Store in:
- Local: `.env.local` (never commit)
- Production: Vercel project env vars (server-only, no `NEXT_PUBLIC_` prefix)
- CI: GitHub Actions secret `DIGITALOCEAN_READ_TOKEN`

---

## Routes in ops-console

| Route | Handler | Returns |
|-------|---------|---------|
| `GET /api/observability/do/droplets` | `lib/do-client.ts` | Droplet list with status |
| `GET /api/observability/do/metrics` | `lib/do-client.ts` | CPU/mem/disk for named droplet |
| `GET /api/observability/do/alerts` | `lib/do-client.ts` | Active alert policies |

---

## Security rules

1. `DIGITALOCEAN_API_TOKEN` is read-only (no write permissions)
2. Token never appears in client bundle — only used inside server routes
3. No wildcard proxy — each route has a defined DO API path mapping
4. Rate limit: max 250 req/hour per DO token; ops-console caches responses for 60 s

---

## Scaffold pages (current)

- `/observability` — hub page (links to sub-sections)
- `/observability/digitalocean` — droplet health cards + alert summary

Both pages are scaffolds. They show what will be surfaced once data plumbing is connected.
Live API calls are through the `do-client.ts` server utility.

---

## How to connect live data

1. Set `DIGITALOCEAN_API_TOKEN` in `.env.local`
2. Un-comment the `fetch()` calls in `app/observability/digitalocean/page.tsx`
3. Remove the `<!-- scaffold -->` banner from the card components

---

## Alert policies (to create in DO)

Recommended alerts to configure in the DigitalOcean dashboard:

| Policy | Threshold | Channel |
|--------|-----------|---------|
| CPU > 85% for 5 min | High | Email + Slack |
| Memory > 90% for 5 min | High | Email + Slack |
| Disk > 85% | Critical | Email |
| Droplet unreachable | Critical | Email + Slack + PagerDuty |

Configure alerts at: DigitalOcean dashboard → Monitoring → Create Alert Policy.

---

## Related

| File | Purpose |
|------|---------|
| `apps/ops-console/lib/do-client.ts` | Server-side DO API client |
| `apps/ops-console/app/observability/page.tsx` | Observability hub |
| `apps/ops-console/app/observability/digitalocean/page.tsx` | Droplet health scaffold |
| `apps/ops-console/app/api/observability/do/droplets/route.ts` | Droplets API route |
| `apps/ops-console/app/api/observability/do/metrics/route.ts` | Metrics API route |
| `apps/ops-console/app/api/observability/do/alerts/route.ts` | Alerts API route |
| `infra/observability/supabase/prometheus-scrape.supabase.yml` | Supabase Prometheus config |
| `docs/ops/SUPABASE_METRICS.md` | Supabase metrics runbook |
