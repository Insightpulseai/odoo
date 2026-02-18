---
name: inventory
description: Warehouse management system for product tracking, storage, shipping, receiving, and inventory valuation.
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# Inventory — Odoo 19.0 Skill Reference

## Overview

Odoo Inventory is a combined inventory application and warehouse management system. It enables users to manage lead times, automate replenishment via reordering rules or MTO, configure advanced multi-step routes, track products by lots/serial numbers, handle shipping and receiving with carrier integrations, and perform inventory valuation using Standard, Average (AVCO), or FIFO costing methods. Used by warehouse managers, inventory planners, logistics teams, and operations staff.

## Key Concepts

- **Product Type**: `Goods` (tangible, trackable), `Service` (intangible, not tracked in inventory), `Combo` (mix of goods and services)
- **Tracked vs. Untracked Goods**: Tracked products maintain on-hand quantity and support reordering rules, valuation, lot/serial tracking. Untracked products are always considered available.
- **Track Inventory**: Options are `By Quantity`, `By Lots`, `By Unique Serial Number`
- **Warehouse**: Physical place with an address where items are stored. Has configurable routes.
- **Location**: Sub-division within a warehouse (shelves, floors, aisles). Types: Internal, Vendor, Customer, Virtual, Production, Transit, Inventory Loss.
- **Route**: Defines how products move through the supply chain (e.g., Buy, Manufacture, Dropship, Resupply Subcontractor on Order).
- **Operation Type**: Categorizes warehouse operations (Receipts, Delivery Orders, Internal Transfers, Manufacturing, etc.).
- **Reordering Rule**: Min/max stock rule that triggers PO or MO generation when forecasted stock drops below minimum.
- **MTO (Make to Order)**: Route that triggers PO/MO immediately upon SO confirmation, bypassing stock checks.
- **MPS (Master Production Schedule)**: Manual dashboard for long-term replenishment forecasting. Should not be used alongside reordering rules.
- **Lot**: A batch identifier for a group of products with common properties (received, stored, shipped together).
- **Serial Number**: A unique identifier assigned to an individual product unit for traceability.
- **Package**: Physical container grouping products (mixed or same); tracked with unique barcodes.
- **Packaging**: Fixed quantity grouping of the same product (e.g., pack of 6, 12, 24); identified by packaging-type barcodes.
- **UoM (Unit of Measure)**: Standard measurement for product quantities. Odoo auto-converts between purchase UoM, sales UoM, and inventory UoM.
- **Putaway Rule**: Defines where incoming products should be stored based on product, category, or route.
- **Storage Category**: Sets item or weight capacity limits on locations.
- **Removal Strategy**: Determines picking order — FIFO (default), LIFO, FEFO, Closest Location, Least Packages.
- **Reservation Method**: Controls when products are reserved for delivery — At Confirmation, Manually, Before Scheduled Date.
- **Picking Method**: Batch, Cluster, or Wave picking for optimizing outbound operations.
- **Inventory Valuation**: Monetary value of inventory. Costing methods: Standard Cost, Average Cost (AVCO), FIFO.
- **Landed Costs**: Additional costs (shipping, insurance, customs) added to product valuation.
- **Consignment (Owned Stock)**: Products in warehouse owned by a third party.
- **Dropshipping**: Vendor ships directly to customer, bypassing internal warehouse.

## Core Workflows

### 1. Receive Products (One-Step)

1. Create or confirm a Purchase Order in the Purchase app.
2. Navigate to `Inventory > Receipts` or click the `Receipt` smart button on the PO.
3. Verify quantities in the `Operations` tab. Click `Details` to assign lot/serial numbers if tracked.
4. Click `Validate` to register receipt. On-hand quantity updates for tracked products.

### 2. Deliver Products (One-Step)

1. Confirm a Sales Order in the Sales app.
2. Navigate to `Inventory > Delivery Orders` or click the `Delivery` smart button on the SO.
3. Verify product lines and quantities. For lot-tracked products, click `Details` to select specific lots.
4. Click `Validate` to confirm shipment. On-hand quantity decreases.

### 3. Configure Multi-Step Flows (2 or 3 Steps)

1. Go to `Inventory > Configuration > Warehouses`, select the warehouse.
2. Set `Incoming Shipments` to 2- or 3-step (Input > Stock, or Input > Quality > Stock).
3. Set `Outgoing Shipments` to 2- or 3-step (Pick > Ship, or Pick > Pack > Ship).
4. Odoo auto-creates the corresponding operation types and locations.

### 4. Set Up Reordering Rules

1. Navigate to the product form, click the refresh icon (or `Min / Max` smart button).
2. Click `New` to add a reordering rule.
3. Set the warehouse/location, minimum quantity, maximum quantity, and preferred route (Buy/Manufacture).
4. For automatic rules, Odoo generates POs/MOs when forecasted stock drops below min. For manual rules, suggestions appear in `Inventory > Operations > Replenishment`.

### 5. Perform Inventory Adjustment

1. Go to `Inventory > Operations > Physical Inventory`.
2. Select products to count. Click `Apply All` or update individual `Counted Quantity` values.
3. Click `Apply All` to confirm. Odoo adjusts on-hand quantities and creates stock move entries.

## Technical Reference

### Key Models

