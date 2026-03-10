---
name: odoo19-testing
description: Odoo 19 Testing - Python unit tests, JS unit tests (HOOT), Tours, Form helper, test tags, web_test_helpers, mock_server
metadata:
  author: odoo/documentation
  version: "19.0"
  source: "content/developer/reference/backend/testing.rst, content/developer/reference/frontend/unit_testing.rst"
  extracted: "2026-02-17"
---

# Odoo 19 Testing

Comprehensive reference for Odoo 19 testing: Python unit tests (TransactionCase,
SingleTransactionCase, HttpCase), Form helper, @tagged decorator, test selection,
Tours (integration testing), assertQueryCount, JavaScript unit testing with HOOT
framework, web_test_helpers, mock_server, and test file conventions.

---

## 1. Overview

Odoo has three kinds of tests:

| Type | Purpose | Technology |
|------|---------|------------|
| **Python unit tests** | Model business logic | unittest + Odoo test classes |
| **JS unit tests** | JavaScript code in isolation | HOOT framework |
| **Tours** | Integration (Python + JS) | Browser simulation |

---

## 2. Python Unit Tests

### 2.1 Test File Structure

```
your_module/
├── ...
├── tests/
│   ├── __init__.py
│   ├── test_foo.py
│   └── test_bar.py
```

**`tests/__init__.py`:**
```python
from . import test_foo, test_bar
```

**Rules:**
- Test modules must be in a `tests` sub-package
- Module names must start with `test_`
- Must be imported from `tests/__init__.py` (otherwise not discovered)
- Test methods must start with `test_`

### 2.2 Test Base Classes

#### TransactionCase

Each test method runs in its own transaction that is **rolled back** at the end.
Most common test class.

```python
from odoo.tests import TransactionCase

class TestMyModel(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Partner',
            'email': 'test@example.com',
        })

    def test_partner_name(self):
        """Test that partner name is set correctly."""
        self.assertEqual(self.partner.name, 'Test Partner')

    def test_partner_email(self):
        """Test email is set correctly."""
        self.assertEqual(self.partner.email, 'test@example.com')

    def test_create_record(self):
        """Test record creation."""
        record = self.env['my.model'].create({
            'name': 'Test Record',
            'partner_id': self.partner.id,
        })
        self.assertTrue(record.id)
        self.assertEqual(record.partner_id, self.partner)
```

**Key methods:**
- `self.env` -- Odoo environment
- `self.ref(external_id)` -- Resolve external ID to database ID
- `self.browse_ref(external_id)` -- Resolve external ID to recordset

#### SingleTransactionCase

All test methods share a **single transaction**. Changes persist across methods.
Use when tests build on each other's results.

```python
from odoo.tests import SingleTransactionCase

class TestWorkflow(SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.order = cls.env['sale.order'].create({
            'partner_id': cls.env.ref('base.res_partner_1').id,
        })

    def test_01_draft(self):
        """Order starts in draft."""
        self.assertEqual(self.order.state, 'draft')

    def test_02_confirm(self):
        """Confirm order (depends on test_01)."""
        self.order.action_confirm()
        self.assertEqual(self.order.state, 'sale')

    def test_03_count(self):
        """Check confirmed orders count."""
        count = self.env['sale.order'].search_count([('state', '=', 'sale')])
        self.assertGreaterEqual(count, 1)
```

#### HttpCase

For tests that need an HTTP server (tours, browser tests). Inherits from
TransactionCase.

```python
from odoo.tests import HttpCase, tagged

@tagged('-at_install', 'post_install')
class TestWebUI(HttpCase):

    def test_admin_page(self):
        """Test that admin can access the settings page."""
        self.url_open('/web')
        # returns an HTTP response

    def test_tour(self):
        """Run a tour test."""
        self.start_tour("/web", "my_module.my_tour", login="admin")

    def test_browser_js(self):
        """Execute JavaScript in a browser."""
        self.browser_js(
            "/web",
            "odoo.startTour('my_tour')",
            ready="odoo.__DEBUG__.services['web_tour.tour']",
            login="admin",
        )
```

**Key methods:**
- `url_open(url, data=None, ...)` -- Make HTTP request to the server
- `start_tour(url, tour_name, login=None, step_delay=None, watch=False, debug=False)` -- Run a tour
- `browser_js(url, code, ready, login, ...)` -- Execute JS in browser

