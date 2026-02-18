---
name: barcode
description: Barcode scanning for inventory operations, product identification, and warehouse transfers.
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# Barcode — Odoo 19.0 Skill Reference

## Overview

Odoo Barcode allows users to assign barcodes to products, product packagings, and locations, then use barcode scanners (or mobile devices) to streamline inventory operations. Scanning triggers receipts, deliveries, internal transfers, and inventory adjustments. The module supports Default (UPC/EAN) and GS1 nomenclatures, RFID scanning, and integrates with the Inventory app for warehouse operations. Used by warehouse operators, shipping/receiving clerks, and inventory managers.

## Key Concepts

- **Barcode Nomenclature**: Rules that define how barcodes are recognized and categorized. Odoo supports two nomenclatures: `Default Nomenclature` (UPC/EAN) and `Default GS1 Nomenclature`.
- **Default Nomenclature**: Uses UPC-A, EAN-8, and EAN-13 encoding. Barcodes are matched to the first rule with a matching pattern.
- **GS1 Nomenclature**: Consolidates product and supply chain data (GTIN, lot, quantity, expiry date) into a single barcode using Application Identifiers (AIs).
- **GTIN (Global Trade Item Number)**: Unique product identifier purchased from GS1 for global supply chain use.
- **Barcode Pattern**: Regular expression defining how character sequences encode information (e.g., `21.....{NNDDD}` for weighted products with 3 decimal places).
- **Barcode Rule**: A named rule with sequence, type (Product, Lot, Location, Package, etc.), encoding, and pattern.
- **UPC/EAN Conversion**: Odoo can auto-convert between UPC-A and EAN-13 formats when matching rules.
- **Barcode Lookup**: Setting (`Stock Barcode Database`) that auto-fetches product info from barcodelookup.com for UPC/EAN/ISBN barcodes.
- **Operation Type (Barcode context)**: Configures which barcode operations are available (Receipts, Deliveries, Internal Transfers, etc.) and whether scanning is enabled.
- **RFID**: Radio-Frequency Identification support for hands-free scanning of tags and EPCs (Electronic Product Codes).

## Core Workflows

### 1. Process a Receipt via Barcode Scanning

1. Open `Barcode` app, tap `Operations`, then `Receipts`.
2. Select an existing receipt or tap `New`.
3. Scan product barcodes to add/increment product lines.
4. For lot-tracked products, scan the lot barcode after the product barcode.
5. Scan the destination location barcode if using multi-location.
6. Tap `Validate` to confirm the receipt.

### 2. Process a Delivery via Barcode Scanning

1. Open `Barcode` app, tap `Operations`, then `Delivery Orders`.
2. Select an existing delivery order.
3. Scan product barcodes to confirm quantities for picking.
4. For serialized products, scan each serial number.
5. Tap `Validate` to confirm the delivery.

### 3. Perform Inventory Adjustment via Barcode

1. Open `Barcode` app, tap `Operations`, then `Internal Transfers` or create a new adjustment.
2. Scan the location barcode to set the counting location.
3. Scan each product barcode to register quantities.
4. Tap `Apply` to confirm the adjustment.

### 4. Create a Transfer from Scratch

1. Open `Barcode` app, tap `Operations`, select an operation type.
2. Tap `New` to create a blank transfer.
3. Scan source location, then product barcodes, then destination location.
4. Tap `Validate` to complete.

### 5. Set Up GS1 Barcode Nomenclature

1. Go to `Inventory > Configuration > Settings > Barcode`.
2. Enable `Barcode Scanner`.
3. Set `Barcode Nomenclature` to `Default GS1 Nomenclature`.
4. Click the arrow icon to view/edit GS1 rules.
5. Ensure products have valid GTINs assigned in the `Barcode` field on the product form.

## Technical Reference

### Key Models

| Model | Description |
|-------|-------------|
| `barcode.nomenclature` | Barcode nomenclature definition |
| `barcode.rule` | Individual barcode rule within a nomenclature |
| `stock.picking` | Transfer (receipt, delivery, internal) processed via barcode |
| `stock.move.line` | Detailed move line (scanned lot/serial/package info) |
| `product.product` | Product with `barcode` field |
| `stock.location` | Location with `barcode` field |
| `stock.quant.package` | Package with barcode |

### Key Fields

- `product.product.barcode`: Product barcode string (any format)
- `stock.location.barcode`: Location barcode
- `barcode.nomenclature.is_gs1_nomenclature`: Boolean flag for GS1 mode
- `barcode.nomenclature.upc_ean_conv`: UPC/EAN conversion mode (`always`, `never`, `ean2upc`, `upc2ean`)
- `barcode.rule.name`: Rule name
- `barcode.rule.sequence`: Priority (lower = higher priority)
- `barcode.rule.type`: `'product'`, `'lot'`, `'location'`, `'package'`, `'weight'`, `'price'`, `'client'`, `'cashier'`, `'coupon'`, `'credit_card'`
- `barcode.rule.encoding`: `'ean13'`, `'ean8'`, `'upca'`, `'gs1_28'`, `'any'`
- `barcode.rule.pattern`: Regex pattern for matching

### Default Nomenclature Rules

| Rule Name | Type | Encoding | Pattern |
|-----------|------|----------|---------|
| Price Barcodes 2 Decimals | Priced Product | EAN-13 | `23.....{NNNDD}` |
| Discount Barcodes | Discounted Product | Any | `22{NN}` |
| Weight Barcodes 3 Decimals | Weighted Product | EAN-13 | `21.....{NNDDD}` |
| Customer Barcodes | Client | Any | `042` |
| Coupon & Gift Card | Coupon | Any | `043\|044` |
| Cashier Barcodes | Cashier | Any | `041` |
| Location barcodes | Location | Any | `414` |
| Package barcodes | Package | Any | `PACK` |
| Lot barcodes | Lot | Any | `10` |
| Product Barcodes | Unit Product | Any | `.*` |

### Key Settings

- `stock.group_stock_tracking_lot` — Lots & Serial Numbers (required for lot barcode scanning)
- Barcode Scanner setting in `Inventory > Configuration > Settings > Barcode`
- `Stock Barcode Database` — Barcode lookup auto-fetch

### Important XML IDs

- `barcodes.default_barcode_nomenclature` — Default Nomenclature
- `barcodes_gs1_nomenclature.default_gs1_nomenclature` — Default GS1 Nomenclature

## API / RPC Patterns

<!-- TODO: not found in docs — Odoo 19 barcode docs do not cover JSON-RPC or XML-RPC examples directly. -->

## Version Notes (19.0)

- **RFID support**: Scan RFID tags and retrieve EPCs for product identification.
- **Barcode Lookup integration**: Auto-creates product records from UPC/EAN/ISBN using the barcodelookup.com database.

<!-- TODO: specific breaking changes between 18.0 and 19.0 not documented in barcode RST source -->

## Common Pitfalls

- **Barcode matched to wrong rule**: Barcodes are matched to the **first** rule with a matching pattern (by sequence). If a generic `.*` pattern has a low sequence number, it catches everything before more specific rules.
- **Product variants need individual barcodes**: Barcodes must be set on product variants, not the product template, for scanning to correctly identify variants.
- **GS1 requires purchased GTINs**: GS1 barcodes using real GTINs must be purchased from GS1. Internal-only barcodes can use custom patterns.
- **New barcode rules do not auto-populate Odoo fields**: Custom rules are recognized but do not automatically fill Odoo data fields without custom development.
- **Location barcodes require Storage Locations feature**: The ability to scan location barcodes is only available when `Storage Locations` is enabled in Inventory settings.
