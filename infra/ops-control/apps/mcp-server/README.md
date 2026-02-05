# Ops Control Room MCP Server

ChatGPT App backend for the Ops Control Room runbook executor.

## 🎯 What This Does

Exposes two MCP tools that ChatGPT can call:

1. **`plan_runbook(prompt)`** → Parse natural language to structured plan
2. **`execute_runbook(runbook_id)`** → Execute plan and stream events

## 🏃 Local Development

### 1. Install Dependencies
```bash
pnpm install
```

### 2. Run in Development Mode
```bash
pnpm dev
```

### 3. Test with MCP Inspector
```bash
npx @modelcontextprotocol/inspector pnpm dev
```

This will open the MCP Inspector UI where you can:
- List available tools
- Call `plan_runbook` with test prompts
- Call `execute_runbook` to see event streams

## 🚀 Deployment

### Option 1: Railway

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login and initialize:**
   ```bash
   railway login
   railway init
   ```

3. **Deploy:**
   ```bash
   railway up
   ```

4. **Get the public URL:**
   ```bash
   railway domain
   ```

### Option 2: Fly.io

1. **Install Fly CLI:**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Create app:**
   ```bash
   fly launch
   ```

3. **Deploy:**
   ```bash
   fly deploy
   ```

### Option 3: Vercel (with Edge Functions)

1. **Add `vercel.json`:**
   ```json
   {
     "functions": {
       "api/mcp.ts": {
         "runtime": "edge"
       }
     }
   }
   ```

2. **Deploy:**
   ```bash
   vercel
   ```

## 🔌 Connect to ChatGPT

1. **Get your deployed URL** (e.g., `https://your-app.railway.app`)

2. **Open ChatGPT Settings:**
   - Go to Settings → Apps
   - Click "Add MCP Server"

3. **Configure connector:**
   ```json
   {
     "url": "https://your-app.railway.app/mcp",
     "name": "Ops Control Room",
     "description": "Runbook executor for deployments, health checks, and incidents"
   }
   ```

4. **Test in ChatGPT:**
   ```
   User: Deploy prod
   
   ChatGPT calls plan_runbook("Deploy prod")
   → Shows inline runbook card
   
   User clicks "Run"
   
   ChatGPT calls execute_runbook(runbook_id)
   → Shows fullscreen log viewer
   ```

## 🛠️ Tool Schemas

### plan_runbook

**Input:**
```json
{
  "prompt": "Deploy prod"
}
```

**Output:**
```json
{
  "id": "deploy_1234567890",
  "kind": "deploy",
  "title": "Deploy to production",
  "summary": "Deploy prod environment (build, migrate, verify).",
  "inputs": [
    { "key": "env", "label": "Environment", "type": "select", "value": "prod" },
    { "key": "repo", "label": "Repo", "type": "text", "value": "jgtolentino/odoo-ce" },
    { "key": "target", "label": "Target", "type": "text", "value": "vercel" }
  ],
  "risks": [
    { "level": "warn", "code": "PROD_CHANGE", "message": "Production deployment will modify live services." }
  ],
  "integrations": ["GitHub", "Vercel", "Supabase"]
}
```

### execute_runbook

**Input:**
```json
{
  "runbook_id": "deploy_1234567890"
}
```

**Output (stream):**
```json
[
  {
    "ts": "2026-01-03T10:30:00.000Z",
    "level": "info",
    "source": "System",
    "message": "Starting deploy execution..."
  },
  {
    "ts": "2026-01-03T10:30:03.000Z",
    "level": "success",
    "source": "Vercel",
    "message": "✓ Build completed (3.2s)"
  }
]
```

## 🔐 Environment Variables

Add these to your deployment environment:

```bash
# Integration API Keys (replace with real values)
VERCEL_TOKEN=your_vercel_token
SUPABASE_SERVICE_KEY=your_supabase_key
GITHUB_TOKEN=your_github_token
DO_API_TOKEN=your_digitalocean_token

# Optional: Logging
LOG_LEVEL=info
```

## 🧪 Testing

### Unit Tests (TODO)
```bash
pnpm test
```

### Integration Tests with Real APIs (TODO)
```bash
VERCEL_TOKEN=xxx pnpm test:integration
```

### Manual Testing with MCP Inspector
```bash
npx @modelcontextprotocol/inspector pnpm dev
```

## 📊 Monitoring

### Add Logging
Use structured logging for production:

```typescript
import { logger } from "./logger";

logger.info("Runbook executed", { 
  runbook_id: plan.id, 
  duration_ms: elapsed 
});
```

### Add Metrics
Track execution counts, success rates, latency:

```typescript
metrics.increment("runbook.executed", { kind: plan.kind });
metrics.histogram("runbook.duration", elapsed, { kind: plan.kind });
```

## 🐛 Debugging

### Enable Debug Logging
```bash
LOG_LEVEL=debug pnpm dev
```

### Test Tool Calls Locally
```bash
# Start server
pnpm dev

# In another terminal, send a test request
echo '{"method":"tools/call","params":{"name":"plan_runbook","arguments":{"prompt":"deploy prod"}}}' | pnpm dev
```

### Common Issues

**"Unknown tool" error:**
- Check tool registration in `server.setRequestHandler(ListToolsRequestSchema)`

**"Invalid input" error:**
- Validate input schema matches the Zod schema
- Check `args` destructuring in `CallToolRequestSchema` handler

**Timeout errors:**
- Increase timeout in deployment config
- Add streaming for long-running executions

## 🔄 Next Steps

- [ ] Add real API integrations (Vercel, Supabase, GitHub)
- [ ] Implement runbook persistence (SQLite/Postgres)
- [ ] Add authentication middleware
- [ ] Add rate limiting
- [ ] Add webhook listeners for async events
- [ ] Add approval workflows for high-risk runbooks
- [ ] Add rollback capabilities
- [ ] Generate ChatGPT widget HTML for inline cards

## 📚 Resources

- [MCP SDK Documentation](https://github.com/modelcontextprotocol/sdk)
- [ChatGPT Apps Guide](https://platform.openai.com/docs/chatgpt-apps)
- [MCP Inspector Tool](https://github.com/modelcontextprotocol/inspector)

---

**Ready to deploy?** Follow the deployment guide above and connect to ChatGPT!
