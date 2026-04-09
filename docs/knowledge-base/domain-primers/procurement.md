# Domain Primer: Procurement & Purchasing

## One-paragraph summary

Procurement controls organizational spend, ensures supply continuity, and enforces purchasing policies. Enterprise-grade procurement goes beyond simple PO creation — it includes requisition workflows, approval hierarchies, vendor evaluation, contract management, and 3-way matching. In SAP, this is MM (Materials Management). In Odoo CE + OCA, the `purchase` module plus OCA extensions like `purchase_request` and `base_tier_validation` cover most patterns.

## Key Concepts

| Concept | Definition | Odoo Model |
|---------|-----------|------------|
| Purchase requisition | Internal request before PO creation | purchase.request (OCA) |
| Purchase order | Formal order to vendor | purchase.order |
| Blanket order | Long-term agreement with call-offs | purchase.blanket.order (OCA) |
| 3-way match | PO qty = receipt qty = invoice qty | Manual in CE; OCA assists |
| Goods receipt | Physical receipt confirmation | stock.picking (incoming) |
| Vendor evaluation | Scoring vendors on performance | res.partner + custom |

## Core Process: Procure-to-Pay

```
Need identified → Purchase request → Approval → PO created → PO sent to vendor
→ Goods received (stock.picking) → Vendor bill received (account.move)
→ 3-way match verified → Payment scheduled → Payment executed
```

## SAP-to-Odoo Quick Map

| SAP | Odoo |
|-----|------|
| Purchase Requisition (BANF) | purchase.request (OCA) |
| Purchase Order (EKKO) | purchase.order |
| Goods Receipt (MIGO 101) | stock.picking validated |
| Invoice Verification (MIRO) | account.move (in_invoice) |
| Release Strategy | base_tier_validation (OCA) |
| Source List | Not native; workaround via pricelists |

## OCA Modules to Know

- `purchase_request`: Requisition workflow
- `purchase_request_tier_validation`: Multi-level approval on requests
- `purchase_blanket_order`: Framework agreements
- `purchase_order_approval_block`: Block POs pending approval
- `base_tier_validation`: Generic approval engine

## What "SAP-grade" Means Here

- No PO without approved requisition (for amounts above threshold)
- Multi-level approval based on amount, category, department
- 3-way match enforced before payment
- Vendor performance tracked and used for sourcing decisions
- Complete audit trail from request to payment
