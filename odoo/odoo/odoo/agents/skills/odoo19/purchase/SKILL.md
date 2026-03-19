---
name: purchase
description: Purchase management for vendor quotations, purchase orders, blanket orders, and procurement automation.
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# Purchase — Odoo 19.0 Skill Reference

## Overview

Odoo Purchase manages the full procurement lifecycle: creating requests for quotation (RFQs), converting them to purchase orders (POs), tracking vendor bills, and automating replenishment. It supports blanket orders for long-term vendor agreements, calls for tenders to compare multiple vendors, purchase templates for recurring orders, and advanced analytics via vendor cost reports and procurement dashboards. Used by procurement officers, purchasing managers, and supply chain teams.

## Key Concepts

- **Request for Quotation (RFQ)**: A document sent to a vendor requesting product pricing and availability. Becomes a PO upon confirmation.
- **Purchase Order (PO)**: A confirmed order to purchase products from a vendor. Triggers receipt creation in Inventory.
- **Vendor Pricelist**: Per-vendor pricing defined in the `Purchase` tab of a product form. Auto-populates price, lead time, and vendor reference on RFQs.
- **Blanket Order**: A long-term purchase agreement with a vendor specifying products, prices, and validity period. New RFQs can be created from the blanket order with pre-populated data.
- **Purchase Agreement**: Umbrella term covering Blanket Orders and Calls for Tenders. Enabled via `Purchase > Configuration > Settings > Purchase Agreements`.
- **Call for Tenders**: Alternative RFQs sent to multiple vendors for the same products, enabling price/lead-time comparison.
- **Purchase Template**: Reusable template for recurring purchase orders with pre-defined products.
- **Order Deadline**: Date by which the vendor must confirm the RFQ. After this date, the RFQ is marked as late.
- **Expected Arrival**: Auto-calculated from Order Deadline + vendor lead time.
- **Reordering Rule (Purchase context)**: Automatically generates RFQs/POs when product stock falls below minimum level and the `Buy` route is configured.
- **Temporary Reordering**: One-time purchase suggestion outside of permanent reordering rules.
- **Bill Control**: Configures when vendor bills are created — on ordered quantities or received quantities.
- **EDI (Electronic Data Interchange)**: Electronic exchange of purchase documents with vendors.
- **Vendor Reference**: The vendor's own order/reference number, useful for matching with incoming shipments.

## Core Workflows

### 1. Create and Confirm a Purchase Order

1. Navigate to `Purchase > Orders > Requests for Quotation`, click `New`.
2. Select a `Vendor`. Optionally set `Vendor Reference`, `Order Deadline`, and `Deliver to` warehouse.
3. In the `Products` tab, click `Add a product` and select products. Prices auto-populate from vendor pricelist if configured.
4. Click `Send by Email` to send the RFQ to the vendor (moves to `RFQ Sent` stage).
5. Click `Confirm Order` to convert the RFQ to a PO. A receipt is auto-created in Inventory.
6. Click `Receive Products` to navigate to the receipt and validate incoming goods.

### 2. Set Up a Blanket Order

1. Enable `Purchase Agreements` in `Purchase > Configuration > Settings > Orders`.
2. Go to `Purchase > Orders > Purchase Agreements`, click `New`.
3. Set `Agreement Type` to `Blanket Order`. Select `Vendor`, configure `Agreement Validity`.
4. Add products with agreed `Unit Price` in the product lines.
5. Click `Confirm`. The blanket order is now active.
6. Click `New Quotation` from the blanket order to create pre-populated RFQs.

### 3. Automated Replenishment via Purchase

