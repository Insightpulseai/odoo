---
applyTo: "addons/**/tests/**/*.py"
---

You are writing Odoo 18 CE tests.

## Test discovery

- Tests live in `<module>/tests/` directory
- `tests/__init__.py` imports test classes: `from . import test_my_feature`
- Module root `__init__.py` must NOT import tests (Odoo discovers them automatically)
- Tag with `@tagged("post_install", "-at_install")` for post-install tests

## Test classes

- `TransactionCase`: each test method runs in a rolled-back transaction (most common)
- `SingleTransactionCase`: all methods share one transaction (rare, for ordered tests)
- `HttpCase`: for testing controllers and browser behavior
- `unittest.TestCase`: for pure Python logic with no Odoo runtime needed

## Patterns

```python
from odoo.tests import TransactionCase, tagged

@tagged("post_install", "-at_install")
class TestMyFeature(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test"})

    def test_feature_behavior(self):
        """Test that the feature does what we expect."""
        result = self.partner.action_do_something()
        self.assertTrue(result)
```

## Database conventions

- Test DB name: `test_<module>` (disposable, never `odoo_dev` or `odoo_staging`)
- Use `cls.env["model"].create(...)` in `setUpClass` for shared fixtures
- Clean up is automatic via transaction rollback

## What to test

- Model constraints and validations
- State machine transitions
- Compute field correctness
- Access control (test as non-admin user with `self.env(user=...)`)
- Controller endpoints (HttpCase)
- XML data integrity (views load without error)

## Do not

- Import tests in module root `__init__.py` (breaks `post_load` modules, duplicates discovery)
- Use `sudo()` in tests unless testing privilege escalation
- Test OCA or CE internals (test your module's behavior only)
- Leave `print()` or `_logger.info()` debug output in committed tests
- Use `time.sleep()` in tests
