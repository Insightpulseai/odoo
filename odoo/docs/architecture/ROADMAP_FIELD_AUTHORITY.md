# Roadmap Field Authority

## Purpose

Define which system owns which fields for roadmap entities. This prevents dual-authority drift and makes sync conflicts deterministic.

## Odoo-owned canonical fields

These fields are authored, validated, and persisted exclusively in Odoo. All other systems receive them as projections.

| Field | Type | Description |
|-------|------|-------------|
| `initiative_id` | Integer | Canonical unique identifier |
| `title` | Char | Initiative title |
| `description` | Text | Full description |
| `canonical_status` | Selection | Idea / Planned / In Progress / At Risk / Blocked / Complete |
| `priority` | Selection | Critical / High / Medium / Low |
| `product_plane` | Selection | Platform / Data Intelligence / Agent Platform / Odoo Copilot / Web / Automations |
| `caf_stage` | Selection | Strategy / Plan / Ready / Migrate / Modernize / Cloud-native / Govern / Secure / Manage |
| `target_quarter` | Char | Target delivery quarter |
| `span_quarters` | Integer | Number of quarters the initiative spans |
| `owner` | Selection | Agent owner (chief-architect, azure-platform, etc.) |
| `kpi_outcome` | Char | Primary KPI or business outcome |
| `kpi_target` | Char | Measurable target for the KPI |
| `dependency_ids` | Many2many | Dependency graph (other initiatives or external deps) |
| `milestone_ids` | One2many | Milestone set with dates |
| `risk_ids` | One2many | Risk register entries |
| `create_date` | Datetime | Audit: creation timestamp |
| `write_date` | Datetime | Audit: last modification timestamp |
| `create_uid` | Many2one | Audit: creator |
| `write_uid` | Many2one | Audit: last modifier |

## Plane-managed workflow overlays

These fields exist only in Plane and are not synced back as canonical state. They are convenience/workflow fields for project management.

| Field | Description |
|-------|-------------|
| Cycle / sprint placement | Which Plane cycle or sprint the work item belongs to |
| Discussion / comments | Threaded conversation on the work item |
| Transient assignee workflow | Day-to-day assignment changes within a sprint |
| Sub-issues / checklists | Granular task breakdowns |
| Labels / modules | Plane-specific categorization |
| Activity log | Plane-internal activity history |

## Allowed Plane → Odoo command fields

When Plane emits a webhook or API call to Odoo, only these fields may be proposed as state changes. Odoo validates before persisting.

| Field | Allowed change | Validation |
|-------|---------------|------------|
| `canonical_status` | Status transitions | Must follow allowed transition rules |
| `owner` | Reassignment | Must be a valid agent owner |
| `priority` | Priority change | Must be a valid priority value |
| `description` | Description update | Accepted as-is |
| `milestone completion` | Mark milestone done | Must reference a valid milestone_id |

All other canonical fields require direct Odoo authoring.

## Prohibited write paths

| Source | Target | Rule |
|--------|--------|------|
| Supabase | Odoo canonical tables | **Prohibited** — Supabase is read-only mirror |
| Fabric / OneLake | Odoo canonical tables | **Prohibited** — analytics mirror, no writeback |
| Databricks | Odoo canonical tables | **Prohibited** — analytical consumer only |
| Plane | Odoo canonical tables (direct DB) | **Prohibited** — must go through Odoo API |
| Roadmap HTML frontend | Odoo canonical tables (direct DB) | **Prohibited** — must go through Odoo API or Supabase RPC |

## Sync conflict resolution

If Plane and Odoo have conflicting state for the same initiative:

1. **Odoo wins** — Odoo's canonical field values are authoritative.
2. **Plane is overwritten** — the next Odoo → Plane projection sync overwrites Plane's stale value.
3. **No merge** — there is no merge/reconciliation strategy. Odoo is the single source of truth.

---

*Last updated: 2026-03-17*
