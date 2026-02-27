# Supabase Features + Integrations — Adoption Map

> **Cross-references**:
> - `docs/architecture/SSOT_BOUNDARIES.md` — ownership boundaries
> - `docs/ops/SUPABASE_SSOT.md` — DB-first model
> - `spec/supabase-maximization/` — full spec bundle with phased rollout
> - `spec/supabase-auth-ssot/` — Auth SSOT (already fully specced)

This doc answers "where does X go?" for Supabase features and integrations.
It is the opinionated decision table — do not re-narrate the SSOT docs above; cross-link to them.

---

## Feature Adoption Tiers

| Tier | Feature | Concrete use in this repo | SSOT location | CI gate |
|------|---------|--------------------------|---------------|---------|
| T1 | Postgres + RLS + RBAC | Every `ops.*`/`ai.*` table; no table without RLS | `supabase/migrations/` | `scripts/ci/check_supabase_contract.sh` RLS gate |
| T1 | Auth | IdP for all non-Odoo surfaces (ops console, dashboards) | `supabase/config.toml [auth]` | `spec/supabase-auth-ssot/` |
| T1 | Vault | All server-readable secrets (OCR endpoints, S3 creds, SMTP) | `ssot/secrets/registry.yaml` (names only — never values) | No plaintext in `git diff` |
| T1 | Edge Functions | Integration bridges: receipt OCR, webhooks, policy checks, Plane sync | `supabase/functions/<name>/` | `supabase functions deploy` in CI |
| T1 | Queues (PGMQ) | Async jobs: receipt digitize, embed-chunk, Odoo sync events | `supabase/migrations/*_queues*.sql` | Idempotency + status columns required |
| T2 | Storage | Receipt images + OCR artifacts; Odoo `ir_attachment` pointer (not binary) | `supabase/storage/` policies | RLS policy on every bucket |
| T2 | Realtime | Run progress UI, task board live updates, activity feeds | Application subscriptions | — |
| T2 | ETL → Iceberg | CDC from Odoo Postgres → analytics lake | `infra/supabase-etl/` + `infra/iceberg/` | No BigQuery refs; `ICEBERG_*` vars required |
| T3 | Vector (pgvector) | Embeddings: runbooks, receipt OCR text, specs (RAG) | `supabase/migrations/*_kb_vector*` | — |
| T3 | MCP Server | Agent-controlled schema queries + controlled operations | `mcp/servers/supabase/` | — |
| T4 | Branching | Preview DBs for schema experiments before prod merge | `.github/workflows/` (supabase branch steps) | — |
| T4 | Log Drains | Edge Function + DB logs → observability backend | `infra/observability/supabase/` | — |

**Tier semantics**: T1 = required for every new feature; T2 = activated this cycle (Phase 2); T3 = wired in Phase 3; T4 = future capability.

---

## Integration Selection Rubric (Buy vs Build)

Use integrations from the Supabase Integrations directory only when:

1. It fills a **real gap** — not available as a Supabase-native primitive
2. It has a **repo SSOT location** — no console-only integrations
3. It can be **drift-gated** — CI can detect if it regresses

### Adopted integrations

| Integration | Purpose | SSOT location |
|------------|---------|---------------|
| **Vercel** | Env var injection; auto-syncs with Edge Function env | `supabase/config.toml` + Vercel dashboard integration |
| **Cloudflare Workers** | Edge gateway / webhook normalization | `infra/cloudflare/` workers config |
| **n8n** | Ops automation; Database Webhooks → n8n trigger | `docs/ops/SUPABASE_N8N.md` + `automations/n8n/` |

Any new integration must add a row to this table before activation.

---

## Odoo ↔ Supabase Boundary

```
Odoo CE (System of Record)          Supabase (System of Control)
──────────────────────────          ────────────────────────────
Accounting, posted docs             Ops pipelines, policies
ERP transactions, HR                Analytics, AI, embeddings
Authoritative relational data       Event stream, task queue
```

**Rules**:
- Odoo writes operational truth → Supabase brokers it to analytics/AI layers
- **No write-backs** from Supabase to Odoo ERP tables (Supabase is read-side for Odoo data)
- Cross-boundary: `webhook-ingest` Edge Function, CDC/ETL worker, auth projection

**Cross-boundary files**:
- `supabase/functions/webhook-ingest/` — Odoo → Supabase event bridge
- `infra/supabase-etl/odoo-expense.toml` — CDC config for expense tables
- `supabase/migrations/*_odoo_sync_queue*` — sync event queue

---

## Secrets Placement (Supabase context)

All Supabase-specific secret names are registered in `ssot/secrets/registry.yaml`.
Values live in Supabase Vault (runtime) or GitHub Actions Secrets (CI).

For the full secrets policy see `CLAUDE.md § Secrets Policy`.

---

## Phase Gating

Features within a Tier are gated:

- **T1 must be complete** before T2 features can merge
- **T2 must be complete** before T3 features can merge
- T4 features can start in parallel with T3 (no shared dependencies)

Phase status is tracked in `spec/supabase-maximization/plan.md`.
