# Odoo 18 Coding Guidelines — Guardrail & Eval Baseline

> **Source**: Odoo 18 contributing/development/coding_guidelines
> **Role**: Benchmark for code quality, guardrail source, eval source
> **NOT**: a persona, a delivery workflow, or a runtime architecture contract

---

## Scope

This document defines the quality bar that every Odoo implementation skill must obey.
Skills that generate, review, or modify Odoo code MUST reference this benchmark.
Judge and review skills use this as the primary eval rubric.

---

## Rule 1: Think Extendable

- Methods stay small and single-responsibility (target under 30 lines).
- Avoid hardcoded business logic that blocks extension by submodules.
- Use `_inherit` for model extension, never copy-paste-modify.
- Provide hook points: small methods that submodules can `super()` on.
- Prefer configuration and parameters over embedded constants.
- Fields use proper delegation patterns (`_inherits`, `related`, `delegate`).

## Rule 2: Never Commit the Transaction

- `cr.commit()` is banned unless there is an exceptional, documented justification.
- The ORM manages transactions. Manual commits break rollback safety.
- If a migration script or queue worker genuinely requires `cr.commit()`, the justification must be documented inline.

## Rule 3: Avoid Broad Exception Catching

- Catch only specific exceptions (`UserError`, `ValidationError`, `IntegrityError`).
- Minimize the scope of `try/except` blocks — wrap only the operation that can fail.
- Never use bare `except:` or `except Exception:` without re-raise or explicit justification.
- Log caught exceptions with full context before continuing.

## Rule 4: Readability and Idiomatic Python

- Readability over cleverness.
- Import ordering: (1) stdlib, (2) odoo core, (3) odoo.addons. Each block separated by one blank line.
- Within a block, `import` before `from`.
- Use recordset methods (`mapped`, `filtered`, `sorted`) over list comprehensions.
- Lazy translation: `_()` with positional args. Never `f"..."`, `.format()`, or `%` inside `_()`.
- Context: use `with_context()`, never mutate `self.env.context` directly.

## Rule 5: XML and File Naming

### File naming conventions

| File type | Pattern | Example |
|-----------|---------|---------|
| Model | `models/<model_name>.py` | `models/sale_order.py` |
| View | `views/<model_name>_views.xml` | `views/sale_order_views.xml` |
| Security | `security/ir.model.access.csv` | |
| Security groups | `security/security.xml` | |
| Data | `data/<descriptive_name>.xml` | `data/cron_jobs.xml` |
| Demo | `demo/<descriptive_name>.xml` | `demo/sale_order_demo.xml` |
| Report | `report/<report_name>.xml` | `report/sale_order_report.xml` |
| Wizard | `wizard/<wizard_name>.py` | `wizard/sale_make_invoice.py` |
| Static assets | `static/src/{js,css,scss,xml}/` | |

### XML ID naming conventions

| Element | Pattern | Example |
|---------|---------|---------|
| Form view | `<model>_view_form` | `sale_order_view_form` |
| List view | `<model>_view_list` | `sale_order_view_list` |
| Search view | `<model>_view_search` | `sale_order_view_search` |
| Kanban view | `<model>_view_kanban` | `sale_order_view_kanban` |
| Action | `<model>_action` | `sale_order_action` |
| Menu root | `<model>_menu_root` | `sale_order_menu_root` |
| Menu item | `<model>_menu` | `sale_order_menu` |
| Security group | `group_<name>` | `group_sale_manager` |
| Record rule | `<model>_rule_<scope>` | `sale_order_rule_multi_company` |
| ACL | `access_<model>_<group>` | `access_sale_order_user` |

### XML formatting

- One attribute per line for records with more than 2 attributes.
- Data file load order in manifest: security groups, ACLs, data, views.
- Odoo 18: `tree` is renamed to `list` globally — never use `tree` in new code.

## Rule 6: Module Structure

```
my_module/
  __init__.py
  __manifest__.py
  models/
    __init__.py
    <model>.py
  views/
    <model>_views.xml
  security/
    ir.model.access.csv
    security.xml
  data/
  demo/
  report/
  wizard/
  static/
    description/
      icon.png
    src/
      js/
      css/
      scss/
      xml/
  controllers/
    __init__.py
    main.py
  tests/
    __init__.py
    test_<model>.py
```

