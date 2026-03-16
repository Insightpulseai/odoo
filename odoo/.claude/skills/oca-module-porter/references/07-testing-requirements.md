# OCA Testing Requirements

Sources:
- https://www.odoo.com/documentation/18.0/developer/reference/backend/testing.html
- https://github.com/OCA/maintainer-quality-tools
- https://github.com/camptocamp/pytest-odoo

---

## Test Directory Structure

```
MODULE/
|-- tests/
|   |-- __init__.py         # Import all test modules
|   |-- test_common.py      # Shared fixtures and base classes
|   |-- test_model_name.py  # Tests for each model
|   `-- test_wizard_name.py # Tests for wizards
```

`__init__.py`:
```python
from . import test_model_name
from . import test_wizard_name
```

---

## Test Case Classes

### TransactionCase (Most Common)

```python
from odoo.tests.common import TransactionCase

class TestModelName(TransactionCase):
    """
    Tests that need a clean database state.
    Database is rolled back after each test method.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Class-level setup (runs once for all tests in class)
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Partner',
        })

    def setUp(self):
        super().setUp()
        # Per-test setup (runs before each test)

    def test_basic_functionality(self):
        """Test basic module functionality"""
        result = self.env['module.model'].create({
            'name': 'Test Record',
            'partner_id': self.partner.id,
        })
        self.assertEqual(result.name, 'Test Record')
        self.assertTrue(result.active)

    def test_constraint_validation(self):
        """Test model constraints"""
        with self.assertRaises(Exception):
            self.env['module.model'].create({
                'name': '',  # Should fail: name is required
            })
```

### HttpCase (Controller / Portal Tests)

```python
from odoo.tests.common import HttpCase

class TestPortalController(HttpCase):
    """
    Tests requiring HTTP server — for controllers, website, portal.
    Slower than TransactionCase.
    """

    def test_portal_page_accessible(self):
        self.authenticate('admin', 'admin')
        response = self.url_open('/my/invoices')
        self.assertEqual(response.status_code, 200)

    def test_portal_page_requires_login(self):
        response = self.url_open('/my/invoices')
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
```

### SavepointCase (Performance-Optimized)

```python
from odoo.tests.common import SavepointCase

class TestHighVolumeOperations(SavepointCase):
    """
    Tests without rollback between tests.
    Faster but requires careful test isolation.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Data created here persists across all tests in class
        cls.records = cls.env['module.model'].create([
            {'name': f'Record {i}'} for i in range(100)
        ])
```

---

## Test Tags

```python
from odoo.tests import tagged

# Standard tag (included in default test suite automatically via BaseCase inheritance)
class TestModelName(TransactionCase):
    pass

# Custom tags
@tagged('post_install', '-at_install')
class TestAfterInstall(TransactionCase):
    """Run after all modules installed, not during install"""
    pass

@tagged('at_install')
class TestDuringInstall(TransactionCase):
    """Run during module installation"""
    pass

# Run specific tags:
# ./odoo-bin --test-tags=MODULE_NAME
# ./odoo-bin --test-tags=post_install
# ./odoo-bin --test-tags=-at_install  (exclude)
```

---

## Common Test Patterns

### Testing Computed Fields

```python
def test_computed_field(self):
    record = self.env['module.model'].create({'value': 10.0})
    self.assertEqual(record.double_value, 20.0)

    record.write({'value': 15.0})
    self.assertEqual(record.double_value, 30.0)
```

### Testing Onchange

```python
def test_onchange_partner(self):
    record = self.env['module.model'].new({'partner_id': self.partner.id})
    record._onchange_partner_id()
    self.assertEqual(record.email, self.partner.email)
```

### Testing Access Rights

```python
def test_user_cannot_write(self):
    user_env = self.env['module.model'].with_user(self.env.ref('base.user_demo'))
    with self.assertRaises(AccessError):
        user_env.create({'name': 'Test'})
