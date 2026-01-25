# Marketplace Integrations

This document describes the marketplace integrations architecture for connecting external services (Google Workspace, AWS S3, GitHub, etc.) with the Odoo CE platform using Supabase as the control plane.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Marketplace Integrations Control Plane                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   External Services                                                      │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│   │  GitHub  │  │  Google  │  │   AWS    │  │  Slack   │              │
│   │ Actions  │  │Workspace │  │   S3/R2  │  │          │              │
│   └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘              │
│        │             │             │             │                      │
│        └──────┬──────┴──────┬──────┴──────┬──────┘                      │
│               ▼             ▼             ▼                              │
│   ┌─────────────────────────────────────────────────────────┐          │
│   │              Supabase Edge Function                      │          │
│   │           (marketplace-webhook handler)                  │          │
│   └─────────────────────┬───────────────────────────────────┘          │
│                         │                                                │
│   ┌─────────────────────▼───────────────────────────────────┐          │
│   │                 Supabase PostgreSQL                      │          │
│   │   ┌─────────────────────────────────────────────────┐   │          │
│   │   │           marketplace schema                     │   │          │
│   │   │  • integrations (registry)                       │   │          │
│   │   │  • oauth_tokens (Vault references)               │   │          │
│   │   │  • webhook_events (event log)                    │   │          │
│   │   │  • artifact_syncs (sync tracking)                │   │          │
│   │   │  • sync_rules (automation rules)                 │   │          │
│   │   │  • api_quotas (rate limiting)                    │   │          │
│   │   └─────────────────────────────────────────────────┘   │          │
│   └─────────────────────┬───────────────────────────────────┘          │
│                         │                                                │
│               ┌─────────┴─────────┐                                      │
│               ▼                   ▼                                      │
│   ┌───────────────────┐  ┌───────────────────┐                         │
│   │   n8n Workflows   │  │   Cron Workers    │                         │
│   │  (orchestration)  │  │ (scheduled syncs) │                         │
│   └─────────┬─────────┘  └─────────┬─────────┘                         │
│             │                      │                                    │
│             └──────────┬───────────┘                                    │
│                        ▼                                                │
│   ┌─────────────────────────────────────────────────────────┐          │
│   │            Destination Services                          │          │
│   │   • Google Drive (artifacts, reports)                    │          │
│   │   • AWS S3 / Cloudflare R2 (backups, archives)          │          │
│   │   • GitHub (specs, PRDs, code)                           │          │
│   │   • Odoo CE (data sync)                                  │          │
│   └─────────────────────────────────────────────────────────┘          │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Supabase Schema (`marketplace`)

The `marketplace` schema provides centralized storage for integration management:

| Table | Purpose |
|-------|---------|
| `integrations` | Registry of configured integrations (providers, configs, status) |
| `oauth_tokens` | OAuth credential references (actual tokens in Vault) |
| `webhook_events` | Incoming webhook event log with deduplication |
| `artifact_syncs` | Track artifact synchronization between services |
| `sync_rules` | Define automatic sync rules with patterns/templates |
| `api_quotas` | Track API quota usage per integration |

### 2. Edge Function (`marketplace-webhook`)

Handles incoming webhooks from external services:

- **GitHub**: `workflow_run`, `push`, `release` events
- **Google Drive**: File change notifications
- **Google Docs**: Document edit webhooks
- **AWS S3**: Object events via SNS
- **Slack**: Event API callbacks

**Endpoint pattern**: `/marketplace-webhook/{provider}`

Example:
```bash
# GitHub webhook endpoint
https://<project>.supabase.co/functions/v1/marketplace-webhook/github

# Google Drive webhook endpoint
https://<project>.supabase.co/functions/v1/marketplace-webhook/google-drive
```

### 3. n8n Workflows

Two primary workflows for artifact synchronization:

#### GitHub Artifacts Mirror (`github-artifacts-mirror.json`)

Mirrors GitHub Actions artifacts to Google Drive and S3:

```
GitHub Webhook → Verify Signature → Fetch Artifacts → Download
                                                         ↓
                    ┌────────────────────────────────────┴────────────────────────────────────┐
                    ↓                                                                          ↓
            Upload to Drive                                                             Upload to S3
                    ↓                                                                          ↓
            Log to Supabase                                                            Log to Supabase
                    └────────────────────────────────────┬────────────────────────────────────┘
                                                         ↓
                                                   Notify Slack
```

#### Workspace Events Handler (`workspace-events-handler.json`)

Processes Google Workspace events and routes to appropriate handlers:

```
Workspace Webhook → Parse Event → Log to Supabase → Route by Source
                                                          ↓
                    ┌───────────────────────────────┬─────┴─────┬───────────────────────────────┐
                    ↓                               ↓           ↓                               ↓
             Handle Drive                    Handle Docs   Handle Gmail                 Handle Sheets
                    ↓                               ↓           ↓                               ↓
             Download File                  Export to MD   Create Task                   Sync Data
                    ↓                               ↓
             Log Sync                        Log Sync
```

## Configuration

### Environment Variables

Required environment variables for the integration system:

