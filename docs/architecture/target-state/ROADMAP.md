# Roadmap Target State

## Canonical write model

Odoo is the sole system of record for roadmap initiatives, milestones, dependencies, KPI mappings, and CAF stage classification. All canonical state transitions are persisted in Odoo first.

The Odoo module `ipai_product_roadmap` owns:
- `roadmap.initiative` — initiative lifecycle and metadata
- `roadmap.milestone` — milestone tracking per initiative
- `roadmap.dependency` — dependency graph between initiatives
- `roadmap.kpi` — KPI/OKR linkage per initiative

Backing store: Azure Database for PostgreSQL (flexible server), resource `ipai-odoo-dev-pg`.

## Projection surfaces

| Surface | Role | Write authority |
|---------|------|-----------------|
| Plane (self-hosted) | Workflow/project-management projection and command surface | Command source only — Odoo validates and persists |
| Supabase (self-hosted on Azure VM) | Operational read model, realtime API surface, agent grounding | Read-only mirror — no direct writes to canonical tables |
| Fabric / OneLake | Analytics mirror | Read-only — analytics distribution, not transactional |
| Databricks | Intelligence and governed app surface | Read-only consumer of OneLake — analytical/decision apps only |
| Roadmap HTML (`apps/roadmap/`) | Frontend projection | Read-only — consumes Supabase realtime or Odoo API |

## Integration topology

```
Plane ──webhook / API command──→ Odoo (validates, persists)
Odoo ──API / sync projection──→ Plane (status, assignments)

Odoo (Azure PG) ──native logical replication──→ Supabase (self-hosted PG)
Odoo (Azure PG) ──Fabric Database Mirroring──→ OneLake (Delta/Parquet)
OneLake ──documented integration path──→ Azure Databricks (serverless compute)
```

## Non-negotiable rules

1. **No shared write authority** between Plane and Odoo. Odoo is always canonical.
2. **No direct writes** from Supabase, Fabric, or Databricks back into canonical roadmap entities.
3. **Plane changes are commands**, not canonical state transitions. Odoo accepts or rejects them.
4. **n8n is for Plane ↔ Odoo work-item sync only**, not for database replication. Native PG logical replication and Fabric mirroring handle data distribution.

## Latency intent

| Path | Purpose | Target latency |
|------|---------|----------------|
| Odoo → Supabase | Operational / near-real-time read path for UIs, agents, APIs | Sub-second (logical replication) |
| Odoo → Fabric → OneLake | Analytics distribution path | Near real-time (minutes) |
| OneLake → Databricks | Governed analytics and decision apps | Minutes (batch-compatible) |
| Plane → Odoo | Work-item command sync | Event-driven (webhook, seconds) |
| Odoo → Plane | Status/assignment projection | Event-driven (webhook, seconds) |

## Operational considerations

- Azure Database for PostgreSQL requires `wal_level=logical` and replication permissions for logical replication.
- Fabric mirroring has initial snapshot overhead and ongoing WAL consumption — monitor WAL growth, CPU, and IOPS on the source.
- Supabase Postgres Changes is suitable for the current scale. If the app becomes higher-fanout or multi-tenant, migrate the live UI to Supabase Broadcast.
- Databricks Apps (GA) are a good fit for governed analytical decision apps once mirrored and curated products are stable, but not for primary operational writeback.

---

*Last updated: 2026-03-17*
