# PRD — InsightPulseAI Odoo Connector for ChatGPT

## 1. Executive Summary

A ChatGPT Apps SDK app that exposes curated Odoo business operations as MCP-backed tools. Users can search customers, review orders, check invoices, monitor projects, and create follow-ups through natural language in ChatGPT.

## 2. Problem

Users context-switch between ChatGPT and Odoo for routine lookups: "What's the status of order SO-2456?", "Show me overdue invoices for TBWA", "Create a follow-up task for the Makati project." Each query requires opening Odoo, navigating to the right view, and mentally translating the result.

## 3. Tool Set

### Sales / CRM

| Tool | Odoo Model | Method | Phase |
|------|-----------|--------|-------|
| `odoo_search_partners` | `res.partner` | `search_read` | 1 |
| `odoo_get_partner` | `res.partner` | `read` | 1 |
| `odoo_search_sale_orders` | `sale.order` | `search_read` | 1 |
| `odoo_get_sale_order` | `sale.order` | `read` | 1 |
| `odoo_list_pipeline_opportunities` | `crm.lead` | `search_read` | 1 |

### Finance

| Tool | Odoo Model | Method | Phase |
|------|-----------|--------|-------|
| `odoo_list_overdue_invoices` | `account.move` | `search_read` | 1 |
| `odoo_get_invoice` | `account.move` | `read` | 1 |
| `odoo_get_customer_statement` | `res.partner` | custom | 2 |

### Projects

| Tool | Odoo Model | Method | Phase |
|------|-----------|--------|-------|
| `odoo_search_projects` | `project.project` | `search_read` | 1 |
| `odoo_get_project_status` | `project.project` | `read` | 1 |
| `odoo_list_project_tasks` | `project.task` | `search_read` | 1 |

### Inventory

| Tool | Odoo Model | Method | Phase |
|------|-----------|--------|-------|
| `odoo_get_product_availability` | `product.product` | `search_read` | 1 |
| `odoo_get_inventory_snapshot` | `stock.quant` | `search_read` | 1 |

### Collaboration (Phase 2)

| Tool | Odoo Model | Method | Phase |
|------|-----------|--------|-------|
| `odoo_create_activity` | `mail.activity` | `create` | 2 |
| `odoo_post_record_note` | various | `message_post` | 2 |

## 4. Auth Model

- User authenticates to connector via OAuth in ChatGPT
- Connector maps session to allowed Odoo identity/policy
- Connector calls Odoo JSON-2 with service bearer token
- `_meta["mcp/www_authenticate"]` triggers OAuth challenge when needed

## 5. Data Contract

### Input

Narrow typed schemas per tool. Example:

```json
{
  "type": "object",
  "properties": {
    "customer_name": { "type": "string" },
    "limit": { "type": "integer", "minimum": 1, "maximum": 25 }
  },
  "required": ["customer_name"],
  "additionalProperties": false
}
```

### Output

```json
{
  "structuredContent": { "records": [...], "count": 1 },
  "content": [{ "type": "text", "text": "Found 1 customer." }],
  "_meta": { "rawById": { "42": { "credit_limit": 500000 } } }
}
```

## 6. Non-goals

- Generic `execute_kw` passthrough
- Arbitrary model/method selection by the model
- Direct Odoo API access from the widget
- Finance/inventory write mutations in Phase 1

## 7. Success Metrics

- Tools invoked per session
- Time saved vs manual Odoo lookup
- Error rate per tool
- User retention after first use

## 8. Risks

- Odoo JSON-2 API tier availability for self-hosted
- Write tool safety (Phase 2+)
- ChatGPT app submission requirements
- Rate limiting at Odoo or gateway layer
