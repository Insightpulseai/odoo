# Supabase Metrics API

> **Prometheus-compatible HTTPS endpoint for Supabase project telemetry.**
> Scrape every 60 s with Basic Auth. No logs here — use the Management API logs
> endpoint for structured log queries (see `SUPABASE_PLATFORM_KIT.md`).

---

## Endpoint & Auth

| Property | Value |
|----------|-------|
| **Endpoint** | `https://<project-ref>.supabase.co/customer/v1/privileged/metrics` |
| **Auth type** | HTTP Basic Auth |
| **Username** | `service_role` |
| **Password** | Secret API key (`sb_secret_...`) |
| **Scrape interval** | 60 s (Supabase-recommended maximum cadence) |
| **Format** | Prometheus text exposition format |

> **Security rule**: The `sb_secret_...` key must **never** appear in client code,
> browser bundles, CI logs, or `NEXT_PUBLIC_*` env vars. Store in Supabase Vault,
> GitHub Secrets, or secret manager only.
>
> This key is **separate** from the anon key and service role JWT used by the
> Supabase JS client. It is the "privileged metrics" credential only.

---

## Vendor-agnostic architecture

```
Supabase Metrics endpoint  (scrape every 60 s)
  ↓
Prometheus collector        (self-hosted, Grafana Agent, or cloud scraper)
  ↓
Long-term time-series store (Prometheus TSDB, Thanos, Mimir, or Grafana Cloud)
  ↓
Visualization / alerting    (Grafana, Alertmanager, PagerDuty, etc.)
```

Supabase explicitly designs the Metrics API to be vendor-agnostic — any
Prometheus-compatible collector can ingest it.

---

## Collector options

| Option | Setup effort | Cost | Recommended for |
|--------|-------------|------|-----------------|
| **Grafana Cloud** (free tier) | Lowest | Free up to limits | Quickest path to dashboards |
| **Self-hosted Prometheus + Grafana** | Medium | Infra only | Full control, existing stack |
| **Datadog** | Medium | Datadog pricing | If Datadog is already in use |
| **Grafana Agent** (remote_write) | Low | Grafana Cloud pricing | Lightweight sidecar |

---

## Canonical scrape config

Reference: `infra/observability/supabase/prometheus-scrape.supabase.yml`

```yaml
scrape_configs:
  - job_name: supabase
    scrape_interval: 60s
    metrics_path: /customer/v1/privileged/metrics
    scheme: https
    basic_auth:
      username: service_role
      password: <sb_secret_...>     # Inject from secrets store; never plaintext here
    static_configs:
      - targets:
          - spdtwktxdalcfigzeqrz.supabase.co:443   # prod project ref
```

Replace `spdtwktxdalcfigzeqrz` with `process.env.NEXT_PUBLIC_SUPABASE_PROJECT_REF`
(non-secret; already public). The password must be injected from secrets at runtime.

---

## What metrics are available

Categories (Supabase Prometheus namespace):

| Category | Example metrics |
|----------|----------------|
| Database | `pg_*` (connections, transaction rate, cache hit ratio) |
| Auth | `gotrue_*` (signups, logins, token refreshes) |
| Storage | `storage_*` (requests, latency, errors) |
| Edge Functions | `edge_runtime_*` (invocations, errors, duration) |
| PostgREST | `postgrest_*` (request rate, latency) |
| Realtime | `realtime_*` (connected clients, messages) |

---

## ops-console `/metrics` surface

The `/metrics` page in ops-console is **read-only, non-proxying**:

- Shows the configured project ref and scrape endpoint URL (non-secret)
- Links out to the configured Grafana dashboard (`GRAFANA_DASHBOARD_URL` env var)
- Does **not** proxy raw Prometheus text through Next.js — raw metrics stay in the
  collector/TSDB where they belong

If you need live metric values in the UI without Grafana, use the
Management API logs endpoint or build a `/api/metrics-summary` route that
queries your TSDB (e.g., PromQL via Prometheus HTTP API) — never the scrape endpoint.

---

## Log Drains (separate, plan-gated)

**Log drains** (structured log shipping to external destinations) are a **different
feature** from metrics and are available on **Team and Enterprise plans only**.

If you are on the Free or Pro plan, use:
- Management API logs query endpoint for ad-hoc log inspection
- Supabase Dashboard → Logs for real-time viewing

---

## Security checklist

- [ ] `sb_secret_...` stored in Supabase Vault / GitHub Secrets / secret manager
- [ ] Secret never in `NEXT_PUBLIC_*` env vars
- [ ] Scrape config YAML template uses `<placeholder>`, not real secret
- [ ] Grafana datasource password stored as Grafana Secret (not plaintext)
- [ ] Rotate metrics secret if service role key is rotated

---

## Related docs

| Doc | Purpose |
|-----|---------|
| `infra/observability/supabase/prometheus-scrape.supabase.yml` | Canonical scrape config template |
| `docs/ops/SUPABASE_PLATFORM_KIT.md` | Management API: logs, branches, security (different from metrics) |
| `docs/ops/ODOO_SH_EQUIVALENT_MATRIX.md` | Full platform observability comparison |
| `docs/ops/VERCEL_AI_OBS_TEAM.md` | Vercel AI Gateway + Observability constraints |
