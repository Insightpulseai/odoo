# Inventory & Warehouse Management Skill Pack

> Odoo 18 CE + OCA | SAP-equivalent: MM-WM (Warehouse Management) + PP (Production Planning)

---

## Scope

Multi-warehouse operations, inventory routes, lot and serial tracking, putaway strategies,
pick-pack-ship, cycle counting, reorder rules, manufacturing (MRP), and stock valuation.
Covers enterprise warehouse complexity achievable on Odoo 18 CE with OCA modules.

---

## Concepts

| Concept | SAP Equivalent | Odoo Surface |
|---------|---------------|--------------|
| Warehouse | Warehouse Number (WM) | `stock.warehouse` |
| Storage Location | Storage Bin (WM) | `stock.location` |
| Goods Receipt | MIGO (101) | `stock.picking` (incoming) |
| Goods Issue | MIGO (201/261) | `stock.picking` (outgoing/internal) |
| Transfer Order | LT01 (TO) | `stock.picking` (internal) |
| Lot/Batch | Batch (CHARG) | `stock.lot` (tracking=lot) |
| Serial Number | Serial (SERNR) | `stock.lot` (tracking=serial) |
| Putaway Strategy | Storage Type/Section | `stock.putaway.rule` |
| Route | Route Determination | `stock.route` |
| Reorder Point | MRP (MD04) | `stock.warehouse.orderpoint` |
| Manufacturing Order | Production Order (CO01) | `mrp.production` |
| Bill of Materials | BOM (CS01) | `mrp.bom` |
| Cycle Count | MI01 (Physical Inventory) | `stock.quant` adjustment |
| Valuation | Material Ledger | `stock.valuation.layer` |

---

## Must-Know Vocabulary

- **stock.warehouse**: Top-level entity. Each warehouse has input, output, packing, and
  stock locations. Multi-step routes configured here (1/2/3-step receipt/delivery).
- **stock.location**: Hierarchical structure. Types: internal, supplier, customer, inventory
  (for adjustments), production, transit.
- **stock.picking**: A transfer document grouping `stock.move` records. Type determined
  by `picking_type_id` (receipts, deliveries, internal transfers).
- **stock.move**: Individual product movement. States: draft, waiting, confirmed, assigned
  (reserved), done, cancel.
- **stock.move.line**: Detailed movement with lot/serial assignment and specific source/dest.
- **stock.quant**: On-hand quantity at a specific location for a specific product/lot.
- **stock.lot**: Lot or serial number record linked to product.
- **stock.route**: Defines the path products take (buy, manufacture, dropship, inter-warehouse).
- **stock.rule**: Procurement rule within a route (push or pull).
- **stock.warehouse.orderpoint**: Reorder rule. Triggers procurement when stock drops below min.
- **mrp.production**: Manufacturing order consuming components and producing finished goods.
- **mrp.bom**: Bill of materials. Types: manufacture, phantom (kit), subcontracting.
- **stock.valuation.layer**: Records cost layers for perpetual inventory valuation.
- **stock.putaway.rule**: Directs incoming products to specific locations based on
  product category or product.

---

## Core Workflows

### 1. Warehouse Configuration
1. Create `stock.warehouse` with code and name.
2. Configure receipt steps: 1-step (direct), 2-step (input + stock), 3-step (input + quality + stock).
3. Configure delivery steps: 1-step (direct), 2-step (pick + ship), 3-step (pick + pack + ship).
4. Define `stock.location` hierarchy under warehouse stock location.
5. Set up putaway rules (`stock.putaway.rule`) for product placement.

### 2. Goods Receipt
1. PO confirmation creates incoming `stock.picking`.
2. Check availability (assign): `action_assign()`.
3. Record received quantities on `stock.move.line`.
4. Assign lot/serial numbers if product tracking enabled.
5. Validate: `button_validate()`. Stock quants updated. Valuation layer created.
6. Partial receipt: remaining auto-creates backorder.

### 3. Pick-Pack-Ship (3-Step Delivery)
1. SO confirmation creates pick transfer (stock -> output/packing zone).
2. **Pick**: Reserve stock. Worker picks from shelf locations. Validate.
3. **Pack**: Products moved to packing zone. Package assignment (`stock.quant.package`).
4. **Ship**: Final transfer from output to customer location. Validate.
5. Carrier integration (if configured) generates shipping labels.

