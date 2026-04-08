# Plan — InsightPulseAI Odoo Connector for ChatGPT

## 1. Architecture

```
ChatGPT (Apps SDK)
  → MCP Server (connector gateway)
    → Odoo JSON-2 API (erp.insightpulseai.com)
```

### Components

1. **Apps SDK Server** — MCP server exposing business tools
2. **Tool Registry** — curated tool definitions with schemas
3. **Odoo Client** — JSON-2 wrapper with allowed model/method mappings
4. **Auth Module** — OAuth flow + session management
5. **Widget Resources** — optional rich UI cards (order summary, invoice aging)

## 2. Repo Layout

```text
apps/odoo-chatgpt-connector/
  server/
    index.ts
    tools/
      customers.ts
      sales.ts
      finance.ts
      projects.ts
      inventory.ts
      collaboration.ts
    auth/
      oauth.ts
      session.ts
    odoo/
      client.ts
      mapping.ts
      transformers.ts
    ui/
      resources.ts
      widgets/
        order-summary.html
        invoice-aging.html
  package.json
  tsconfig.json
  README.md
```

## 3. Implementation Phases

### Phase 1 — Read-only tools

- 13 read tools across customers, sales, finance, projects, inventory
- JSON-2 client with bearer auth
- OAuth flow for ChatGPT user authentication
- Gateway validation and rate limiting

### Phase 2 — Scoped writes

- `odoo_create_activity`, `odoo_post_record_note`
- Human confirmation UX via structured content
- Audit logging for all write operations

### Phase 3 — Rich widgets

- Order summary cards
- Invoice aging tables
- Project health dashboards

## 4. Odoo JSON-2 Client

```typescript
// Endpoint: /json/2/<model>/<method>
// Auth: Bearer token
// Body: JSON params
async function callOdoo(model: string, method: string, params: unknown): Promise<unknown>
```

### Allowed mappings (Phase 1)

| Tool | Model | Method | Fields |
|------|-------|--------|--------|
| `odoo_search_partners` | `res.partner` | `search_read` | name, email, phone, company |
| `odoo_get_sale_order` | `sale.order` | `read` | name, partner, amount, state |
| `odoo_list_overdue_invoices` | `account.move` | `search_read` | partner, amount, due date |

## 5. Open Decisions

1. Gateway hosting: Azure Container App vs Azure Functions
2. Whether to use Odoo API keys or Entra-issued tokens for service auth
3. Widget complexity for Phase 3
4. ChatGPT app submission timing (private test vs public)