```

### Testing Workflows / State Changes

```python
def test_approval_workflow(self):
    record = self.env['module.model'].create({'name': 'Test', 'state': 'draft'})
    self.assertEqual(record.state, 'draft')

    record.action_confirm()
    self.assertEqual(record.state, 'confirmed')

    record.action_approve()
    self.assertEqual(record.state, 'approved')
```

### Testing Constraints

```python
def test_unique_name_constraint(self):
    self.env['module.model'].create({'name': 'Unique'})
    with self.assertRaises(IntegrityError):
        self.env['module.model'].create({'name': 'Unique'})
    # or for Python constraints:
    with self.assertRaises(ValidationError):
        self.env['module.model'].create({'value': -1})
```

---

## Running Tests

### Via Odoo CLI

```bash
# Run all tests for a module
./odoo-bin -d odoo_test --test-enable -i MODULE --stop-after-init

# Run specific test class
./odoo-bin -d odoo_test --test-enable -i MODULE \
  --test-tags=MODULE.TestClassName --stop-after-init

# Run specific test method
./odoo-bin -d odoo_test --test-enable -i MODULE \
  --test-tags=MODULE.TestClassName.test_method_name --stop-after-init
```

### Via pytest-odoo

```bash
# Install
pip3 install pytest-odoo coverage

# Basic run
pytest --odoo-database=odoo_test --addons-path=. MODULE/tests/

# With coverage
pytest --odoo-database=odoo_test \
  --cov=MODULE \
  --cov-report=html:coverage_html \
  --cov-report=term-missing \
  MODULE/tests/

# Run specific test
pytest --odoo-database=odoo_test \
  MODULE/tests/test_model.py::TestModelName::test_method

# Verbose
pytest -v --odoo-database=odoo_test MODULE/tests/

# Skip slow tests
pytest -m "not slow" --odoo-database=odoo_test MODULE/tests/
```

---

## OCA Test Coverage Expectations

| Maturity Level | Coverage Expectation |
|----------------|---------------------|
| Alpha | Minimal (proof of concept) |
| Beta | Basic coverage of main features |
| Production/Stable | >75% recommended |
| Mature | >85% recommended |

Coverage is checked automatically via Coveralls/Codecov in CI. A PR showing
decreased coverage will receive a warning comment from the bot.

---

## What to Test for a Ported Module

When porting, focus on verifying:

1. **Install test**: Module installs without errors
2. **Load test**: Module is found in `ir.module.module`
3. **Basic CRUD**: Create, read, update, delete records
4. **Computed fields**: Values are computed correctly
5. **Constraints**: Validation errors are raised appropriately
6. **State transitions**: Workflow methods work correctly
7. **Access rights**: Groups have correct access

If existing tests exist in the source version — they should still pass after porting.
If they don't, it indicates a migration gap that needs fixing.

---

## Minimal Smoke Test Script

```bash
#!/usr/bin/env bash
# smoke_test.sh — Minimal acceptance test for a ported module
MODULE="${1:?Usage: smoke_test.sh MODULE_NAME}"
DB="${ODOO_DB:-odoo_test}"

echo "=== Smoke Test: ${MODULE} ==="

# 1. Syntax check
echo "1. Python syntax check..."
python3 -m py_compile ${MODULE}/**/*.py 2>&1
if [ $? -eq 0 ]; then
    echo "   PASS: No syntax errors"
else
    echo "   FAIL: Syntax errors found"
    exit 1
fi

# 2. Manifest version
echo "2. Manifest version check..."
VERSION=$(python3 -c "
import ast
with open('${MODULE}/__manifest__.py') as f:
    m = ast.literal_eval(f.read())
print(m.get('version', 'MISSING'))
")
echo "   Version: ${VERSION}"

# 3. Install
echo "3. Module install..."
./odoo-bin -d ${DB} --test-enable -i ${MODULE} --stop-after-init \
  --log-level=warn 2>&1 | tail -5

echo "=== Smoke Test Complete ==="
```