### Manifest conventions

- Version: `19.0.x.y.z`
- License: `LGPL-3`
- `data` key order: security groups, ACLs, data, views
- Dependencies: minimal and explicit — only what you directly use

## Rule 7: CSS / SCSS

- Class prefix: `o_<module>_` (e.g., `.o_ipai_copilot_panel`). Never bare class names.
- SCSS variables: `$o-*` prefix (e.g., `$o-ipai-primary`).
- No `!important` except when overriding Odoo core styles.
- No ID selectors.

## Rule 8: JavaScript / OWL

- Follow OWL component conventions.
- Register assets in `__manifest__.py` under `assets` key.
- Use proper asset bundles (`web.assets_backend`, `web.assets_frontend`).
- Component class names: PascalCase.
- Template names: `<module>.<ComponentName>`.

## Rule 9: Programming in Odoo

- Propagate context — use `with_context()`, never mutate `self.env.context`.
- Use `env.ref()` for known XML IDs, not `search()`.
- Use `Command` tuples for x2many writes: `Command.create()`, `Command.link()`, `Command.set()`, etc.
- `ensure_one()` before single-record operations.
- `sudo()` usage must be documented with a comment explaining why.
- Use `search(..., limit=1)` when expecting a single record.
- Recordset methods over list comprehensions: `mapped()`, `filtered()`, `sorted()`.

## Rule 10: Lazy Translation

```python
# Correct — lazy interpolation
raise UserError(_('Cannot delete %s in state %s', rec.name, rec.state))

# Banned — eager interpolation inside _()
raise UserError(_('Cannot delete %s' % rec.name))
raise UserError(_('Cannot delete {}'.format(rec.name)))
raise UserError(_(f'Cannot delete {rec.name}'))
```

---

## Standard Guardrail Block

All Odoo skill contracts MUST include this guardrail block (or a superset):

```yaml
guardrails:
  - prefer inherited extension over core patching
  - methods should remain small and single-responsibility
  - do not hardcode logic that blocks extension by submodules
  - do not call cr.commit() unless explicitly justified and documented
  - catch only specific exceptions
  - follow Odoo file, XML, and import conventions
```

---

## Field Naming Conventions

| Element | Pattern | Example |
|---------|---------|---------|
| Many2one | `*_id` | `partner_id` |
| One2many | `*_ids` | `line_ids` |
| Many2many | `*_ids` | `tag_ids` |
| Compute method | `_compute_<field>` | `_compute_total` |
| Search method | `_search_<field>` | `_search_display_name` |
| Inverse method | `_inverse_<field>` | `_inverse_amount` |
| Default method | `_default_<field>` | `_default_stage_id` |
| Onchange | `_onchange_<field>` | `_onchange_partner_id` |
| Constraint | `_check_<field>` | `_check_date_range` |
| Action method | `action_<verb>` | `action_confirm` |
| Boolean field | `is_*` or `has_*` | `is_active`, `has_attachments` |

## Model Class Attribute Order

Strict sequence within a model class:

1. Private attributes (`_name`, `_description`, `_inherit`, `_order`, etc.)
2. Default methods
3. Field declarations (related, computed, stored)
4. SQL constraints
5. Compute, inverse, search methods
6. Selection methods
7. Constrains and onchange methods
8. CRUD methods (create, read, write, unlink)
9. Action methods
10. Business methods

## ORM Hard Rules

- Never use `cr.commit()` — ORM handles transactions.
- Use `env.ref()` for known XML IDs, not `search()`.
- Context: `with_context()`, never mutate.
- x2many: `Command` tuples only.
- `sudo()`: document why.
- `ensure_one()` before single-record access.

---

## Cross-References

- `agents/knowledge/benchmarks/odoo-developer-howtos.md`
- `~/.claude/rules/odoo18-coding.md`
- `~/.claude/rules/oca-governance.md`

---

*This benchmark is the quality bar. It is not a persona, not a skill taxonomy, not a delivery workflow.*
