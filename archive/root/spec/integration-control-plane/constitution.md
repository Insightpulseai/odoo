# Constitution: Integration Control Plane

> Non-negotiable rules governing the `ctrl` schema and all cross-system integration infrastructure.

---

## 1. Supabase Is the Integration State Store, NOT a Data Warehouse

Supabase holds **integration metadata** (identity maps, sync cursors, event logs, entity links). It does NOT replicate or warehouse business data from Odoo, Plane, or any other system. Business data stays in the system of record; the control plane only tracks **references, relationships, and sync state**.

## 2. All Cross-System Identity Resolution Goes Through `ctrl.identity_map`

No integration code may resolve "Plane issue X = Odoo task Y" by ad-hoc lookups, hardcoded mappings, or side-channel joins. Every cross-system entity reference MUST be registered in `ctrl.identity_map` and resolved via the `resolve_identity()` RPC. This is the single source of truth for entity identity across systems.

## 3. Sync State Is Immutable Append-Only

- `ctrl.sync_state` cursors are advanced forward only; previous cursor values are never overwritten.
- `ctrl.integration_events` rows are never updated or deleted (retention policy handles cleanup).
- This guarantees auditability, replayability, and forensic debugging of all sync operations.

## 4. No Business Logic in the Control Plane

The `ctrl` schema is **infrastructure**. It answers:
- "Which entities are linked across systems?"
- "Where is sync up to?"
- "What events happened?"

It does NOT answer:
- "Should this invoice be approved?"
- "What stage should this task be in?"
- "Is this deal qualified?"

Business rules live in Odoo (ERP), app code, or domain-specific Edge Functions -- never in `ctrl.*` tables or RPCs.

## 5. Extends Existing Patterns, Does Not Duplicate

The `ctrl` schema **generalizes** patterns already established in `spec/schema/entities.yaml`:

| Existing (odoo schema) | Generalized (ctrl schema) | Relationship |
|------------------------|--------------------------|--------------|
| `odoo.entity_mappings` | `ctrl.identity_map` | ctrl extends: any system pair, not just Supabase-Odoo |
| `odoo.sync_cursors` | `ctrl.sync_state` | ctrl extends: any system pair, adds status + error tracking |
| (no equivalent) | `ctrl.entity_links` | New: bidirectional relationship graph |
| (no equivalent) | `ctrl.integration_events` | New: immutable event log |

The `odoo.*` tables remain authoritative for Odoo-specific sync. The `ctrl.*` tables handle the **superset** of all system integrations. Migration path: `odoo.entity_mappings` rows can be projected into `ctrl.identity_map` via a view or sync function.

## 6. Schema Namespace: `ctrl`

All integration control plane tables live in the `ctrl` schema, separate from:
- `app` (application-owned entities)
- `odoo` (Odoo sync tables)
- `ops` (operations and observability)
- `auth` (Supabase Auth)
- `mcp_jobs` (job queue)

This separation enforces ownership boundaries and prevents schema coupling.

## 7. RLS Policy

- `ctrl.*` tables are **NOT exposed to the PostgREST API** by default.
- Access is restricted to `service_role` and specific Edge Functions.
- If app-layer access is ever needed, it must go through an RPC with explicit authorization checks.

## 8. Idempotency

All write operations (`resolve_identity`, `link_entities`, `advance_cursor`, `log_event`) MUST be idempotent. Calling them twice with the same inputs produces the same result without side effects. This is critical for retry-safe sync pipelines.

---

## Cross-References

- `spec/schema/entities.yaml` -- existing entity schema (odoo.sync_cursors, odoo.entity_mappings)
- `spec/odoo-decoupled-platform/prd.md` -- Odoo decoupled architecture
- `spec/parallel-control-planes/prd.md` -- multi-control-plane patterns
- `docs/infra/ODOO_SUPABASE_MASTER_PATTERN.md` -- Supabase integration patterns