```bash
# Supabase
SUPABASE_URL=https://<project>.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<service_role_key>

# GitHub
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
GITHUB_WEBHOOK_SECRET=<webhook_secret>

# Google (OAuth2)
GOOGLE_CLIENT_ID=<client_id>
GOOGLE_CLIENT_SECRET=<client_secret>
GOOGLE_DRIVE_ARTIFACTS_FOLDER_ID=<folder_id>

# AWS S3
AWS_ACCESS_KEY_ID=<access_key>
AWS_SECRET_ACCESS_KEY=<secret_key>
AWS_S3_ARTIFACTS_BUCKET=<bucket_name>
AWS_REGION=us-east-1

# Slack
SLACK_BOT_TOKEN=xoxb-xxxxxxxxxxxx
SLACK_ARTIFACTS_CHANNEL=#ci-artifacts
```

### Registering Integrations

Use the `marketplace.register_integration` function to add new integrations:

```sql
-- Register GitHub Actions integration
SELECT marketplace.register_integration(
    'github-actions',
    'GitHub Actions',
    'github',
    'automation',
    '{"api_base": "https://api.github.com", "default_org": "Insightpulseai-net"}'::JSONB
);

-- Register Google Drive integration
SELECT marketplace.register_integration(
    'google-drive',
    'Google Drive',
    'google_drive',
    'storage',
    '{"api_base": "https://www.googleapis.com/drive/v3"}'::JSONB
);
```

### Creating Sync Rules

Define automatic sync rules for artifact mirroring:

```sql
-- Sync GitHub artifacts to Google Drive
INSERT INTO marketplace.sync_rules (
    name,
    description,
    source_integration_id,
    source_pattern,
    destination_integration_id,
    destination_template,
    artifact_types,
    priority
) VALUES (
    'GitHub Artifacts to Drive',
    'Mirror GitHub Actions artifacts to Google Drive',
    (SELECT id FROM marketplace.integrations WHERE slug = 'github-actions'),
    'artifacts/*',
    (SELECT id FROM marketplace.integrations WHERE slug = 'google-drive'),
    'CI-Artifacts/{date}/{workflow}/{name}',
    ARRAY['zip', 'pdf', 'json'],
    5
);
```

## Usage Patterns

### 1. Artifact Mirroring (GitHub → Drive/S3)

When a GitHub workflow completes successfully:

1. GitHub sends `workflow_run` webhook to Edge Function
2. Edge Function verifies signature and logs event
3. Matching sync rules are evaluated
4. n8n workflow downloads artifacts and uploads to destinations
5. Sync status is tracked in `marketplace.artifact_syncs`

### 2. Document Sync (Google Docs → GitHub)

When a spec/PRD document is edited:

1. Google Docs triggers change webhook
2. Edge Function logs event and identifies document type
3. n8n workflow exports document as Markdown
4. GitOps runner commits changes to repository

### 3. Email to Task (Gmail → Task System)

When an email arrives with specific labels:

1. Gmail push notification triggers webhook
2. Edge Function logs notification
3. n8n workflow fetches email details
4. Task is created in Odoo or project management system

## Monitoring

### Health Check

```bash
curl https://<project>.supabase.co/functions/v1/marketplace-webhook/health
```

### Integration Health View

```sql
SELECT * FROM marketplace.v_integration_health;
```

### Recent Syncs

```sql
SELECT * FROM marketplace.v_recent_syncs LIMIT 20;
```

### Quota Status

```sql
SELECT * FROM marketplace.v_quota_status WHERE usage_percent > 75;
```

## Security

### OAuth Token Management

- OAuth tokens are stored in Supabase Vault
- Only token references are stored in `oauth_tokens` table
- Tokens are refreshed automatically before expiration
- Service role access only for sensitive operations

### Webhook Verification

- GitHub: HMAC-SHA256 signature verification
- Google: Channel token verification
- S3: SNS signature verification

### Row Level Security

- Service role: Full access to all tables
- Authenticated users: Read-only access to non-sensitive data
- OAuth tokens: Service role only (no authenticated access)

## Troubleshooting

### Common Issues

1. **Webhook not receiving events**
   - Verify webhook URL is publicly accessible
   - Check webhook secret configuration
   - Review Edge Function logs in Supabase dashboard

2. **Artifact sync failing**
   - Check OAuth token expiration
   - Verify destination permissions (Drive folder, S3 bucket)
   - Review `marketplace.artifact_syncs` for error messages

3. **Rate limiting**
   - Check `marketplace.api_quotas` for usage
   - Implement exponential backoff in n8n workflows
   - Consider batch processing for large sync operations

### Debug Queries

```sql
-- Check pending webhook events
SELECT * FROM marketplace.webhook_events
WHERE NOT processed
ORDER BY created_at DESC
LIMIT 10;

-- Check failed syncs
SELECT * FROM marketplace.artifact_syncs
WHERE status = 'failed'
ORDER BY created_at DESC
LIMIT 10;

-- Check integration errors
SELECT slug, name, status, health_status, error_message
FROM marketplace.integrations
WHERE status = 'error' OR health_status = 'unhealthy';
```

## Related Documentation

- [MCP Jobs System](../infra/MCP_JOBS_SYSTEM.md) - Job queue backend
- [n8n Workflows](../../n8n/README.md) - Workflow automation
- [Supabase Functions](../../supabase/functions/README.md) - Edge Function reference
