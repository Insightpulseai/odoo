# Preset.io Parity Roadmap

Self-hosted Superset capabilities matching Preset.io's managed offering.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    IPAI Superset Platform                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   Odoo CE ──► Virtual Datasets ──► Superset ──► Dashboards         │
│      │              │                   │             │              │
│      │              ▼                   ▼             ▼              │
│      │       Semantic Layer      MCP Server     Embedded            │
│      │       (metrics/dims)      (AI access)    Analytics           │
│      │                                                              │
│      └──────────────────────────────────────────────────────────────│
│                                                                      │
│   AI Layer:  Claude ◄─── MCP ───► Text-to-SQL ───► RAG Pipeline    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Capability Matrix

| Preset.io Feature | Status | IPAI Implementation |
|-------------------|--------|---------------------|
| **Core BI** |||
| Drag-and-drop charts | ✅ | Apache Superset CE |
| SQL Lab IDE | ✅ | Apache Superset CE |
| Dashboard builder | ✅ | Apache Superset CE |
| **Semantic Layer** |||
| Virtual datasets | ✅ | `infra/superset/virtual_datasets.sql` |
| Metrics/dimensions | 🚧 | Superset dataset config |
| dbt integration | ⬜ | Planned via dbt Semantic Layer |
| Cube integration | ⬜ | Planned |
| Snowflake Metrics | ⬜ | N/A (PostgreSQL focus) |
| **AI / Text-to-SQL** |||
| Text-to-SQL | 🚧 | `mcp/servers/superset-mcp-server/` |
| RAG pipeline | ⬜ | Planned via embeddings |
| AI Assist | ⬜ | Planned |
| **MCP Integration** |||
| MCP Server | ✅ | `mcp/servers/superset-mcp-server/` |
| AI agent access | ✅ | Via Claude Desktop/VS Code |
| Custom tools | 🚧 | Dashboards, datasets, charts |
| **Security** |||
| RBAC | ✅ | Superset native |
| Row-level security | ✅ | Superset RLS policies |
| Multi-workspace | 🚧 | Multiple Superset instances |
| **Embedded Analytics** |||
| Embed charts | ✅ | Superset embed API |
| Embed dashboards | ✅ | Superset embed API |
| White-label | 🚧 | Custom CSS + Tableau tokens |
| Guest tokens | ✅ | Superset guest token API |
| **Design System** |||
| Tableau tokens | ✅ | `@ipai/design-tokens/tableauTokens` |
| Custom themes | ✅ | `@ipai/design-tokens/tableau.css` |
| Tailwind preset | ✅ | `@ipai/design-tokens/tailwind-tableau.preset` |

**Legend:** ✅ Implemented | 🚧 In Progress | ⬜ Planned

## Implementation Phases

### Phase 1: Foundation (Current)

**Completed:**
- Apache Superset deployment on DigitalOcean
- MCP server for programmatic access
- Tableau design tokens for consistent styling
- Virtual datasets for Odoo data

**Files:**
```
infra/superset/
├── manifest.json          # Pinned image reference
├── do-app-spec.yaml       # DigitalOcean deployment
├── superset_config.py     # Superset configuration
├── virtual_datasets.sql   # Pre-built semantic views
└── Dockerfile            # Custom image

mcp/servers/superset-mcp-server/
├── src/
│   ├── index.ts           # MCP server entry
│   ├── superset-client.ts # API client
│   └── tools/
│       ├── dashboards.ts  # Dashboard operations
│       ├── datasets.ts    # Dataset management
│       └── charts.ts      # Chart operations
└── package.json

packages/ipai-design-tokens/
├── src/tableauTokens.ts   # TypeScript module
├── src/tableauTokens.json # Canonical tokens
├── tableau.css            # CSS custom properties
└── tailwind-tableau.preset.js
```

### Phase 2: Semantic Layer

**Goals:**
1. Implement metric definitions in Superset datasets
2. Create curated business metrics (KPIs)
3. Add dbt integration for transformation layer

**Implementation:**

```sql
-- Example: Odoo sales metrics as virtual dataset
CREATE VIEW superset_sales_metrics AS
SELECT
  so.date_order::date AS order_date,
  rp.name AS customer,
  pt.name AS product,
  sol.product_uom_qty AS quantity,
  sol.price_subtotal AS revenue,
  -- Calculated metrics
  sol.price_subtotal / NULLIF(sol.product_uom_qty, 0) AS avg_unit_price
FROM sale_order so
JOIN sale_order_line sol ON sol.order_id = so.id
JOIN res_partner rp ON so.partner_id = rp.id
JOIN product_product pp ON sol.product_id = pp.id
JOIN product_template pt ON pp.product_tmpl_id = pt.id
WHERE so.state IN ('sale', 'done');
```

### Phase 3: AI / Text-to-SQL

**Architecture:**

```
User Query: "Show me top 10 customers by revenue this quarter"
         │
         ▼
┌─────────────────┐
│  MCP Server     │ ◄── Claude/AI Agent
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ RAG Pipeline    │
│ - Embed query   │
│ - Find datasets │
│ - Generate SQL  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Superset SQL    │
│ Lab API         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Results + Chart │
└─────────────────┘
```

**Required Components:**

1. **Embedding Service**
   - Use OpenAI embeddings or local model
   - Index dataset metadata (tables, columns, descriptions)

