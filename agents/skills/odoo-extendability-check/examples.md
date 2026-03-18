# Examples — odoo-extendability-check

## Example 1: Well-structured module — PASS

**Input**: `ipai_helpdesk/models/helpdesk_ticket.py` — ticket management model.

**Review**:
```
Extendability Report

Violations: none

Details:
- Method sizes: largest is action_resolve at 22 lines — PASS
- Hook points: _validate_resolution(), _apply_resolution(), _notify_resolution() — PASS
- Inheritance: _inherit = 'mail.thread' with proper super() calls — PASS
- No hardcoded values — PASS
- CRUD: create() override is 8 lines, delegates to _prepare_ticket_defaults() — PASS
- Fields: related fields use related=, computes use _compute_ methods — PASS

Example of good pattern found:
  def action_resolve(self):
      self.ensure_one()
      self._validate_resolution()
      self._apply_resolution()
      self._notify_resolution()
      return True

Risk assessment: low
```

## Example 2: Monolithic method — FAIL

**Input**: `ipai_invoice_automation/models/auto_invoice.py` — automated invoicing.

**Review**:
```
Extendability Report

Violations:
- [HIGH] models/auto_invoice.py:25-95 — method too large (70 lines, threshold 30)
  Method: action_generate_invoices
  The method handles validation, line preparation, invoice creation, payment
  registration, and email notification all in one block. A submodule cannot
  override just the payment step without copying the entire method.

  Suggestion: extract into:
    - _validate_invoice_generation(self) — pre-condition checks (lines 28-40)
    - _prepare_invoice_lines(self, order) — line data preparation (lines 42-58)
    - _create_invoice(self, vals) — invoice record creation (lines 60-72)
    - _register_payment(self, invoice) — payment registration (lines 74-85)
    - _notify_invoice_created(self, invoice) — email notification (lines 87-93)

- [HIGH] models/auto_invoice.py:45 — hardcoded value blocks extension
  Code: `if order.amount_total > 50000:`
  Suggestion: move threshold to system parameter `ipai.invoice.auto_review_threshold`
  or a field on the company/configuration.

- [MEDIUM] models/auto_invoice.py:78 — hardcoded email
  Code: `template = 'ipai_invoice_automation.email_invoice_created'`
  Suggestion: make template reference configurable via a field or method
  `_get_invoice_email_template()` so submodules can override.

- [LOW] models/auto_invoice.py:15-22 — business logic in create()
  Code: create() override contains tax computation logic (8 lines)
  Suggestion: extract to `_compute_default_taxes()` method.

Refactoring suggestions:
1. Break action_generate_invoices into 5 methods (lines 25-95)
2. Replace hardcoded 50000 threshold with system parameter (line 45)
3. Make email template configurable via overridable method (line 78)
4. Extract tax computation from create() to dedicated method (lines 15-22)

Risk assessment: high
```

## Example 3: Copy instead of inherit — FAIL

**Input**: `ipai_sale_custom/models/sale_order.py` — sale order customization.

**Review**:
```
Extendability Report

Violations:
- [CRITICAL] models/sale_order.py — copy instead of _inherit
  The file defines a new model `ipai.sale.order` that duplicates 150 lines from
  `sale.order` instead of using `_inherit = 'sale.order'`. This means upstream
  bug fixes and OCA module extensions will not apply to this model.

  Code (line 8): `_name = 'ipai.sale.order'`
  Expected: `_inherit = 'sale.order'` (no _name, extending existing model)

- [HIGH] models/sale_order.py:35-80 — duplicated method
  Method: _compute_amount_total duplicates sale.order._amount_all with minor changes.
  Suggestion: inherit and call super(), then apply the delta:
    @api.depends('order_line.price_total', 'discount_global')
    def _amount_all(self):
        super()._amount_all()
        for order in self:
            order.amount_total -= order.discount_global

- [MEDIUM] models/sale_order.py:90 — hardcoded selection
  Code: `state = fields.Selection([('draft', 'Draft'), ('sent', 'Sent'), ('done', 'Done')])`
  The original sale.order has more states. By redefining the field, submodules
  adding states will conflict.
  Suggestion: do not redefine state field; use selection_add if adding new options.

Refactoring suggestions:
1. Change model to _inherit = 'sale.order' (remove _name)
2. Remove duplicated _compute_amount_total, override with super() + delta
3. Remove state field redefinition, use selection_add if needed

Risk assessment: critical (architecture violation — must fix before merge)
```
