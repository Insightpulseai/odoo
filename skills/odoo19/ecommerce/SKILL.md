---
name: ecommerce
description: Odoo eCommerce for building and managing online stores with product catalog, checkout, shipping, and order handling
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# ecommerce -- Odoo 19.0 Skill Reference

## Overview

Odoo eCommerce is an open-source online store platform integrated with the Odoo Website builder. It provides end-to-end tools for configuring products, managing categories and variants, customizing catalog and product page design, handling ordering and checkout flows, setting up delivery methods (including Click & Collect), processing orders from sale through delivery and invoicing, managing pricing with pricelists and discounts, and analyzing store performance. It supports both B2B and B2C business models with per-website configuration.

## Key Concepts

- **Product (eCommerce)**: A sellable item published on the website shop. Created from frontend (`+New > Product`) or backend (`Website > eCommerce > Products`). Supports images, videos, descriptions, digital files, cross-selling, upselling, combos, and stock management.
- **Product Visibility**: Controlled via `Is Published` toggle. Multi-website availability set via `Website` field on the Sales tab (blank = all websites, specific = one website only).
- **Categories**: Hierarchical groupings displayed on the shop page for filtering products.
- **Variants**: Product variations (size, color, etc.) configured via product attributes.
- **Pricelists**: Flexible pricing rules based on currency, time period, volume, customer location (GeoIP), or customer type. Each pricelist can be assigned to one website. Selectable pricelists appear in the catalog toolbar.
- **Country Groups**: Groups of countries assigned to pricelists for GeoIP-based pricing.
- **Promotional Code**: E-commerce-specific discount code attached to a pricelist.
- **Comparison Price**: Strikethrough original price displayed alongside a discounted sales price.
- **Customer Accounts**: Portal accounts that control shop access, checkout behavior, and document visibility. Options: `On invitation` or `Free sign up`.
- **B2B / B2C**: Configurable per-website. B2B typically uses tax-excluded prices, invitation-only access, and hidden pricing. B2C uses tax-included prices and guest checkout.
- **Checkout Steps**: Order Summary > Address & Delivery > Extra Info (optional) > Payment > Order Confirmation.
- **Add to Cart Behavior**: Configurable: `Stay on Product Page` or `Go to cart`.
- **Buy Now**: Optional button that skips directly to the Order Summary step.
- **Click & Collect**: In-store pickup option. Customers reserve online and collect at a configured warehouse.
- **Express Checkout**: Payment provider feature allowing customers to skip the address form.
- **Abandoned Cart**: Automatic email reminders for incomplete checkouts.
- **Cross-selling**: Optional products (at Add to Cart), accessory products (at Order Summary), alternative products (on product page).
- **Product Combos**: Bundle configurations where customers choose from a set of related products.
- **Digital Files**: Downloadable documents (certificates, eBooks, etc.) attached to products, available on the product page or in the customer portal after purchase.
- **Delivery Methods**: External providers (FedEx, UPS, DHL), custom methods (Fixed Price, Based on Rules, Sendcloud), and Pick up in store.
- **Automatic Invoice**: Setting that auto-generates and sends invoices upon payment confirmation.
- **Order Handling Lifecycle**: Quotation (cart) > Quotation Sent (checkout completed, payment pending) > Sales Order (payment received) > Delivery Order > Invoice.

## Core Workflows

### 1. Create and Publish a Product

1. Go to Website app, click `+New` > `Product`.
2. Enter Product Name, Barcode, Sales Price, Sales Taxes, Website Category, and an image.
3. Click `Save` -- redirected to product page for frontend customization.
4. Click `Product` in top-right to access backend product form for advanced configuration.
5. Add ecommerce description in `Sales` tab > `Ecommerce description` section.
6. Add media in `Sales` tab > `Ecommerce Media` > `Add Media`.
7. Configure optional/accessory/alternative products in `Sales` tab for cross-selling.
8. Toggle `Unpublished` to `Published` on the product's website page.

### 2. Configure Pricing and Pricelists

1. Go to `Website > Configuration > Settings`, enable `Pricelists` in the eCommerce section.
2. Go to `Website > eCommerce > Pricelists`, click `New`.
3. Configure pricing rules in the `Sales Price` tab (percentage, formula, or fixed).
4. In the `Ecommerce` tab, assign a `Website`, enable `Selectable` if it should appear in the catalog selector, and optionally add a `Promotional Code`.
5. Assign `Country Groups` for GeoIP-based automatic pricelist selection.
6. For discounted prices, enable `Comparison Price` in settings and set `Compare to Price` on the product form.

### 3. Process an Order (Sale to Invoice)

1. Customer adds product to cart, completes checkout, and pays.
2. Sales order created automatically in `Website > eCommerce > Orders` (status: Sales Order).
3. Delivery order auto-created -- click `Delivery` smart button on the sales order.
4. Process warehouse operations (pick, pack, ship). Click `Validate` when shipped.
5. Invoice: auto-generated if `Automatic Invoice` is enabled, or manually created from the sales order.
6. Customer views orders and invoices in the customer portal.

### 4. Set Up Delivery Methods