### 2.3 Common Assertions

```python
# Standard unittest assertions
self.assertEqual(record.name, 'Expected')
self.assertNotEqual(record.state, 'done')
self.assertTrue(record.active)
self.assertFalse(record.parent_id)
self.assertIn('draft', possible_states)
self.assertNotIn(partner, excluded_partners)
self.assertGreater(record.amount, 0)
self.assertGreaterEqual(len(records), 5)
self.assertLess(record.sequence, 100)
self.assertIsNone(result)
self.assertIsNotNone(record.create_date)
self.assertAlmostEqual(record.amount, 99.99, places=2)

# Assert raises
with self.assertRaises(UserError):
    record.unlink()

with self.assertRaises(ValidationError):
    record.write({'amount': -1})

with self.assertRaises(AccessError):
    record.with_user(portal_user).write({'name': 'Hack'})
```

### 2.4 Test Environment and Users

```python
class TestSecurity(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create test users with specific groups
        cls.user_manager = cls.env['res.users'].create({
            'name': 'Test Manager',
            'login': 'test_manager',
            'groups_id': [
                (4, cls.env.ref('project.group_project_manager').id),
            ],
        })

        cls.user_basic = cls.env['res.users'].create({
            'name': 'Test User',
            'login': 'test_user',
            'groups_id': [
                (4, cls.env.ref('project.group_project_user').id),
            ],
        })

        cls.user_portal = cls.env['res.users'].create({
            'name': 'Portal User',
            'login': 'test_portal',
            'groups_id': [
                (4, cls.env.ref('base.group_portal').id),
            ],
        })

    def test_manager_access(self):
        """Managers can create tasks."""
        task = self.env['project.task'].with_user(self.user_manager).create({
            'name': 'Manager Task',
        })
        self.assertTrue(task.id)

    def test_portal_no_create(self):
        """Portal users cannot create tasks."""
        with self.assertRaises(AccessError):
            self.env['project.task'].with_user(self.user_portal).create({
                'name': 'Portal Task',
            })

    def test_basic_user_own_records(self):
        """Basic users can only see their own tasks (record rule)."""
        task = self.env['project.task'].with_user(self.user_manager).create({
            'name': 'Manager Only Task',
            'user_id': self.user_manager.id,
        })
        # Basic user shouldn't find this task
        found = self.env['project.task'].with_user(self.user_basic).search([
            ('id', '=', task.id),
        ])
        self.assertFalse(found)
```

### 2.5 Form Helper

The `Form` class simulates form view interactions for testing onchange logic
and view behavior:

```python
from odoo.tests import Form

class TestFormBehavior(TransactionCase):

    def test_onchange_partner(self):
        """Test that changing partner updates address fields."""
        partner = self.env['res.partner'].create({
            'name': 'Test',
            'street': '123 Main St',
        })

        # Create a new record through form simulation
        with Form(self.env['sale.order']) as order_form:
            order_form.partner_id = partner
            # After setting partner_id, onchange fires automatically
            # Check that partner-dependent fields are set

        order = order_form.record
        self.assertEqual(order.partner_id, partner)

    def test_form_creation(self):
        """Test form-based record creation."""
        with Form(self.env['my.model']) as f:
            f.name = 'Test Record'
            f.state = 'draft'

        record = f.record
        self.assertEqual(record.name, 'Test Record')
        self.assertTrue(record.id)

    def test_form_editing(self):
        """Test editing an existing record through form."""
        record = self.env['my.model'].create({'name': 'Original'})

        with Form(record) as f:
            f.name = 'Modified'

        self.assertEqual(record.name, 'Modified')

    def test_one2many_manipulation(self):
        """Test One2many field manipulation in forms."""
        with Form(self.env['sale.order']) as order_form:
            order_form.partner_id = self.env.ref('base.res_partner_1')

            # Add a new line
            with order_form.order_line.new() as line:
                line.product_id = self.env.ref('product.product_product_1')
                line.product_uom_qty = 5

            # Edit existing line
            with order_form.order_line.edit(0) as line:
                line.product_uom_qty = 10

        order = order_form.record
        self.assertEqual(len(order.order_line), 1)
        self.assertEqual(order.order_line.product_uom_qty, 10)

    def test_many2many_manipulation(self):
        """Test Many2many field manipulation in forms."""
        tag1 = self.env['project.tags'].create({'name': 'Tag 1'})
        tag2 = self.env['project.tags'].create({'name': 'Tag 2'})

        with Form(self.env['project.task']) as f:
            f.name = 'Tagged Task'
            f.tag_ids.add(tag1)
            f.tag_ids.add(tag2)

        task = f.record
        self.assertEqual(len(task.tag_ids), 2)

        # Remove a tag
        with Form(task) as f:
            f.tag_ids.remove(tag1.id)

        self.assertEqual(len(task.tag_ids), 1)
```

