# Odoo 19 ORM: Models

## Concept

Odoo models are the core primitives for data persistence and business logic. They inherit from `models.Model` (regular DB-persisted), `models.TransientModel` (temporary data like wizards), or `models.AbstractModel` (interfaces/mixins).

## Applies To

- Backend development
- Database schema definition
- Business logic implementation

## Core Models

- `odoo.models.Model`: Main superclass for persistent records.
- `odoo.models.TransientModel`: Superclass for wizard records (cleared periodically).
- `odoo.models.AbstractModel`: Superclass for mixins/interfaces (no table created).

## Extension Pattern

**Inheritance (`_inherit`):**

```python
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    new_field = fields.Char()

    def action_confirm(self):
        # Pre-logic
        res = super().action_confirm()
        # Post-logic
        return res
```

**Delegation (`_inherits`):**
Transparently link to another model (like OOP inheritance but with DB foreign keys).

## Common Mistakes

- **Forgetting `super()`:** Breaks the inheritance chain.
- **Using `os` or `sys`:** Odoo modules should be self-contained; avoid system calls unless necessary.
- **Direct SQL Injection:** Always use the ORM or parameterized queries (`self.env.cr.execute(query, params)`).
- **Mutating `self` inside loops:** `self` is a recordset; iterating effectively creates singleton recordsets.

## Agent Notes

- Always check `_inherit` vs `_name`. `_name` creates a new model; `_inherit` without `_name` extends an existing one.
- AbstractModels are powerful for sharing logic across different models (e.g., `mail.thread`).

## Source Links

- [ORM API - Models](https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html#models)
