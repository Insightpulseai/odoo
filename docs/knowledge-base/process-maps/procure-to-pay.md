# Process Map: Procure-to-Pay (P2P)

## End-to-End Flow

```
[Requestor]      [Procurement]     [Warehouse]       [Finance]
Purchase Req     Purchase Order    Goods Receipt      Vendor Bill
  │                 │                  │                  │
  ▼                 ▼                  ▼                  ▼
Request → Approve → PO → Send → Receive → 3-Way Match → Bill → Payment
  │                 │                  │                  │
purchase.request  purchase.order   stock.picking     account.move
(OCA)                                                     │
                                                    Payment Order
                                                    (OCA account_payment_order)
```

## Step Details

| Step | Odoo Model | Key Fields | Trigger |
|------|-----------|------------|---------|
| Purchase Request | purchase.request (OCA) | requested_by, line_ids | Manual |
| Approval | tier.review | status, reviewer_id | Tier validation |
| Purchase Order | purchase.order | partner_id, order_line | "Create PO" from request |
| Send to Vendor | purchase.order | state='purchase' | "Confirm Order" |
| Goods Receipt | stock.picking | move_ids, received_qty | Vendor ships goods |
| Vendor Bill | account.move (in_invoice) | invoice_line_ids | Manual entry or vendor portal |
| 3-Way Match | N/A (manual) | PO qty = receipt qty = bill qty | Finance review |
| Payment | account.payment / payment.order | amount, journal_id | Payment run |

## Variants

### Direct PO (no requisition)
```
Purchase Order → Goods Receipt → Vendor Bill → Payment
```
For low-value or pre-approved purchases.

### Blanket order with call-offs
```
Blanket Order (annual) → Call-off PO 1 → Receipt → Bill
                       → Call-off PO 2 → Receipt → Bill
```
Using OCA `purchase_blanket_order`.

### Service purchase (no receipt)
```
Purchase Request → PO → Vendor Bill → Payment
```
No stock.picking for service products; match PO directly to bill.

## Controls

| Control | Type | Implementation |
|---------|------|----------------|
| Requisition approval | Preventive | purchase_request_tier_validation (OCA) |
| PO approval | Preventive | purchase_order_approval_block (OCA) |
| Budget check | Preventive | Analytic budget validation |
| 3-way match | Detective | Manual or OCA purchase_stock_picking_invoice_link |
| Payment approval | Preventive | account_payment_order with approval workflow |
| Vendor block | Preventive | partner.purchase_blocked field |

## SoD Requirements

| Activity | Role | Cannot Also Be |
|----------|------|----------------|
| Create purchase request | Requestor | Approver |
| Approve request | Budget Owner | Requestor for same request |
| Create PO | Buyer | Goods Receiver |
| Receive goods | Warehouse Worker | Invoice Processor |
| Process vendor bill | AP Clerk | Payment Releaser |
| Release payment | Finance Manager | AP Clerk for same invoice |

## KPIs

| KPI | Measure | Source |
|-----|---------|--------|
| Requisition-to-PO time | Request date → PO date | purchase.request → purchase.order |
| On-time delivery rate | Receipts on/before scheduled date | stock.picking |
| Invoice processing time | Bill date → payment date | account.move → account.payment |
| Vendor payment accuracy | Bills matching PO terms | account.move.line |
