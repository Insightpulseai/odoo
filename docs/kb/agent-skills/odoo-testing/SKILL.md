---
name: odoo-testing
description: Odoo 18 test patterns — TransactionCase, HttpCase, test data, assertions
category: qa
priority: high
---

# Odoo 18 Testing Patterns

## Test Classes

| Class | Use case | Isolation |
|-------|----------|-----------|
| `TransactionCase` | Standard model/logic tests | DB rollback after each test method |
| `HttpCase` | Controller routes, full HTTP stack | Separate transaction per request |
| `tagged()` | Control when tests run | Decorator on class or method |

`SavepointCase` is **deprecated in Odoo 18** — use `TransactionCase` instead.

```python
# Correct
from odoo.tests import TransactionCase, tagged

@tagged('post_install', '-at_install')
class TestSaleOrder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()  # NEVER skip this
        cls.partner = cls.env['res.partner'].create({'name': 'Test'})
```

## Test Discovery

- Test files live in `tests/` inside the module
- Every test file must be imported in `tests/__init__.py`
- Class names must start with `Test`

```python
# tests/__init__.py
from . import test_sale_logic
from . import test_invoice_flow
```

## Test Data

Create data in `setUpClass` via `cls.env`. Reference XML demo data with `cls.env.ref()`.

```python
# Correct — setUpClass with cls.env
@classmethod
def setUpClass(cls):
    super().setUpClass()
    cls.product = cls.env['product.product'].create({
        'name': 'Widget', 'list_price': 100.0,
    })
    cls.currency = cls.env.ref('base.USD')

# Wrong — hardcoded database IDs
def test_bad(self):
    partner = self.env['res.partner'].browse(42)  # NEVER do this
```

## Common Assertions

```python
def test_order_total(self):
    order = self.env['sale.order'].create({...})
    self.assertEqual(order.amount_total, 100.0)

    # Bulk field assertion across recordset
    self.assertRecordValues(order.order_line, [
        {'product_id': self.product.id, 'price_unit': 100.0},
    ])

    # Exception testing
    with self.assertRaises(ValidationError):
        order.write({'date_order': False})

# Form testing (simulates UI onchanges)
from odoo.tests.common import Form

def test_form_onchange(self):
    with Form(self.env['sale.order']) as f:
        f.partner_id = self.partner
        self.assertTrue(f.pricelist_id)
```

## Mocking

```python
from unittest.mock import patch
from freezegun import freeze_time

@tagged('post_install', '-at_install')
class TestMailSend(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context={'testing': True})

    # Mock outbound mail
    @patch('odoo.addons.mail.models.mail_mail.MailMail.send')
    def test_no_real_email(self, mock_send):
        self.env['mail.mail'].create({...}).send()
        mock_send.assert_called_once()

    # Freeze time for date-sensitive logic
    @freeze_time('2026-01-15')
    def test_deadline(self):
        self.assertEqual(fields.Date.today(), date(2026, 1, 15))
```

## Running Tests

```bash
# Run tests for a single module (disposable DB)
odoo -d test_mymodule -i ipai_finance_ppm --test-enable --stop-after-init

# Run only specific tagged tests
odoo -d test_mymodule -i ipai_finance_ppm --test-tags=post_install --stop-after-init

# Run a single test class
odoo -d test_mymodule -i ipai_finance_ppm --test-tags=.TestSaleOrder --stop-after-init
```

## What NOT To Do

| Anti-pattern | Why | Do instead |
|-------------|-----|------------|
| Test on `odoo_dev` or `odoo_prod` | Pollutes real data | Use `test_<module>` DB |
| Skip `super().setUpClass()` | Breaks env setup, causes cryptic errors | Always call super first |
| Hardcode record IDs (`browse(42)`) | IDs differ across databases | Use `create()` or `env.ref()` |
| Test OCA module internals | Not your code to validate | Test your `ipai_*` overrides only |
| Import `SavepointCase` | Deprecated in 19 | Use `TransactionCase` |
| Run tests on host machine | Missing deps, wrong Python | Run inside devcontainer |
