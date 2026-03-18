# Installation Guide

## Prerequisites

- Node.js >= 18.0.0
- pnpm (recommended) or npm
- n8n instance with Public API enabled
- n8n API key

## Step 1: Clone and Install

```bash
cd agents/mcp/n8n-api-bridge
pnpm install
```

## Step 2: Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and set:

```bash
N8N_BASE_URL=https://your-n8n-instance.com
N8N_API_KEY=your-api-key-here
ALLOW_MUTATIONS=false  # Set to true only in trusted environments
```

### Getting Your n8n API Key

1. Log in to your n8n instance
2. Click your profile icon → **Settings**
3. Navigate to **API** section
4. Click **Create API Key**
5. Copy the key and paste it into `.env`

## Step 3: Build and Test

```bash
# Type check
pnpm typecheck

# Run tests
pnpm test

# Build
pnpm build
```

## Step 4: Run Server

### Development Mode

```bash
pnpm dev
```

### Production Mode

```bash
pnpm start
```

## Step 5: Configure MCP Client

### For Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "n8n": {
      "command": "node",
      "args": ["/absolute/path/to/odoo/agents/mcp/n8n-api-bridge/dist/index.js"],
      "env": {
        "N8N_BASE_URL": "https://n8n.insightpulseai.com",
        "N8N_API_KEY": "your-api-key-here",
        "ALLOW_MUTATIONS": "false"
      }
    }
  }
}
```

### For Claude Code

Add to MCP server configuration:

```json
{
  "n8n-bridge": {
    "command": "node",
    "args": ["/absolute/path/to/odoo/agents/mcp/n8n-api-bridge/dist/index.js"],
    "env": {
      "N8N_BASE_URL": "https://n8n.insightpulseai.com",
      "N8N_API_KEY": "your-api-key-here",
      "ALLOW_MUTATIONS": "false"
    }
  }
}
```

## Step 6: Verify Installation

After restarting your MCP client, verify the server is working:

### List Available Tools

The MCP client should show 10 available tools:

- `n8n_list_workflows`
- `n8n_get_workflow`
- `n8n_activate_workflow`
- `n8n_deactivate_workflow`
- `n8n_trigger_workflow`
- `n8n_list_executions`
- `n8n_get_execution`
- `n8n_delete_execution`
- `n8n_list_credentials`
- `n8n_list_tags`

### Test Read Operations

Ask Claude:

```
Can you list my n8n workflows?
```

Expected response: JSON list of workflows from your n8n instance.

### Test Write Operations (if enabled)

If `ALLOW_MUTATIONS=true`, ask Claude:

```
Can you trigger workflow [workflow-id]?
```

Expected response: Execution details showing the workflow started.

## Troubleshooting

### "N8N_API_KEY is required" Error

- Verify `.env` file exists
- Check API key is not the placeholder value
- Ensure `.env` is in the correct directory

### "Permission denied" Errors

- Check `ALLOW_MUTATIONS` is set to `true` for write operations
- Verify API key has sufficient permissions in n8n

### Connection Timeout

- Verify `N8N_BASE_URL` is correct and accessible
- Check network connectivity to n8n instance
- Increase `REQUEST_TIMEOUT` if needed

### "Unknown tool" Errors

- Restart MCP client after configuration changes
- Verify `dist/index.js` exists (run `pnpm build`)
- Check MCP client logs for startup errors

## Security Best Practices

1. **Use Read-Only Mode by Default**
   - Keep `ALLOW_MUTATIONS=false` unless write operations are needed
   - Create separate API keys for read vs write access

2. **Protect API Keys**
   - Never commit `.env` to version control
   - Use environment-specific API keys
   - Rotate keys regularly

3. **Network Security**
   - Use HTTPS for n8n instance
   - Consider VPN or IP whitelisting for production
   - Monitor API usage through n8n audit logs

4. **Minimal Permissions**
   - Use n8n's credential sharing to limit API key access
   - Grant only necessary permissions per environment

## Next Steps

- Read [README.md](./README.md) for tool documentation
- Explore [examples/](./examples/) for usage patterns
- Check [src/types.ts](./src/types.ts) for API types
