---
name: sales
description: Sales order management with quotations, invoicing, pricelists, and product configuration
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# sales -- Odoo 19.0 Skill Reference

## Overview

Odoo Sales manages the complete order-to-invoice cycle: creating quotations, sending them to customers, confirming sales orders, managing invoicing policies, handling down payments, processing returns, and configuring product pricing via pricelists. It integrates with Inventory for delivery, Accounting for invoicing, Project for service products, and Subscriptions for recurring billing. Used by sales teams, account managers, and billing staff.

## Key Concepts

- **Quotation**: A draft sales proposal sent to a customer; becomes a Sales Order upon confirmation.
- **Sales Order (SO)**: A confirmed quotation representing a binding agreement to deliver products/services.
- **Invoicing Policy**: Determines when an invoice can be created -- either on **Ordered quantities** or **Delivered quantities**.
- **Down Payment**: Partial upfront payment (percentage or fixed amount) collected before full delivery.
- **Pricelist**: Dynamic pricing rules that override the default sales price based on customer, quantity, date, or product category.
- **Recurring Plan**: Subscription billing period (Monthly, Quarterly, Yearly) used with recurring pricelist rules.
- **Fiscal Position**: Tax and account mapping rules applied per customer or transaction.
- **Quotation Template**: Pre-defined quotation layouts with default products, optional products, and terms.
- **Loyalty / Discount Program**: Promotional programs offering coupons, discounts, or rewards.

## Core Workflows

### 1. Create and Send a Quotation

1. Navigate to **Sales > Orders > Quotations**, click **New**.
2. Select a **Customer** and optionally a **Pricelist**.
3. In the **Order Lines** tab, click **Add a product** and select products.
4. Adjust quantities, unit prices, and discounts as needed.
5. Optionally set an **Expiration Date** and add **Optional Products**.
6. Click **Send by Email** to send the quotation to the customer.
7. When the customer accepts, click **Confirm** to convert to a Sales Order.

### 2. Invoice a Sales Order

1. From the confirmed SO, click **Create Invoice**.
2. Choose invoice type: **Regular invoice**, **Down payment (percentage)**, or **Down payment (fixed amount)**.
3. Click **Create Draft Invoice**.
4. Review the draft invoice, then click **Confirm** to post it.
5. Click **Pay** to register payment.

### 3. Invoice Based on Milestones

1. Create a service product with **Invoicing Policy** set to **Based on Milestones**.
2. Set **Create on Order** to **Project & Task** (or **Task**).
3. Create and confirm a SO with this product.
4. In the linked Project, configure milestones with **Delivered %** values.
5. When a milestone is reached, the **Delivered** column on the SO updates.
6. Click **Create Invoice** to bill for completed milestones.

### 4. Invoice Based on Timesheets

1. Create a service product with **Invoicing Policy** set to **Based on Timesheets** and **Create on Order** set to **Project & Task**.
2. Create and confirm a SO; a project and task are auto-created.
3. Log time on the task via the **Timesheets** tab.
4. Return to the SO; **Delivered** quantities reflect logged hours.
5. Click **Create Invoice** to bill for time spent.

### 5. Process Returns and Refunds

1. **Before invoicing**: Open the SO, click the **Delivery** smart button, then **Return** on the delivery order to create a reverse transfer. Validate the return. Invoice only for kept products.
2. **After invoicing**: Create a reverse transfer as above. Then, on the invoice, click **Credit Note** to issue a refund.

## Technical Reference

### Models

| Model | Description |
|-------|-------------|
| `sale.order` | Sales orders and quotations |
| `sale.order.line` | SO line items |
| `sale.order.template` | Quotation templates |
| `sale.order.template.line` | Template line items |
| `product.pricelist` | Pricelists |
| `product.pricelist.item` | Pricelist rules |
| `account.move` | Invoices and credit notes |

### Key Fields on `sale.order`

| Field | Type | Description |
|-------|------|-------------|
| `partner_id` | Many2one | Customer |
| `order_line` | One2many | Order lines |
| `state` | Selection | `draft`, `sent`, `sale`, `cancel` |
| `pricelist_id` | Many2one | Applied pricelist |
| `amount_total` | Monetary | Total amount |
| `invoice_ids` | Many2many | Related invoices |
| `date_order` | Datetime | Order date |
| `validity_date` | Date | Quotation expiration |
| `payment_term_id` | Many2one | Payment terms |

### Key Fields on `sale.order.line`

| Field | Type | Description |
|-------|------|-------------|
| `product_id` | Many2one | Product |
| `product_uom_qty` | Float | Ordered quantity |
| `qty_delivered` | Float | Delivered quantity |
| `qty_invoiced` | Float | Invoiced quantity |
| `price_unit` | Float | Unit price |
| `discount` | Float | Discount percentage |
| `price_subtotal` | Monetary | Subtotal (excl. tax) |

### Menu Paths

- Quotations: `Sales > Orders > Quotations`
- Sales Orders: `Sales > Orders > Orders`
- Products: `Sales > Products > Products`
- Pricelists: `Sales > Products > Pricelists`
- Settings: `Sales > Configuration > Settings`

## API / RPC Patterns

<!-- TODO: Sales-specific external API examples not found in docs -->

Standard ORM access:

```python
# Create a quotation
so = env['sale.order'].create({
    'partner_id': partner_id,
    'order_line': [(0, 0, {
        'product_id': product_id,
        'product_uom_qty': 5,
    })],
})

# Confirm quotation to sales order
so.action_confirm()

# Create invoice
so._create_invoices()
```

## Version Notes (19.0)

<!-- TODO: Specific 18-to-19 breaking changes not documented in the reviewed RST files. -->

- Pricelists no longer require a pricelist to be set on the SO to confirm it (since Odoo 17+).
- Chatter is available on pricelist forms for notes and communications.
- Milestone invoicing requires at least one project with Milestones enabled before the option appears on products.
- Down payment handling improved: the system shows **Already invoiced** and **Amount to invoice** on subsequent invoice creation.

## Common Pitfalls

- **Invoicing policy mismatch**: Setting **Ordered quantities** on a service product billed by timesheets results in immediate full invoicing, not incremental. Use **Based on Timesheets** or **Based on Milestones** for progressive billing.
- **Down payment with delivered quantities policy**: If the product cost is less than the down payment and nothing is delivered, Odoo cannot create a final invoice (negative totals are not allowed). A credit note is created instead.
- **Pricelist priority**: If multiple pricelist rules match, Odoo applies the most specific one (product > category > all products). Product-level rules always override category-level rules.
- **Default pricelist determination**: The default pricelist is the first one found in the pricelist list without an assigned Country Group, read top to bottom by name.
- **Analytic distribution required**: For time/material invoicing, the analytic distribution must be correctly set on invoices and expenses; otherwise, project profitability tracking breaks.
