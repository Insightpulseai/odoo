---
name: odoo-fullstack-ai-dev
description: Comprehensive guide for AI-First Odoo 19 full-stack development, covering Backend (ORM), Frontend (Owl), and Testing.
---

# Odoo 19 Full Stack AI-First Developer Skill

## 1. AI-First Development Protocol

This skill empowers you to act as an elite "AI-First" Odoo developer.

- **Code Generation**: Always prefer generating complete, runnable modules or components over snippets.
- **Architecture**: Use established design patterns (e.g., Service Layer for complex logic, Mixins for reusability).
- **Explanation**: When explaining code, focus on the _why_ (Odoo architecture) and _how_ (implementation details).
- **Prototyping**: Use Odoo Studio concepts (or actual Studio if available) to conceptualize views/reports, then implement them in code (XML/Python) for version control.

## 2. Server Framework (Backend)

### Models & ORM

- **Definition**: Inherit from `models.Model`, `models.TransientModel`, or `models.AbstractModel`.
- **Fields**:
  - Basic: `Char`, `Text`, `Integer`, `Float`, `Boolean`, `Date`, `Datetime`, `Binary`, `Selection`, `Html`.
  - Relational: `Many2one`, `One2many`, `Many2many`.
  - Compute: `@api.depends('dep_field')` triggers. Store=True for performance unless logic is strictly dynamic.
- **Methods**:
  - CRUD overrides: `create`, `write`, `unlink`.
  - Decorators: `@api.model`, `@api.constrains`, `@api.onchange` (UI only).
  - **AI Tip**: When generating CRUD overrides, always call `super()` explicitly.

### Security

1.  **Access Rights (`ir.model.access.csv`)**: Define CRUD (1/0) permissions for Groups on Models.
2.  **Record Rules (`ir.rule`)**: Domain-based filters for row-level security (e.g., User can only see their own Leads).

### Business Logic

- **Environment (`self.env`)**: Access ORM, User (`self.env.user`), and Context (`self.env.context`).
- **Searching**: `search(domain)`, `search_count(domain)`. Domain notation: `['&', ('field', '=', val), ('field2', '!=', val)]`.
- **Mapped**: `records.mapped('field_name')` for efficient value extraction.

## 3. Web Framework (Owl)

### Components

Odoo 19 uses **Owl** (Odoo Web Library), a React-like component system.

- **Structure**:
  ```javascript
  import { Component, useState } from "@odoo/owl";
  export class MyComponent extends Component {
    static template = "my_module.MyTemplate";
    setup() {
      this.state = useState({ count: 0 });
    }
  }
  ```
- **Hooks**: `onWillStart`, `onMounted`, `useService` (access RPC, User, Notification services).

### Views & Client Actions

- **Registry**: Register main components in `registry.category("actions")`.
- **Patching**: Use `patch()` to modify existing Odoo components (e.g., `FormController`) without replacing them.

### XML Templates (QWeb)

- **Directives**: `t-if`, `t-foreach`, `t-out` (replacing `t-esc`), `t-call`.
- **Inheritance**: `xpath` to inject content into existing views.
  ```xml
  <xpath expr="//field[@name='partner_id']" position="after">
      <field name="custom_field"/>
  </xpath>
  ```

## 4. Application Structure

### Module Manifest (`__manifest__.py`)

- **Depends**: List all module dependencies (e.g., `['base', 'sale']`).
- **Data**: List all XML/CSV files to load (security, views, data, reports).
- **Assets**: Define JS/CSS bundles in the `assets` dictionary (e.g., `web.assets_backend`).

### Directory Layout

```text
my_module/
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── my_model.py
├── views/
│   └── my_view.xml
├── security/
│   └── ir.model.access.csv
├── static/
│   └── src/
│       └── components/
└── tests/
    ├── __init__.py
    └── test_my_flow.py
```

## 5. Testing & CI

### Python Tests (`TransactionCase`)

