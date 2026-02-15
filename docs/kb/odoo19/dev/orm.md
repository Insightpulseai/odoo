# Odoo ORM: Models, Fields, Environment

## What it is

The Object-Relational Mapping (ORM) layer is the core of Odoo's backend. It maps Python classes to PostgreSQL database tables and provides an API to interact with data.

## Key concept

- **Models:** Python classes inheriting from `models.Model` (regular), `models.TransientModel` (wizards), or `models.AbstractModel` (interfaces).
- **Fields:** Attributes defining database columns (`Char`, `Integer`, `Many2one`, etc.).
- **Environment:** The context in which recordsets are accessed (`self.env`), containing user, company, and language data.

## Implementation patterns

### Defining a Model

```python
from odoo import models, fields, api

class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Custom Model'

    name = fields.Char(required=True)
    value = fields.Integer()

    @api.depends('value')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.name} ({record.value})"
```

### Recordset Operations

- **Search:** `records = self.env['my.model'].search([('value', '>', 10)])`
- **Browse:** `record = self.env['my.model'].browse(1)`
- **Write:** `record.write({'value': 20})`
- **Create:** `new_record = self.env['my.model'].create({'name': 'New', 'value': 20})`

## Gotchas

- **Computed Fields:** Must depend on stored fields to trigger updates. Use `store=True` to persist in DB.
- **Environment Cache:** The ORM caches data heavily. Use `invalidate_cache()` if bypassing ORM via SQL.
- **Access Rights:** ORM methods check ACLs by default. Use `sudo()` to bypass checks ONLY when necessary.

## References

- [Odoo ORM Documentation](https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html)
