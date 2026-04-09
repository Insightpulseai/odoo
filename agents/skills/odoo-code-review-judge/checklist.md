# Checklist — odoo-code-review-judge

## Module structure
- [ ] Directory layout follows conventions (models/, views/, security/, data/, static/)
- [ ] `__manifest__.py` version is `18.0.x.y.z`
- [ ] `__manifest__.py` license is `LGPL-3`
- [ ] Manifest data key order: security groups, ACLs, data, views
- [ ] Dependencies are minimal and explicit
- [ ] File naming matches model names

## Python style
- [ ] Import ordering: stdlib, odoo core, odoo.addons (separated by blank lines)
- [ ] `import` before `from` within each block
- [ ] Recordset methods used over list comprehensions (`mapped`, `filtered`, `sorted`)
- [ ] Lazy translation: `_()` with positional args (no f-strings, no .format())
- [ ] Model class attribute order follows convention (10-step sequence)
- [ ] Field naming: `*_id` for M2O, `*_ids` for O2M/M2M, `is_*`/`has_*` for booleans
- [ ] Method naming: `_compute_*`, `_onchange_*`, `_check_*`, `action_*`

## XML structure
- [ ] XML IDs follow naming convention (`_view_form`, `_view_list`, `_action`, `_menu`)
- [ ] No deprecated `tree` views (must be `list` in Odoo 18)
- [ ] Record formatting: one attribute per line when >2 attributes
- [ ] ACL CSV: all 4 CRUD columns present, ID pattern `access_<model>_<group>`

## Transaction safety
- [ ] No `cr.commit()` without explicit justification comment
- [ ] No raw `cr.execute()` without justification
- [ ] ORM methods used correctly
- [ ] `with_context()` used (no context mutation)
- [ ] `sudo()` usage documented with comment

## Extendability
- [ ] No methods over 30 lines
- [ ] No hardcoded values that should be configurable
- [ ] `_inherit` used for extension (no copy-paste)
- [ ] Proper hook points for submodule override

## Exception handling
- [ ] No bare `except:` or `except Exception:` without re-raise
- [ ] Try/except scope is minimal
- [ ] Caught exceptions logged with context

## CSS/SCSS
- [ ] Class prefix: `o_<module>_`
- [ ] SCSS variables: `$o-*` prefix
- [ ] No bare class names
- [ ] No `!important` (except overriding core)
- [ ] No ID selectors

## JS/OWL
- [ ] Component conventions followed
- [ ] Assets registered in manifest
- [ ] Proper asset bundle used

## Evidence
- [ ] All violations cited with file path and line number
- [ ] Evidence captured in `docs/evidence/{stamp}/odoo-review/code-review-judge/`