1. Go to `Website > Configuration > Settings > Delivery` section.
2. Enable desired third-party providers (FedEx, UPS, DHL, etc.) and `Save`.
3. Go to `Website > Configuration > Delivery Methods`, select or create a method.
4. Set `Provider` (Fixed Price, Based on Rules, or a shipping connector).
5. Configure `Availability` tab for destination/content conditions.
6. Switch from `Test Environment` to `Production Environment`, then publish.
7. For Click & Collect: enable in settings, configure `Pick up in store` provider, add warehouses in `Stores` tab.

### 5. Configure Customer Accounts and B2B

1. Go to `Website > Configuration > Settings > General`.
2. Set `Customer Account` to `On invitation` (B2B) or `Free sign up` (B2C).
3. Set `Ecommerce Access`: `All users` (public) or `Logged in users` (restricted).
4. Set `Sign in/up at checkout`: `Optional`, `Disabled`, or `Mandatory`.
5. For B2B: set `Display Product Prices` to `Tax Excluded`, hide prices via `Prevent Sale of Zero Priced Product`, create a zero-priced pricelist.
6. Enable `Shared Customer Accounts` for multi-website account sharing.
7. Grant portal access: `Website > eCommerce > Customers`, select customer, `Actions > Grant portal access`.

## Technical Reference

### Models

| Model | Description |
|-------|-------------|
| `product.template` | Product template (backend product form) |
| `product.product` | Product variant |
| `product.public.category` | eCommerce website category |
| `product.pricelist` | Pricelist configuration |
| `sale.order` | Sales order (quotation/confirmed order) |
| `sale.order.line` | Sales order line |
| `stock.picking` | Delivery order |
| `account.move` | Invoice |
| `delivery.carrier` | Delivery method |

### Key Fields (Product - Sales Tab)

- `is_published`: Published on website
- `website_id`: Website restriction (blank = all)
- `sale_ok`: Can be sold
- `optional_product_ids`: Optional products (cross-selling at Add to Cart)
- `accessory_product_ids`: Accessory products (cross-selling at Order Summary)
- `alternative_product_ids`: Alternative products (upselling on product page)
- `compare_list_price`: Compare-to price (strikethrough)
- `website_description`: eCommerce HTML description
- `product_variant_ids`: Product variants

### Key Settings (`Website > Configuration > Settings > eCommerce`)

| Setting | Description |
|---------|-------------|
| `Add to Cart` | Stay on Product Page / Go to cart |
| `Display Product Prices` | Tax Excluded / Tax Included |
| `Pricelists` | Enable flexible pricing |
| `Comparison Price` | Enable strikethrough pricing |
| `Product Reference Price` | Display price per unit |
| `Discounts, Loyalty & Gift Card` | Enable discount programs, eWallets, gift cards |
| `Prevent Sale of Zero Priced Product` | Hide prices, show Contact Us button |
| `Automatic Invoice` | Auto-generate invoice on payment |
| `Follow up abandoned carts` | Send reminders for incomplete checkouts |
| `Newsletter` | Add newsletter signup at checkout |
| `Click & Collect` | In-store pickup |
| `Orders Assignment` | Default Sales Team / Salesperson |
| `Customer Account` | On invitation / Free sign up |
| `Ecommerce Access` | All users / Logged in users |
| `Sign in/up at checkout` | Optional / Disabled / Mandatory |

### System Parameters

| Key | Purpose |
|-----|---------|
| `sale.async_emails` | Set to `True` for asynchronous email sending (high-traffic sites) |

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

- Product creation from frontend includes Barcode, Sales Taxes, and Website Category fields directly in the creation dialog.
- Product combos available for bundle configurations (shared with Point of Sale).
- AI-powered ecommerce description generation via `/` command in the rich text editor.
- `Get notified when back in stock` button auto-appears on out-of-stock product pages.
- Click & Collect with per-warehouse stock availability display.
- Express checkout support for compatible payment providers.
- Quick reorder available from the cart (Order Summary step).
- `Order Again` button in customer portal for reordering from previous orders.
- B2B fields toggle (`Show B2B Fields`) in website editor for VAT and Company Name at checkout.
- Google Merchant Center integration for multi-channel product syndication (Google, TikTok, Facebook, Instagram).
- Asynchronous email sending via `sale.async_emails` system parameter for flash sale performance.

## Common Pitfalls

- **Pricelist per website**: Each pricelist can only be assigned to one website. Duplicate pricelists for use on multiple websites.
- **Product multi-website availability**: Products can be on one website or all websites, but not a subset. Duplicate products for selective multi-website availability.
- **Country groups and selectable pricelists conflict**: When using GeoIP-based country groups, disable `Selectable` on pricelists to prevent non-country-group pricelists from overriding the automatic selection.
- **Wire transfer orders**: Orders paid via wire transfer are not auto-confirmed. The sales order must be manually confirmed after payment receipt, and products are not reserved in stock until confirmation.
- **Compare to Price hidden by pricelists**: The `Compare to Price` strikethrough is not displayed if discounted pricelists apply. Use a promotional code pricelist instead.
