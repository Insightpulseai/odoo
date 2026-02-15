# Testing: TransactionCase, HttpCase, Tours

## What it is

Odoo includes a testing framework based on `unittest` to ensure module reliability.

## Key concepts

- **TransactionCase:** Tests run in a transaction that is rolled back at the end. Ideal for backend logic.
- **HttpCase:** Tests that can interact with the HTTP layer. Required for Tours.
- **Tours:** JavaScript-based integration tests that simulate user interaction in the browser.

## Implementation patterns

### TransactionCase

```python
from odoo.tests.common import TransactionCase

class TestMyModel(TransactionCase):
    def setUp(self):
        super().setUp()
        self.record = self.env['my.model'].create({'name': 'Test'})

    def test_compute(self):
        self.record.value = 10
        self.assertEqual(self.record.display_name, 'Test (10)')
```

### HttpCase (Tour)

```python
from odoo.tests.common import HttpCase, tagged

@tagged('post_install', '-at_install')
class TestUi(HttpCase):
    def test_my_tour(self):
        self.start_tour("/web", 'my_module_tour', login="admin")
```

## Gotchas

- **Post-install vs At-install:** Use `post_install=True` for tests relying on fully loaded module data or cross-module dependencies.
- **Demo Data:** Tests often rely on demo data. Ensure `demo/` files are correctly loaded in the manifest.

## References

- [Odoo Testing Documentation](https://www.odoo.com/documentation/19.0/developer/reference/backend/testing.html)