1. On the product form, go to the `Inventory` tab and enable the `Buy` route.
2. In the `Purchase` tab, add at least one vendor with price and lead time.
3. Create a reordering rule (from the product form's refresh/Min-Max smart button) with min/max quantities.
4. When forecasted stock drops below minimum, Odoo generates a draft PO (automatic) or suggests one in the replenishment report (manual).

### 4. Compare Vendors with Call for Tenders

1. Enable `Purchase Agreements` in Purchase settings.
2. Create a new Purchase Agreement with `Agreement Type` = `Call for Tenders`.
3. Add desired products and quantities.
4. Click `Confirm`, then create multiple RFQs to different vendors from the agreement.
5. Compare prices and lead times. Select the best offer and confirm.

### 5. Manage Vendor Bills

1. After receiving products, go to the PO and click `Create Bill`.
2. Verify quantities and amounts on the vendor bill form.
3. Click `Confirm` to register the bill.
4. Payment can be registered from Accounting.

## Technical Reference

### Key Models

| Model | Description |
|-------|-------------|
| `purchase.order` | Purchase order / RFQ |
| `purchase.order.line` | PO line item |
| `purchase.requisition` | Purchase agreement (blanket order / call for tenders) |
| `purchase.requisition.line` | Agreement line item |
| `product.supplierinfo` | Vendor pricelist entry (on product's Purchase tab) |
| `stock.picking` | Receipt (auto-created on PO confirmation) |
| `account.move` | Vendor bill |

### Key Fields

- `purchase.order.state`: `'draft'` (RFQ), `'sent'` (RFQ Sent), `'purchase'` (PO), `'done'` (Locked), `'cancel'`
- `purchase.order.date_order`: Order Deadline / Confirmation Date
- `purchase.order.date_planned`: Expected Arrival
- `purchase.order.partner_ref`: Vendor Reference
- `purchase.order.requisition_id`: Link to blanket order
- `purchase.requisition.type_id`: Agreement type
- `product.supplierinfo.partner_id`: Vendor
- `product.supplierinfo.price`: Vendor unit price
- `product.supplierinfo.delay`: Delivery lead time (days)

### Key Settings

- `purchase.use_po_lead` — Security Lead Time for Purchase
- `purchase_requisition.group_purchase_requisition` — Purchase Agreements (Blanket Orders / Calls for Tenders)

### Important XML IDs

- `purchase.purchase_rfq` — RFQ list action
- `purchase.purchase_form_action` — PO form action
- `purchase.route_warehouse0_buy` — Buy route

## API / RPC Patterns

<!-- TODO: not found in docs — Odoo 19 purchase docs do not cover JSON-RPC or XML-RPC examples directly. -->

Standard ORM methods apply:

```python
# Create and confirm a purchase order
po_vals = {
    'partner_id': vendor.id,
    'order_line': [(0, 0, {
        'product_id': product.id,
        'product_qty': 100.0,
        'price_unit': 10.50,
    })],
}
po = env['purchase.order'].create(po_vals)
po.button_confirm()
```

## Version Notes (19.0)

- **Product type changes**: `Consumable` and `Storable Product` distinction replaced by `Goods` with `Track Inventory` checkbox. Purchase behavior unchanged — both tracked and untracked goods can be purchased.
- **Inventory valuation on purchase**: Vendor bills now impact stock valuation account directly (perpetual method). See Inventory SKILL.md for valuation changes.

<!-- TODO: specific breaking changes between 18.0 and 19.0 not documented in purchase RST source -->

## Common Pitfalls

- **Missing vendor pricelist causes zero prices on RFQs**: If no vendor is configured in the product's `Purchase` tab, products added to an RFQ have `0.00` unit price by default.
- **Blanket order prices must be set manually**: Pre-existing product prices do not auto-populate on blanket order lines. The `Unit Price` must be explicitly entered.
- **Reordering rules require at least one vendor**: Automatic PO generation fails if no vendor is listed on the product's `Purchase` tab.
- **Dropship option requires Inventory setting**: The `Dropship` delivery address on RFQs only appears if the `Dropshipping` setting is enabled in `Inventory > Configuration > Settings`.
- **Order Deadline vs. Expected Arrival**: Order Deadline is when the vendor must confirm; Expected Arrival is when goods arrive. Confusing these leads to incorrect planning.
