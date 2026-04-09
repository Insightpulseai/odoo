# Procure-to-Pay Skill Pack

> Odoo 18 CE + OCA | SAP-equivalent: MM (Materials Management) + FI-AP

---

## Scope

End-to-end procurement lifecycle: purchase requisition, request for quotation, purchase
order, goods receipt, three-way invoice matching, and payment execution. Covers approval
workflows, blanket orders, vendor management, and landed costs -- all achievable on
Odoo 18 CE with OCA modules.

---

## Concepts

| Concept | SAP Equivalent | Odoo Surface |
|---------|---------------|--------------|
| Purchase Requisition | ME51N (PR) | OCA `purchase.request` |
| Request for Quotation | ME41 (RFQ) | `purchase.order` (state=draft) |
| Purchase Order | ME21N (PO) | `purchase.order` (state=purchase) |
| Goods Receipt | MIGO (GR) | `stock.picking` (type=incoming) |
| Invoice Verification | MIRO | `account.move` (type=in_invoice) |
| Three-Way Match | GR/IR clearing | Core CE feature via Purchase Settings (`purchase_method='receive'`) |
| Blanket Order | Outline Agreement (ME31) | OCA `purchase.blanket.order` |
| Vendor Evaluation | MM Vendor Rating | No OCA equivalent — requires custom `ipai_*` module |
| Approval Workflow | Release Strategy | OCA `base_tier_validation` |
| Payment Run | F110 | OCA `account.payment.order` |

---

## Must-Know Vocabulary

- **purchase.order**: The PO model. States: draft (RFQ), sent, purchase (confirmed), done, cancel.
- **purchase.order.line**: Individual line items on a PO. Links to `product.product`.
- **purchase.request**: OCA model for internal purchase requisitions before RFQ creation.
- **purchase.request.line**: Line items on a requisition. Can generate RFQs.
- **purchase.blanket.order**: OCA framework agreement with quantity/amount limits and validity.
- **stock.picking**: Goods receipt document. Type determined by `picking_type_id`.
- **stock.move**: Individual product movement within a picking.
- **account.move**: Vendor bill for invoice matching against PO/receipt.
- **base.tier.definition**: OCA approval tier rules (amount thresholds, user groups).
- **Landed cost**: `stock.landed.cost` distributes freight/duty across received goods.

---

## Core Workflows

### 1. Purchase Requisition (OCA)
1. User creates `purchase.request` with required products, quantities, and dates.
2. Approval tier fires based on `base_tier_validation` rules (e.g., >PHP 100K needs manager).
3. Approved requisition lines are converted to RFQs via `purchase.request.line.make.purchase.order`.
4. Multiple requisitions can be consolidated into a single RFQ per vendor.

### 2. RFQ to Purchase Order
1. `purchase.order` created in draft (RFQ state).
2. Send RFQ to vendor(s) via email or portal.
3. Vendor responds with pricing. Update lines.
4. Confirm RFQ: state transitions to `purchase`. Sequence number assigned.
5. PO confirmation triggers procurement rules for stock replenishment.

### 3. Goods Receipt
1. PO confirmation auto-creates `stock.picking` (incoming type).
2. Warehouse receives goods. Validate picking: `button_validate()`.
3. Partial receipts supported: backorder created for remaining quantities.
4. Serial/lot tracking enforced if product has `tracking='serial'` or `'lot'`.
5. Receipt posts stock valuation journal entry (perpetual inventory).

### 4. Invoice Matching (Three-Way)
1. Create vendor bill `account.move` (type=in_invoice).
2. Link bill lines to PO lines via `purchase_line_id`.
3. Odoo validates: invoice qty <= received qty (if `purchase_method='receive'`).
4. Discrepancies flagged: price variance, quantity variance, tax mismatch.
5. Post bill. AP balance increases.

### 5. Payment Execution
1. Select open vendor bills for payment.
2. Via OCA `account_payment_order`: create batch payment order.
3. Payment order advances: draft -> open -> generated -> uploaded.
4. Bank file generated (SEPA/local format).
5. Payment reconciles against vendor bills automatically.

### 6. Blanket Order (OCA)
1. Create `purchase.blanket.order` with vendor, validity dates, and line items.
2. Set maximum quantity or amount per line.
3. Create call-off POs referencing the blanket order.
4. System tracks consumed vs remaining quantities.
5. Alerts on expiry or threshold breach.

---

## Edge Cases

- **Over-receipt**: Odoo allows receiving more than PO qty by default. Control via
  `stock.picking` validation rules or OCA `purchase_order_qty_change_no_reconfirmation`.
- **Price variance**: Invoice price differs from PO price. Odoo posts the difference to
  a price difference account (`property_account_creditor_price_difference`).
- **Partial delivery + partial invoice**: Each partial receipt can be independently invoiced.
  Track coverage via `purchase.order.line.qty_received` vs `qty_invoiced`.
- **Drop shipping**: PO with route `buy` + delivery to customer. `stock.picking` goes
  directly from vendor to customer location. No warehouse receipt.
- **Backdated receipts**: Posting a receipt with an earlier date affects stock valuation.
  Use `stock.move.date` carefully for period-correct costing.
- **Multi-currency PO**: Exchange rate locked at PO confirmation date. Invoice may use
  a different rate, generating exchange difference entries.
