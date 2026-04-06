# Order-to-Cash Skill Pack

> Odoo 18 CE + OCA | SAP-equivalent: SD (Sales & Distribution) + FI-AR

---

## Scope

Complete sales lifecycle: quotation, sales order confirmation, delivery (picking, packing,
shipping), customer invoicing, payment collection, and credit management. Covers pricing,
discounts, customer portal, and returns -- all on Odoo 18 CE with OCA modules.

---

## Concepts

| Concept | SAP Equivalent | Odoo Surface |
|---------|---------------|--------------|
| Quotation | VA21 (Inquiry/Quotation) | `sale.order` (state=draft) |
| Sales Order | VA01 (SO) | `sale.order` (state=sale) |
| Delivery Note | VL01N (Outbound Delivery) | `stock.picking` (type=outgoing) |
| Customer Invoice | VF01 (Billing) | `account.move` (type=out_invoice) |
| Credit Note | VF01 (Credit Memo) | `account.move` (type=out_refund) |
| Payment | F-28 (Incoming Payment) | `account.payment` |
| Pricing Condition | VK11 (Pricing) | `product.pricelist` |
| Sales Order Type | Order Type (TA/OR) | OCA `sale.order.type` |
| Credit Block | VKM1 (Credit Mgmt) | OCA `sale_tier_validation` + credit limit |
| Returns | VL01N (Returns) | `stock.picking` (return type) + `sale.order` RMA |

---

## Must-Know Vocabulary

- **sale.order**: The sales order model. States: draft (quotation), sent, sale (confirmed),
  done, cancel. Quotation becomes SO on confirmation.
- **sale.order.line**: Line items linking to `product.product` with qty, price, tax.
- **sale.order.type**: OCA model to classify orders (standard, sample, consignment, return).
  Drives default journal, warehouse, invoice policy.
- **stock.picking**: Delivery order. Auto-created on SO confirmation based on procurement rules.
- **account.move**: Invoice generated from SO. `invoice_origin` field links back to SO number.
- **product.pricelist**: Multi-level pricing engine. Rules based on quantity, date, partner.
- **sale.advance.payment.inv**: Wizard for creating invoices from SO (delivered qty or full).
- **crm.lead**: If CRM installed, quotations can originate from pipeline opportunities.
- **payment.provider**: Online payment configuration for customer portal payments.

---

## Core Workflows

### 1. Quotation to Sales Order
1. Create `sale.order` in draft (quotation) state.
2. Add lines with products, quantities, unit prices.
3. Apply pricelist rules via `pricelist_id` on the order.
4. Send quotation to customer (email or portal link).
5. Customer confirms via portal or salesperson confirms manually.
6. State changes to `sale`. Procurement triggers (delivery order created).

### 2. Delivery (Pick-Pack-Ship)
1. SO confirmation creates `stock.picking` for outgoing delivery.
2. **Pick**: Assign stock (`action_assign()`). Reserve available quantities.
3. **Pack**: If multi-step delivery configured, intermediate picking for packing.
4. **Ship**: Validate final picking. `button_validate()` confirms shipment.
5. Partial delivery creates a backorder for remaining quantities.
6. Tracking number added to picking for customer notification.

### 3. Invoicing
1. Invoice policy on product: `order` (invoice on confirmation) or `delivery` (invoice on ship).
2. Create invoice via `sale.advance.payment.inv` wizard or `_create_invoices()` method.
3. Invoice lines auto-populated from SO lines (respecting delivered quantities if policy=delivery).
4. Post invoice: `action_post()`. AR balance increases.
5. Send invoice to customer via email/portal.

### 4. Payment Collection
1. Customer pays via bank transfer, check, or online payment.
2. Record payment: `account.payment` with `partner_type='customer'`.
3. Payment auto-reconciles against open invoice.
4. For online payments: `payment.provider` (Stripe, PayPal, etc.) handles flow.
5. Partial payments create `account.partial.reconcile`.

### 5. Returns and Credit Notes
1. Customer returns goods: create return picking from original delivery.
2. Return picking validated. Stock moves back to warehouse.
3. Create credit note from original invoice or as standalone.
4. Credit note reconciles against original invoice balance.
5. Refund payment if applicable.

### 6. Pricelist Management
1. Create `product.pricelist` with currency and rules.
2. Rule types: fixed price, percentage discount, formula (cost + margin).
3. Rules can be product-specific, category-specific, or global.
4. Date validity on rules for promotional pricing.
5. Assign pricelist to partner or use on specific SO.

---

## Edge Cases

- **Invoiced before delivered**: If policy is `order`, invoice is created at SO confirmation.
  If delivery fails, credit note must be issued manually.
- **Partial delivery + partial invoice**: Each delivery can be independently invoiced.
  Track via `sale.order.line.qty_delivered` vs `qty_invoiced`.
- **Over-delivery**: Odoo allows delivery of more than ordered qty. The invoice reflects
  `qty_delivered`, which may exceed `product_uom_qty`.
- **Backorder cancellation**: Cancelling a backorder does not cancel the SO. The SO remains
  partially delivered. Manual reconciliation needed.
- **Multi-warehouse delivery**: SO lines can source from different warehouses via routes.
  Creates separate pickings per warehouse.
- **Down payment**: Use `sale.advance.payment.inv` with `advance_payment_method='percentage'`
  or `'fixed'`. Creates a deposit invoice. Final invoice deducts the deposit.
- **Kit products**: BOM type `phantom`. SO line shows the kit; delivery shows components.
  Invoice shows the kit product, not components.

