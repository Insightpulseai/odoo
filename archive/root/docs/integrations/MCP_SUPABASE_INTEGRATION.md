# MCP + Supabase Integration Architecture

This document describes the enhanced integration between Claude MCP, n8n, Supabase, and GitHub.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Claude Code / MCP Client                        │
└─────────────────────────────────────────┬───────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    Supabase Edge Functions                              │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │ MCP Gateway  │ │ Cron         │ │ GitHub App   │ │ GitHub-MM    │   │
│  │ (middleware) │ │ Processor    │ │ Auth         │ │ Bridge       │   │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘   │
└─────────────────────────────────────────┬───────────────────────────────┘
                                          │
                    ┌─────────────────────┼─────────────────────┐
                    ▼                     ▼                     ▼
           ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
           │   Supabase    │     │   Supabase    │     │   Supabase    │
           │   Queues      │     │   Webhooks    │     │   Vault       │
           │   (PGMQ)      │     │   (pg_net)    │     │   (secrets)   │
           └───────────────┘     └───────────────┘     └───────────────┘
                    │                     │                     │
                    ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                              n8n Workflows                              │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │ Git Ops      │ │ MCP Worker   │ │ GitHub Event │ │ BIR Alerts   │   │
│  │ Workflow     │ │ Workflow     │ │ Handler      │ │ Cron         │   │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                          │
                    ┌─────────────────────┼─────────────────────┐
                    ▼                     ▼                     ▼
           ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
           │   GitHub      │     │   Mattermost  │     │   Odoo ERP    │
           │   API         │     │   Webhooks    │     │   JSON-RPC    │
           └───────────────┘     └───────────────┘     └───────────────┘
```

## Edge Functions

### 1. MCP Gateway (`/functions/v1/mcp-gateway`)

Central middleware for all MCP operations with:
- **Authentication**: API key or JWT validation
- **Rate Limiting**: Per-action limits (100 executions/hour, 500 searches/hour)
- **Routing**: Routes to appropriate n8n workflows
- **Queueing**: Low-priority jobs go to PGMQ queue

```bash
# Example: Execute workflow
curl -X POST https://YOUR_PROJECT.supabase.co/functions/v1/mcp-gateway \
  -H "x-api-key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "execute_workflow",
    "workflow_id": "finance-hub",
    "payload": {"action": "health_check"},
    "priority": "normal"
  }'
```

### 2. Cron Processor (`/functions/v1/cron-processor`)

Replaces n8n scheduleTrigger with more reliable Supabase-managed cron:

```bash
# List all cron jobs
curl https://YOUR_PROJECT.supabase.co/functions/v1/cron-processor/jobs

# Register a new job
curl -X POST https://YOUR_PROJECT.supabase.co/functions/v1/cron-processor/register \
  -d '{
    "name": "daily-report",
    "schedule": "0 9 * * *",
    "workflow_id": "daily-report",
    "payload": {}
  }'

# Manually trigger a job
curl -X POST https://YOUR_PROJECT.supabase.co/functions/v1/cron-processor/trigger \
  -d '{"job_name": "bir-deadline-alerts"}'
```

### 3. GitHub App Auth (`/functions/v1/github-app-auth`)

OAuth and installation token management for pulser-hub GitHub App:

```bash
# Start OAuth flow
curl https://YOUR_PROJECT.supabase.co/functions/v1/github-app-auth/authorize

# Get installation token (for API calls)
curl -X POST https://YOUR_PROJECT.supabase.co/functions/v1/github-app-auth/installation-token \
  -d '{"installation_id": "12345678"}'

# List repos the app can access
curl -X POST https://YOUR_PROJECT.supabase.co/functions/v1/github-app-auth/repos \
  -d '{"installation_id": "12345678"}'
```

### 4. GitHub-Mattermost Bridge (`/functions/v1/github-mattermost-bridge`)

Routes GitHub events to Mattermost channels (like GitHub + Slack):

| Event | Channel | Emoji |
|-------|---------|-------|
| `push` | `#dev-commits` | 📤 |
| `pull_request` | `#dev-prs` | 🆕/🎉/❌ |
| `issues` | `#dev-issues` | 🆕/✅ |
| `release` | `#releases` | 🚀 |
| `workflow_run` | `#ci-cd` | ✅/❌ |
| `deployment` | `#deployments` | 🚀 |

## Supabase Integrations

### Queues (PGMQ)