**Form API:**

| Method / Property | Description |
|-------------------|-------------|
| `Form(model_or_record)` | Create form for new record or edit existing |
| `form.field = value` | Set field value (triggers onchange) |
| `form.record` | Access the saved record after form context exits |
| `form.save()` | Explicitly save (auto-saved on context exit) |

**O2MProxy (One2many):**

| Method | Description |
|--------|-------------|
| `.new()` | Add new line (returns nested form context) |
| `.edit(index)` | Edit line at index (returns nested form context) |
| `.remove(index)` | Remove line at index |

**M2MProxy (Many2many):**

| Method | Description |
|--------|-------------|
| `.add(record)` | Link a record |
| `.remove(id=...)` | Unlink record by ID |
| `.clear()` | Remove all |

---

## 3. Test Tags and Selection

### 3.1 The @tagged Decorator

```python
from odoo.tests import TransactionCase, tagged

# Default tags (implicit): 'standard', 'at_install'

# Remove from default suite, add custom tag
@tagged('-standard', 'nice')
class NiceTest(TransactionCase):
    ...

# Post-install test (common for HttpCase)
@tagged('-at_install', 'post_install')
class PostInstallTest(TransactionCase):
    ...

# Multiple custom tags
@tagged('-standard', 'slow', 'integration')
class SlowIntegrationTest(TransactionCase):
    ...

# Plain unittest with explicit tags (not auto-tagged)
import unittest
from odoo.tests import tagged

@tagged('standard', 'at_install')
class SmallTest(unittest.TestCase):
    ...
```

**Warning:** `@tagged` is a **class decorator only** -- it has no effect on
functions or methods.

### 3.2 Special Tags

| Tag | Default | Description |
|-----|---------|-------------|
| `standard` | Implicit | Included in default test run |
| `at_install` | Implicit | Run right after module installation |
| `post_install` | Not default | Run after ALL modules are installed |

`post_install` is usually paired with `-at_install`:
```python
@tagged('-at_install', 'post_install')
```

### 3.3 Running Tests (CLI)

```bash
# Run all standard tests
odoo-bin --test-enable -i my_module

# Run tests for specific module
odoo-bin --test-tags /my_module

# Run tests with specific tag
odoo-bin --test-tags nice

# Run multiple tags (OR logic)
odoo-bin --test-tags nice,standard

# Exclude slow tests
odoo-bin --test-tags 'standard,-slow'

# Run specific test class
odoo-bin --test-tags /my_module:TestMyModel

# Run specific test method
odoo-bin --test-tags .test_partner_name

# Full qualified test
odoo-bin --test-tags /account:TestAccountInvoice.test_invoice_creation

# Run tests from stock, excluding slow
odoo-bin --test-tags '/stock,-slow'

# Run only non-standard tests
odoo-bin --test-tags '-standard,slow,/stock'
```

**Tag syntax:** `[-][tag][/module][:class][.method]`

### 3.4 Test Execution Notes

- Tests are run when installing (`-i`) or updating (`-u`) modules with `--test-enable`
- `--test-tags` implies `--test-enable`
- `--test-tags` defaults to `+standard`
- Multiple comma-separated values are additive (OR)
- `-` prefix deselects even if selected by other tags
- Tests only run in installed modules

---

## 4. Integration Testing (Tours)

### 4.1 Tour File Structure

```
your_module/
├── static/
│   └── tests/
│       └── tours/
│           └── your_tour.js
├── tests/
│   ├── __init__.py
│   └── test_calling_the_tour.py
└── __manifest__.py
```

### 4.2 JavaScript Tour Definition

