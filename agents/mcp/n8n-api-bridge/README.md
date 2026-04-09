# n8n MCP Bridge

Model Context Protocol (MCP) server providing Claude.ai with programmatic access to the n8n Public API for workflow automation and monitoring.

---

## Overview

The n8n MCP Bridge enables AI agents (particularly Claude) to interact with n8n workflows through a standardized MCP interface. This bridge provides:

- **Read Operations**: List workflows, view executions, inspect workflow details
- **Write Operations**: Retry failed executions, trigger workflows (when mutations enabled)
- **AI Agent Tools**: Discover and execute n8n AI agent tools (jiraTool, notionTool, Odoo/Supabase tools)
- **Audit Logging**: Track AI agent interactions with n8n for compliance
- **Security Controls**: Environment-based mutation guards prevent accidental changes

**Use Cases:**
- Monitor workflow execution status and troubleshoot failures
- Analyze workflow performance and execution history
- Automate workflow retry logic for transient failures
- **NEW:** Execute AI-powered workflows with LLM context (support automation, knowledge base queries, sentiment analysis)
- **NEW:** Discover and integrate with n8n LangChain AI agents and tools
- Maintain audit trails of AI-assisted workflow operations

---

## Architecture

```
┌─────────────────┐
│   Claude.ai     │
│  (MCP Client)   │
└────────┬────────┘
         │ MCP Protocol (stdio/HTTP)
         ▼
┌─────────────────┐
│  n8n MCP Bridge │
│   (This Server) │
│                 │
│  ┌───────────┐  │
│  │  Config   │  │
│  │  Loader   │  │
│  └─────┬─────┘  │
│        │        │
│  ┌─────▼─────┐  │
│  │ n8n Client│  │
│  └─────┬─────┘  │
│        │        │
│  ┌─────▼─────┐  │
│  │   Tools   │  │
│  │ Registry  │  │
│  └───────────┘  │
└────────┬────────┘
         │ HTTPS + API Key
         ▼
┌─────────────────┐
│  n8n Public API │
│ (n8n.insightpulseai.com) │
└─────────────────┘
```

**Flow:**
1. Claude sends MCP request via stdio transport
2. Bridge validates parameters using Zod schemas
3. n8n Client adds authentication (X-N8N-API-KEY header)
4. Bridge enforces mutation guards (ALLOW_MUTATIONS check)
5. HTTP request to n8n Public API
6. Response formatted as MCP tool result
7. Claude receives structured JSON response

---

## Setup

### Prerequisites

- **Node.js**: >= 18.0.0
- **n8n Instance**: Running with Public API enabled
- **n8n API Key**: Generated from n8n user settings
- **pnpm**: Package manager (or npm/yarn)

### Installation

```bash
# Navigate to bridge directory
cd agents/mcp/n8n-api-bridge

# Install dependencies
pnpm install

# Build TypeScript
pnpm build
```

### Environment Configuration

1. **Copy example configuration:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your values:**
   ```bash
   # n8n Public API Configuration
   N8N_BASE_URL=https://n8n.insightpulseai.com
   N8N_API_KEY=n8n_api_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

   # Security: Set to 'true' only in trusted environments
   ALLOW_MUTATIONS=false

   # MCP Server Configuration
   MCP_PORT=3100
   MCP_LOG_LEVEL=info

   # Optional: Request timeout in milliseconds
   REQUEST_TIMEOUT=30000
   ```

3. **Obtain n8n API Key:**
   - Log in to your n8n instance
   - Navigate to: Settings → API
   - Click "Create API Key"
   - Copy the generated key (format: `n8n_api_...`)

### Starting the Server

**Development mode (with auto-reload):**
```bash
pnpm dev
```

**Production mode:**
```bash
pnpm build
pnpm start
```

**Expected output:**
```
[INFO] Starting n8n MCP Bridge Server
[INFO] n8n API: https://n8n.insightpulseai.com
[INFO] Mutations allowed: false
[INFO] n8n MCP Bridge Server ready
[INFO] Registered 5 tools
```

