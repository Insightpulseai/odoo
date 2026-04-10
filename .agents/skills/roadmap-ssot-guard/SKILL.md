---
name: Roadmap SSOT Guard
description: Enforce roadmap data authority — Odoo is canonical write model, Plane is projection, Supabase is read-only mirror, Fabric is analytics mirror
---

# Roadmap SSOT Guard Skill

## When to use
When working on roadmap, planning, or initiative data across Odoo, Plane, Supabase, or Databricks.

## Authority model

| System | Role | Write authority |
|--------|------|-----------------|
| Odoo | Canonical write model | YES — sole SSOT |
| Plane | Workflow projection + command surface | Command source only |
| Supabase | Operational read model | Read-only mirror |
| Fabric/OneLake | Analytics mirror | Read-only |
| Databricks | Intelligence apps | Read-only consumer |

## Prohibited patterns

- No direct writes from Supabase to canonical roadmap tables
- No Fabric/Databricks writeback to Odoo
- No unrestricted bidirectional sync between Plane and Odoo
- No n8n-based CDC for data replication (use native PG logical replication)
- Plane changes are commands — Odoo validates and persists

## Conflict resolution

Odoo wins. Plane is overwritten on next sync. No merge strategy.

## Reference docs
- `docs/architecture/ROADMAP_TARGET_STATE.md`
- `docs/architecture/ROADMAP_FIELD_AUTHORITY.md`
- `docs/architecture/ROADMAP_INTEGRATION_DECISIONS.md`