- **Location**: `tests/` directory.
- **Execution**: Tests run in a transaction that rolls back after execution.
- **Key Methods**: `self.env['model'].create(...)`, `self.assertEqual(...)`.
- **Tagging**: `@tagged('at_install', 'post_install')` to control execution time.

### Integration

- **Tours**: JavaScript integration tests that drive the UI.
- **FormTours**: (Newer) verifying Form view behaviors specifically.

## 6. Odoo Studio (Prototyping)

Use Studio knowledge for:

- **Mockups**: Quickly visualizing a view layout before coding it in XML.
- **Reports**: Designing PDF layouts visually to generate the QWeb structure.
- **Automations**: Testing triggers (e.g., "On Update") to verify logic before implementing in Python listeners.

## 7. AI-Assisted Workflows

- **Refactoring**: "Refactor this method to use `mapped` and `filtered` for better performance."
- **Debugging**: "Analyze this traceback and suggest a fix regarding Access Rights."
- **Scaffolding**: "Generate the directory structure and manifest for a module named `estate_management`."

## 8. Functional Domain Architecture (L3)

Mapping business requirements to technical models.

### Finance & Accounting (`account`)

- **Core Models**:
  - `account.move` (Journal Entries & Invoices)
  - `account.move.line` (Journal Items - the atomic ledger)
  - `account.account` (Chart of Accounts)
  - `account.journal` (Sales, Purchase, Bank, Cash, Misc)
- **Key Concepts**:
  - **Reconciliation**: Matching payments (`account.payment`) with invoices via `account.partial.reconcile`.
  - **Analytic Accounting**: `account.analytic.line` for cost centers/project tracking.
  - **Fiscal Positions**: Auto-mapping taxes based on partner country/group.
- **AI Tip**: "When creating an invoice via code, ensure you post it (`action_post()`) to generate the move lines."

### Sales & CRM (`sale`, `crm`)

- **Core Models**:
  - `crm.lead` (Leads & Opportunities)
  - `sale.order` (Quotations & SOs)
  - `sale.order.line` (Line items)
- **Flow**: Lead -> Opportunity -> Quotation -> SO -> Invoice/Delivery.
- **Pricelists**: `product.pricelist` for currency/reign-specific pricing rules.

### Supply Chain (`stock`, `mrp`, `purchase`)

- **Inventory (`stock`)**:
  - `stock.picking` (Transfer definition)
  - `stock.move` (Stock moves)
  - `stock.quant` (Physical inventory on hand)
  - **Routes**: Pull/Push rules defining logistics (e.g., MTO, Cross-dock).
- **Manufacturing (`mrp`)**:
  - `mrp.production` (Manufacturing Orders)
  - `mrp.bom` (Bill of Materials)
  - `mrp.workcenter` (Routing/Capacity)
- **Purchase (`purchase`)**:
  - `purchase.order`, `purchase.order.line`.

### Productivity & Content

- **Documents (`documents`)**:
  - `documents.document`: Central file storage.
  - **AI Digitization**: Integration with OCR for auto-encoding vendor bills.
- **Knowledge (`knowledge`)**:
  - `knowledge.article`: Collaborative rich-text pages.
  - **Templates**: Reusable structures for articles.

### Website & eCommerce (`website`, `website_sale`)

- **Core Models**:
  - `website`: Per-domain configuration.
  - `website.page`: URL routing to QWeb views.
  - `product.public.category`: eCommerce catalog organization.
- **CMS**: In-line editing uses `web_editor` snippets.

### General & Configuration (`base`)

- **Core Models**:
  - `res.company`: Multi-company hierarchy and branches.
  - `res.users`: User authentication, language, and timezone.
  - `res.groups`: Access security (e.g., "Sales / User: Own Documents Only").
  - `res.partner`: The contact book (Customers, Vendors, Employees).
- **Settings**:
  - `res.config.settings`: Transient models for "Settings" views.
  - `ir.config_parameter`: System parameters (key-value storage).
- **Developer Mode**:
  - Activated via `?debug=1`. Unlocks "Technical" menu and "Edit View Form".
