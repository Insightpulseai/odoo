# MCP Quick Start Guide

Get started with the local MCP server in 5 minutes.

## Step 1: Start the Local MCP Server

```bash
cd /Users/tbwa/odoo-ce

# Start Odoo and local MCP together
docker-compose -f docker-compose.prod.yml -f docker-compose.mcp-local.yml up -d

# Check logs
docker logs -f ipai-mcp-local
```

You should see:
```
✅ Local MCP Server initialized
   Skills DB: /data/mcp_skills.db
   RAG DB: /data/mcp_rag.db
   Memory DB: /data/mcp_memory.db
INFO:     Uvicorn running on http://0.0.0.0:8765
```

## Step 2: Verify Health

```bash
curl http://localhost:8765/health
```

Expected response:
```json
{
  "status": "ok",
  "version": "0.1.0",
  "databases": {
    "skills": "True",
    "rag": "True",
    "memory": "True"
  }
}
```

## Step 3: Check Status

```bash
curl -H "X-API-Key: dev-only-insecure-key" \
  http://localhost:8765/status | jq
```

Expected response:
```json
{
  "status": "ok",
  "stats": {
    "skills": 0,
    "active_conversations": 0,
    "indexed_commits": 0
  },
  "config": {
    "odoo_lab_url": "http://odoo:8069",
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "repo_path": "/mnt/addons"
  }
}
```

## Step 4: Create Your First Skill

```bash
curl -X POST http://localhost:8765/skills \
  -H "X-API-Key: dev-only-insecure-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "odoo-developer",
    "version": "0.1.0",
    "status": "dev",
    "metadata": {
      "description": "Odoo CE 18.0 development expert",
      "triggers": ["odoo", "module", "xml", "python"]
    },
    "file_path": "skills/odoo-developer.yaml"
  }'
```

## Step 5: List Skills

```bash
curl -H "X-API-Key: dev-only-insecure-key" \
  http://localhost:8765/skills | jq
```

You should see your newly created skill!

## Step 6: Save a Conversation

```bash
curl -X POST http://localhost:8765/conversations \
  -H "X-API-Key: dev-only-insecure-key" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session-001",
    "user_id": "tbwa@insightpulseai.net",
    "messages": [
      {
        "role": "user",
        "content": "How do I create an Odoo module?"
      },
      {
        "role": "assistant",
        "content": "To create an Odoo module, you need to create a directory with __manifest__.py, __init__.py, and your model/view files."
      }
    ],
    "context": {
      "workspace": "/Users/tbwa/odoo-ce",
      "active_files": ["addons/ipai_expense/__manifest__.py"],
      "odoo_instance": "odoo_lab"
    },
    "summary": "User learned how to create Odoo modules"
  }'
```

## Step 7: List Conversations

```bash
curl -H "X-API-Key: dev-only-insecure-key" \
  "http://localhost:8765/conversations?limit=10" | jq
```

## Step 8: Open VS Code Workspace

```bash
code .vscode/mcp-dev.code-workspace
```

This workspace:
- Connects to local MCP (priority 1)
- Sets `ODOO_INSTANCE=odoo_lab`
- Configures Python analysis for Odoo development

## Troubleshooting

### Port Already in Use

```bash
# Check what's using port 8765
lsof -i :8765

# Stop the service
docker-compose -f docker-compose.mcp-local.yml down
```

### Database Not Initialized

```bash
# Check database files exist
ls -la mcp/local/data/sqlite/

# Restart to reinitialize
docker-compose -f docker-compose.mcp-local.yml down
rm -rf mcp/local/data/sqlite/*.db
docker-compose -f docker-compose.prod.yml -f docker-compose.mcp-local.yml up -d
```

### Connection Refused

Make sure Odoo is running first:

```bash
docker-compose -f docker-compose.prod.yml up -d odoo db
# Wait for Odoo to be healthy
docker ps | grep ipai-ce
```

## Next Steps

1. **Explore API Documentation**: http://localhost:8765/docs (FastAPI auto-generated docs)
2. **Read Implementation Status**: `docs/MCP_IMPLEMENTATION_STATUS.md`
3. **Review Architecture**: `docs/README_MCP_STACK.md`
4. **Start Phase 2**: Implement MCP Coordinator for production

## Useful Commands

```bash
# View logs
docker logs -f ipai-mcp-local

# Restart service
docker-compose -f docker-compose.mcp-local.yml restart mcp-local

# Stop all services
docker-compose -f docker-compose.prod.yml -f docker-compose.mcp-local.yml down

# Check database size
du -sh mcp/local/data/sqlite/

# Interactive shell in container
docker exec -it ipai-mcp-local bash

# Test API endpoints
curl -X GET http://localhost:8765/skills -H "X-API-Key: dev-only-insecure-key"
curl -X GET http://localhost:8765/conversations -H "X-API-Key: dev-only-insecure-key"
curl -X GET http://localhost:8765/commits -H "X-API-Key: dev-only-insecure-key"
```

## Security Note

⚠️ The default API key `dev-only-insecure-key` is for development only. The service binds to `127.0.0.1:8765` (localhost only) to prevent external access.

For production MCP, use the remote coordinator at `mcp.insightpulseai.net` with proper authentication.
