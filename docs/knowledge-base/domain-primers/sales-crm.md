# Domain Primer: Sales & CRM

## One-paragraph summary

Sales & CRM covers the revenue side of the business — from lead generation through opportunity management, quotation, order fulfillment, and customer relationship management. In SAP, this spans CRM and SD (Sales & Distribution). Odoo CE provides strong native CRM and sales capabilities that cover most SMB and mid-market needs. OCA modules add approval workflows, order classification, and enhanced pipeline management.

## Key Concepts

| Concept | Definition | Odoo Model |
|---------|-----------|------------|
| Lead/Opportunity | Potential sale being tracked | crm.lead |
| Sales team | Revenue accountability unit | crm.team |
| Quotation | Draft sales order (offer to customer) | sale.order (draft state) |
| Sales order | Confirmed customer order | sale.order (sale state) |
| Delivery | Physical shipment of goods | stock.picking (outgoing) |
| Customer invoice | Bill to customer | account.move (out_invoice) |

## Core Process: Order-to-Cash

```
Lead → Opportunity → Quotation → Sales Order → Delivery → Invoice → Payment
```

## SAP-to-Odoo Quick Map

| SAP | Odoo |
|-----|------|
| CRM Opportunity | crm.lead |
| Sales Order (VA01) | sale.order |
| Delivery (VL01N) | stock.picking |
| Billing (VF01) | account.move |
| Pricing Conditions | product.pricelist |
| Sales Organization | crm.team |

## OCA Modules to Know

- `sale_order_type`: Classify orders by type (standard, return, sample)
- `sale_tier_validation`: Approval workflows on sales orders
- `crm_stage_probability`: Win probability per stage
- `sale_order_line_date`: Delivery date per line

## What "SAP-grade" Means Here

- Structured pipeline with probability-based forecasting
- Approval workflows for discounts beyond threshold
- Automated quote-to-order-to-invoice flow
- Margin analysis and profitability tracking
- Territory/team-based revenue attribution