---

## Controls & Compliance

| Control | Implementation |
|---------|---------------|
| Sales order approval | OCA `sale_tier_validation` for amount-based approval |
| Credit limit check | `res.partner.credit_limit` field. Custom or OCA check before SO confirm |
| Pricing authorization | Pricelist rules with min margins. Discount limits per user group |
| Segregation of duties | Separate groups: Sales/Quotation, Stock/Delivery, Invoicing |
| Sequential numbering | SO sequence and invoice sequence must be gap-free (legal) |
| Revenue recognition | Invoice on delivery policy ensures revenue matches shipment |
| Customer portal access | Portal users see only their own orders, invoices, deliveries |
| Return authorization | Return picking requires validation. OCA RMA modules for formal process |

---

## Odoo/OCA Implementation Surfaces

### Core Odoo 18 CE Models
- `sale.order` / `sale.order.line` -- sales order lifecycle
- `stock.picking` / `stock.move` -- delivery management
- `account.move` / `account.move.line` -- customer invoices and credit notes
- `account.payment` -- payment collection
- `product.pricelist` / `product.pricelist.item` -- pricing engine
- `product.product` / `product.template` -- product master
- `res.partner` -- customer master with credit limit, pricelist assignment
- `sale.advance.payment.inv` -- invoice creation wizard
- `crm.lead` -- opportunity-to-quote flow (if CRM installed)

### OCA Modules (18.0-compatible)
| Module | Repo | Purpose |
|--------|------|---------|
| `sale_order_type` | OCA/sale-workflow | Order type classification with defaults |
| `sale_tier_validation` | OCA/sale-workflow | Approval tiers on sales orders |
| `base_tier_validation` | OCA/server-ux | Generic approval engine (dependency) |
| `sale_order_line_price_history` | OCA/sale-workflow | Historical price lookup per customer/product |
| `sale_blanket_order` | OCA/sale-workflow | Framework agreements on sales side |
| `sale_order_revision` | OCA/sale-workflow | Quotation versioning (rev A, rev B, ...) |
| `sale_stock_picking_back_order` | OCA/sale-workflow | Enhanced backorder handling |
| `sale_order_general_discount` | OCA/sale-workflow | Header-level discount application |
| `account_payment_order` | OCA/bank-payment | Batch collection orders (direct debit) |

---

## Azure/Platform Considerations

- **Customer portal**: Odoo portal served via Azure Front Door. Enable HTTPS, WAF, and
  rate limiting on `/my/orders`, `/my/invoices` endpoints.
- **Email delivery**: Order confirmations and invoices sent via Zoho SMTP. Monitor
  delivery rates in `mail.mail` failed queue.
- **Online payments**: If using payment providers (Stripe), webhook endpoints must be
  reachable through Azure Front Door. Whitelist provider IPs.
- **Performance**: `sale.order.line` joined with `stock.move` and `account.move.line`
  for status dashboards. Composite index on `(order_id, product_id)`.
- **Reporting**: Sales reports (`sale.report`) are SQL views. For cross-system analytics,
  extract via Databricks JDBC to lakehouse.
- **PDF generation**: Invoice PDFs rendered by Odoo wkhtmltopdf. Ensure container has
  the binary installed and fonts available.

---

## Exercises

### Exercise 1: Full O2C Cycle
Create a quotation for Customer A with 3 line items. Confirm as SO. Process delivery
(full shipment). Create and post invoice. Register payment. Verify all documents are
linked and customer balance is zero.

### Exercise 2: Partial Delivery and Invoicing
Create SO for 100 units. Deliver 60 units (backorder for 40). Invoice the 60 delivered.
Deliver remaining 40. Invoice the rest. Verify two invoices link to the same SO.

### Exercise 3: Down Payment Flow
Create SO for PHP 500,000. Generate a 20% down payment invoice (PHP 100,000). Collect
payment. Later, deliver goods and create final invoice. Verify the final invoice shows
PHP 500,000 minus PHP 100,000 deposit = PHP 400,000 due.

### Exercise 4: Pricelist Configuration
Create a pricelist "Wholesale" with: 10% discount on all products, 15% on Category A,
fixed price PHP 250 for Product X. Assign to a partner. Create a quotation and verify
each rule applies correctly.

### Exercise 5: Return and Credit Note
From a delivered SO, create a return picking for 10 of 50 units. Validate the return.
Create a credit note for the returned items. Verify stock levels and AR balance adjust.

---

## Test Prompts for Agents

1. "Create a sales quotation for 3 products with the Wholesale pricelist. Send it to
   the customer via portal. Show me the portal URL."

2. "We shipped 200 of 300 ordered units. Create an invoice for only the shipped quantity.
   Show the SO status with remaining to deliver and invoice."

3. "Customer wants a 20% down payment on a PHP 1.2M order. Generate the deposit invoice,
   collect payment, then process the final invoice after delivery."

4. "Set up order types: Standard (invoice on delivery, main warehouse), Sample (no invoice,
   sample warehouse), and Consignment. Create one SO of each type."

5. "Customer returned 15 units from SO-00042. Process the return, create credit note,
   and reconcile against the original invoice. Show the net AR balance."

6. "Configure a two-tier approval: SO < PHP 200K auto-approved, SO >= PHP 200K requires
   sales manager approval. Test with two quotations at PHP 150K and PHP 350K."

7. "Generate a monthly sales report grouped by product category and salesperson for Q1
   2026. Show revenue, COGS (from delivery valuation), and gross margin."
