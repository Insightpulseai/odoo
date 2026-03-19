# Odoo Query Examples

> **Tool**: `odoo_query`
> **Purpose**: Query Odoo System of Record for business data

---

## Common Queries

### 1. Recent Invoices

**Natural language**:
```
Show me the 10 most recent customer invoices posted this month
```

**Claude.ai tool call** (behind the scenes):
```json
{
  "model": "account.move",
  "domain": "[['move_type', '=', 'out_invoice'], ['state', '=', 'posted'], ['invoice_date', '>=', '2026-02-01']]",
  "fields": ["name", "partner_id", "invoice_date", "amount_total", "currency_id"],
  "limit": 10
}
```

**Expected response format**:
| Invoice # | Customer | Date | Amount | Currency |
|-----------|----------|------|--------|----------|
| INV/2026/00123 | Acme Corp | 2026-02-15 | 125000.00 | PHP |
| INV/2026/00124 | Beta LLC | 2026-02-16 | 98500.00 | PHP |

---

### 2. Overdue Invoices

**Natural language**:
```
List all customer invoices that are overdue by more than 30 days
```

**Tool call**:
```json
{
  "model": "account.move",
  "domain": "[['move_type', '=', 'out_invoice'], ['state', '=', 'posted'], ['invoice_date_due', '<', '2026-01-20'], ['payment_state', '!=', 'paid']]",
  "fields": ["name", "partner_id", "invoice_date_due", "amount_residual"],
  "limit": 100
}
```

---

### 3. Top Customers by Revenue

**Natural language**:
```
Who are our top 10 customers by total invoice amount this year?
```

**Tool call**:
```json
{
  "model": "account.move",
  "domain": "[['move_type', '=', 'out_invoice'], ['state', '=', 'posted'], ['invoice_date', '>=', '2026-01-01']]",
  "fields": ["partner_id", "amount_total"],
  "limit": 1000
}
```

**Post-processing**: Claude aggregates by `partner_id` and sorts by total `amount_total`.

---

### 4. Product Search

**Natural language**:
```
Find all products with "laptop" in the name
```

**Tool call**:
```json
{
  "model": "product.product",
  "domain": "[['name', 'ilike', 'laptop']]",
  "fields": ["name", "default_code", "list_price", "standard_price", "qty_available"],
  "limit": 50
}
```

---

### 5. Vendor Bill Analysis

**Natural language**:
```
Show me all vendor bills received in the last 7 days
```

**Tool call**:
```json
{
  "model": "account.move",
  "domain": "[['move_type', '=', 'in_invoice'], ['invoice_date', '>=', '2026-02-13']]",
  "fields": ["name", "partner_id", "invoice_date", "amount_total", "payment_state"],
  "limit": 100
}
```

---

### 6. Sales Orders in Progress

**Natural language**:
```
List all confirmed sales orders that haven't been fully invoiced yet
```

**Tool call**:
```json
{
  "model": "sale.order",
  "domain": "[['state', 'in', ['sale', 'done']], ['invoice_status', '!=', 'invoiced']]",
  "fields": ["name", "partner_id", "date_order", "amount_total", "invoice_status"],
  "limit": 100
}
```

---

### 7. Inventory Stock Levels

**Natural language**:
```
Check inventory levels for products below reorder point
```

**Tool call**:
```json
{
  "model": "product.product",
  "domain": "[['type', '=', 'product'], ['qty_available', '<', 10]]",
  "fields": ["name", "default_code", "qty_available", "virtual_available"],
  "limit": 100
}
```

---

### 8. Partner Contact Information

**Natural language**:
```
Get contact details for all customers in Manila
```

**Tool call**:
```json
{
  "model": "res.partner",
  "domain": "[['is_company', '=', true], ['city', 'ilike', 'manila'], ['customer_rank', '>', 0]]",
  "fields": ["name", "email", "phone", "street", "city"],
  "limit": 100
}
```

---

### 9. Payment Reconciliation Status

**Natural language**:
```
Show unreconciled payments from the last month
```

**Tool call**:
```json
{
  "model": "account.payment",
  "domain": "[['date', '>=', '2026-01-20'], ['is_reconciled', '=', false]]",
  "fields": ["name", "partner_id", "date", "amount", "payment_type"],
  "limit": 100
}
```

---

### 10. Employee Directory

**Natural language**:
```
List all active employees with their job positions
```

