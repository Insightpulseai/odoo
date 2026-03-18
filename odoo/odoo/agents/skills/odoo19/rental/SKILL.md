---
name: rental
description: Rental order management with flexible pricing, pickup/return tracking, and inventory integration
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# rental -- Odoo 19.0 Skill Reference

## Overview

Odoo Rental manages the full lifecycle of renting physical products: creating rental orders with configurable pricing periods, tracking product pickups and returns, handling late fees, managing deposits, and integrating with Inventory for stock tracking across multiple locations. Used by equipment rental businesses, vehicle hire companies, and any organization that lends physical assets.

## Key Concepts

- **Rental Order**: A sales order for rented products with a defined rental period (pickup and return dates).
- **Rental Period**: The duration of a rental, defined by start and end dates/times.
- **Pricing Period**: A configurable time unit (hourly, daily, weekly, etc.) with an associated rental price.
- **Delay Cost**: Additional charges for late returns (hourly fine, daily fine).
- **Padding Time**: Minimum buffer time between two rentals of the same product (for cleaning, maintenance).
- **Rental Transfer**: Stock moves (delivery for pickup, receipt for return) tracking product location.
- **Deposit**: A refundable security deposit collected as an optional service product alongside the rental.
- **Customer/Rental Location**: Internal inventory location used to track products during the rental period.

## Core Workflows

### 1. Configure Rental Products

1. Navigate to **Rental > Products**, click **New**.
2. Tick the **Rental** checkbox.
3. Set **Product Type** to **Goods** and enable **Track Inventory** (By Unique Serial Number recommended).
4. Open the **Rental prices** tab.
5. Under **Pricing**, click **Add a price** to define pricing periods (e.g., 1 day = $100, 3 days = $250, 1 week = $500).
6. Under **Reservations**, configure **Hourly Fine**, **Daily Fine**, and **Reserve product** padding time.
7. Save.

### 2. Create a Rental Order

1. Navigate to **Rental > Orders > Orders**, click **New**.
2. Select a **Customer**.
3. Configure the **Rental period** (start/end dates) using the calendar picker. Click **Apply**.
4. In **Order Lines**, click **Add a product** and select the rental product.
5. Odoo auto-calculates the cheapest pricing rule for the selected duration.
6. Click **Send** to send the quotation; click **Confirm** when the customer accepts.

### 3. Pickup and Return

1. On the confirmed rental order, click **Pickup**.
2. Validate the warehouse delivery form to record the product leaving stock.
3. When the customer returns the product, click **Return** on the rental order.
4. Enter the returned quantity and serial numbers (if applicable).
5. Click **Validate** to complete the return receipt.
6. Print pickup/return receipts via **Actions > Print > Pickup and Return Receipt**.

### 4. Invoice a Rental

1. From the **Rental Orders** dashboard, click **To Invoice** in the Invoice Status section.
2. Open the rental order, click **Create Invoice**.
3. Select **Regular invoice**, click **Create Draft**.
4. Confirm the invoice, then send or print.
5. Click **Pay** and register payment.

### 5. Manage Deposits

1. Create a service product for the deposit (e.g., "Camera Deposit") with **Invoicing Policy** = **Delivered quantities**.
2. On the rental product form, **Sales** tab, add the deposit product to **Optional Products**.
3. When creating a rental order, the **Configure your product** popup shows the deposit option.
4. Upon return, refund the deposit via a credit note on the invoice and set the delivered quantity to 0 on the SO.

## Technical Reference

### Models

| Model | Description |
|-------|-------------|
| `sale.order` | Rental orders (extended SO with rental fields) |
| `sale.order.line` | Rental order line items with rental period |
| `sale.temporal.recurrence` | Rental pricing periods |
| `product.template` | Products with `rent_ok` flag |
| `product.pricing` | Rental pricing rules per product |
| `stock.picking` | Pickup (delivery) and return (receipt) transfers |

### Key Fields on Rental Products

| Field | Type | Description |
|-------|------|-------------|
| `rent_ok` | Boolean | Product can be rented |
| `extra_hourly` | Float | Hourly late fee |
| `extra_daily` | Float | Daily late fee |

### Key Configuration (Settings)

| Setting | Description |
|---------|-------------|
| Default Delay Costs | Per-hour and per-day late return fees |
| Default Padding Time | Buffer hours between consecutive rentals |
| Rental Transfers | Enable stock moves for pickup/return tracking |
| Minimal Rental Duration | Minimum rental period for online orders |
| Unavailability Days | Days when pickup/return are not possible |

### Price Computing Rules

1. Only one pricing line is used per calculation.
2. The cheapest applicable line is always selected.
3. The pricing is multiplied to cover the full rental duration.

### Menu Paths

- Rental Orders: `Rental > Rental Orders`
- Products: `Rental > Products`
- Settings: `Rental > Configuration > Settings`
- Rental Periods: `Rental > Configuration > Rental Periods`

## API / RPC Patterns

<!-- TODO: Rental-specific external API examples not found in docs -->

Standard ORM access:

```python
# Search active rental orders
env['sale.order'].search([('is_rental_order', '=', True), ('rental_status', '=', 'pickup')])
```

## Version Notes (19.0)

<!-- TODO: Specific 18-to-19 breaking changes not documented in the reviewed RST files. -->

- Rental orders are built on `sale.order` with rental-specific fields and workflow states.
- Rental Transfers feature creates a `Customer/Rental` location in Inventory automatically upon enablement. Do not modify this location.
- Customer signature integration requires the **Sign** app.

## Common Pitfalls

- **Price computing selects cheapest, not most intuitive**: For an 8-day rental with 1-day ($100) and 3-day ($250) pricing, Odoo picks 3x the 3-day rate ($750), not 1x week + 1x day. This can surprise users expecting different logic.
- **Rental Transfers creates internal location**: Enabling Rental Transfers auto-creates a `Customer/Rental` location. Modifying or deleting it corrupts inventory tracking.
- **Serial number tracking is essential for high-value items**: Without serial numbers, it is impossible to track which specific unit was rented and returned.
- **Deposit refunds are manual**: There is no automatic deposit refund workflow. The deposit must be refunded manually via credit note after product return.
- **Padding time is not per-product by default**: Default Padding Time applies globally unless overridden at the product level.