---

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `N8N_BASE_URL` | ✅ Yes | - | n8n instance URL (e.g., `https://n8n.insightpulseai.com`) |
| `N8N_API_KEY` | ✅ Yes | - | n8n Public API key (format: `n8n_api_...`) |
| `ALLOW_MUTATIONS` | No | `false` | Enable write operations (activate, trigger, retry) |
| `MCP_PORT` | No | `3100` | MCP server port (stdio mode ignores this) |
| `MCP_LOG_LEVEL` | No | `info` | Log verbosity: `debug`, `info`, `warn`, `error` |
| `REQUEST_TIMEOUT` | No | `30000` | n8n API request timeout in milliseconds |

### Security: ALLOW_MUTATIONS

**⚠️ CRITICAL SECURITY CONTROL**

The `ALLOW_MUTATIONS` flag determines whether the bridge can modify n8n state:

**When `ALLOW_MUTATIONS=false` (default - SAFE):**
- ✅ Read operations: List workflows, view executions, get workflow details
- ✅ Audit logging: Track events without modification
- ❌ Write operations: Retry execution (blocked)

**When `ALLOW_MUTATIONS=true` (DANGEROUS):**
- ✅ All read operations
- ✅ All write operations: Retry failed executions
- ⚠️ **Risk**: AI agent can trigger workflow re-execution

**Best Practices:**
- **Development/Testing**: Set `false`, use read-only monitoring
- **Production (trusted AI)**: Set `true` only if AI has approval to retry workflows
- **Shared environments**: Always use `false`
- **Audit trail**: Enable n8n audit logging when mutations are on

### Port Configuration

**MCP_PORT** is for future HTTP transport support. Currently, the bridge uses **stdio transport** (communicates via stdin/stdout), so port configuration is ignored but reserved for backward compatibility.

---

## Available Tools

All tools return structured JSON responses with `success`, `data`, `error` fields.

### Read Operations (Always Available)

| Tool | Description | Parameters | Example |
|------|-------------|------------|---------|
| `n8n.list_workflows` | List all workflows with metadata | `limit?` (1-100), `cursor?` | List first 10 workflows |
| `n8n.get_workflow` | Get complete workflow definition | `id` (string) | View workflow nodes and connections |
| `n8n.list_executions` | List execution history | `limit?` (1-100), `workflowId?`, `cursor?` | Find recent failed executions |
| `n8n.get_execution` | Get execution details and logs | `id` (string) | Inspect error messages from failed run |
| `n8n.audit` | Log audit event (read-only logging) | `event` (category, action, metadata) | Track AI workflow interactions |

### Write Operations (Requires ALLOW_MUTATIONS=true)

| Tool | Description | Parameters | Example |
|------|-------------|------------|---------|
| `n8n.retry_execution` | Retry a failed execution | `id` (string) | Re-run failed workflow with same input |

---

## Claude.ai Integration

### Adding to Claude Desktop App

1. **Open Claude Desktop settings:**
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. **Add MCP server configuration:**
   ```json
   {
     "mcpServers": {
       "n8n-bridge": {
         "command": "node",
         "args": [
           "/absolute/path/to/agents/mcp/n8n-api-bridge/dist/index.js"
         ],
         "env": {
           "N8N_BASE_URL": "https://n8n.insightpulseai.com",
           "N8N_API_KEY": "n8n_api_xxxxxxxx",
           "ALLOW_MUTATIONS": "false",
           "MCP_LOG_LEVEL": "info"
         }
       }
     }
   }
   ```

3. **Restart Claude Desktop**

4. **Verify connection:**
   - Start a new conversation
   - Ask: "List available n8n tools"
   - Claude should respond with tool names and descriptions

### Remote MCP Server (Future)

For HTTP transport (not yet implemented):

```json
{
  "mcpServers": {
    "n8n-bridge": {
      "url": "https://mcp.insightpulseai.com/n8n",
      "headers": {
        "Authorization": "Bearer YOUR_MCP_TOKEN"
      }
    }
  }
}
```

### Example Queries to Test

**Read-only operations (safe):**
```
"Show me the last 5 n8n workflows"
"Get details for workflow ID abc123"
"List failed executions in the last hour"
"What went wrong with execution xyz789?"
"Log an audit event for workflow review"
```

**Write operations (requires ALLOW_MUTATIONS=true):**
```
"Retry the failed execution xyz789"
```

**Expected responses:**
- Successful tool call returns structured JSON with workflow/execution data
- Failed tool call returns error message with HTTP status code
- Mutation blocked returns: `"Permission denied: Mutation operation 'retryExecution' is disabled. Set ALLOW_MUTATIONS=true to enable."`

