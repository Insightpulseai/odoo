---
name: Odoo Testing
description: Write Python tests, JS tests, smoke tests, or debug test failures in Odoo 18 CE. Use when creating or fixing module tests.
---

# Odoo Testing

## Purpose

Write and run correct Odoo 18 CE module tests using `TransactionCase`, `HttpCase`, and the `Form` helper.

## When to use

- Writing `TransactionCase` or `HttpCase` tests
- Using the `Form` test helper for UI simulation
- Writing JS/Owl component tests
- Debugging test failures or install smoke issues
- Setting up test fixtures

## Inputs or assumptions

- Test databases are disposable: `test_<module>` naming
- Never use `odoo_dev`, `odoo_staging`, or `odoo` for tests
- Module root `__init__.py` must NOT import tests

## Source priority

1. Local test files in `addons/`
2. Odoo 18 CE testing documentation
3. OCA test patterns

## Workflow

1. Create `tests/__init__.py` importing all test modules
2. Write test class extending `TransactionCase`
3. Use `@tagged("post_install", "-at_install")`
4. Create fixtures in `setUpClass`
5. Run: `odoo-bin -d test_<module> -i <module> --test-enable --stop-after-init --no-http`

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

## What to test

- Model constraints and validations
- State machine transitions (all valid + invalid paths)
- Compute field correctness
- Default values
- Access control (test as restricted user: `self.env(user=limited_user)`)
- XML data integrity (views load, menus resolve)
- Controller endpoints (HttpCase)

## Output format

Test class files with proper imports, fixtures, and assertions.

## Verification

- All tests pass: `--test-enable --stop-after-init`
- No `print()` or `time.sleep()` in test code
- Disposable DB used (`test_<module>`)

## Anti-patterns

- Using `odoo_dev` or shared databases for tests
- Adding `from . import tests` in module root `__init__.py`
- Leaving debug `print()` or excessive `_logger` in tests
- Using `time.sleep()` in tests
- Testing CE/OCA internals (only test your module's behavior)
- Mocking the database when integration tests are feasible
