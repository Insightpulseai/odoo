---
name: manufacturing
description: Manufacturing resource planning (MRP) for production orders, bills of materials, work centers, and shop floor control.
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# Manufacturing — Odoo 19.0 Skill Reference

## Overview

Odoo Manufacturing (MRP) enables manufacturers to schedule, plan, and process manufacturing orders. It supports bills of materials (BoMs) with components and operations, work center management, multi-step manufacturing flows, subcontracting workflows, the Shop Floor module for real-time production control, and reporting on OEE, production analysis, and delays. Used by production planners, shop floor operators, manufacturing engineers, and operations managers.

## Key Concepts

- **Manufacturing Order (MO)**: A production order to manufacture a specific quantity of a product using a BoM. States: Draft, Confirmed, In Progress, To Close, Done.
- **Bill of Materials (BoM)**: Blueprint listing components, quantities, and optionally operations/instructions needed to produce or repair a product.
- **BoM Type**: `Manufacture this Product` (standard), `Kit` (auto-explodes into components on SO/DO), `Subcontracting` (produced by third-party).
- **Component**: A product listed in a BoM that is consumed during manufacturing.
- **Operation**: A step in the production process, performed at a specific work center, with defined duration and instructions.
- **Work Order**: An individual task within an MO, corresponding to a BoM operation. Processed at a work center.
- **Work Center**: Physical location where operations are performed. Tracks costs, capacity, OEE, and scheduling.
- **Shop Floor**: Companion module providing a visual tablet interface for processing MOs and work orders on the factory floor.
- **By-Product**: A residual product created during production in addition to the main product.
- **Sub-Assembly**: A component that is itself manufactured via its own BoM, enabling multi-level BoMs.
- **Kit**: A BoM type that does not create an MO; instead, components are picked directly on the SO delivery.
- **Flexible Consumption**: Controls whether component quantities can deviate from BoM specification — `Blocked`, `Allowed`, `Allowed with Warning`.
- **Manufacturing Readiness**: Determines when an MO shows as ready — when all components are available, or when only first-operation components are available.
- **Component Status**: Visual indicator (green/red) on MO showing availability of required components.
- **Subcontracting**: Third-party manufacturer produces goods on behalf of the company. Three workflows: Basic, Resupply Subcontractor, Dropship to Subcontractor.
- **Master Production Schedule (MPS)**: Dashboard for manual long-term replenishment based on sales forecasts.
- **OEE (Overall Equipment Effectiveness)**: Metric measuring work center productivity based on availability, performance, and quality.
- **Unbuild Order**: Reverses a manufacturing process, returning finished goods back to components.
- **Manufacturing Backorder**: Created when an MO is partially completed, leaving remaining quantity in a new MO.

## Core Workflows

### 1. Create and Process a Manufacturing Order

1. Navigate to `Manufacturing > Operations > Manufacturing Orders`, click `New`.
2. Select the product (must have a BoM of type `Manufacture this Product`).
3. Set quantity and scheduled date. Click `Confirm`.
4. Odoo reserves components. Component Status shows availability.
5. If work orders are defined, process each via `Work Orders` tab or Shop Floor module.
6. Click `Produce All` or register production quantities manually.
7. Click `Validate` (or `Mark as Done`) to close the MO.

### 2. Configure a Bill of Materials

1. Go to `Manufacturing > Products > Bills of Materials`, click `New`.
2. Select the product. Set `BoM Type` to `Manufacture this Product`.
3. In the `Components` tab, add component products and quantities via `Add a line`.
4. (Optional) In the `Operations` tab, add operations specifying work center, duration, and instructions. Requires `Work Orders` setting enabled.
5. (Optional) Configure the `Miscellaneous` tab: Flexible Consumption, Manufacturing Readiness, Manufacturing Lead Time, Routing.
6. (Optional) Add by-products in the `By-products` tab (requires By-Products setting).

### 3. Multi-Step Manufacturing (2 or 3 Steps)

1. Go to `Inventory > Configuration > Warehouses`, select the warehouse.
2. Set `Manufacture` to 2-step (`Pick components then Manufacture`) or 3-step (`Pick components, Manufacture, then Store`).
3. Confirming an MO now generates a picking operation for components before manufacturing starts.

### 4. Process Work Orders via Shop Floor

1. Open the `Shop Floor` module from the Odoo dashboard.
2. Select a work center page or view `All` MOs.
3. Click on a work order card to start. An operator signs in via the operator panel.
4. Complete each step by clicking the step line or ticking the checkbox.
5. Register production quantity via the `Register Production` line.
6. Click `Mark as Done` (if more work orders remain) or `Close Production` (if final).