**Tool call**:
```json
{
  "model": "hr.employee",
  "domain": "[['active', '=', true]]",
  "fields": ["name", "work_email", "job_id", "department_id", "work_phone"],
  "limit": 200
}
```

---

## Advanced Queries

### Multi-Condition Filtering

**Natural language**:
```
Find invoices over ₱100,000 posted in February that are still unpaid
```

**Tool call**:
```json
{
  "model": "account.move",
  "domain": "[['move_type', '=', 'out_invoice'], ['state', '=', 'posted'], ['invoice_date', '>=', '2026-02-01'], ['invoice_date', '<=', '2026-02-29'], ['amount_total', '>', 100000], ['payment_state', '!=', 'paid']]",
  "fields": ["name", "partner_id", "invoice_date", "amount_total", "amount_residual"],
  "limit": 50
}
```

---

### Computed Field Queries

**Natural language**:
```
Show products with profit margin below 20%
```

**Tool call** (requires post-processing by Claude):
```json
{
  "model": "product.product",
  "domain": "[['type', '=', 'product']]",
  "fields": ["name", "list_price", "standard_price"],
  "limit": 500
}
```

Claude computes: `margin = (list_price - standard_price) / list_price * 100`

---

## Tips for Effective Queries

### 1. Use Specific Domains

**❌ Too broad**:
```json
{
  "model": "account.move",
  "domain": "[]",
  "limit": 1000
}
```

**✅ Well-scoped**:
```json
{
  "model": "account.move",
  "domain": "[['move_type', '=', 'out_invoice'], ['invoice_date', '>=', '2026-02-01'], ['state', '=', 'posted']]",
  "limit": 100
}
```

### 2. Limit Field Selection

**❌ Fetch all fields**:
```json
{
  "fields": []  // Returns ALL fields (slow)
}
```

**✅ Specific fields only**:
```json
{
  "fields": ["name", "partner_id", "amount_total"]
}
```

### 3. Set Reasonable Limits

- **Exploratory queries**: `limit: 10-50`
- **Analytics**: `limit: 100-500`
- **Exports**: `limit: 1000` (max)

### 4. Use Odoo Domain Operators

| Operator | Example | Meaning |
|----------|---------|---------|
| `=` | `['state', '=', 'posted']` | Equals |
| `!=` | `['state', '!=', 'draft']` | Not equals |
| `>` | `['amount', '>', 1000]` | Greater than |
| `>=` | `['date', '>=', '2026-01-01']` | Greater or equal |
| `<` | `['qty', '<', 10]` | Less than |
| `<=` | `['date', '<=', '2026-12-31']` | Less or equal |
| `in` | `['state', 'in', ['draft', 'posted']]` | In list |
| `not in` | `['state', 'not in', ['cancel']]` | Not in list |
| `like` | `['name', 'like', 'INV%']` | Case-sensitive match |
| `ilike` | `['name', 'ilike', 'invoice']` | Case-insensitive match |

---

## Common Odoo Models

| Model | Description | Common Fields |
|-------|-------------|---------------|
| `account.move` | Invoices, bills, journal entries | name, partner_id, invoice_date, amount_total |
| `res.partner` | Customers, vendors, contacts | name, email, phone, city, country_id |
| `product.product` | Products and variants | name, default_code, list_price, qty_available |
| `sale.order` | Sales orders | name, partner_id, date_order, amount_total |
| `purchase.order` | Purchase orders | name, partner_id, date_order, amount_total |
| `stock.picking` | Delivery orders, receipts | name, partner_id, scheduled_date, state |
| `account.payment` | Payments | name, partner_id, date, amount, payment_type |
| `hr.employee` | Employees | name, work_email, job_id, department_id |

---

## Troubleshooting

### Query Returns Empty Results

**Possible causes**:
1. Domain filter too restrictive
2. Date range outside available data
3. Wrong model name

**Debug strategy**:
1. Simplify domain: `domain: "[]"` (all records)
2. Increase limit: `limit: 500`
3. Verify model name: check Odoo documentation

### Query Times Out

**Possible causes**:
1. Too many records returned
2. Complex domain with multiple joins
3. Missing database indexes

**Solutions**:
1. Add date range filter
2. Reduce limit to 100
3. Request specific fields only

---

*For more examples, see `/odoo/docs/ai/CLAUDE_AI_N8N_CONNECTOR.md`*
