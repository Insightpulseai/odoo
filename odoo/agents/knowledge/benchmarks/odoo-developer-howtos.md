# Odoo 19 Developer How-To Guides — Skill Reference

> Knowledge base reference derived from Odoo 19 developer documentation (howtos section).
> Source: Odoo 19 developer documentation
> Purpose: Maps developer how-to guides to implementation skill lanes for agent execution.
> Cross-references: `agents/knowledge/benchmarks/odoo-coding-guidelines.md` (guardrail source)

---

## 10 Implementation Skill Lanes

### 1. Module Scaffolding (backend_foundation)

Create new Odoo module structure with correct directory layout, manifest, init files, security
stubs, and README. Covers `__manifest__.py` conventions (version `19.0.x.y.z`, LGPL-3 license,
minimal dependencies), `__init__.py` import chains, and the `ipai_<domain>_<feature>` naming
convention for custom modules.

### 2. ORM Model Extension (backend_customization)

Extend Odoo models with fields, computed fields, constraints, and business logic using `_inherit`.
Covers Odoo 19 class attribute order (10-step sequence), field naming conventions (`*_id`, `*_ids`,
`is_*`, `has_*`), `Command` tuples for x2many writes, recordset methods (`mapped`, `filtered`,
`sorted`), and the prohibition on `cr.commit()`.

### 3. View Customization (ui_customization)

Safely extend Odoo UI through inherited views, actions, and menus. Covers xpath expressions
(inside, after, before, replace, attributes), XML ID conventions (`<model>_view_form`,
`<model>_action`), window actions, menu wiring, and the Odoo 19 terminology change from
`tree` to `list` in user-facing strings.

### 4. Security and ACL Rules (security)

Define security groups, ACLs (`ir.model.access.csv`), and record rules for module security.
Covers the mandatory 4 CRUD columns, `access_<model>_<group>` ID pattern, group hierarchy
with `implied_ids`, multi-company record rules, and the Odoo 19 mutual exclusivity of Portal
and Internal User groups.

### 5. Test Authoring (quality)

Write Python tests for module functionality using `TransactionCase`, `HttpCase`, and `SavepointCase`.
Covers `@tagged` decorators, test data creation in `setUp`/`setUpClass`, disposable `test_<module>`
database naming, and the mandatory failure classification system (passes locally, init only,
env issue, migration gap, real defect).

### 6. Upgrade-Safe Extension (maintainability)

Ensure all changes use inheritance-based patterns and survive Odoo version upgrades. Covers
`_inherit` enforcement, vendor/OCA file protection, migration script requirements for schema
changes, deprecated pattern detection (`cr.commit()`, context mutation, f-string translations,
raw x2many tuples), and Odoo 19 breaking changes (`groups_id` to `group_ids`, `tree` to `list`).

### 7. Report Customization (reporting)

Customize PDF reports, QWeb report templates, and operational print surfaces. Covers inherited
QWeb templates, `ir.actions.report` configuration, paper format customization, `t-esc` vs
`t-raw` for output escaping, and testing with actual data records.

### 8. Webclient and OWL Extension (frontend)

Extend the web client using OWL components, JS/TS customizations, and SCSS styling. Covers
OWL component patterns (static template, setup()), `patch()` for extending existing components,
asset bundle registration (`web.assets_backend` vs `web.assets_frontend`), CSS class naming
(`o_<module>_` prefix), and the lesson learned from `ipai_ai_widget` deprecation (no global
Composer patches).

### 9. QWeb and Website Customization (website)

Customize QWeb themes, website building blocks (snippets), and frontend surfaces. Covers
snippet registration in the website editor, snippet options for configurability, portal page
extension, inherited template patterns, and drag-and-drop testing.

### 10. Data Migration Scripts (data)

Write data migration, seed, transform, or backfill scripts. Covers `migrations/<version>/`
directory structure, `migrate(cr, version)` entry point, pre-migration (raw SQL, ORM not
loaded) vs post-migration (ORM available), idempotency patterns (`IF NOT EXISTS`), fresh
install guards, and the prohibition on `cr.commit()` in migration scripts.

---

## Cross-References

- `agents/knowledge/benchmarks/odoo-coding-guidelines.md` — coding conventions and guardrails
- `agent-platform/ssot/learning/odoo_developer_skill_map.yaml` — skill map YAML
- `agents/skills/odoo-module-scaffolding/` — skill 1 implementation
- `agents/skills/odoo-orm-model-extension/` — skill 2 implementation
- `agents/skills/odoo-view-customization/` — skill 3 implementation
- `agents/skills/odoo-security-acl-rules/` — skill 4 implementation
- `agents/skills/odoo-test-authoring/` — skill 5 implementation
- `agents/skills/odoo-upgrade-safe-extension/` — skill 6 implementation
- `agents/skills/odoo-report-customization/` — skill 7 implementation
- `agents/skills/odoo-webclient-owl-extension/` — skill 8 implementation
- `agents/skills/odoo-qweb-website-customization/` — skill 9 implementation
- `agents/skills/odoo-data-migration-script/` — skill 10 implementation