### 5. Subcontracting (Basic)

1. Enable Subcontracting in `Manufacturing > Configuration > Settings > Operations`.
2. Create a BoM with `BoM Type` = `Subcontracting`. Specify the subcontractor.
3. Create a Purchase Order for the subcontracted product from the subcontractor vendor.
4. Upon receipt, Odoo auto-creates and closes a subcontracting MO.

## Technical Reference

### Key Models

| Model | Description |
|-------|-------------|
| `mrp.production` | Manufacturing Order |
| `mrp.bom` | Bill of Materials |
| `mrp.bom.line` | BoM component line |
| `mrp.routing.workcenter` | BoM operation (work order template) |
| `mrp.workcenter` | Work center definition |
| `mrp.workcenter.productivity` | Work center productivity/time tracking |
| `mrp.workorder` | Work order (instance of an operation in an MO) |
| `mrp.unbuild` | Unbuild order |
| `mrp.production.backorder` | Manufacturing backorder |
| `stock.picking` | Component picking (for multi-step manufacturing) |

### Key Fields

- `mrp.bom.type`: `'normal'` (Manufacture), `'phantom'` (Kit), `'subcontract'` (Subcontracting)
- `mrp.bom.consumption`: `'flexible'`, `'warning'`, `'strict'` (Flexible Consumption setting)
- `mrp.bom.ready_to_produce`: `'all_available'`, `'asap'` (Manufacturing Readiness)
- `mrp.production.state`: `'draft'`, `'confirmed'`, `'progress'`, `'to_close'`, `'done'`, `'cancel'`
- `mrp.production.product_qty` / `qty_producing`: Planned vs. actual produced quantity
- `mrp.workcenter.time_efficiency`: Multiplier for operation duration calculation
- `mrp.workcenter.costs_hour`: Hourly cost of the work center
- `mrp.bom.produce_delay`: Manufacturing lead time (days)
- `mrp.bom.days_to_prepare_mo`: Days to prepare (replenish components/sub-assemblies)

### Key Settings

- `mrp.group_mrp_routings` — Work Orders (enables Operations tab on BoMs, work centers)
- `mrp.group_mrp_byproducts` — By-Products
- `mrp.group_mrp_subcontracting` — Subcontracting

### Important XML IDs

- `mrp.mrp_production_action` — Manufacturing Orders action
- `mrp.mrp_bom_form_view` — BoM form view
- `mrp.mrp_workcenter_action` — Work Centers action
- `stock.route_warehouse0_manufacture` — Manufacture route

## API / RPC Patterns

<!-- TODO: not found in docs — Odoo 19 manufacturing docs do not cover JSON-RPC or XML-RPC examples directly. -->

Standard ORM methods apply:

```python
# Create and confirm a Manufacturing Order
mo_vals = {
    'product_id': product.id,
    'product_qty': 10.0,
    'bom_id': bom.id,
    'product_uom_id': product.uom_id.id,
}
mo = env['mrp.production'].create(mo_vals)
mo.action_confirm()
# Set quantity producing and validate
mo.qty_producing = 10.0
mo.button_mark_done()
```

## Version Notes (19.0)

- **Shop Floor module** replaces the legacy tablet view from earlier versions (available since 16.4, refined in 19.0).
- **Inventory valuation for manufactured products** follows the new 19.0 valuation model: journal entries at invoice level, not per stock move. See Inventory SKILL.md for details.
- **Product type changes**: The old `Storable Product` / `Consumable` distinction is replaced by `Goods` with a `Track Inventory` checkbox.

<!-- TODO: specific breaking model/field changes between 18.0 and 19.0 not documented in RST source -->

## Common Pitfalls

- **Work Orders require the setting to be enabled**: The `Operations` tab on BoMs and work center scheduling only appear after enabling `Work Orders` in `Manufacturing > Configuration > Settings > Operations`.
- **Kit BoMs do not generate MOs**: A BoM with type `Kit` explodes components directly onto the delivery order. No manufacturing order is created.
- **MPS should not be used with reordering rules**: The Master Production Schedule is a manual tool; combining it with automated reordering rules causes conflicting procurement signals.
- **Subcontracting BoM must specify the subcontractor**: The `Subcontractors` field on the BoM form must list the vendor. Without it, Odoo does not recognize the product as subcontracted.
- **Flexible Consumption = Blocked prevents quantity deviations**: If set to `Blocked`, operators cannot consume more or fewer components than the BoM specifies, which can block production if exact quantities are unavailable.
