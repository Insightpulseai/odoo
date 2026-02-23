# MAXIMIZE_FEATURES.md — Supabase Primitive Capability Map

> **Principle**: Use Supabase-native primitives to their fullest before adding a
> partner integration. Every integration layer adds operational surface. Justify each
> one with a capability gap that cannot be closed by a primitive.

---

## 1. Supabase Primitive Map

| Primitive | Capability | Current Usage in `ipai` | "Don't Add Integration Until…" Rule |
|-----------|-----------|------------------------|-------------------------------------|
| **PostgreSQL 16** | Relational + JSON + full-text + vector storage | `ops.*`, `auth.*`, `public.kb_*` schemas; migrations in `supabase/migrations/` | …PostgreSQL itself cannot model the data. |
| **Row-Level Security (RLS)** | Fine-grained, declarative row-level authorization | Enabled on ops tables; `kb_nodes` policy zones via `addon_kind` + `edit_policy` columns | …you need cross-tenant or attribute-based access control that RLS cannot express. |
| **Edge Functions** | Serverless Deno functions; webhook adapters, API shims | 42 Edge Functions deployed; n8n webhook bridge, GitHub event relay | …the Edge Function invocation latency or cold-start time is unacceptable for the use case. |
| **pg_cron** | Scheduled SQL jobs (cron syntax) | Cron jobs for stale task cleanup, KB freshness checks | …you need distributed scheduling across >1 Supabase project or a visual scheduling UI. |
| **pgmq (Queues)** | Durable, at-least-once message queue in Postgres | Task bus for agent jobs (`ops.task_queue`), n8n trigger queue | …you need pub/sub fan-out to many consumers or message-level TTL < 1 second. |
| **Realtime** | CDC-based WebSocket broadcasts (INSERT/UPDATE/DELETE events) | Used by ops-console live dashboard; ERP event stream | …you need >10 000 concurrent subscribers or sub-10 ms latency SLA. |
| **Storage** | S3-compatible object storage with RLS policies | Receipt/invoice blobs for OCR pipeline; evidence log archives | …you need multi-region replication or CDN edge caching at scale. |
| **pgvector / RAG** | `vector(1536)` embeddings + IVFFlat/HNSW indexes | `kb_embeddings` table; semantic chunk retrieval for GraphRAG Layer 2 | …you need approximate-nearest-neighbor at >10 M vectors or sub-5 ms p99 search. |

---

## 2. GraphRAG Layer → Primitive Mapping

The GraphRAG KB system uses four tables, each mapped to a Supabase primitive:

| Table | Primitive | Purpose |
|-------|-----------|---------|
| `kb_chunks` | PostgreSQL | Text chunk storage with provenance metadata |
| `kb_embeddings` | pgvector | 1536-dim OpenAI/Claude embeddings (Layer 2) |
| `kb_nodes` | PostgreSQL | Graph nodes with policy metadata (Layer 1) |
| `kb_edges` | PostgreSQL | Directed typed edges for graph traversal (Layer 1) |

All four tables use RLS policies and are managed exclusively via migrations in
`supabase/migrations/`. See `supabase/migrations/20260223000008_kb_graph_layer.sql`.

---

## 3. Current Primitive Utilization

| Primitive | Status |
|-----------|--------|
| PostgreSQL 16 | ✅ Active — primary store |
| RLS | ✅ Active — ops + KB tables |
| Edge Functions | ✅ Active — 42 deployed |
| pg_cron | ✅ Active — maintenance jobs |
| pgmq | ✅ Active — ops task bus |
| Realtime | ✅ Active — dashboard stream |
| Storage | ✅ Active — blob store |
| pgvector | ✅ Active — kb_embeddings |

**Score: 8 / 8 primitives active.** No capacity gaps justify an additional
persistence or streaming integration today.

---

## 4. Integration Trigger Rules

An integration is justified **only when all of the following hold**:

1. **Capability gap**: A Supabase primitive cannot address the requirement (see
   column 4 of the table above for exact thresholds).
2. **Lane classification**: The integration fits a defined lane in
   `docs/supabase/INTEGRATIONS_POLICY.md`.
3. **Data contract documented**: Tables touched + RLS implications written up.
4. **Secret handling declared**: Where the credential lives (Vault key name);
   never in repo.
5. **Exit plan exists**: How to remove the integration if it no longer provides
   value.
6. **Evidence added**: The integration can be detected by
   `scripts/audit_supabase_integrations.py --repo` — add a file, workflow name, or
   package.json dep that signals its presence.

---

## 5. Autodetection

Refresh the integration inventory without manual editing:

```bash
# Repo-evidence scan (deterministic, CI-safe)
python scripts/audit_supabase_integrations.py --repo
# → writes: docs/supabase/integrations_detected.json
# → updates: reports/supabase_feature_integration_matrix.json integrations.*

# Machine-wide scan (read-only, local environment)
python scripts/audit_supabase_integrations.py --machine
# → writes: docs/supabase/machine_integrations_detected.json
# → updates: reports/supabase_feature_integration_matrix.json machine_autodetection
```

The matrix (`reports/supabase_feature_integration_matrix.json`) is **script-populated**.
Do not hand-edit the `integrations.*` or `machine_autodetection` sections.

---

*Last updated: 2026-02-23 | See `docs/supabase/INTEGRATIONS_POLICY.md` for lane rules.*
