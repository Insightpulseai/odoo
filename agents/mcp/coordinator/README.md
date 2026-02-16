# MCP Coordinator

Intelligent routing and aggregation service for multiple MCP servers.

## Overview

The MCP Coordinator provides:
- **Context-aware routing** - Routes requests to appropriate MCP servers based on context
- **Automatic failover** - Falls back to secondary servers if primary fails
- **Request aggregation** - Combines responses from multiple servers
- **Caching** - Stores routing decisions and responses for performance
- **Usage metrics** - Tracks requests and performance

## Architecture

```
VS Code / Claude Desktop
         ↓
MCP Coordinator (port 8766)
    ↓               ↓
Odoo Prod MCP   Odoo Lab MCP
(port 8767)     (port 8765)
    ↓               ↓
Odoo Prod       Odoo Lab
(production)    (development)
```

## Routing Logic

### Priority 1: Explicit Target
```json
{
  "query": "What are the latest expenses?",
  "target": "odoo_prod"
}
```
Routes directly to specified target.

### Priority 2: Context-Based
```json
{
  "query": "Generate BIR 1601-C for Finance SSC",
  "context": {"finance-ssc": true}
}
```
- `finance-ssc` → Odoo Prod (production data required)
- `migration`, `oca`, `development` → Odoo Lab (testing environment)

### Priority 3: Default with Failover
```json
{
  "query": "How do I create an Odoo module?"
}
```
Routes to default target (configured via `DEFAULT_TARGET` env var) with automatic failover.

## Deployment

### Local Development
```bash
cd mcp/coordinator

# Build image
docker build -t mcp-coordinator:dev .

# Run locally
docker run -d \
  --name mcp-coordinator \
  -p 8766:8766 \
  -e SUPABASE_URL=$SUPABASE_URL \
  -e SUPABASE_SERVICE_ROLE_KEY=$SUPABASE_SERVICE_ROLE_KEY \
  -e COORDINATOR_API_KEY=dev-key \
  --network ipai_backend \
  mcp-coordinator:dev
```

### DigitalOcean App Platform
```bash
# Create app spec
doctl apps create --spec infra/do/mcp-coordinator.yaml

# Deploy
doctl apps create-deployment <APP_ID>
```

## API Endpoints

### Health Check
```bash
curl http://localhost:8766/health
```

Response:
```json
{
  "status": "ok",
  "version": "0.1.0",
  "targets": ["odoo_prod", "odoo_lab"]
}
```

### Route Request
```bash
curl -X POST http://localhost:8766/route \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the latest expenses?",
    "context": {"finance-ssc": true}
  }'
```

Response:
```json
{
  "data": { ... },
  "routing": {
    "target": "odoo_prod",
    "reason": "Finance SSC context requires production data",
    "confidence": 0.95
  }
}
```

### Aggregate Requests
```bash
curl -X POST http://localhost:8766/aggregate \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "List all skills",
    "context": {}
  }'
```

Response:
```json
{
  "query": "List all skills",
  "results": {
    "odoo_prod": [...],
    "odoo_lab": [...]
  },
  "aggregation": {
    "targets": ["odoo_prod", "odoo_lab"],
    "mode": "parallel"
  }
}
```

## Configuration

Environment variables:

```bash
# Server settings
COORDINATOR_API_KEY=your-secure-key
ENVIRONMENT=production

# MCP targets
ODOO_PROD_MCP_URL=http://odoo-prod-mcp:8767
ODOO_LAB_MCP_URL=http://localhost:8765

# Supabase
SUPABASE_URL=https://xkxyvboeubffxxbebsll.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Redis (optional)
REDIS_URL=redis://localhost:6379

# Routing
DEFAULT_TARGET=odoo_prod
ENABLE_AGGREGATION=true
CACHE_TTL=300
```

## Monitoring

The coordinator logs all routing decisions and errors:

```bash
# View logs
docker logs -f mcp-coordinator

# Check status
curl -H "X-API-Key: your-api-key" http://localhost:8766/status
```

## Next Steps

1. Deploy to DigitalOcean App Platform at `mcp.insightpulseai.com`
2. Configure DNS and SSL
3. Setup Redis for caching
4. Implement usage analytics dashboard
5. Add rate limiting and authentication
