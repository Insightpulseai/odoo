# Examples — odoo-orm-model-extension

## Example 1: Add profitability fields to project.project

**Input**: Extend `project.project` with margin tracking fields

**Output**:
```python
from odoo import api, fields, models
from odoo.tools import float_compare


class ProjectProject(models.Model):
    _inherit = 'project.project'

    budget_amount = fields.Monetary(string='Budget', currency_field='currency_id')
    actual_cost = fields.Monetary(compute='_compute_actual_cost', store=True)
    margin_pct = fields.Float(compute='_compute_margin_pct', digits=(5, 2))
    is_over_budget = fields.Boolean(compute='_compute_margin_pct')

    @api.depends('budget_amount', 'actual_cost')
    def _compute_margin_pct(self):
        for rec in self:
            if float_compare(rec.budget_amount, 0.0, precision_digits=2) > 0:
                rec.margin_pct = ((rec.budget_amount - rec.actual_cost) / rec.budget_amount) * 100
                rec.is_over_budget = rec.actual_cost > rec.budget_amount
            else:
                rec.margin_pct = 0.0
                rec.is_over_budget = False
```

- Compilation: PASS
- Test install: PASS (`test_ipai_finance_ppm`)

## Example 2: Rejected — direct core modification attempted

**Input**: Modify `vendor/odoo/addons/sale/models/sale_order.py` to add a field

**Output**:
- Validation: FAIL (BLOCKER)
- Reason: Direct modification of core Odoo source is prohibited
- Recommendation: Create `ipai_sale_<feature>` module using `_inherit = 'sale.order'`

## Example 3: x2many write with Command tuples

**Input**: Update order lines on a sale order

**Output**:
```python
from odoo.fields import Command

order.write({'order_line': [
    Command.create({'product_id': product.id, 'product_uom_qty': 5}),
    Command.update(existing_line.id, {'product_uom_qty': 10}),
    Command.delete(obsolete_line.id),
]})
```
- Uses Command tuples: PASS (not raw `(0, 0, vals)` tuples)