### 4. Internal Transfers
1. Create `stock.picking` with internal picking type.
2. Source and destination locations within or across warehouses.
3. Inter-warehouse transfer uses transit location.
4. Validate transfer. Quants update at both locations.

### 5. Lot and Serial Tracking
1. Product configured with `tracking='lot'` or `tracking='serial'`.
2. On receipt: assign lot/serial numbers to `stock.move.line`.
3. Full traceability: upstream (where did this lot come from?) and downstream (where did it go?).
4. Expiry dates via `product_expiry` module (installed by default in 18 CE).
5. Lot recall: trace all deliveries containing the affected lot.

### 6. Reorder Rules and Procurement
1. Create `stock.warehouse.orderpoint` for product at specific warehouse/location.
2. Set minimum quantity, maximum quantity, and multiple.
3. Scheduler (`stock.scheduler`) runs periodically (cron) to check and trigger.
4. Triggers procurement based on product route: PO (buy) or MO (manufacture).
5. Lead times from `product.supplierinfo` or `mrp.bom` used for scheduling.

### 7. Manufacturing (MRP)
1. Define `mrp.bom` with components and operations (if work centers configured).
2. MO created from reorder rules or manually.
3. Components reserved from stock (`stock.move` for raw materials).
4. Production recorded: consume components, produce finished goods.
5. Byproducts and scrap handled via dedicated moves.
6. Cost rollup: component costs + operation costs = finished goods cost.

### 8. Cycle Counting
1. Odoo uses `stock.quant` inventory adjustments (no separate inventory document).
2. Filter quants by location, product category, or last count date.
3. Update `inventory_quantity` on `stock.quant`. Apply adjustment.
4. Discrepancies post to inventory adjustment account.
5. Schedule periodic counts via cron or manual campaign.

---

## Edge Cases

- **Negative stock**: Odoo allows negative quants by default. Disable with
  `stock.location.allow_negative_stock=False` (OCA module) or warehouse config.
- **Reservation conflicts**: Two pickings reserve the same stock. First-come-first-served
  based on `stock.move.date` priority. Manual unreservation may be needed.
- **Phantom BOM**: Kit product. SO line shows kit, but picking shows individual components.
  No manufacturing order created -- explosion is immediate.
- **Scrap during production**: Use `mrp.production` scrap button. Creates stock move to
  scrap location. Cost charged to production.
- **Multi-UoM**: Product stocked in kg but sold in units. UoM conversion on
  `product.template.uom_id` vs `uom_po_id`. Rounding errors accumulate.
- **Cross-dock**: Receipt triggers immediate delivery without storage. Configure route
  with `stock.rule` push from input to output.
- **Consignment stock**: Supplier-owned inventory in your warehouse. Use owner field on
  `stock.quant` (`owner_id`). Not consumed until ownership transfer.
- **Backdated moves**: Posting `stock.move` with past date affects valuation layers
  retroactively. Can cause discrepancies with GL if period is locked.

---

## Controls & Compliance

| Control | Implementation |
|---------|---------------|
| Stock accuracy | Cycle count program with ABC classification. Target: A items monthly, B quarterly, C annually. |
| Lot traceability | Mandatory lot assignment on receipt. `tracking` field on `product.template`. |
| Expiry management | `product_expiry` module. Alerts on `use_date`, `removal_date`. FEFO strategy. |
| Segregation of duties | Warehouse user != inventory adjustment approver. Separate groups. |
| Valuation reconciliation | Monthly comparison of `stock.valuation.layer` totals vs GL inventory accounts. |
| Negative stock prevention | OCA `stock_no_negative` or custom constraint on `stock.quant`. |
| Access control | Location-based `ir.rule` to restrict users to their warehouse. |
| Scrap authorization | Scrap moves require validation by supervisor group. |

---

## Odoo/OCA Implementation Surfaces

### Core Odoo 18 CE Models
- `stock.warehouse` -- warehouse definition and multi-step config
- `stock.location` -- hierarchical location tree
- `stock.picking` / `stock.picking.type` -- transfer documents
- `stock.move` / `stock.move.line` -- product movements
- `stock.quant` -- on-hand quantities per location/lot
- `stock.lot` -- lot and serial number records
- `stock.route` / `stock.rule` -- procurement routes
- `stock.warehouse.orderpoint` -- reorder rules
- `stock.putaway.rule` -- putaway strategies
- `stock.valuation.layer` -- inventory valuation
- `mrp.production` / `mrp.bom` / `mrp.bom.line` -- manufacturing
- `mrp.workcenter` / `mrp.workorder` -- production operations