```javascript
/** @odoo-module */
import tour from 'web_tour.tour';

tour.register('my_module_tour', {
    url: '/web',
}, [
    // Step 1: Open the Apps menu
    tour.stepUtils.showAppsMenuItem(),

    // Step 2: Click on the module app
    {
        trigger: '.o_app[data-menu-xmlid="my_module.menu_root"]',
        run: "click",
    },

    // Step 3: Click create button
    {
        trigger: '.o-kanban-button-new',
        content: "Click to create a new record",
        tooltipPosition: "bottom",
        run: "click",
    },

    // Step 4: Fill in a field
    {
        trigger: 'div.o_field_widget[name="name"] input',
        content: "Enter the record name",
        run: "edit Test Record",
    },

    // Step 5: Select a value
    {
        trigger: 'div.o_field_widget[name="state"] select',
        run: "select draft",
    },

    // Step 6: Save
    {
        trigger: '.o_form_button_save',
        content: "Save the record",
        run: "click",
    },

    // Step 7: Verify (no run = just check trigger exists)
    {
        trigger: '.o_form_view .o_field_widget[name="name"]:contains("Test Record")',
        content: "Verify the record was saved",
    },
]);
```

### 4.3 Tour Step Properties

| Property | Required | Description |
|----------|----------|-------------|
| `trigger` | Yes | CSS selector for the target element |
| `run` | No | Action to perform (string or async function) |
| `content` | No | Tooltip text (recommended for debugging) |
| `tooltipPosition` | No | `top`, `right`, `bottom`, `left` |
| `isActive` | No | Conditions array: `mobile`/`desktop`, `community`/`enterprise`, `auto`/`manual` |
| `timeout` | No | Max wait time in ms (default: 10000) |
| `break` | No | `true` to set debugger breakpoint (debug mode) |
| `pause` | No | `true` to pause tour until `play()` called (debug mode) |

### 4.4 Tour Run Actions

| Action | Description |
|--------|-------------|
| `"click"` | Click the trigger element |
| `"dblclick"` | Double-click |
| `"edit content"` | Clear and fill with content |
| `"fill content"` | Focus and type content (without clearing) |
| `"editor content"` | Focus wysiwyg and type content |
| `"press content"` | Keyboard event sequence |
| `"clear"` | Clear input/textarea |
| `"check"` | Ensure checkbox is checked |
| `"uncheck"` | Ensure checkbox is unchecked |
| `"hover"` | Hover over element |
| `"select value"` | Select option by value |
| `"selectByIndex idx"` | Select option by index |
| `"selectByLabel label"` | Select option by visible text |
| `"drag_and_drop target"` | Drag to target selector |
| `"range value"` | Set range input value |
| `async run(helpers) {...}` | Custom async function |

### 4.5 Python Tour Caller

```python
from odoo.tests import HttpCase, tagged

@tagged('-at_install', 'post_install')
class TestMyTour(HttpCase):

    def test_my_module_tour(self):
        """Run the main module tour."""
        # Optional: setup test data
        self.env['my.model'].create({'name': 'Tour Test'})

        # Run the tour
        self.start_tour("/web", "my_module_tour", login="admin")

    def test_tour_with_watch(self):
        """Run tour with visible Chrome window (local debugging)."""
        self.start_tour("/web", "my_module_tour", login="admin", watch=True)

    def test_tour_with_debug(self):
        """Run tour with devtools and breakpoints."""
        self.start_tour("/web", "my_module_tour", login="admin", debug=True)
```

### 4.6 Manifest Assets for Tours

```python
{
    'assets': {
        'web.assets_tests': [
            'my_module/static/tests/tours/my_tour.js',
        ],
    },
}
```

### 4.7 Tour Best Practices

- Last step(s) should return client to a "stable" state
- Ensure all network requests complete before tour ends
- Use `content` for every step (helps debugging)
- Test both `community` and `enterprise` editions if applicable
- Use `isActive: ["desktop"]` or `isActive: ["mobile"]` for responsive tests

### 4.8 Debugging Tours

**Browser console:**
```javascript
odoo.startTour("tour_name");  // Run tour manually
```

**URL parameter:**
```
?debug=tests  // Enable test mode in browser
```

**Step debugging:**
```javascript
// Add to a step:
{ break: true }   // Debugger breakpoint
{ pause: true }   // Pause until play() called in console
{ run() { debugger; } }  // Breakpoint when step executes
```

