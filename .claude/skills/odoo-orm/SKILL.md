---
name: Odoo ORM
description: Edit Odoo Python models, fields, inheritance, compute logic, recordsets, or ORM methods. Use when working with model definitions or data access.
---

# Odoo ORM

## Purpose

Write correct Odoo 18 CE model definitions, field declarations, inheritance, compute logic, and recordset operations.

## When to use

- Adding or modifying model fields
- Writing compute/inverse/onchange methods
- Extending models via `_inherit`
- Working with recordsets, environments, or contexts
- Handling domain expressions or search logic
- Error handling with `UserError` / `ValidationError`

## Inputs or assumptions

- Odoo 18 CE Python API
- `@api.multi` does not exist (removed since 13.0)
- All custom models use `ipai.` prefix

## Source priority

1. Local model files in `addons/`
2. Odoo 18 CE ORM documentation
3. OCA module patterns

## Workflow

1. Read existing model code before modifying
2. Prefer `_inherit` extension over new models
3. Declare all field dependencies in `@api.depends`
4. Iterate `self` in all compute methods (multi-record)
5. Test with `odoo-bin --test-enable`

## Models

```python
class MyModel(models.Model):
    _name = "ipai.my.model"
    _description = "My Model"
    _order = "sequence, name"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    state = fields.Selection([
        ("draft", "Draft"),
        ("confirmed", "Confirmed"),
        ("done", "Done"),
    ], default="draft", required=True)
```

## Inheritance patterns

| Pattern | Use case |
|---------|----------|
| `_inherit = "existing.model"` (no `_name`) | Add fields/methods to existing model |
| `_inherit = "existing.model"` + `_name = "new.model"` | Prototype inheritance (copy) |
| `_inherits = {"res.partner": "partner_id"}` | Delegation (composition) |

Prefer extension (`_inherit` without `_name`) for 90% of cases.

## Field types

- `Char`, `Text`, `Html`, `Integer`, `Float`, `Monetary`, `Boolean`
- `Date`, `Datetime`
- `Selection` — use `selection_add` to extend inherited selections
- `Many2one`, `One2many`, `Many2many`
- `Binary`, `Image`
- `Reference` — polymorphic reference (rare)

## Compute fields

```python
total = fields.Float(compute="_compute_total", store=True)

@api.depends("line_ids.amount")
def _compute_total(self):
    for record in self:
        record.total = sum(record.line_ids.mapped("amount"))
```

- Always iterate `self` (recordsets can be multi-record)
- Use `store=True` if the value should be searchable/groupable
- Declare `@api.depends` with all field dependencies

## Decorators

| Decorator | Purpose |
|-----------|---------|
| `@api.depends(...)` | Recompute triggers for stored compute fields |
| `@api.constrains(...)` | Validation on write/create |
| `@api.onchange(...)` | UI-only feedback (not triggered on API writes) |
| `@api.model` | Class-level method (no recordset) |
| `@api.model_create_multi` | Batch-optimized create |

## Recordset operations

- `self.env["model"].search([domain])` — search
- `self.env["model"].browse(ids)` — load by ID
- `self.env.ref("module.xml_id")` — load by XML ID
- `record.mapped("field.subfield")` — extract values
- `record.filtered(lambda r: r.state == "draft")` — filter
- `record.sorted(key="name")` — sort

## Output format

Python model code following OCA conventions with proper imports, field declarations, and method signatures.

## Verification

- Module installs without error
- Compute fields produce correct values
- Constraints fire on invalid data
- `@api.depends` covers all dependencies (no stale compute cache)

## Anti-patterns

- Using raw SQL unless ORM performance is proven insufficient
- Calling `sudo()` in user-facing flows without security justification
- Shadowing CE/OCA field names with different semantics
- Creating `_transient` models unless genuinely wizard-only
- Using `_auto = False` without a reporting use case
- Forgetting to iterate `self` in compute methods
