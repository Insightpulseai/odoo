---
name: point_of_sale
description: Point of Sale system for retail shops and restaurants with payment processing and inventory integration
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# point_of_sale -- Odoo 19.0 Skill Reference

## Overview

Odoo Point of Sale (POS) is a web-based application for processing retail and restaurant transactions. It supports multiple payment methods, barcode scanning, customer management, receipt printing, restaurant floor plans, and IoT hardware integration. The POS operates offline-capable and syncs with Inventory, Sales, and Accounting upon session close. Used by cashiers, retail managers, and restaurant staff.

## Key Concepts

- **POS Session**: A working period for a POS instance; opened by a user, closed with cash control reconciliation.
- **POS Config (Shop)**: A configured point-of-sale instance with its own settings, payment methods, and product catalog.
- **Payment Method**: A configured way to accept payment (cash, bank card, customer account, etc.).
- **POS Order**: A completed transaction in the POS, equivalent to a sales order.
- **POS Category**: Product categories used to organize products on the POS interface.
- **Restaurant Floor/Table**: Layout configuration for restaurant mode; orders are associated with tables.
- **Fiscal Position**: Tax mapping rules applied automatically based on customer or transaction type.
- **IoT Box**: Hardware gateway connecting POS to receipt printers, barcode scanners, scales, payment terminals, and customer displays.
- **Cash Control**: Opening/closing cash count to reconcile the cash drawer.

## Core Workflows

### 1. Configure a POS Shop

1. Navigate to **Point of Sale > Configuration > Point of Sale**.
2. Click **New** or select an existing POS.
3. Configure: name, warehouse, pricelist, payment methods, default customer, receipt header/footer.
4. Under **Connected Devices**, optionally enable IoT Box for printers, scanners, scales.
5. For restaurant mode, enable **Is a Bar/Restaurant**, configure floors and tables.
6. Save configuration.

### 2. Open a Session and Process Sales

1. Navigate to **Point of Sale** and click **Open Session** on the desired POS.
2. Enter opening cash balance if cash control is enabled.
3. On the POS interface, add products by clicking, scanning barcodes, or searching.
4. Select or create a customer.
5. Adjust quantities, apply discounts, or modify prices as needed.
6. Click **Payment**, select payment method, enter amount, and validate.
7. Print or email receipt.

### 3. Close a Session

1. Click the hamburger menu and select **Close**.
2. Count cash in the drawer and enter the closing balance.
3. Review the session summary (total sales, payments by method).
4. Click **Close Session**. Orders are posted to Accounting and Inventory.

### 4. Process Returns

1. In the POS interface, click **Refund** from an existing order.
2. Select the product(s) and quantity to return.
3. Process the refund payment.
4. The return generates a reverse inventory move.

### 5. Apply Sales Orders in POS

1. In the POS session, click **Quotations/Orders**.
2. Select an existing sales order from the Sales app.
3. Choose **Apply a down payment** (partial) or **Settle the order** (full).
4. Process payment as usual. The SO is updated accordingly.

## Technical Reference

### Models

| Model | Description |
|-------|-------------|
| `pos.config` | POS shop configuration |
| `pos.session` | POS session (open/close) |
| `pos.order` | POS transaction |
| `pos.order.line` | POS order line items |
| `pos.payment` | Payment records for POS orders |
| `pos.payment.method` | Payment method configuration |
| `pos.category` | POS product categories |
| `restaurant.floor` | Restaurant floor layout |
| `restaurant.table` | Table on a restaurant floor |

### Key Fields on `pos.order`

| Field | Type | Description |
|-------|------|-------------|
| `session_id` | Many2one | POS session |
| `partner_id` | Many2one | Customer |
| `lines` | One2many | Order lines |
| `payment_ids` | One2many | Payments |
| `amount_total` | Float | Total amount |
| `amount_paid` | Float | Amount paid |
| `amount_return` | Float | Change returned |
| `state` | Selection | `draft`, `paid`, `done`, `invoiced`, `cancel` |
| `fiscal_position_id` | Many2one | Fiscal position applied |

### Key Fields on `pos.config`

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | POS name |
| `module_pos_restaurant` | Boolean | Restaurant mode |
| `payment_method_ids` | Many2many | Payment methods |
| `pricelist_id` | Many2one | Default pricelist |
| `iface_tipproduct` | Boolean | Enable tips |
| `iface_start_categ_id` | Many2one | Starting product category |
| `warehouse_id` | Many2one | Stock warehouse |

### Menu Paths

- Dashboard: `Point of Sale > Dashboard`
- Orders: `Point of Sale > Orders > Orders`
- Sessions: `Point of Sale > Orders > Sessions`
- Configuration: `Point of Sale > Configuration > Point of Sale / Payment Methods`
- Products: `Point of Sale > Products`

## API / RPC Patterns

<!-- TODO: POS-specific external API/RPC examples not found in docs -->

The POS uses internal JS-to-server RPC calls. Standard ORM access for backend operations:

```python
# Retrieve orders for a session
env['pos.order'].search([('session_id', '=', session_id)])

# Get session totals
session = env['pos.session'].browse(session_id)
session.cash_register_balance_end_real
```

## Version Notes (19.0)

<!-- TODO: Specific 18-to-19 breaking changes not documented in the reviewed RST files. -->

- POS UI is fully web-based (OWL framework).
- IoT Box or Windows IoT can be used for hardware integration.
- Restaurant features (floors, tables, order printing, bill splitting) are part of the POS module, enabled via configuration toggle.

## Common Pitfalls

- **Cash control discrepancies**: Failing to count cash accurately at session close leads to accounting mismatches. Always reconcile before closing.
- **Offline orders not synced**: If the POS goes offline, orders queue locally. Ensure network is restored before closing the session to avoid data loss.
- **Payment terminal configuration**: Each terminal brand (Adyen, Stripe, Worldline, etc.) requires specific setup. Misconfiguration causes payment failures.
- **Product availability**: Only products with **Available in POS** checked appear in the POS interface. Missing products are usually just not flagged.
- **IoT Box requires network**: The IoT Box must be on the same network as the POS device. Firewall rules or network segmentation can block discovery.
