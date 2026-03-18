# Examples: Billing and Metering Design

## Example 1: Per-Seat + Usage Hybrid (Odoo SaaS)

**Scenario**: Odoo CE multi-tenant platform billing per-seat base plus API usage overage.

**Meter definitions**:
| Meter | Unit | Aggregation | Free | Standard | Enterprise |
|-------|------|-------------|------|----------|------------|
| active_users | users | max/month | 3 | 25 | unlimited |
| api_calls | requests | sum/month | 1,000 | 50,000 | 500,000 |
| storage_gb | GB | max/month | 1 | 10 | 100 |

**Pricing**:
- Standard: $49/mo base + $2/user over 25 + $0.001/API call over 50k
- Enterprise: $299/mo base + unlimited users + $0.0005/API call over 500k

**Event schema**:
```json
{
  "event_id": "evt_abc123",
  "tenant_id": "acme-corp",
  "meter_id": "api_calls",
  "quantity": 1,
  "timestamp": "2026-03-17T10:30:00Z",
  "idempotency_key": "req_xyz789"
}
```

**Pipeline**: Application emits events to Azure Event Hub. Azure Functions aggregates hourly into Cosmos DB. End-of-month job produces billing summary per tenant.

---

## Example 2: Azure Marketplace Metered Billing

**Scenario**: SaaS listed on Azure Marketplace with custom metered dimensions.

**Marketplace meter mapping**:
| Marketplace Dimension ID | Internal Meter | Unit | Included in Plan |
|--------------------------|---------------|------|-----------------|
| `api_calls_overage` | api_calls | per 1000 | 50,000/mo |
| `storage_overage` | storage_gb | per GB | 10 GB |

**Submission flow**:
```
Hourly aggregation job
  → Calculate overage above plan inclusion
  → POST to Marketplace Metering API:
    POST https://marketplaceapi.microsoft.com/api/usageEvent
    {
      "resourceUri": "/subscriptions/{sub}/resourceGroups/{rg}",
      "quantity": 12.5,
      "dimension": "api_calls_overage",
      "effectiveStartTime": "2026-03-17T00:00:00Z",
      "planId": "standard-plan"
    }
  → Store submission receipt for reconciliation
```

**Reconciliation**: Daily job compares submitted events with Marketplace acceptance responses. Alerts on rejected events.

---

## Example 3: Odoo-Integrated Invoice Generation

**Scenario**: Billing data flows into Odoo for invoice generation.

**Integration flow**:
1. End-of-month: rating engine produces billing summary per tenant
2. Odoo RPC: create `account.move` (invoice) with line items per meter
3. Tax computation via Odoo fiscal positions
4. Invoice sent via Odoo email (Zoho SMTP)

**Odoo invoice creation**:
```python
invoice_vals = {
    'partner_id': tenant.odoo_partner_id,
    'move_type': 'out_invoice',
    'invoice_line_ids': [
        Command.create({
            'name': f'Standard Plan - {period}',
            'quantity': 1,
            'price_unit': 49.00,
        }),
        Command.create({
            'name': f'API Calls Overage ({overage_calls:,} calls)',
            'quantity': overage_calls / 1000,
            'price_unit': 1.00,
        }),
    ],
}
invoice = env['account.move'].create(invoice_vals)
invoice.action_post()
```
