# Testing Odoo 18 - Official Patterns

**Documentation Reference:** [Odoo 18 Testing Docs](https://www.odoo.com/documentation/18.0/developer/reference/backend/testing.html)

---

## Quick Start

```bash
# Run all module tests
./bin/odoo-tests.sh

# Run specific module
./bin/odoo-tests.sh ipai_expense

# Run with specific tags
./bin/odoo-tests.sh ipai_expense /ipai_expense

# Run multiple modules
./bin/odoo-tests.sh "ipai_expense,ipai_equipment" "/ipai_"
```

---

## Test Structure (Odoo 18 Standard)

### Directory Layout

Every Odoo module with tests must follow this structure:

```
addons/ipai_expense/
├── __init__.py
├── __manifest__.py
├── models/
├── views/
├── security/
└── tests/                      # ← Tests subpackage
    ├── __init__.py             # Import all test files
    ├── test_business_flow.py   # Python unit tests
    └── test_expense_ocr.py     # Additional tests
```

### tests/__init__.py

**Required** - Must import all test modules:

```python
# -*- coding: utf-8 -*-
from . import test_business_flow
from . import test_expense_ocr
```

---

## Python Unit Tests

### TransactionCase Pattern

**File:** `tests/test_business_flow.py`

```python
from odoo.tests.common import TransactionCase, tagged
from odoo import fields


@tagged('post_install', '-at_install', 'ipai_expense')
class TestIpaiExpenseFlow(TransactionCase):
    """Test expense submission and approval workflow"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create test data
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Test Employee',
        })

        cls.Expense = cls.env['ipai.expense']

    def test_01_expense_creation(self):
        """Test expense can be created"""
        expense = self.Expense.create({
            'employee_id': self.employee.id,
            'description': 'Client Meeting',
            'date': fields.Date.today(),
            'amount': 1500.0,
        })

        self.assertTrue(expense)
        self.assertEqual(expense.state, 'draft')

    def test_02_expense_submit_approve_flow(self):
        """Test submission and approval"""
        expense = self.Expense.create({
            'employee_id': self.employee.id,
            'description': 'Travel Expense',
            'amount': 850.0,
        })

        expense.action_submit()
        self.assertEqual(expense.state, 'submitted')

        expense.action_approve()
        self.assertEqual(expense.state, 'approved')
```

### Key Points

1. **Use `TransactionCase`** from `odoo.tests.common`
2. **`setUpClass`** for test data creation
3. **`@tagged`** decorator for test filtering
4. **Test naming:** `test_XX_description` for ordered execution
5. **Assertions:** Use standard `self.assertEqual`, `self.assertTrue`, etc.

---

## Test Tags (Odoo 18)

Tags control when tests run:

### Standard Tags

- **`-at_install`** - Don't run during module installation
- **`post_install`** - Run after module is installed
- **`standard`** - Default tag
- **Custom tags** - Module-specific (e.g., `ipai_expense`)

### Tag Usage

```python
@tagged('post_install', '-at_install', 'ipai_expense')
class TestMyFeature(TransactionCase):
    pass
```

### Run by Tag

```bash
# Run only ipai_expense tests
./bin/odoo-tests.sh ipai_expense /ipai_expense

# Run all ipai_ modules
./bin/odoo-tests.sh "ipai_expense,ipai_equipment" "/ipai_"

# Run standard tests only
odoo-bin -d test_db -i ipai_expense --test-enable --test-tags=standard
```

---

## Test Types

### 1. Unit Tests (TransactionCase)

Fast tests for business logic:

```python
from odoo.tests.common import TransactionCase

class TestBusinessLogic(TransactionCase):
    def test_calculation(self):
        result = self.env['my.model'].calculate_tax(100)
        self.assertEqual(result, 112.0)
```

### 2. Integration Tests (SavepointCase)

Database rollback per test method:

```python
from odoo.tests.common import SavepointCase

class TestIntegration(SavepointCase):
    def test_workflow(self):
        # Test is rolled back after execution
        pass
```

### 3. HTTP Tests (HttpCase)

For testing controllers and routes:

```python
from odoo.tests import HttpCase, tagged

@tagged('post_install', '-at_install')
class TestAPI(HttpCase):
    def test_expense_endpoint(self):
        response = self.url_open('/api/expenses')
        self.assertEqual(response.status_code, 200)
```

### 4. Tour Tests (JavaScript Integration)

Test UI workflows:

```python
from odoo.tests import HttpCase, tagged

@tagged('-at_install', 'post_install', 'ipai_expense_tour')
class TestExpenseTour(HttpCase):
    def test_expense_tour(self):
        self.start_tour("/web", "ipai_expense_tour", login="admin")
```

---

## Running Tests

### Command Line

```bash
# Install module and run all tests
odoo-bin -d test_db -i ipai_expense --test-enable --stop-after-init

# Run specific tags
odoo-bin -d test_db -i ipai_expense --test-enable --test-tags=/ipai_expense

# Run multiple tags
odoo-bin -d test_db -i ipai_expense --test-enable --test-tags="/ipai_expense,/unit"

# Verbose logging
odoo-bin -d test_db -i ipai_expense --test-enable --log-level=test
```

### Helper Script

```bash
# Our helper (auto-detects modules)
./bin/odoo-tests.sh

# Specific module
./bin/odoo-tests.sh ipai_expense

# Multiple modules with tags
./bin/odoo-tests.sh "ipai_expense,ipai_equipment" "/ipai_"

# With custom database
DB_NAME=my_test_db ./bin/odoo-tests.sh ipai_expense
```

---

## CI/CD Integration

### GitHub Actions (Current Setup)

```yaml
- name: Run Odoo 18 tests
  run: |
    # Auto-detect and run all module tests
    ./bin/odoo-tests.sh

# Or specific modules
- name: Run specific module tests
  run: |
    ./bin/odoo-tests.sh "ipai_expense,ipai_equipment" "/ipai_"
```

### Test Matrix (Already Configured)

Our CI runs 3 test suites in parallel:
1. **Unit Tests** - Tagged `/unit`
2. **Integration Tests** - Tagged `/integration`
3. **All Tests** - Complete suite with coverage

---

## Best Practices

### 1. Test Naming

```python
def test_01_creation(self):      # ✅ Good - numbered for order
def test_submit_flow(self):      # ✅ Good - descriptive
def testSubmit(self):            # ❌ Bad - not descriptive
```

### 2. Test Data

```python
@classmethod
def setUpClass(cls):
    super().setUpClass()
    # Create shared test data here
    cls.employee = cls.env['hr.employee'].create({...})

def setUp(self):
    super().setUp()
    # Create per-test data here
```

### 3. Assertions

```python
# ✅ Good - specific assertions
self.assertEqual(expense.state, 'draft')
self.assertTrue(expense.employee_id)
self.assertIn('amount', expense._fields)

# ❌ Bad - generic assertions
self.assertTrue(expense.state == 'draft')
```

### 4. Test Independence

```python
# ✅ Good - tests don't depend on each other
def test_01_create(self):
    expense = self.Expense.create({...})
    self.assertTrue(expense)

def test_02_submit(self):
    expense = self.Expense.create({...})  # Create own data
    expense.action_submit()
```

### 5. Use Tags Appropriately

```python
# Fast unit tests
@tagged('post_install', '-at_install', 'unit', 'ipai_expense')

# Slow integration tests
@tagged('post_install', '-at_install', 'integration', 'ipai_expense')

# Tours (slowest)
@tagged('-at_install', 'post_install', 'ipai_expense_tour')
```

---

## JavaScript Tests (Odoo 18 HOOT)

**File:** `addons/ipai_expense/static/tests/env.test.js`

```javascript
/** @odoo-module **/

import { test, expect } from "@odoo/hoot";
import { makeMockEnv } from "@web/../tests/web_test_helpers";

test("ipai_expense: web client env loads", async () => {
  const env = await makeMockEnv();
  expect(env).toBeDefined();
});
```

**Run JS tests:**
```bash
odoo-bin -d test_db --test-enable --test-tags=/web
```

---

## Common Issues

### 1. Tests Not Running

**Problem:** Tests don't execute

**Solution:** Check `tests/__init__.py` imports:
```python
from . import test_my_module  # Must import
```

### 2. Import Errors

**Problem:** `ModuleNotFoundError`

**Solution:** Ensure test module is in PYTHONPATH:
```bash
export PYTHONPATH=/path/to/odoo:$PYTHONPATH
```

### 3. Database Errors

**Problem:** Tests fail with DB errors

**Solution:** Use clean test database:
```bash
dropdb test_db
createdb test_db
```

### 4. Slow Tests

**Problem:** Tests take too long

**Solution:** Use test tags to run subsets:
```bash
./bin/odoo-tests.sh ipai_expense /unit  # Fast tests only
```

---

## Examples in This Repository

### Module: ipai_expense

**Tests:**
- `tests/test_expense_ocr.py` - OCR field validation
- `tests/test_business_flow.py` - Complete workflow tests

**Run:**
```bash
./bin/odoo-tests.sh ipai_expense
```

### Module: ipai_equipment

**Tests:**
- `tests/test_booking_cron.py` - Cron job tests
- `tests/test_equipment_flow.py` - Booking workflow

**Run:**
```bash
./bin/odoo-tests.sh ipai_equipment
```

---

## References

- [Odoo 18 Testing Documentation](https://www.odoo.com/documentation/18.0/developer/reference/backend/testing.html)
- [Odoo 18 JS Testing (HOOT)](https://www.odoo.com/documentation/18.0/developer/reference/frontend/unit_testing.html)
- [OCA Testing Guidelines](https://github.com/OCA/maintainer-tools)

---

**Last Updated:** 2025-11-23
**Odoo Version:** 18.0
**Maintained by:** InsightPulse AI DevOps
