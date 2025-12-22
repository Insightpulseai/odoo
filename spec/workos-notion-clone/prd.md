# PRD — Work OS Notion Clone (Odoo CE 18 + OCA 18) — Bootstrapped in `jgtolentino/odoo-ce`

## 1) Summary
Build a **Notion-style Work OS** as a set of Odoo modules under `addons/` that delivers:
- Notion-like **Pages** (nested tree + rich blocks)
- Notion-like **Databases** (typed properties, rows as pages/records)
- **Views** (table/kanban/calendar) and saved views
- **Templates** (page/database templates)
- **Collaboration** (comments, mentions, activity log)
- **Permissions** (workspace/space/page/db scopes)
- **Search** (global + scoped)

This is a **clone**: Odoo is the backend and UI runtime; Notion is only a reference target.

## 2) Goals
### Product Goals
- Credible parity for daily workflows: create page, nest pages, add blocks, build database, create views, share/permission, comment, search.
- Zero-empty-state demo tenant: templates and sample workspaces preloaded.

### Engineering Goals
- Modules are **bounded** and **thin**:
  - platform primitives (tokens/audit/permissions) reused
  - workos-specific modules separated by concerns
- CI enforces Spec Kit structure + parity gating.

## 3) Non-goals (v1)
- Full Notion API clone (public API, integrations, marketplace)
- Real-time multi-cursor co-editing (Google Docs-level)
- Offline sync clients
- Full timeline/Gantt and formula engine parity (can be phased)

## 4) Users / Personas
- Knowledge Ops (SOPs, KB, onboarding)
- PM/Operations (databases for tasks/projects)
- Finance/Ops (policy libraries, approvals-lite references)
- Admin (permissions, templates, governance)

## 5) Domain Model (Canonical Odoo Objects)
### 5.1 Core Objects
- `ipai.workos.workspace`
- `ipai.workos.space`
- `ipai.workos.page`
- `ipai.workos.block`
- `ipai.workos.database`
- `ipai.workos.property`
- `ipai.workos.row` (or rows as pages; choose one canonical representation)
- `ipai.workos.view`
- `ipai.workos.template`
- `ipai.workos.permission` (scopes: workspace/space/page/db)
- `ipai.workos.comment`
- `ipai.workos.activity`

### 5.2 Block Types (v1)
- paragraph, heading, bulleted list, numbered list
- to-do, toggle (collapsible)
- divider, quote, callout
- image/file embed (Odoo attachment-backed)
- link preview (optional v1.1)

## 6) Features (Parity Targets)

### P0 — Pages + Blocks
- Create/edit page title + icon/cover (optional cover v1.1)
- Nested pages (tree sidebar)
- Block editor: add/move/delete blocks, basic formatting
- Page templates (create page from template)

### P0 — Databases
- Create database with properties:
  - text, number, select, multi-select
  - date, checkbox, person (res.users)
- Rows as records (create/update)
- Relation property (db-to-db)
- Rollup-lite (count, sum on relation; phase if needed)

### P0 — Views
- Table view (grid)
- Kanban view (group by select/status)
- Calendar view (date property)
- Saved views (per user + shared)

### P0 — Collaboration
- Comments on page + inline comment anchors (lite)
- Mentions (@user) and notifications
- Activity log (create/edit/move/share)

### P0 — Permissions / Sharing
- Workspace roles: admin/member/guest
- Space visibility: private/shared
- Page/db permissions: view/comment/edit/manage
- Share link token (optional: internal-only v1, public link v1.1)

### P1 — Governance + Quality-of-life
- Version history lite (append audit events + diff-lite)
- Import/export (markdown export; import phase)
- Templates marketplace (tenant templates)

## 7) UX Requirements (Notion "feel" inside Odoo)
- Left sidebar: workspace → spaces → page tree
- Main editor: block-based with slash command
- Database: Notion-like "top bar" with view selector + filters/sorts
- Quick add row, quick add page
- Minimal chrome (reduce ERP heaviness) using theme tokens + OWL widgets

## 8) Architecture in `jgtolentino/odoo-ce`

### 8.1 Module Set (recommended)
Platform shared (if not already present):
- `ipai_platform_theme` (tokens, density, typography)
- `ipai_platform_audit` (activity/event log)
- `ipai_platform_permissions` (scope + role rules) *(create if missing)*

Work OS:
- `ipai_workos_core` (workspace/space/page shell + menus)
- `ipai_workos_blocks` (block model + editor primitives)
- `ipai_workos_db` (database + properties + rows)
- `ipai_workos_views` (view model + table/kanban/calendar controllers)
- `ipai_workos_templates` (template creation + apply)
- `ipai_workos_collab` (comments/mentions/notifications)
- `ipai_workos_search` (global + scoped search indexing)

### 8.2 Frontend/Assets
- OWL components for:
  - block editor surface
  - database view switcher
  - inline cell editor (table)
- SCSS tokens from `kb/design_system/tokens.yaml` compiled into `ipai_platform_theme`

### 8.3 Storage
- Attachments via Odoo filestore + `ir.attachment`
- Block content stored as structured JSON (validated schema) + rendered preview HTML (cached)

## 9) Parity Validation (Scored, CI-gated)
Each capability has a `capability_id` in `catalog/equivalence_matrix.csv`.

Rubric (0–100):
- Workflow Fidelity (20) — page/db lifecycle states, templates, share flows
- UX Fidelity (30) — sidebar/editor/db interactions, defaults
- Data Fidelity (15) — objects/properties/relations correctness
- Permission Fidelity (20) — roles + scopes + share rules
- Reporting/Search (10) — search quality and saved views
- Performance (5) — editor and grid responsiveness

CI rule:
- **P0 score regression blocks merge**
- parity_report.json is uploaded as artifact

## 10) Acceptance Criteria (MVP)
A demo tenant can:
1. Create nested pages, edit blocks via slash command, move blocks, create from template
2. Create a database, add typed properties, add rows, create 3 view types, save view
3. Add comments and @mentions with notifications
4. Restrict access by workspace/space/page/db permissions
5. Search finds pages + database rows by title and block text
6. No empty-state screens (seeded templates + sample workspaces)

## 11) Bootstrapping Instructions (Repo-local)
- Specs live at: `spec/workos-notion-clone/*`
- Catalog entries updated in:
  - `catalog/best_of_breed.yaml`
  - `catalog/equivalence_matrix.csv`
- Modules created under:
  - `addons/ipai_workos_*`
- CI gates:
  - `.github/workflows/spec-and-parity.yml`
- Tools:
  - `tools/parity/*`, `tools/audit/*`

## 12) Pulser SDK Installation
Add Pulser jobs in `pulser/jobs/*.yaml` to run:
- catalog build
- parity audit
- Odoo tests
- demo tenant seed
- release packaging
