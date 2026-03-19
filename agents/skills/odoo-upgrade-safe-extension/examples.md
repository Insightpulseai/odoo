# Examples — odoo-upgrade-safe-extension

## Example 1: Module passes upgrade safety audit

**Input**: Audit `ipai_finance_ppm` module

**Output**:
- Inheritance audit:
  - `models/project_profitability.py`: `_inherit = 'project.project'` — PASS
- Core modifications: none found — PASS
- OCA modifications: none found — PASS
- Migration scripts: no schema changes detected — N/A
- Deprecated patterns: none found — PASS
- Odoo 19 compatibility: no `groups_id` usage, no `tree` in user-facing — PASS
- Overall: **SAFE**

## Example 2: Module fails — core file modified

**Input**: Audit module that edited `vendor/odoo/addons/sale/models/sale_order.py`

**Output**:
- Core modifications: `vendor/odoo/addons/sale/models/sale_order.py` — FAIL (BLOCKER)
- Reason: Direct modification of upstream Odoo source breaks upgrade safety
- Recommendation: Revert core change; create `ipai_sale_<feature>` module with `_inherit = 'sale.order'`
- Overall: **UNSAFE**

## Example 3: Deprecated patterns detected

**Input**: Audit module with legacy x2many writes

**Output**:
- Deprecated patterns found:
  - `models/order.py:45`: `(0, 0, {'name': 'New'})` — use `Command.create({'name': 'New'})`
  - `models/order.py:52`: `self.env.context['skip_check'] = True` — use `self.with_context(skip_check=True)`
  - `models/order.py:78`: `_(f'Order {rec.name} confirmed')` — use `_('Order %s confirmed', rec.name)`
- Overall: **UNSAFE** (3 deprecated patterns must be fixed before upgrade)

## Example 4: Missing migration script

**Input**: Module adds a required field to existing model without migration

**Output**:
- Migration scripts: MISSING
- Reason: New required field `margin_pct` on `project.project` needs a pre-migration to set default values for existing records
- Recommendation: Create `migrations/19.0.1.1.0/pre-migrate.py` with `ALTER TABLE` or ORM default
- Overall: **UNSAFE** (will fail on upgrade for existing databases)
