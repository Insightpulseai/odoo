---
name: repairs
description: Repair order management for returned or damaged products, with parts tracking and customer invoicing.
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# Repairs — Odoo 19.0 Skill Reference

## Overview

Odoo Repairs assists companies in creating and processing repair orders for damaged products returned by customers. It tracks the full repair lifecycle: processing a customer return, creating a repair order with parts (add, remove, recycle), executing the repair, and returning the repaired product. Integrates with Sales (for returns and invoicing), Inventory (for stock movements), and optionally with Quality (for quality checks on repaired products). Used by repair technicians, service managers, and customer service teams.

## Key Concepts

- **Repair Order (RO)**: A record tracking the repair of a specific product. States: Draft, Confirmed, Under Repair, Repaired, Done, Cancelled.
- **Parts**: Components used in the repair, listed in the `Parts` tab. Each part has a `Type`:
  - `Add` — A component to be added to the product during repair.
  - `Remove` — A component to be removed from the product during repair.
  - `Recycle` — A component removed and designated for later reuse.
- **Under Warranty**: Checkbox on the RO. If ticked, the customer is not charged for parts used in the repair.
- **Reverse Transfer**: A return receipt created from a delivery order (via the `Return` button), used to bring damaged products back to the warehouse.
- **Product Moves**: Smart button on completed ROs showing the stock movement history during and after repair.
- **Demand vs. Done**: `Demand` column lists the planned quantity of parts; `Done` column tracks actual quantity used.
- **Used Checkbox**: Indicates whether a part was actually consumed during the repair. Parts not marked as used trigger an `Uncomplete Move(s)` warning on completion.
- **Create Quotation**: Button on completed ROs (for non-warranty repairs) that generates a Sales Order with the repair cost for customer invoicing.

## Core Workflows

### 1. Process a Customer Return

1. In the Sales app, open the original SO. Click the `Delivery` smart button.
2. On the delivery order, click `Return`. A `Reverse Transfer` popup appears.
3. Adjust the return `Quantity` if needed. Click `Return`.
4. When the product arrives, click `Validate` on the reverse transfer form to register receipt.

### 2. Create a Repair Order

1. Navigate to `Repairs` app, click `New`.
2. Select the `Customer`.
3. Select the `Product to Repair` and set `Product Quantity`.
4. In the `Return` field, link to the reverse transfer from step 1.
5. Tick `Under Warranty` if applicable (customer will not be charged for parts).
6. Set `Scheduled Date` and assign a `Responsible` user.
7. In the `Parts` tab, click `Add a line`:
   - Set `Type` to `Add`, `Remove`, or `Recycle`.
   - Select the `Product` (part) and set `Demand` quantity.
8. Add internal notes in the `Repair Notes` tab.
9. Click `Confirm Repair`. Odoo reserves required components.

### 3. Execute the Repair

1. Open the confirmed RO.
2. Click `Start Repair`. The RO moves to `Under Repair` stage.
3. As parts are used, update the `Done` column and tick the `Used` checkbox.
4. When repair is complete, click `End Repair`.
5. If not all parts were used, an `Uncomplete Move(s)` popup appears. Click `Validate` to confirm or `Discard` to adjust.
6. The RO moves to `Repaired` stage. A `Product Moves` smart button shows stock movement history.

### 4. Return Repaired Product to Customer

**Under Warranty:**
1. Navigate to the original SO in Sales. Click the `Delivery` smart button.
2. Click the reverse transfer. Click `Return` to create a new delivery.
3. Confirm and validate the delivery to ship the repaired product back.

**Not Under Warranty:**
1. On the completed RO, click `Create Quotation`.
2. A new SO is pre-populated with repair parts and costs.
3. Confirm the SO and invoice the customer.
4. Process the delivery to return the repaired product.

## Technical Reference

### Key Models

| Model | Description |
|-------|-------------|
| `repair.order` | Repair order |
| `repair.line` | Repair order part line (components) |
| `stock.picking` | Return receipt / delivery for repaired product |
| `sale.order` | Sales order (generated for non-warranty invoice) |

### Key Fields

- `repair.order.name`: RO reference number
- `repair.order.product_id`: Product to repair
- `repair.order.product_qty`: Quantity to repair
- `repair.order.partner_id`: Customer
- `repair.order.picking_id`: Linked return (reverse transfer)
- `repair.order.under_warranty`: Boolean warranty flag
- `repair.order.schedule_date`: Scheduled repair date
- `repair.order.user_id`: Responsible user
- `repair.order.state`: `'draft'`, `'confirmed'`, `'under_repair'`, `'done'`, `'cancel'`
- `repair.line.type`: `'add'`, `'remove'`, `'recycle'`
- `repair.line.product_id`: Part/component product
- `repair.line.product_uom_qty`: Demand quantity
- `repair.line.qty_done`: Actual quantity used
- `repair.line.lot_id`: Lot/serial number for the part
- `repair.order.picking_type_id`: Operation type (defaults to `YourCompany: Repairs`)

### Important XML IDs

- `repair.action_repair_order_tree` — Repair Orders list action
- `repair.action_repair_order_form` — Repair Order form view

## API / RPC Patterns

<!-- TODO: not found in docs — Odoo 19 repairs docs do not cover JSON-RPC or XML-RPC examples directly. -->

## Version Notes (19.0)

- **Product type changes**: Repaired products use the new `Goods` type with `Track Inventory` checkbox (replacing `Storable Product`).
- **Reservation methods**: Repair orders support configurable reservation methods (At Confirmation, Manually, Before Scheduled Date) via the Repairs operation type.

<!-- TODO: specific breaking changes between 18.0 and 19.0 not documented in repairs RST source -->

## Common Pitfalls

- **Under Warranty skips customer charging**: When `Under Warranty` is ticked, the `Create Quotation` button behavior changes — the customer is not charged for parts. Ensure warranty status is correct before confirming.
- **Uncomplete Moves warning on End Repair**: If parts listed in the `Parts` tab are not marked as `Used`, Odoo warns about the discrepancy. Click `Validate` to proceed or `Discard` to fix quantities first.
- **Return must be validated before creating RO**: The reverse transfer (return) should be validated (product received back in warehouse) before starting the repair. Otherwise, the product is not available in stock for the repair process.
- **RO does not auto-create a return delivery**: After repair, the product must be manually returned to the customer by creating a new delivery from the original SO's reverse transfer. The RO itself does not generate outbound shipments.
- **Parts with Type = Remove reduce stock**: Removed parts are moved out of the repaired product. If these parts have value, they should be tracked (potentially recycled) to avoid inventory discrepancies.
