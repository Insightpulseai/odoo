# Odoo 19 Functional Domain Architecture (L3)

This document maps core business requirements to Odoo's technical architecture. Use this reference to understand _what_ standard models to implement for specific functional needs.

## 1. Finance & Accounting (`account`)

The backbone of Odoo's ERP. All financial transactions eventually flow here.

### Core Models

- **`account.move`**: The central model. Represents both **Journal Entries** and **Invoices/Bills**.
- **`account.move.line`**: The atomic ledger item. Every `move` has multiple `lines` (debit/credit) that must balance.
- **`account.account`**: The Chart of Accounts definitions.
- **`account.journal`**: Buckets for transactions (Sales, Purchase, Bank, Cash, Miscellaneous).
- **`account.payment`**: Records the actual money transfer.

### Key Concepts

- **Reconciliation**: The process of linking a Payment (`account.payment`) to an Invoice (`account.move`) to mark it as Paid. technically handled via `account.partial.reconcile` and `account.full.reconcile`.
- **Analytic Accounting**: A parallel dimension for tracking costs/revenues by Project or Department, independent of the General Ledger. Uses `account.analytic.line`.
- **Fiscal Positions**: Rules that automatically swap taxes and accounts based on the partner's location (e.g., Domestic vs. Export).

---

## 2. Sales & CRM (`sale`, `crm`)

The "Order to Cash" flow.

### Core Models

- **`crm.lead`**: Represents both unqualified **Leads** and qualified **Opportunities**.
- **`sale.order`**: Represents both **Quotations** (Draft) and **Sales Orders** (Confirmed).
- **`sale.order.line`**: detailed line items of an order.

### The Flow

1.  **Lead**: Raw contact info.
2.  **Opportunity**: Qualified potential business.
3.  **Quotation**: Proposal sent to customer (`sale.order` state='draft').
4.  **Sales Order**: Confirmed agreement (`sale.order` state='sale').
5.  **Delivery/Invoice**: Downstream documents generated from the SO.

### Key Concepts

- **Pricelists**: `product.pricelist` allows complex pricing rules based on currency, quantity, date, or customer segment.

---

## 3. Supply Chain (`stock`, `mrp`, `purchase`)

The "Procure to Pay" and "Make to Order" flows.

### Inventory (`stock`)

- **`stock.picking`**: Represents a transfer document (e.g., "WH/IN/0001").
- **`stock.move`**: A planned movement of a specific product.
- **`stock.move.line`**: The actual execution of a move (reserved/done quantities).
- **`stock.quant`**: Represents the _actual_ physical stock on hand at a specific location.
- **Routes & Rules**: The logic engine. "If I need product X at Location A, Trigger a Buy/Manufacture/Transfer rule."

### Manufacturing (`mrp`)

- **`mrp.production`**: The Manufacturing Order (MO).
- **`mrp.bom`**: Bill of Materials. Defines components and operations.
- **`mrp.workorder`**: Specific steps tracked on the shop floor (if using Work Centers).

### Purchase (`purchase`)

- **`purchase.order`**: RFQs and Purchase Orders.

---

## 4. Productivity & Content

### Documents (`documents`)

- **`documents.document`**: The central file repository.
- **AI Integration**: Odoo's OCR automatically extracts data from PDFs (Vendor Bills) to create draft `account.move` records.

### Knowledge (`knowledge`)

- **`knowledge.article`**: The Notion-like documentation system.
- **Templates**: Articles can be used as blueprints for process documentation or standard operating procedures.

---

## 5. Website & eCommerce (`website`)

### Core Models

- **`website`**: Configuration container for a specific domain.
- **`website.page`**: Semantic routing to QWeb views.
- **`product.public.category`**: The category tree visible to e-commerce shoppers (distinct from internal product categories).

### CMS

- Uses **Snippets** (`web_editor`) for drag-and-drop page building. Content is stored as HTML fields or QWeb views.

---

## 6. General Platform (`base`)

### Security & Access

- **`res.groups`**: Functional roles (e.g., "Sales / Manager").
- **`ir.model.access`**: CRUD Table (Who can Create/Read/Update/Delete).
- **`ir.rule`**: Row-Level Security (e.g., "User sees only their own documents").

### Configuration

- **`res.company`**: The entity boundaries. Odoo 19 supports rigid multi-company separation and "Branches".
- **`res.config.settings`**: The Transient models that power the "Settings" screens. They generally write to `ir.config_parameter`.