---

## Development

### Project Structure

```
agents/mcp/n8n-api-bridge/
├── src/
│   ├── index.ts          # MCP server entry point
│   ├── config.ts         # Environment validation
│   ├── client.ts         # n8n API client
│   ├── n8nClient.ts      # Legacy client (deprecated)
│   ├── types.ts          # TypeScript types and Zod schemas
│   └── tools.ts          # MCP tool definitions
├── dist/                 # Compiled JavaScript (generated)
├── package.json          # Dependencies and scripts
├── tsconfig.json         # TypeScript configuration
├── .env.example          # Example environment configuration
└── README.md             # This file
```

### Running in Dev Mode

```bash
# Watch mode with auto-reload
pnpm dev

# Typecheck without compilation
pnpm typecheck

# Lint TypeScript code
pnpm lint
```

### Testing

```bash
# Run tests (when implemented)
pnpm test

# Watch mode for tests
pnpm test:watch
```

### Adding New Tools

1. **Define Zod schema in `types.ts`:**
   ```typescript
   export const NewToolParamsSchema = z.object({
     param1: z.string().describe('Description'),
     param2: z.number().optional(),
   });

   export type NewToolParams = z.infer<typeof NewToolParamsSchema>;
   ```

2. **Add n8n Client method in `client.ts`:**
   ```typescript
   async newOperation(params: NewToolParams): Promise<ResponseType> {
     // Mutation guard if needed
     if (params.modifiesState) {
       this.checkMutationsAllowed('newOperation');
     }

     return this.request<ResponseType>('POST', '/api/v1/resource', params);
   }
   ```

3. **Register tool in `tools.ts`:**
   ```typescript
   {
     name: 'n8n.new_operation',
     description: 'What this tool does',
     inputSchema: NewToolParamsSchema,
     handler: async (params) => {
       const result = await client.newOperation(params);
       return { success: true, data: result };
     },
   }
   ```

4. **Test the tool:**
   ```bash
   pnpm build
   pnpm start
   # Test with Claude or MCP test harness
   ```

---

## Troubleshooting

### Common Errors

#### 1. Authentication Failed (HTTP 401)

**Error:**
```
n8n API error: Authentication failed: Invalid API key (HTTP 401)
```

**Causes:**
- Incorrect `N8N_API_KEY` in `.env`
- API key expired or revoked
- Wrong n8n instance URL

**Fix:**
1. Verify API key format: `n8n_api_...`
2. Regenerate API key in n8n Settings → API
3. Check `N8N_BASE_URL` matches your instance
4. Test API key manually:
   ```bash
   curl -H "X-N8N-API-KEY: your_key_here" \
        https://n8n.insightpulseai.com/api/v1/workflows
   ```

#### 2. Mutations Disabled

**Error:**
```
Permission denied: Mutation operation 'retryExecution' is disabled. Set ALLOW_MUTATIONS=true to enable.
```

**Cause:**
- `ALLOW_MUTATIONS=false` in `.env` (default)

**Fix:**
1. **If intentional**: This is the expected behavior for read-only mode
2. **If unintentional**: Edit `.env` and set `ALLOW_MUTATIONS=true`
3. Restart the server: `pnpm start`

#### 3. Configuration Error on Startup

**Error:**
```
Configuration error: N8N_API_KEY is required. Set a valid API key in .env file.
```

**Cause:**
- Missing or placeholder API key in `.env`

**Fix:**
1. Ensure `.env` exists (copy from `.env.example`)
2. Replace `__REPLACE_WITH_YOUR_API_KEY__` with real API key
3. Verify no whitespace around `=` in `.env` file

#### 4. Network Error

**Error:**
```
Network error: connect ECONNREFUSED 127.0.0.1:5678
```

**Causes:**
- n8n instance not running
- Wrong `N8N_BASE_URL` (e.g., localhost when should be domain)
- Firewall blocking connection

**Fix:**
1. Verify n8n is running: `curl https://n8n.insightpulseai.com/healthz`
2. Check URL format: Must include `https://` and no trailing slash
3. Test connectivity: `ping n8n.insightpulseai.com`

#### 5. MCP Connection Timeout

