---
applyTo: "addons/**/*.py"
---

You are editing Odoo 18 CE Python code.

## ORM conventions

- Use `fields.*` declarations, not raw SQL columns
- Compute methods: `@api.depends(...)` with `_compute_<field>` naming
- Inverse methods: `_inverse_<field>` naming
- Onchange: prefer `@api.onchange` only when compute cannot work
- Constraints: `@api.constrains(...)` with `_check_<rule>` naming
- Default values: use `default=` parameter or `_default_<field>` method

## Inheritance

- Use `_inherit` for extension (same `_name` = extend, different `_name` = delegation)
- Never copy-paste upstream models; inherit and override specific methods
- Call `super()` unless you are explicitly replacing behavior
- Use `_inherits` (delegation) sparingly and only for composition

## Method safety

- No `sudo()` in user-facing flows unless security-justified and documented
- No `with_context(active_test=False)` to bypass archive filters silently
- No raw SQL unless performance-critical and commented why ORM is insufficient
- Use `self.env.ref('module.xml_id')` for record references, not hardcoded IDs

## Import style

```python
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
```

## Naming

- Model: `ipai.<domain>.<entity>` (e.g., `ipai.finance.ppm.project`)
- Module: `ipai_<domain>_<feature>` directory name
- Python files: lowercase, underscored, matching model name

## Do not

- Add fields that shadow CE or OCA field names
- Import from `odoo.addons.enterprise_*` or any EE module
- Use `_auto = False` without a clear reporting reason
- Create models with `_transient = True` unless genuinely wizard-only