---

## 5. Performance Testing

### 5.1 assertQueryCount

Measure and limit database queries:

```python
class TestPerformance(TransactionCase):

    def test_create_performance(self):
        """Ensure create doesn't exceed query count."""
        partner = self.env.ref('base.res_partner_1')
        with self.assertQueryCount(11):
            self.env['my.model'].create({
                'name': 'Test',
                'partner_id': partner.id,
            })

    def test_search_performance(self):
        """Ensure search is efficient."""
        with self.assertQueryCount(3):
            self.env['my.model'].search([('state', '=', 'draft')])
```

Can also be used with `--log-sql` CLI parameter for manual analysis.

---

## 6. JavaScript Unit Testing (HOOT Framework)

### 6.1 Overview

Odoo uses **HOOT** (Hierarchically Organized Odoo Tests), a home-grown testing
framework. It provides:

- Tags system
- Global object mocking
- Integration with `web_test_helpers` for web client testing
- `mock_server` for simulating server responses

### 6.2 Test File Setup

#### File Location

All JavaScript test files go under `/static/tests/` in the addon:
```
my_module/static/tests/my_widget.test.js
my_module/static/tests/my_service.test.js
```

#### File Naming

- Test files **must** end with `.test.js`
- Non-test helper files can be any `.js` (they're treated as helpers)
- `.hoot.js` files are global modules for the entire test run (special constraints)

#### Asset Bundle Registration

```python
{
    'assets': {
        'web.assets_unit_tests': [
            'my_module/static/tests/**/*',
        ],
    },
}
```

#### Running Tests

Navigate to `/web/tests` URL, or use Debug menu -> Run Unit Tests.

### 6.3 Writing HOOT Tests

#### Basic Test Structure

```javascript
/** @odoo-module */
import { describe, test, expect } from "@odoo/hoot";

describe("MyWidget", () => {
    test("should render correctly", async () => {
        // Arrange
        const widget = createWidget();

        // Act
        await widget.mount();

        // Assert
        expect(widget.el).toBeVisible();
        expect(widget.el.textContent).toBe("Hello World");
    });

    test("should handle click", async () => {
        const widget = createWidget();
        await widget.mount();

        await click(widget.el.querySelector("button"));

        expect(widget.state.clicked).toBe(true);
    });
});
```

#### Nested Describe Blocks

```javascript
describe("MyComponent", () => {
    describe("rendering", () => {
        test("should show title", async () => { ... });
        test("should show items", async () => { ... });
    });

    describe("interactions", () => {
        test("should handle click", async () => { ... });
        test("should handle input", async () => { ... });
    });
});
```

### 6.4 HOOT Assertions (expect)

```javascript
import { expect } from "@odoo/hoot";

// Value assertions
expect(value).toBe(expected);           // strict equality
expect(value).not.toBe(unexpected);     // negation
expect(value).toEqual(expected);        // deep equality
expect(value).toBeTruthy();
expect(value).toBeFalsy();
expect(value).toBeNull();
expect(value).toBeUndefined();
expect(value).toBeGreaterThan(n);
expect(value).toBeLessThan(n);
expect(value).toBeWithin(min, max);
expect(value).toInclude(item);
expect(value).toHaveLength(n);
expect(value).toMatch(regex);

// DOM assertions
expect(element).toBeVisible();
expect(element).toBeDisplayed();
expect(element).toHaveClass("my-class");
expect(element).toHaveAttribute("data-id", "123");
expect(element).toHaveText("Hello");
expect(element).toHaveValue("input value");
expect(selector).toHaveCount(3);        // number of matching elements

// Function assertions
expect(fn).toThrow();
expect(fn).toThrow(/error message/);
```

### 6.5 web_test_helpers

The `web_test_helpers` module provides utilities for testing Odoo web client
components:

```javascript
/** @odoo-module */
import { describe, test, expect } from "@odoo/hoot";
import {
    click,
    contains,
    defineModels,
    fields,
    models,
    mountView,
    mountWithCleanup,
    onRpc,
    patchWithCleanup,
    serverState,
} from "@web/../tests/web_test_helpers";
```

#### Defining Test Models

```javascript
class Partner extends models.Model {
    _name = "res.partner";

    name = fields.Char();
    email = fields.Char();
    is_company = fields.Boolean();
    parent_id = fields.Many2one({ relation: "res.partner" });
    child_ids = fields.One2many({ relation: "res.partner", relation_field: "parent_id" });
    tag_ids = fields.Many2many({ relation: "partner.tag" });

    _records = [
        { id: 1, name: "John", email: "john@example.com", is_company: false },
        { id: 2, name: "Acme Corp", email: "info@acme.com", is_company: true },
    ];
}

class PartnerTag extends models.Model {
    _name = "partner.tag";
    name = fields.Char();
    _records = [
        { id: 1, name: "Important" },
        { id: 2, name: "VIP" },
    ];
}

defineModels([Partner, PartnerTag]);
```

#### Mounting Views

```javascript
test("should render list view", async () => {
    await mountView({
        type: "list",
        resModel: "res.partner",
        arch: `<list><field name="name"/><field name="email"/></list>`,
    });

    expect(".o_data_row").toHaveCount(2);
    expect(".o_data_cell:first").toHaveText("John");
});

test("should render form view", async () => {
    await mountView({
        type: "form",
        resModel: "res.partner",
        resId: 1,
        arch: `
            <form>
                <group>
                    <field name="name"/>
                    <field name="email"/>
                </group>
            </form>
        `,
    });

    expect(".o_field_widget[name='name'] input").toHaveValue("John");
});
```

#### Interacting with Views

```javascript
test("should create record", async () => {
    await mountView({
        type: "list",
        resModel: "res.partner",
        arch: `<list editable="bottom"><field name="name"/></list>`,
    });

    // Click create
    await click(".o_list_button_add");

    // Type in the name field
    await contains(".o_field_widget[name='name'] input").edit("New Partner");

    // Save
    await click(".o_list_button_save");

    expect(".o_data_row").toHaveCount(3);
});
```

#### Intercepting RPCs

```javascript
test("should call custom RPC", async () => {
    onRpc("my_method", (args) => {
        expect(args.args[0]).toEqual([1]);
        return { result: "success" };
    });

    await mountView({
        type: "form",
        resModel: "res.partner",
        resId: 1,
        arch: `
            <form>
                <button name="my_method" type="object" string="Do Something"/>
            </form>
        `,
    });

    await click("button[name='my_method']");
});

test("should intercept search_read", async () => {
    onRpc("web_search_read", (args) => {
        expect(args.kwargs.domain).toEqual([["is_company", "=", true]]);
    });

    await mountView({
        type: "list",
        resModel: "res.partner",
        domain: [["is_company", "=", true]],
        arch: `<list><field name="name"/></list>`,
    });
});
```

#### Patching

```javascript
import { patchWithCleanup } from "@web/../tests/web_test_helpers";
import { browser } from "@web/core/browser/browser";

test("should handle localStorage", async () => {
    patchWithCleanup(browser.localStorage, {
        getItem: (key) => "mocked_value",
    });

    // Test code that uses localStorage
});
```

### 6.6 Mock Server

The mock server simulates Odoo server responses in JavaScript tests:

```javascript
import { defineModels, models, fields } from "@web/../tests/web_test_helpers";

class MyModel extends models.Model {
    _name = "my.model";

    name = fields.Char();
    state = fields.Selection({
        selection: [["draft", "Draft"], ["done", "Done"]],
    });

    _records = [
        { id: 1, name: "Record 1", state: "draft" },
        { id: 2, name: "Record 2", state: "done" },
    ];

    // Override model methods for testing
    action_confirm() {
        const record = this._records.find(r => r.id === this.id);
        if (record) {
            record.state = "done";
        }
        return true;
    }
}

defineModels([MyModel]);
```

The mock server automatically handles standard ORM methods:
- `web_search_read` / `search_read`
- `read`
- `create`
- `write`
- `unlink`
- `name_search`
- `fields_get`
- `onchange`

Custom methods need to be defined on the model class.

### 6.7 Complete JavaScript Test Example

```javascript
/** @odoo-module */
import { describe, test, expect, beforeEach } from "@odoo/hoot";
import {
    click,
    contains,
    defineModels,
    fields,
    models,
    mountView,
    onRpc,
} from "@web/../tests/web_test_helpers";

class Task extends models.Model {
    _name = "project.task";

    name = fields.Char();
    state = fields.Selection({
        selection: [
            ["draft", "Draft"],
            ["in_progress", "In Progress"],
            ["done", "Done"],
        ],
    });
    user_id = fields.Many2one({ relation: "res.users" });
    priority = fields.Selection({
        selection: [["0", "Normal"], ["1", "Important"], ["2", "Urgent"]],
    });

    _records = [
        { id: 1, name: "Task 1", state: "draft", priority: "0" },
        { id: 2, name: "Task 2", state: "in_progress", priority: "1" },
        { id: 3, name: "Task 3", state: "done", priority: "2" },
    ];

    action_start() {
        // Mock server-side action
        return true;
    }
}

defineModels([Task]);

describe("Task Views", () => {
    test("list view shows all tasks", async () => {
        await mountView({
            type: "list",
            resModel: "project.task",
            arch: `
                <list>
                    <field name="name"/>
                    <field name="state"/>
                    <field name="priority"/>
                </list>
            `,
        });

        expect(".o_data_row").toHaveCount(3);
    });

    test("form view shows task details", async () => {
        await mountView({
            type: "form",
            resModel: "project.task",
            resId: 1,
            arch: `
                <form>
                    <header>
                        <button name="action_start" type="object" string="Start"/>
                        <field name="state" widget="statusbar"/>
                    </header>
                    <sheet>
                        <group>
                            <field name="name"/>
                            <field name="priority"/>
                        </group>
                    </sheet>
                </form>
            `,
        });

        expect(".o_field_widget[name='name'] input").toHaveValue("Task 1");
    });

    test("can edit task name", async () => {
        let writeArgs;
        onRpc("web_save", (args) => {
            writeArgs = args;
        });

        await mountView({
            type: "form",
            resModel: "project.task",
            resId: 1,
            arch: `
                <form>
                    <field name="name"/>
                </form>
            `,
        });

        await contains(".o_field_widget[name='name'] input").edit("Updated Task");
        await click(".o_form_button_save");

        expect(writeArgs).toBeTruthy();
    });

    test("kanban view groups by state", async () => {
        await mountView({
            type: "kanban",
            resModel: "project.task",
            arch: `
                <kanban default_group_by="state">
                    <templates>
                        <t t-name="card">
                            <field name="name"/>
                        </t>
                    </templates>
                </kanban>
            `,
            groupBy: ["state"],
        });

        expect(".o_kanban_group").toHaveCount(3);
    });
});
```

---

## 7. Onboarding Tours

### 7.1 Structure

```
your_module/
├── data/
│   └── your_tour.xml
├── static/src/js/tours/
│   └── your_tour.js
└── __manifest__.py
```

### 7.2 XML Registration

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="your_tour" model="web_tour.tour">
        <field name="name">your_tour</field>
        <field name="sequence">10</field>
        <field name="rainbow_man_message">Congrats, that was a great tour!</field>
    </record>
</odoo>
```

### 7.3 Manifest

```python
{
    'data': [
        'data/your_tour.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'your_module/static/src/js/tours/your_tour.js',
        ],
    },
}
```

### 7.4 Tour Record Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Must match JavaScript registry name |
| `sequence` | No | Order for execution (default: 1000) |
| `url` | No | Starting URL (default: `/odoo`, or from JS registry) |
| `rainbow_man_message` | No | Completion message (False = no effect) |

---

## 8. Screenshots and Screencasts

When tests fail during headless browser execution:

```bash
# Default screenshot location on failure
/tmp/odoo_tests/{db_name}/screenshots/

