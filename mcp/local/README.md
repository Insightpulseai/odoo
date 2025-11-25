# Local MCP Server

SQLite-backed MCP server for local Odoo development with Claude memory and commit embeddings.

## Features

- **Skills Registry**: Local development skills (dev, testing, stable, approved status)
- **RAG Embeddings**: Local corpora for experimentation
- **Claude Memory**: Conversation history with context links
- **Commit Embeddings**: Extensible like CLAUDE.md but embedded in SQLite
- **Session Context**: Current workspace state tracking

## Quick Start

### 1. Build and Start

```bash
# Start with docker-compose
docker-compose -f docker-compose.prod.yml -f docker-compose.mcp-local.yml up -d mcp-local

# Check logs
docker logs -f ipai-mcp-local

# Verify health
curl http://localhost:8765/health
```

### 2. Check Status

```bash
curl -H "X-API-Key: dev-only-insecure-key" \
  http://localhost:8765/status | jq
```

### 3. List Skills

```bash
curl -H "X-API-Key: dev-only-insecure-key" \
  http://localhost:8765/skills | jq
```

## Database Structure

Three SQLite databases in `./data/sqlite/`:

- **mcp_skills.db**: Skills metadata registry
- **mcp_rag.db**: RAG embeddings for local corpora
- **mcp_memory.db**: Conversations, commits, context links

## API Endpoints

### Skills

- `GET /skills` - List skills (filter by `?status=dev`)
- `POST /skills` - Create/update skill

### Conversations (Claude Memory)

- `GET /conversations` - List conversations (filter by `?session_id=xxx`)
- `POST /conversations` - Save conversation

### Commits

- `GET /commits` - List indexed commits (filter by `?author=xxx`)

### Odoo Integration

- `GET /odoo/models` - List Odoo models from lab instance (TODO)

## VS Code Integration

Use the `mcp-dev` workspace:

```bash
code .vscode/mcp-dev.code-workspace
```

This workspace:
- Connects to local MCP (port 8765) with priority 1
- Connects to remote MCP (mcp.insightpulseai.net) as fallback
- Sets `ODOO_INSTANCE=odoo_lab` for development

## Development

### Add a New Skill

```bash
curl -X POST http://localhost:8765/skills \
  -H "X-API-Key: dev-only-insecure-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-new-skill",
    "version": "0.1.0",
    "status": "dev",
    "metadata": {
      "description": "My experimental skill",
      "triggers": ["keyword1", "keyword2"]
    },
    "file_path": "skills/my-new-skill.yaml"
  }'
```

### Save a Conversation

```bash
curl -X POST http://localhost:8765/conversations \
  -H "X-API-Key: dev-only-insecure-key" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "my-session-123",
    "user_id": "user@example.com",
    "messages": [
      {"role": "user", "content": "How do I create an Odoo module?"},
      {"role": "assistant", "content": "Here's how to create an Odoo module..."}
    ],
    "context": {
      "workspace": "/Users/tbwa/odoo-ce",
      "files": ["addons/ipai_expense/__manifest__.py"]
    },
    "summary": "User asked about Odoo module creation"
  }'
```

## Configuration

Environment variables (set in `docker-compose.mcp-local.yml`):

- `MCP_LOCAL_API_KEY` - API key for endpoints (default: dev-only-insecure-key)
- `ODOO_LAB_URL` - Odoo lab instance URL (default: http://odoo:8069)
- `ODOO_LAB_DB` - Odoo database name (default: odoo)
- `ODOO_LAB_USERNAME` - Odoo username (default: admin)
- `ODOO_LAB_PASSWORD` - Odoo password (from .env.production)

## Data Persistence

SQLite databases persist in `./data/sqlite/` (gitignored).

**To reset all data:**

```bash
docker-compose -f docker-compose.mcp-local.yml down
rm -rf mcp/local/data/sqlite/*.db
docker-compose -f docker-compose.prod.yml -f docker-compose.mcp-local.yml up -d mcp-local
```

## Next Steps

1. Implement embedding generation (sentence-transformers)
2. Add commit indexing from git history
3. Implement Odoo XML-RPC client
4. Add RAG query endpoints with vector similarity
5. Implement context link generation
6. Add skill promotion workflow (dev → testing → stable)

## Architecture

```
Local MCP Server (port 8765)
    ↓
SQLite Databases
    ├── mcp_skills.db (skills metadata)
    ├── mcp_rag.db (RAG embeddings)
    └── mcp_memory.db (conversations + commits)
    ↓
Odoo Lab Instance (http://odoo:8069)
    └── OCA modules + custom addons
```

## Security

⚠️ **This is a development-only service:**

- Default API key is insecure
- Binds to localhost only (127.0.0.1:8765)
- Conversation history is local-only (never synced to production)
- For production MCP, use the remote coordinator at `mcp.insightpulseai.net`
