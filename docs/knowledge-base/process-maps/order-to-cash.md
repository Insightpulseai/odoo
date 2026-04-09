# Process Map: Order-to-Cash (O2C)

## End-to-End Flow

```
[CRM]           [Sales]          [Warehouse]       [Finance]
Lead            Quotation        Delivery Order     Customer Invoice
  │               │                  │                  │
  ▼               ▼                  ▼                  ▼
Opportunity → Sales Order → Pick → Pack → Ship → Invoice → Payment
  │               │                  │                  │
crm.lead    sale.order        stock.picking      account.move
                                                       │
                                                  Payment Receipt
                                                  (account.payment)
```

## Step Details

| Step | Odoo Model | Key Fields | Trigger |
|------|-----------|------------|---------|
| Lead | crm.lead | name, partner_id, expected_revenue | Manual/import |
| Opportunity | crm.lead | stage_id, probability | Stage change |
| Quotation | sale.order (draft) | partner_id, order_line, pricelist_id | "New Quotation" |
| Sales Order | sale.order (sale) | confirmation_date | "Confirm" button |
| Delivery | stock.picking | move_ids, scheduled_date | SO confirmation |
| Invoice | account.move | invoice_line_ids, amount_total | "Create Invoice" |
| Payment | account.payment | amount, journal_id | Manual or payment link |

## Variants

### Service (no delivery)
```
Quotation → Sales Order → Invoice → Payment
```
No stock.picking created for service products.

### Partial delivery
```
SO (100 units) → Delivery 1 (60 units) → Invoice 1 (60 units)
                → Delivery 2 (40 units) → Invoice 2 (40 units)
```
Backorder created automatically for remaining quantity.

### Prepayment
```
Quotation → Down Payment Invoice → Payment → Sales Order → Delivery → Final Invoice
```
Down payment deducted from final invoice.

## Controls

| Control | Type | Implementation |
|---------|------|----------------|
| Quotation approval | Preventive | sale_tier_validation (OCA) |
| Credit check | Preventive | partner.credit_limit field check |
| Delivery confirmation | Detective | stock.picking validation |
| Invoice-to-order match | Detective | Automatic from SO lines |
| Payment allocation | Corrective | Reconciliation |

## KPIs

| KPI | Measure | Source |
|-----|---------|--------|
| Quote-to-order rate | Confirmed SO / Total quotations | sale.order |
| Order fulfillment time | SO date → delivery date | stock.picking |
| Days sales outstanding | Average collection time | account.move |
| Revenue by product | Sum of invoice lines by product | account.move.line |