# Custom screenshot directory
odoo-bin --test-tags /my_module --screenshots /path/to/screenshots

# Record screencasts
odoo-bin --test-tags /my_module --screencasts /path/to/videos
```

---

## 9. Complete Python Test Example

```python
from odoo.tests import TransactionCase, Form, HttpCase, tagged
from odoo.exceptions import UserError, ValidationError, AccessError


class TestProjectTaskLogic(TransactionCase):
    """Test project task business logic."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project = cls.env['project.project'].create({
            'name': 'Test Project',
        })
        cls.user_admin = cls.env.ref('base.user_admin')
        cls.user_demo = cls.env.ref('base.user_demo')

    def _create_task(self, **kwargs):
        """Helper to create a task with defaults."""
        vals = {
            'name': 'Test Task',
            'project_id': self.project.id,
        }
        vals.update(kwargs)
        return self.env['project.task'].create(vals)

    def test_create_task(self):
        """Test basic task creation."""
        task = self._create_task()
        self.assertTrue(task.id)
        self.assertEqual(task.name, 'Test Task')
        self.assertEqual(task.project_id, self.project)

    def test_task_default_state(self):
        """New tasks should be in draft state."""
        task = self._create_task()
        self.assertEqual(task.state, 'draft')

    def test_task_state_transition(self):
        """Test state transition from draft to in_progress."""
        task = self._create_task()
        task.action_start()
        self.assertEqual(task.state, 'in_progress')

    def test_cannot_start_done_task(self):
        """Starting a done task should raise UserError."""
        task = self._create_task(state='done')
        with self.assertRaises(UserError):
            task.action_start()

    def test_task_deadline_validation(self):
        """Past deadline should raise ValidationError."""
        with self.assertRaises(ValidationError):
            self._create_task(date_deadline='2020-01-01')

    def test_task_compute_progress(self):
        """Test progress computation."""
        task = self._create_task(hours_planned=10, hours_spent=5)
        self.assertAlmostEqual(task.progress, 50.0)

    def test_task_form_onchange(self):
        """Test onchange via Form helper."""
        with Form(self.env['project.task']) as f:
            f.name = 'Form Task'
            f.project_id = self.project
            # Verify onchange set the user
        task = f.record
        self.assertEqual(task.project_id, self.project)

    def test_task_security_basic_user(self):
        """Basic user cannot delete tasks."""
        task = self._create_task(user_id=self.user_demo.id)
        with self.assertRaises(AccessError):
            task.with_user(self.user_demo).unlink()

    def test_task_batch_create(self):
        """Test batch creation performance."""
        vals_list = [{'name': f'Task {i}', 'project_id': self.project.id} for i in range(10)]
        tasks = self.env['project.task'].create(vals_list)
        self.assertEqual(len(tasks), 10)

    def test_query_count(self):
        """Ensure search is efficient."""
        # Create some tasks first
        self._create_task()
        with self.assertQueryCount(3):
            self.env['project.task'].search([('project_id', '=', self.project.id)])


@tagged('-at_install', 'post_install')
class TestProjectTaskTour(HttpCase):
    """Integration test using tour."""

    def test_task_creation_tour(self):
        """Test creating a task through the UI."""
        self.env['project.project'].create({'name': 'Tour Project'})
        self.start_tour("/web", "project_task_tour", login="admin")
```

---

## 10. Test Patterns and Best Practices

### 10.1 Setup Pattern

```python
@classmethod
def setUpClass(cls):
    super().setUpClass()
    # Create shared test data here (runs once per class)
    cls.partner = cls.env['res.partner'].create({...})

def setUp(self):
    super().setUp()
    # Per-test setup (runs before each test method)
    self.record = self.env['my.model'].create({...})
```

### 10.2 Testing Exceptions

```python
def test_validation(self):
    with self.assertRaises(ValidationError) as cm:
        self.env['my.model'].create({'amount': -1})
    self.assertIn('positive', str(cm.exception))
```

### 10.3 Testing with Different Users

```python
def test_multi_user(self):
    # Test as different users
    record_as_admin = self.record.with_user(self.admin_user)
    record_as_basic = self.record.with_user(self.basic_user)

    record_as_admin.write({'name': 'Admin Edit'})  # Should work
    with self.assertRaises(AccessError):
        record_as_basic.write({'name': 'Basic Edit'})  # Should fail
```

### 10.4 Testing Computed Fields

```python
def test_computed_field(self):
    record = self.env['my.model'].create({
        'price': 100,
        'quantity': 5,
    })
    self.assertEqual(record.total, 500)

    record.write({'quantity': 10})
    self.assertEqual(record.total, 1000)
```

### 10.5 Testing Cron Jobs

```python
def test_cron_cleanup(self):
    # Create test records
    old_record = self.env['my.model'].create({
        'name': 'Old',
        'create_date': '2020-01-01',
    })
    # Run cron
    cron = self.env.ref('my_module.cron_cleanup')
    cron.method_direct_trigger()
    # Verify
    self.assertFalse(old_record.exists())
```