### OCA Modules (18.0-compatible)
| Module | Repo | Purpose |
|--------|------|---------|
| `stock_available_unreserved` | OCA/stock-logistics-warehouse | Show unreserved available qty |
| `stock_demand_estimate` | OCA/stock-logistics-warehouse | Demand forecasting for reorder |
| `stock_no_negative` | OCA/stock-logistics-warehouse | Prevent negative stock |
| `stock_inventory_discrepancy` | OCA/stock-logistics-warehouse | Threshold alerts on count discrepancies |
| `stock_putaway_product_template` | OCA/stock-logistics-warehouse | Putaway by product template |
| `stock_picking_batch` | OCA/stock-logistics-workflow | Batch picking for wave picking |
| `stock_move_line_auto_fill` | OCA/stock-logistics-workflow | Auto-fill done qty on moves |
| `stock_landed_costs_delivery` | OCA/stock-logistics-workflow | Landed cost on delivery |
| `product_expiry_simple` | OCA/product-attribute | Simplified expiry tracking |

---

## Azure/Platform Considerations

- **Barcode scanning**: Odoo barcode module works in browser. Deploy on tablets connected
  via Azure Front Door. Low-latency requirement (<200ms) for scan-to-validate.
- **Stock valuation table size**: `stock.valuation.layer` and `stock.move.line` grow fast.
  Partition by `create_date` or archive older layers.
- **MRP scheduler**: The procurement scheduler (`stock.scheduler`) can be CPU-intensive.
  Run via dedicated cron with timeout >300s on Azure Container Apps.
- **Multi-warehouse sync**: Inter-warehouse transfers via transit locations. Monitor
  in-transit stock with scheduled reports.
- **IoT integration**: Weigh scales, label printers via Odoo IoT Box (CE-compatible).
  Network access through Azure VNet if on-premise devices.

---

## Exercises

### Exercise 1: Multi-Step Warehouse Setup
Create a warehouse with 3-step receipt (input -> quality -> stock) and 3-step delivery
(pick -> pack -> ship). Process a PO receipt through all three steps. Then process a
SO delivery through pick-pack-ship.

### Exercise 2: Lot Traceability
Receive 500 units of Product A across 5 lots (100 each). Deliver 250 units from lots
1-3. Run upstream and downstream traceability reports. Simulate a recall on lot 2 and
identify all affected deliveries.

### Exercise 3: Reorder Rules
Configure an orderpoint for Product B: min=100, max=500, multiple=50. Set current stock
to 80. Run the scheduler. Verify a PO is created for 500 units (round up to max by
multiple). Receive and verify stock level.

### Exercise 4: Cycle Count Program
Select 20 products across A/B/C categories. Adjust `stock.quant.inventory_quantity` for
5 products with discrepancies. Apply adjustments. Verify the GL entries for inventory
adjustment. Generate a discrepancy report.

### Exercise 5: MRP Production
Create a BOM for Product X (3 components). Create an MO for 50 units. Reserve components.
Mark 2 units as scrap during production. Produce 48 units. Verify component consumption,
finished goods receipt, scrap entries, and unit cost calculation.

---

## Test Prompts for Agents

1. "Set up a warehouse with 2-step receipt and 3-step delivery. Create the picking types
   and locations. Show the route configuration."

2. "We received 1000 units of Product A in lot BATCH-2026-Q1. Move 300 to Zone A and
   700 to Zone B using putaway rules. Verify quant distribution."

3. "Current stock of Product B is 45 units. Reorder point is 100, max is 400. What happens
   when the scheduler runs? Show the resulting procurement document."

4. "Create a manufacturing order for 100 units of Finished Good X. The BOM has 3 components.
   One component is short by 20 units. Show the reservation status and suggest resolution."

5. "Run a cycle count for all products in Warehouse A, Zone 1. Five products show variance.
   Apply adjustments and show the inventory adjustment journal entries."

6. "Show all products with negative stock across all warehouses. Explain how each went
   negative and propose corrections."

7. "Trace serial number SN-2026-00042 from receipt through manufacturing to final customer
   delivery. Show the complete chain of stock moves."