**Symptom:**
- Claude Desktop shows "MCP server not responding"
- No tool list appears

**Causes:**
- Server crashed on startup
- Invalid TypeScript compilation
- Missing dependencies

**Fix:**
1. Check server logs: `pnpm start` (look for errors)
2. Rebuild: `pnpm build`
3. Verify dependencies: `pnpm install`
4. Check Claude Desktop logs:
   - macOS: `~/Library/Logs/Claude/mcp-server-n8n-bridge.log`

### Debugging Tips

**Enable debug logging:**
```bash
# In .env
MCP_LOG_LEVEL=debug
```

**Manual API testing:**
```bash
# Test workflow list
curl -H "X-N8N-API-KEY: $N8N_API_KEY" \
     https://n8n.insightpulseai.com/api/v1/workflows

# Test execution list
curl -H "X-N8N-API-KEY: $N8N_API_KEY" \
     https://n8n.insightpulseai.com/api/v1/executions
```

**Check environment variables are loaded:**
```typescript
// Add to index.ts temporarily
console.error('ENV CHECK:', {
  baseUrl: process.env.N8N_BASE_URL,
  apiKeyPresent: !!process.env.N8N_API_KEY,
  mutations: process.env.ALLOW_MUTATIONS,
});
```

**Validate Zod schemas:**
```typescript
// Test parameter validation
const result = ListWorkflowsParamsSchema.safeParse({ limit: 150 });
console.error(result.success ? 'Valid' : result.error);
```

---

## Security

### API Key Storage

**❌ NEVER:**
- Commit `.env` file to Git (already in `.gitignore`)
- Hardcode API keys in source code
- Share API keys in chat/email
- Use production keys in development

**✅ ALWAYS:**
- Store API key in `.env` (local development)
- Use environment variables in production
- Rotate API keys quarterly
- Use separate keys for dev/staging/production
- Revoke keys immediately if compromised

### Mutation Controls

**Defense-in-depth approach:**

1. **Environment flag**: `ALLOW_MUTATIONS=false` default
2. **Client-side guard**: `checkMutationsAllowed()` method
3. **Tool registration**: Write tools only added if mutations enabled
4. **n8n permissions**: API key should have minimal required permissions

**Recommended permission levels:**
- **Read-only monitoring**: n8n "Viewer" role API key
- **Limited write**: n8n "Editor" role with workflow restrictions
- **Full access**: n8n "Admin" role (use with extreme caution)

### Rate Limiting Considerations

**n8n Public API limits (as of 2024):**
- **Rate limit**: Varies by n8n version and hosting (cloud vs self-hosted)
- **Typical limits**: 120 requests/minute per API key
- **Burst allowance**: Usually 2x rate limit for short bursts

**Bridge-side mitigation:**
- `REQUEST_TIMEOUT` prevents hung requests (default 30s)
- Pagination via `limit` parameter (max 250 per request)
- Cursor-based pagination prevents duplicate processing

**Best practices:**
- Batch operations when possible
- Use `cursor` for large result sets
- Monitor 429 (Rate Limit) responses
- Implement exponential backoff in client code if needed

### Audit Logging

**What gets logged:**
- All tool invocations (via MCP server logs)
- n8n API requests/responses (debug level)
- Authentication failures
- Mutation operations (always logged)

**Audit event tool:**
```typescript
// Log AI interaction
await tools.call('n8n.audit', {
  event: {
    category: 'workflow',
    action: 'reviewed_by_ai',
    metadata: {
      workflowId: 'abc123',
      agent: 'claude',
      timestamp: new Date().toISOString(),
    }
  }
});
```

**Compliance considerations:**
- Audit events stored in n8n database
- Queryable via n8n UI or database
- Retain logs per organizational policy
- Export for SIEM integration if needed

---

## License

Apache-2.0

---

## Support

**Issues:**
- GitHub: [Insightpulseai/odoo](https://github.com/Insightpulseai/odoo)
- Path: `agents/mcp/n8n-api-bridge/`

**Documentation:**
- [n8n Public API Reference](https://docs.n8n.io/api/)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Claude MCP Integration Guide](https://docs.anthropic.com/en/docs/model-context-protocol)

**Related Projects:**
- n8n: https://n8n.io
- Model Context Protocol: https://modelcontextprotocol.io
- Anthropic Claude: https://claude.ai
