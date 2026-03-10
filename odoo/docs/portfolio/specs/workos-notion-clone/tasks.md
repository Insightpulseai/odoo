# Tasks — Notion Clone Module (Executable Graph)

## A) Spec + Catalog
- [x] Add `spec/workos-notion-clone/{constitution,prd,plan,tasks}.md`
- [x] Update `catalog/best_of_breed.yaml` with Notion target + hero flows
- [x] Add P0/P1 capability rows to `catalog/equivalence_matrix.csv`:
  - [x] `workos.pages.blocks` (P0)
  - [x] `workos.db.properties` (P0)
  - [x] `workos.views.table` (P0)
  - [x] `workos.views.kanban` (P0)
  - [x] `workos.views.calendar` (P0)
  - [x] `workos.collab.comments` (P0)
  - [x] `workos.permissions.scopes` (P0)
  - [x] `workos.search.global` (P0)
  - [x] `workos.templates.page_db` (P1)

## B) Modules — Scaffolding
- [x] Scaffold `addons/ipai_workos_core`
- [x] Scaffold `addons/ipai_workos_blocks`
- [x] Scaffold `addons/ipai_workos_db`
- [x] Scaffold `addons/ipai_workos_views`
- [x] Scaffold `addons/ipai_workos_templates`
- [x] Scaffold `addons/ipai_workos_collab`
- [x] Scaffold `addons/ipai_workos_search`
- [x] Ensure manifests depend on correct Odoo modules (`web`, `mail`, `base`, etc.)

## C) Work OS Shell
- [ ] Workspace/Space/Page models + menus/actions
- [ ] Sidebar tree UI (workspace -> spaces -> pages)
- [ ] Page create/move/archive
- [ ] Demo seed: sample workspace + SOP pages

## D) Blocks + Editor (P0)
- [ ] Block schema (JSON) + validators
- [ ] Block types: paragraph/heading/list/todo/toggle/divider/quote/callout
- [ ] OWL editor surface: insert/move/delete blocks, slash menu
- [ ] Autosave and conflict-lite handling
- [ ] Tests: create/edit/move blocks

## E) Databases (P0)
- [ ] Database + Property + Row models
- [ ] Property types: text/number/select/multi/date/checkbox/person
- [ ] Row editor in table view (inline edit)
- [ ] Relation property (db-to-db) (P1 if needed)
- [ ] Tests: create db, add props, add rows, edit cells

## F) Views (P0)
- [ ] View model + saved views (user + shared)
- [ ] Table view UI (grid + sorting/filtering-lite)
- [ ] Kanban view (group by select/status)
- [ ] Calendar view (date property)
- [ ] Tests: view creation + switching + persistence

## G) Permissions (P0)
- [ ] Workspace roles: admin/member/guest
- [ ] Space visibility: private/shared
- [ ] Page/DB permissions: view/comment/edit/manage
- [ ] Record rules + ACLs + share token (P1)
- [ ] Tests: permission matrix

## H) Collaboration (P0)
- [ ] Comments on pages + db rows
- [ ] Mentions + notifications
- [ ] Activity log events for edits/moves/shares
- [ ] Tests: comment + mention triggers

## I) Search (P0)
- [ ] Index page title + block text + db row titles
- [ ] Global search + scoped search (space/db)
- [ ] Tests: search returns expected items

## J) Parity + CI
- [x] Define `kb/parity/rubric.json` checks for each capability_id
- [x] Extend `tools/parity/parity_audit.py` beyond manual scoring:
  - [x] verify modules exist
  - [x] verify menus/actions/views exist
  - [x] run smoke tests and parse results into score
- [x] Update `kb/parity/baseline.json` after P0 stabilization

## K) Pulser SDK
- [ ] Add Pulser job YAMLs:
  - [ ] build_catalog
  - [ ] build_equivalence_matrix
  - [ ] generate_spec_kit
  - [ ] parity_audit
  - [ ] odoo_test
  - [ ] seed_demo_tenant
  - [ ] release_package
- [ ] Add `pulser/README.md`
