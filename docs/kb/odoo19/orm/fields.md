# Odoo 19 ORM: Fields

## Concept

Fields define the structure of the database table and the data types of records.

## Applies To

- Database Schema
- Form/Tree Views
- API Serialization

## Core Models

- `odoo.fields.Char`, `Text`, `Html`
- `odoo.fields.Integer`, `Float`, `Monetary`
- `odoo.fields.Boolean`
- `odoo.fields.Selection`
- `odoo.fields.Date`, `Datetime`
- `odoo.fields.Binary`
- **Relational:** `Many2one`, `One2many`, `Many2many`

## Extension Pattern

**Adding a Field:**

```python
class Partner(models.Model):
    _inherit = 'res.partner'

    is_vip = fields.Boolean(string="VIP Customer", default=False)
```

**Computed Fields:**

```python
total = fields.Float(compute='_compute_total', store=True)

@api.depends('line_ids.amount')
def _compute_total(self):
    for record in self:
        record.total = sum(record.line_ids.mapped('amount'))
```

## Common Mistakes

- **Non-stored Compute Fields:** Cannot be searched unless `search=` argument is provided.
- **Missing `@api.depends`:** Computed fields won't update when dependencies change.
- **Mutable Defaults:** Using mutable types (list/dict) as default values (use a function instead).
- **One2many without Inverse:** `One2many` must strictly point to a `Many2one` on the target model.

## Agent Notes

- `Monetary` fields require a `currency_id` field on the model.
- `Date` and `Datetime` fields have specific helpers for conversion (`fields.Date.today()`).

## Source Links

- [ORM API - Fields](https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html#fields)