Available queues:
- `mcp_operations` - MCP gateway async jobs
- `git_operations` - Git commands
- `workflow_executions` - n8n triggers
- `notifications` - Mattermost/email
- `sync_events` - Realtime sync

```sql
-- Send a message
SELECT queue_send('mcp_operations', '{"action": "execute", "workflow": "test"}'::jsonb);

-- Read messages (for workers)
SELECT * FROM queue_read('mcp_operations', 10, 30);

-- Acknowledge processed message
SELECT queue_ack('mcp_operations', 12345);

-- Get queue stats
SELECT * FROM queue_stats();
```

### Database Webhooks

Automatic n8n triggers on database changes:

| Table | Event | Webhook |
|-------|-------|---------|
| `mcp_job_queue` | Complete/Fail | `/webhook/mcp-job-status` |
| `github_webhook_events` | Insert | `/webhook/github-event` |
| `cron_executions` | Failure | `/webhook/cron-alert` |

### Vault (Secrets)

Store sensitive data encrypted:

```sql
-- Store a secret
SELECT store_secret('github_private_key', '-----BEGIN...', 'GitHub App Key');

-- Retrieve in functions
SELECT get_secret('github_private_key');
```

## n8n Workflows

### Git Operations (`/webhook/git-operations`)

```json
{
  "operation": "push",      // clone, status, pull, push, commit
  "repo_path": "/workspace/repo",
  "branch": "main",
  "message": "Update from MCP"
}
```

### MCP Worker (`/webhook/mcp-execute`)

Processes queued MCP jobs from the gateway.

## Database Tables

### Core Tables

| Table | Purpose |
|-------|---------|
| `mcp_job_queue` | Async job queue |
| `mcp_request_log` | Request audit trail |
| `api_keys` | API key authentication |
| `cron_jobs` | Cron job definitions |
| `cron_executions` | Execution history |

### GitHub Tables

| Table | Purpose |
|-------|---------|
| `github_installations` | App installations |
| `github_installation_tokens` | Cached access tokens |
| `github_oauth_tokens` | User OAuth tokens |
| `github_webhook_events` | Webhook event log |
| `github_mattermost_messages` | Mattermost message log |

## Environment Variables

Required for edge functions:

```bash
# Supabase (automatic)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...

# GitHub App
GITHUB_APP_ID=2191216
GITHUB_CLIENT_ID=Iv23liwGL7fnYySPPAjS
GITHUB_CLIENT_SECRET=xxx
GITHUB_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----..."
GITHUB_CALLBACK_URL=https://mcp.insightpulseai.com/callback

# n8n
N8N_WEBHOOK_URL=https://n8n.insightpulseai.com

# Mattermost
MATTERMOST_WEBHOOK_URL=https://mattermost.example.com/hooks/xxx
```

## Setup Steps

1. **Deploy migrations**:
   ```bash
   supabase db push
   ```

2. **Deploy edge functions**:
   ```bash
   supabase functions deploy mcp-gateway
   supabase functions deploy cron-processor
   supabase functions deploy github-app-auth
   supabase functions deploy github-mattermost-bridge
   ```

3. **Set secrets**:
   ```bash
   supabase secrets set GITHUB_PRIVATE_KEY="$(cat private-key.pem)"
   supabase secrets set GITHUB_CLIENT_SECRET="xxx"
   supabase secrets set MATTERMOST_WEBHOOK_URL="https://..."
   ```

4. **Enable pg_cron** (in Supabase dashboard):
   ```sql
   SELECT cron.schedule(
     'mcp-cron-processor',
     '* * * * *',
     $$SELECT net.http_post(...)$$
   );
   ```

5. **Update GitHub App webhook**:
   - URL: `https://YOUR_PROJECT.supabase.co/functions/v1/github-mattermost-bridge`

6. **Import n8n workflows**:
   - `workflows/n8n/git-operations-workflow.json`

## Monitoring

### Queue Health
```sql
SELECT * FROM queue_stats();
SELECT * FROM get_mcp_queue_stats();
```

### Cron Status
```bash
curl https://YOUR_PROJECT.supabase.co/functions/v1/cron-processor/status
```

### Recent Errors
```sql
SELECT * FROM mcp_request_log WHERE status = 'error' ORDER BY created_at DESC LIMIT 10;
SELECT * FROM cron_executions WHERE status = 'failed' ORDER BY started_at DESC LIMIT 10;
```
