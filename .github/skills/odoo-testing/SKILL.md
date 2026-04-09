---
name: Odoo Testing
description: Use when writing Python tests, JS tests, smoke tests, or debugging test failures in Odoo 18 CE.
---

# Odoo Testing

## When to use

- Writing `TransactionCase` or `HttpCase` tests
- Using the `Form` test helper for UI simulation
- Writing JS/Owl component tests
- Debugging test failures or install smoke issues
- Setting up test fixtures

## Test file layout

```
<module>/tests/
├── __init__.py          # Imports all test modules
├── test_<feature>.py    # Feature tests
└── test_<other>.py      # Additional test files
```

**Critical**: Module root `__init__.py` must NOT import tests. Odoo discovers them via `tests/__init__.py`.

## Python test classes

| Class | Use case | DB behavior |
|-------|----------|-------------|
| `TransactionCase` | Standard model tests | Rolls back per method |
| `SingleTransactionCase` | Ordered sequential tests | Shared transaction |
| `HttpCase` | Controller / browser tests | Full HTTP stack |
| `unittest.TestCase` | Pure Python logic | No Odoo runtime |

## Standard pattern

```python
from odoo.tests import TransactionCase, tagged

@tagged("post_install", "-at_install")
class TestMyFeature(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.record = cls.env["ipai.my.model"].create({
            "name": "Test Record",
        })

    def test_default_state(self):
        self.assertEqual(self.record.state, "draft")

    def test_confirm_transition(self):
        self.record.action_confirm()
        self.assertEqual(self.record.state, "confirmed")

    def test_constraint_enforced(self):
        with self.assertRaises(ValidationError):
            self.record.write({"name": False})
```

## Form helper (UI simulation)

```python
from odoo.tests import Form

def test_form_defaults(self):
    form = Form(self.env["ipai.my.model"])
    form.name = "Test"
    record = form.save()
    self.assertEqual(record.state, "draft")
```

## Tags

| Tag | Meaning |
|-----|---------|
| `post_install` | Run after all modules are installed |
| `-at_install` | Do NOT run during module installation |
| `standard` | Default tag for standard tests |

Use `@tagged("post_install", "-at_install")` for most tests.

## Running tests

```bash
# Test a specific module (disposable DB)
odoo -d test_my_module -i ipai_my_module --test-enable --stop-after-init --no-http

# Test with specific test class
odoo -d test_my_module -i ipai_my_module --test-enable --test-tags /ipai_my_module --stop-after-init
```

## What to test

- Model constraints and validations
- State machine transitions (all valid paths + invalid paths)
- Compute field correctness
- Default values
- Access control (test as restricted user: `self.env(user=limited_user)`)
- XML data integrity (views load, menus resolve)
- Controller endpoints (HttpCase)

## Do not

- Use `odoo_dev` or `odoo_staging` for test databases
- Add `from . import tests` in module root `__init__.py`
- Leave debug `print()` or excessive `_logger` in tests
- Use `time.sleep()` in tests
- Test CE/OCA internals (only test your module's behavior)
- Mock the database when integration tests are feasible
