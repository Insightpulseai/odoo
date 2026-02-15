# Odoo 19 Testing

## Concept

Odoo uses `unittest` to run server-side tests. Tests are essential for preventing regressions and are automatically run by the Odoo CIs.

## Test Types

1. **TransactionCase:** Runs each test in a transaction that is rolled back. Fast and clean.
2. **SingleTransactionCase:** Runs all tests in a class within _one_ transaction. Useful for sharing state but risks pollution.
3. **HttpCase:** Integration tests that can spawn a headless browser (Chrome) for testing tours (UI flows).

## File Structure

`your_module/tests/__init__.py`:

```python
from . import test_foo
from . import test_bar
```

`your_module/tests/test_foo.py`:

```python
from odoo.tests.common import TransactionCase, tagged

@tagged('post_install', '-at_install')
class TestFoo(TransactionCase):
    def test_logic(self):
        record = self.env['my.model'].create({'name': 'Test'})
        self.assertEqual(record.name, 'Test')
```

## Running Tests

Command line:
`./odoo-bin -i my_module --test-enable`
`./odoo-bin --test-tags /my_module`

## Common Mistakes

- **Forgetting `__init__.py`:** Test files not imported in `tests/__init__.py` will NOT run.
- **Side Effects:** Tests should not commit data. `TransactionCase` handles rollback automatically.
- **Wrong Tags:** `@tagged('at_install')` runs _during_ installation (before all data is loaded). `@tagged('post_install')` is safer for business logic.

## Agent Notes

- **Tours (HttpCase):** Define a sequence of UI steps in JS (`registry.category("web_tour.tours").add(...)`) and execute them from Python using `self.start_tour("/web", "my_tour_name", login="admin")`.
- **Form:** `odoo.tests.common.Form` simulates backend form views (onchange interactions) in Python access.

## Source Links

- [Testing Odoo](https://www.odoo.com/documentation/19.0/developer/reference/backend/testing.html)