2. **RAG Retriever**
   - Vector store for dataset metadata (Supabase pgvector)
   - Cosine similarity matching

3. **SQL Generator**
   - LLM prompt with retrieved context
   - SQL validation before execution

**MCP Tools to Add:**

```typescript
// mcp/servers/superset-mcp-server/src/tools/ai.ts
export const textToSqlTool = {
  name: "text_to_sql",
  description: "Convert natural language to SQL and execute",
  inputSchema: {
    type: "object",
    properties: {
      query: { type: "string", description: "Natural language question" },
      database_id: { type: "number", description: "Superset database ID" }
    },
    required: ["query", "database_id"]
  },
  handler: async (input: { query: string; database_id: number }) => {
    // 1. Embed the query
    // 2. Find relevant datasets via RAG
    // 3. Generate SQL with context
    // 4. Execute via Superset SQL Lab API
    // 5. Return results
  }
};
```

### Phase 4: Embedded Analytics

**Implementation:**

```typescript
// Example: Embed Superset dashboard in React app
import { SupersetEmbedSDK } from '@superset/embed-sdk';
import { tableauColors } from '@ipai/design-tokens/tableauTokens';

const embedDashboard = async (dashboardId: string, container: HTMLElement) => {
  const sdk = new SupersetEmbedSDK({
    supersetUrl: process.env.SUPERSET_URL,
    guestTokenEndpoint: '/api/superset/guest-token',
  });

  await sdk.embedDashboard({
    id: dashboardId,
    container,
    fetchGuestToken: async () => {
      const res = await fetch('/api/superset/guest-token', {
        method: 'POST',
        body: JSON.stringify({ dashboard_id: dashboardId })
      });
      return res.json().then(d => d.token);
    },
    dashboardUiConfig: {
      hideTitle: true,
      filters: { expanded: false },
    },
  });
};
```

**Guest Token API (Odoo integration):**

```python
# addons/ipai/ipai_superset_connector/controllers/main.py
from odoo import http
import requests

class SupersetController(http.Controller):
    @http.route('/api/superset/guest-token', type='json', auth='user')
    def get_guest_token(self, dashboard_id):
        user = http.request.env.user

        # Get Superset access token
        superset_url = http.request.env['ir.config_parameter'].sudo().get_param('superset.url')
        admin_token = http.request.env['ir.config_parameter'].sudo().get_param('superset.admin_token')

        # Create guest token with RLS
        response = requests.post(
            f"{superset_url}/api/v1/security/guest_token/",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "user": {"username": user.login, "first_name": user.name},
                "resources": [{"type": "dashboard", "id": dashboard_id}],
                "rls": [{"clause": f"company_id = {user.company_id.id}"}]
            }
        )

        return {"token": response.json()["token"]}
```

## Configuration

### Environment Variables

```bash
# .env.superset
SUPERSET_URL=https://superset.insightpulseai.net
SUPERSET_SECRET_KEY=<generate with openssl rand -base64 42>
SUPERSET_ADMIN_USER=admin
SUPERSET_ADMIN_PASSWORD=<secure password>

# Database
DATABASE_URL=postgresql://superset:password@postgres:5432/superset

# Redis (caching)
REDIS_URL=redis://redis:6379/0

# AI/Embeddings (Phase 3)
OPENAI_API_KEY=<for embeddings>

# Odoo Integration
ODOO_URL=https://erp.insightpulseai.net
ODOO_API_KEY=<odoo api key>
```

### Superset Config

```python
# infra/superset/superset_config.py
import os

# Basic config
SECRET_KEY = os.environ.get('SUPERSET_SECRET_KEY')
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

# Cache
CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_REDIS_URL': os.environ.get('REDIS_URL'),
}

# Feature flags
FEATURE_FLAGS = {
    'ENABLE_TEMPLATE_PROCESSING': True,
    'ENABLE_EXPLORE_JSON_CSRF_PROTECTION': False,
    'EMBEDDED_SUPERSET': True,
    'DASHBOARD_RBAC': True,
}

# Guest token (embedded analytics)
GUEST_TOKEN_JWT_SECRET = os.environ.get('SUPERSET_SECRET_KEY')
GUEST_TOKEN_JWT_ALGO = 'HS256'
GUEST_TOKEN_JWT_EXP_SECONDS = 300

# Talisman config (CSP for embedding)
TALISMAN_ENABLED = True
TALISMAN_CONFIG = {
    'content_security_policy': {
        'frame-ancestors': ["'self'", "https://*.insightpulseai.net"],
    }
}
```

## Verification Commands

```bash
# Health check
curl https://superset.insightpulseai.net/health

# API auth test
curl -X POST https://superset.insightpulseai.net/api/v1/security/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "<password>", "provider": "db"}'

# MCP server test
cd mcp/servers/superset-mcp-server
npm run build
node dist/index.js
```

## References

- [Preset.io Product](https://preset.io/product/)
- [Superset Semantic Layer](https://preset.io/blog/understanding-superset-semantic-layer/)
- [Text-to-SQL in Superset](https://preset.io/blog/building-preset-ai-assist-how-we-brought-text-to-sql-into-apache-superset/)
- [MCP Integration](https://preset.io/blog/apache-superset-community-update-november-2025/)
- [Superset Embedding](https://superset.apache.org/docs/using-superset/embedded-dashboards/)
