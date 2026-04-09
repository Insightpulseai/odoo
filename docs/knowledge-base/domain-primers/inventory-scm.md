# Domain Primer: Inventory & Supply Chain

## One-paragraph summary

Inventory management ensures the right products are available at the right place and time. Supply chain management extends this to procurement, logistics, and demand planning. In SAP, this is MM-WM (Warehouse Management), MM-IM (Inventory Management), and PP (Production Planning). Odoo CE includes robust inventory with multi-warehouse, routes, lot/serial tracking, and MRP — unusually strong for a CE product.

## Key Concepts

| Concept | Definition | Odoo Model |
|---------|-----------|------------|
| Warehouse | Physical or logical storage facility | stock.warehouse |
| Location | Specific storage area within warehouse | stock.location |
| Transfer/Picking | Movement of goods between locations | stock.picking |
| Lot/Serial | Batch or individual unit tracking | stock.lot |
| Route | Automated supply chain path | stock.route |
| BOM | Bill of materials for manufacturing | mrp.bom |

## Core Processes

- **Receipt**: Vendor → Input location → Stock (via routes)
- **Delivery**: Stock → Output location → Customer
- **Internal transfer**: Warehouse A → Warehouse B
- **Manufacturing**: Raw materials → Work center → Finished goods
- **Inventory adjustment**: Physical count vs system count reconciliation

## SAP-to-Odoo Quick Map

| SAP | Odoo |
|-----|------|
| Plant (WERKS) | stock.warehouse |
| Storage Location (LGORT) | stock.location |
| Goods Movement (MIGO) | stock.picking + stock.move |
| Batch (MSC1N) | stock.lot |
| BOM (CS01) | mrp.bom |
| MRP Run | mrp.production (auto-generated) |

## What "SAP-grade" Means Here

- Real-time inventory visibility across all locations
- Full traceability (lot/serial → receipt → customer)
- Automated replenishment via routes and reordering rules
- Multi-step picking/packing/shipping workflows
- Cycle counting and inventory valuation