- **Cancelled PO with partial receipt**: Cannot cancel a PO if receipts exist. Must
  return goods first or reduce PO lines to received quantities.

---

## Controls & Compliance

| Control | Implementation |
|---------|---------------|
| Approval thresholds | OCA `base_tier_validation` on `purchase.order` and `purchase.request` |
| Segregation: requester != approver | Tier definition with `reviewer_ids` excluding creator |
| Three-way match | `purchase_method='receive'` on product: invoice qty capped at received qty |
| Vendor onboarding | `res.partner` with `supplier_rank > 0`. Require tax ID, bank details |
| Budget check | OCA `purchase_request_budget` or custom `ipai_*` budget validation |
| Audit trail | `mail.tracking.value` on PO fields. OCA `base_tier_validation` logs approvals |
| Duplicate invoice detection | Odoo checks `ref` (vendor bill number) uniqueness per vendor |
| Receipt confirmation | Warehouse user != procurement user (group separation) |

---

## Odoo/OCA Implementation Surfaces

### Core Odoo 18 CE Models
- `purchase.order` / `purchase.order.line` -- PO lifecycle
- `stock.picking` / `stock.move` -- goods receipt
- `account.move` / `account.move.line` -- vendor bills
- `account.payment` -- payment registration
- `product.supplierinfo` -- vendor pricelist per product
- `stock.landed.cost` -- landed cost allocation
- `stock.warehouse.orderpoint` -- reorder rules triggering procurement

### OCA Modules (18.0-compatible)
| Module | Repo | Purpose |
|--------|------|---------|
| `purchase_request` | OCA/purchase-workflow | Purchase requisitions with approval |
| `purchase_blanket_order` | OCA/purchase-workflow | Framework agreements / blanket POs |
| `purchase_order_type` | OCA/purchase-workflow | PO classification (standard, consignment, service) |
| `purchase_tier_validation` | OCA/purchase-workflow | Tier-based approval on POs |
| `base_tier_validation` | OCA/server-ux | Generic approval engine |
| `purchase_request_tier_validation` | OCA/purchase-workflow | Approval tiers on requisitions |
| `account_payment_order` | OCA/bank-payment | Batch payment processing |
| `purchase_stock_picking_return_invoicing` | OCA/stock-logistics-workflow | Invoice adjustments on returns |

---

## Azure/Platform Considerations

- **Email integration**: RFQ emails sent via Zoho SMTP (`smtp.zoho.com:587`). Configure
  `ir.mail_server` with credentials from Azure Key Vault.
- **Vendor portal**: Odoo portal allows vendors to view POs and upload invoices. Expose
  via Azure Front Door with WAF rules.
- **Document storage**: Vendor invoices (PDF) attached to `account.move`. For large volumes,
  consider Azure Blob Storage via `ir.attachment` backend override.
- **Performance**: `purchase.order.line` joins with `stock.move` and `account.move.line`
  for matching views. Index `purchase_line_id` on both tables.
- **Integration**: EDI with vendors via OCA `edi` framework or Azure Logic Apps for
  XML/cXML/EDIFACT translation.

---

## Exercises

### Exercise 1: End-to-End P2P Cycle
Create a purchase request for 100 units of Product A. Approve it. Convert to RFQ. Confirm
PO. Receive 80 units (partial). Create vendor bill for 80 units. Register payment. Verify
all document links are intact.

### Exercise 2: Three-Way Match Validation
Configure Product B with `purchase_method='receive'`. Create PO for 50 units at PHP 100.
Receive 40 units. Attempt to create a vendor bill for 50 units. Verify Odoo caps at 40.
Then receive remaining 10 and invoice the rest.

### Exercise 3: Approval Tiers
Install `base_tier_validation` and `purchase_tier_validation`. Configure:
- PO < PHP 50K: auto-approve
- PO PHP 50K-500K: manager approval
- PO > PHP 500K: director + finance approval
Test with three POs at different amounts.

### Exercise 4: Blanket Order Management
Create a blanket order for Office Supplies vendor, valid 6 months, max PHP 1M.
Create three call-off POs totaling PHP 800K. Verify remaining balance. Attempt a
fourth PO that exceeds the limit.

### Exercise 5: Landed Cost Allocation
Receive 3 products on one PO. Create a landed cost for freight (PHP 15,000) and
customs duty (PHP 8,000). Allocate by weight. Verify the updated unit cost on
each `stock.valuation.layer`.

---

## Test Prompts for Agents

1. "Create a purchase request for 200 units of Item X at estimated PHP 500/unit. Route it
   through two-tier approval. Convert approved request to a PO."

2. "We received 150 of 200 ordered units. Create a vendor bill for only the received
   quantity. Show the PO status indicating the remaining 50 are pending."

3. "Set up a blanket order with Vendor ABC for PHP 2M over 12 months. Create the first
   call-off PO for PHP 300K and show remaining blanket balance."

4. "A vendor invoice shows PHP 520/unit but the PO says PHP 500/unit. Post the bill and
   show me where the price variance is recorded in the GL."

5. "Generate a payment order for all vendor bills due this week. Group by vendor. Export
   the bank file. Show the resulting AP balance change."

6. "Show all POs with goods received but not yet invoiced (GR/IR open items). This is
   the equivalent of SAP GR/IR clearing account analysis."

7. "A shipment was rejected at receiving. Process a return to vendor and generate the
   corresponding credit note. Verify the PO line quantities update correctly."
