# Odoo.sh Equivalence Matrix

> **Reference for which platform layer covers which capability.**
> Use this to decide where to implement a feature and what gaps need tooling.

---

## Summary

| Layer | Primary scope |
|-------|--------------|
| **Odoo.sh** | Stateful Odoo runtime: build, deploy, DB cloning, module migrations |
| **Vercel Previews** | Web app preview hosting: branch → unique URL, PR status, Toolbar comments |
| **Supabase Platform Kit** | Embedded Supabase control-plane UI via Management API (projects, branches, logs, security) |
| **Your composition** | All three layered — Vercel for `apps/*`, Supabase Platform Kit in `ops-console`, Odoo pipeline for ERP runtime |

---

## Full Capability Matrix

| Capability | Odoo.sh (native) | Vercel Previews (native) | Supabase Platform Kit (native) | Your composition |
|------------|-----------------|-------------------------|-------------------------------|-----------------|
| **Primary scope** | Odoo runtime hosting + lifecycle | Web app preview hosting (Next.js, edge/serverless) | Embedded Supabase Management API control plane | Odoo pipeline + Vercel for apps + Platform Kit in ops-console |
| **Branch / PR preview** | Dev/Stage/Prod branches; staging promotes to prod | Preview deployment on every PR/branch push; unique URL per branch | Not a deploy system; UI for Supabase project/branch management | Vercel Previews for `apps/*`; Odoo pipeline for ERP deploy |
| **Staging uses prod-like DB** | Staging **duplicates production DB** per build (Odoo.sh native) | No automatic DB clone; external DB branching is your responsibility | Supabase supports DEV branches as "ephemeral servers" + merge into prod | Supabase Branching (DEV branch) for Supabase parity; Odoo pipeline for ERP DB |
| **DB migration workflow** | Odoo module upgrades / migrations (wave-based, Odoo-specific) | App deploy only; DB is out-of-scope | Management API: create branch, run migrations, merge branch | CI runs Odoo module waves + Supabase migration / merge gates |
| **Promotion to prod** | Merge staging → production (Odoo.sh workflow) | Merge to main branch → triggers production deploy | Merge DEV branch into production via Management API | GitHub "promote" workflow: stage → prod for Odoo; Supabase branch merge for DB |
| **Rollback semantics** | Odoo runtime + DB tightly coupled; rollbacks are complex | Rollback deployment artifact is simple; DB state is external | PITR restore available but causes data loss for rows written after restore point | Roll-forward bias for DB; artifact rollback for apps; PITR as last resort |
| **Logs & debugging** | Odoo logs + build logs (platform-hosted) | Build logs + runtime logs for edge/serverless functions | Management API: logs query endpoint (`/v1/projects/{ref}/analytics/endpoints/logs.all`) | ops-console aggregates: GitHub Actions logs + Odoo logs + Supabase logs |
| **Security checks** | App-level (Odoo module security) | App-level; add CI scanners | Security advisor endpoint: `GET /v1/projects/{ref}/advisors/security` — run before prod | CI preflight: OCA gates + GitGuardian + Supabase security advisor |
| **Embedded admin UI** | Odoo.sh UI (hosting console, external) | Vercel deploy console (external) | **Platform Kit embeds lightweight Supabase dashboard in your app** via Management API | `apps/ops-console` is the unified UI; Platform Kit covers Supabase surfaces |
| **Multi-tenant "platform" mode** | Not a multi-tenant platform toolkit | Multi-tenant app patterns possible in your code | Supabase explicitly supports "use Supabase as a platform" (Management API + Platform Kit) | ops-console manages internal org only (not customer OAuth) |
| **Observability / metrics** | Odoo logs only; no Prometheus | Vercel Analytics + Speed Insights (plan-gated) | **Prometheus-compatible Metrics API** (60 s scrape, Basic Auth) — see `SUPABASE_METRICS.md` | Prometheus scrape → Grafana; Vercel Speed Insights for frontend |
| **Log drains (structured logs)** | Odoo log files | Vercel Log Drains (Pro/Enterprise plan) | Supabase Log Drains (Team/Enterprise plan) | Not in current scope; use logs query endpoint instead |
| **Backup / PITR** | Odoo DB backup is infrastructure-level | Not applicable (stateless app) | PITR restore via Management API; warns about data loss post-restore point | PITR only for disaster recovery; roll-forward preferred |

---

## Bottom-line decision table

| Situation | Use |
|-----------|-----|
| Preview a UI change in `apps/ops-console` | Vercel Previews |
| Preview an Odoo module change | Odoo staging pipeline |
| Run a DB migration safely before prod | Supabase DEV branch → merge |
| Inspect Supabase project health, branches, logs, security | ops-console Platform Kit surfaces |
| Set up Prometheus metrics for Supabase | Supabase Metrics API → Grafana (see `SUPABASE_METRICS.md`) |
| Roll back a broken deploy | App: Vercel rollback; DB: roll-forward preferred; Odoo: staged rollback script |
| Embed a Supabase-like admin panel in your app | Supabase Management API via `/api/supabase-proxy` (already live in ops-console) |

---

## Related docs

| Doc | Purpose |
|-----|---------|
| `docs/ops/SUPABASE_PLATFORM_KIT.md` | How to embed Management API surfaces in ops-console |
| `docs/ops/SUPABASE_METRICS.md` | Prometheus metrics endpoint + scrape config |
| `docs/ops/VERCEL_PREVIEWS.md` | Vercel Preview deployments + Toolbar workflow |
| `docs/platform/GOLDEN_PATH.md` | Full release lane contract (Preview → Staging → Production) |
| `docs/ops/ODOO_SH_EQUIVALENT.md` | Original Odoo.sh feature parity notes (pre-matrix) |