| Model | Description |
|-------|-------------|
| `product.product` | Product variant (holds barcode, qty on hand) |
| `product.template` | Product template (shared across variants) |
| `stock.warehouse` | Warehouse definition |
| `stock.location` | Inventory location (internal, virtual, transit, etc.) |
| `stock.picking` | Transfer/picking operation (receipt, delivery, internal) |
| `stock.picking.type` | Operation type configuration |
| `stock.move` | Individual product movement line |
| `stock.move.line` | Detailed move line (lot/serial, package info) |
| `stock.quant` | On-hand inventory quantity at a specific location |
| `stock.lot` | Lot/serial number record |
| `stock.quant.package` | Physical package |
| `product.packaging` | Product packaging definition (fixed quantity) |
| `stock.warehouse.orderpoint` | Reordering rule |
| `stock.route` | Inventory route |
| `stock.rule` | Pull/push rule within a route |
| `stock.valuation.layer` | Inventory valuation entry |
| `stock.scrap` | Scrap order |
| `uom.uom` | Unit of measure |
| `uom.category` | UoM category (for conversion grouping) |

### Key Fields

- `product.template.type`: `'goods'`, `'service'`, `'combo'`
- `product.template.tracking`: `'none'`, `'lot'`, `'serial'`
- `stock.picking.type.reservation_method`: `'at_confirm'`, `'manual'`, `'by_date'`
- `stock.warehouse.reception_steps`: `'one_step'`, `'two_steps'`, `'three_steps'`
- `stock.warehouse.delivery_steps`: `'ship_only'`, `'pick_ship'`, `'pick_pack_ship'`
- `product.category.removal_strategy_id`: links to removal strategy (FIFO, LIFO, FEFO, etc.)
- `stock.location.removal_strategy_id`: removal strategy override at location level

### Key Settings (in `res.config.settings`)

- `group_stock_tracking_lot` — Lots & Serial Numbers
- `group_stock_expiration_date` — Expiration Dates
- `group_stock_multi_locations` — Storage Locations
- `group_stock_adv_location` — Multi-Step Routes
- `group_stock_packaging` — Packages
- `group_stock_production_lot` — Display Lots & Serial Numbers on Delivery Slips

### Important XML IDs

- `stock.warehouse0` — default warehouse
- `stock.stock_location_stock` — WH/Stock location
- `stock.stock_location_customers` — Customer location (virtual)
- `stock.stock_location_suppliers` — Vendor location (virtual)
- `stock.picking_type_in` — Receipts operation type
- `stock.picking_type_out` — Delivery Orders operation type
- `stock.picking_type_internal` — Internal Transfers operation type
- `stock.route_warehouse0_mto` — Make to Order route
- `stock.removal_fifo` / `stock.removal_lifo` — Removal strategies

## API / RPC Patterns

<!-- TODO: not found in docs — Odoo 19 inventory docs do not cover JSON-RPC or XML-RPC examples directly. -->

Standard ORM methods apply:

```python
# Create a stock picking (delivery)
picking_vals = {
    'partner_id': partner_id,
    'picking_type_id': picking_type_out_id,
    'location_id': stock_location_id,
    'location_dest_id': customer_location_id,
    'move_ids': [(0, 0, {
        'name': product.name,
        'product_id': product.id,
        'product_uom_qty': 5.0,
        'product_uom': product.uom_id.id,
        'location_id': stock_location_id,
        'location_dest_id': customer_location_id,
    })],
}
picking = env['stock.picking'].create(picking_vals)
picking.action_confirm()
picking.action_assign()  # Reserve stock
picking.button_validate()  # Validate transfer
```

## Version Notes (19.0)

### Inventory Valuation Changes (Major)

- **Perpetual accounting** no longer posts real-time journal entries at each stock movement. Instead, stock valuation account impacts occur at invoice level, with a closing entry handling the difference.
- **Periodic Anglo-Saxon** is now fully supported (was unsupported in 18.0).
- **Automated closing entries** replace manual closing for all Continental methods.
- Perpetual entries reduced from "Invoices + every move" to "Invoices + one closing entry" — significant performance improvement.
- New features: Invoices to issue, Bills to receive, Prepaid expenses, Deferred revenues — all handled via closing entry workflow.
- Accounting valuation no longer requires the Inventory app to be installed (Accounting only mode supported).

### Product Type Simplification

- In 19.0, `Product Type` is now `Goods`, `Service`, or `Combo`. The old `Consumable` and `Storable Product` distinction has been replaced by the `Track Inventory` checkbox on Goods.

## Common Pitfalls

- **Untracked goods silently skip inventory updates**: Receiving or delivering untracked products does not change on-hand quantity. Reordering rules, valuation, and inventory reports only work with tracked products.
- **Removal strategy priority**: When set on both product category (`Force Removal Strategy`) and location (`Removal Strategy`), the **product category** value takes precedence.
- **MPS conflicts with reordering rules**: Using the Master Production Schedule alongside automated reordering rules causes conflicting replenishment signals. Use one or the other, never both.
- **Multi-step routes require Storage Locations and Multi-Step Routes settings**: Both must be enabled under `Inventory > Configuration > Settings > Warehouse` before configuring 2- or 3-step flows.
- **Lot/serial number assignment must happen before validation**: Attempting to validate a receipt without assigning required lot/serial numbers triggers a blocking error.
