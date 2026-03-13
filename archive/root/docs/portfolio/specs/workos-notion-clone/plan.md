# Plan — Notion Clone Module (Odoo CE 18 + OCA 18)

## Phase 0 — Repo/Spec Spine
- Add Spec Kit bundle under `spec/workos-notion-clone/`
- Add catalog rows (best_of_breed + equivalence_matrix)
- Ensure CI gates present (spec + parity)

Deliverables:
- Spec validated in CI
- Baseline parity report artifact produced

## Phase 1 — Work OS Shell
- `ipai_workos_core`: workspace/space/page tree, sidebar, menus, basic page view
- `ipai_platform_permissions`: scope model + record rules scaffolds
- `ipai_platform_audit`: activity event emission on CRUD

Deliverables:
- Create workspace/space/page, navigate tree, seeded demo

## Phase 2 — Blocks + Editor
- `ipai_workos_blocks`: block schema, rendering, move/reorder, slash menu
- OWL editor surface + autosave cadence
- Attachments (image/file block)

Deliverables:
- P0 pages parity >= 70; editor smoke tests

## Phase 3 — Databases + Properties
- `ipai_workos_db`: database/property model + row CRUD
- Property types P0 (text/number/select/multi/date/checkbox/person)
- Relations (db-to-db) phase if time allows

Deliverables:
- Database creation + row editing works with table view baseline

## Phase 4 — Views
- `ipai_workos_views`:
  - table (grid)
  - kanban (group by select/status)
  - calendar (date prop)
- Saved views and view switcher

Deliverables:
- 3 view types + saved views, parity >= 75

## Phase 5 — Collaboration + Search
- `ipai_workos_collab`: comments, mentions, notifications
- `ipai_workos_search`: indexing + scoped search

Deliverables:
- Commenting, @mentions, global search; parity >= 80 for P0 set

## Phase 6 — Templates + Polish + Release
- `ipai_workos_templates`: page/db templates + apply
- White-label token packs; reduce ERP chrome
- Seeded tenant packs; release packaging

Deliverables:
- Demo tenant with zero empty states
- Release tag with parity report + upgrade rehearsal
