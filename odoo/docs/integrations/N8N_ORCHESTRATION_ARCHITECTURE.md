# n8n Orchestration Architecture

> Enterprise workflow automation connecting Plane, Odoo, Supabase, GitHub Enterprise, Slack, Figma, Vercel, and DigitalOcean

## Integration Hub Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                               n8n Workflow Engine                                    │
│                        (Self-Hosted on DigitalOcean)                                 │
│                                                                                       │
│  ┌────────────────┐   ┌────────────────┐   ┌────────────────┐   ┌────────────────┐ │
│  │  GitHub Nodes  │   │  Slack Nodes   │   │ Supabase Nodes │   │  HTTP Requests │ │
│  │  - Webhooks    │   │  - Messages    │   │  - Database    │   │  - Plane API   │ │
│  │  - Issues      │   │  - Channels    │   │  - Edge Funcs  │   │  - Odoo RPC    │ │
│  │  - PRs         │   │  - Notify      │   │  - Storage     │   │  - Figma API   │ │
│  └────────────────┘   └────────────────┘   └────────────────┘   └────────────────┘ │
│                                                                                       │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                         │
            ┌────────────────────────────┼────────────────────────────┐
            │                            │                            │
            ▼                            ▼                            ▼
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│   GitHub Enterprise │     │  Slack Workspace    │     │   Supabase Project  │
│                     │     │                     │     │  (spdtwktxdalcfigzeqrz)│
│ - Webhooks          │────▶│ - #compliance       │◀────│ - Edge Functions    │
│ - Issues            │     │ - #deployments      │     │ - ops.work_items    │
│ - PRs               │     │ - #operations       │     │ - ops.task_queue    │
│ - Actions           │     │ - DMs               │     │ - ops.platform_events│
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
            │                            │                            │
            │                            │                            │
            ▼                            ▼                            ▼
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│   Plane (fin-ops)   │     │   Odoo ERP 19.0     │     │  DigitalOcean Apps  │
│                     │     │                     │     │                     │
│ - Issues            │◀───▶│ - BIR Compliance    │────▶│ - n8n Instance      │
│ - Cycles            │     │ - Project Tasks     │     │ - Odoo Production   │
│ - Modules           │     │ - Pulser Connector  │     │ - Monitoring        │
│ - Webhooks          │     │ - XML-RPC API       │     │ - Backups           │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
            │                            │                            │
            │                            │                            │
            └────────────────────────────┼────────────────────────────┘
                                         │
                                         ▼
                          ┌─────────────────────────────────┐
                          │  Design & Deployment Pipeline   │
                          │                                 │
                          │  Figma ────▶ Vercel Deploy     │
                          │    │            │               │
                          │    └────────────┼──────────┐    │
                          │                 │          │    │
                          │           Supabase ◀── GitHub   │
                          └─────────────────────────────────┘
```

## Core Integration Patterns

### Pattern 1: Cross-Platform Task Sync (GitHub → Plane → Odoo)

**Trigger**: GitHub Enterprise issue created with label `bir:filing`

**Workflow**:
```
1. GitHub Webhook → n8n
2. n8n → Supabase Edge Function (plane-sync)
3. Edge Function → Plane API (create issue in fin-ops)
4. n8n → Odoo XML-RPC (create bir.filing.deadline)
5. n8n → Supabase (log to ops.work_items)
6. n8n → Slack (#compliance channel notification)
7. n8n → GitHub (add comment with Plane + Odoo links)
```

**Data Flow**:
```json
{
  "github_issue": {
    "id": 12345,
    "title": "[1601-C] March 2026 Withholding Tax",
    "labels": ["bir:filing", "priority:high"]
  },
  "plane_issue": {
    "id": "uuid-abc-123",
    "url": "https://plane.insightpulseai.com/fin-ops/issues/uuid-abc-123",
    "state": "backlog",
    "priority": "high"
  },
  "odoo_deadline": {
    "id": 456,
    "form_type": "1601-C",
    "deadline_date": "2026-04-10",
    "plane_sync_status": "synced"
  }
}
```

**Result**: Single issue synchronized across GitHub (development), Plane (project management), and Odoo (ERP compliance tracking).

---

### Pattern 2: Design to Deployment Pipeline (Figma → Vercel → Supabase)

**Trigger**: Figma design update webhook

**Workflow**:
```
1. Figma Webhook → n8n
2. n8n → Extract design tokens (colors, typography, spacing)
3. n8n → GitHub (commit tokens to design-system repo)
4. GitHub → Vercel (auto-deploy via GitHub integration)
5. n8n → Supabase (log deployment event)
6. n8n → Slack (#deployments notification)
```

**Use Case**: Designers update Figma → Tokens auto-commit → Vercel redeploys → Team notified.

---

### Pattern 3: Odoo Task Bus Orchestration (External → Odoo → Result)

**Trigger**: Slack slash command `/odoo-status`

**Workflow**:
```
1. Slack Slash Command → n8n
2. n8n → Supabase (insert intent to ops.taskbus_intents)
   {
     "intent_type": "odoo.modules.status",
     "args": {"module": "ipai_bir_plane_sync"}
   }
3. n8n → Wait 30 seconds (poll Supabase for completion)
4. Odoo cron → ipai_pulser_connector claims intent
5. Odoo → Execute module status check
6. Odoo → Write result to ops.taskbus_intents
7. n8n → Retrieve result from Supabase
8. n8n → Slack (DM user with status report)
```

**Benefits**: Non-blocking async execution, audit trail in Supabase, no direct Odoo access needed.

---

### Pattern 4: Scheduled BIR Compliance Reminders (Cron → Multi-System Notify)

**Trigger**: Daily cron at 9 AM Manila time

**Workflow**:
```
1. n8n Cron Trigger → Daily 9:00 AM +0800
2. n8n → Odoo XML-RPC (query deadlines due within 3 days)
3. For each deadline:
   a. n8n → Plane API (add comment to linked issue)
   b. n8n → Slack (#compliance channel reminder)
   c. n8n → GitHub (create issue if missing)
4. n8n → Supabase (log reminder events)
```

---

### Pattern 5: GitHub Actions → DigitalOcean Deployment → Monitoring

**Trigger**: GitHub push to `main` branch

**Workflow**:
```
1. GitHub Webhook → n8n
2. n8n → Trigger DigitalOcean App Platform deployment
3. n8n → Wait for deployment completion
4. n8n → Test deployment health (HTTP request to new endpoint)
5. n8n → Supabase (log deployment metrics)
6. n8n → Slack (#deployments with status)
7. If failure: n8n → Trigger rollback workflow
```

---

## Supabase Integration Capabilities

Based on the [Supabase Partners Integration catalog](https://supabase.com/partners/integrations), n8n provides:

### Available Supabase Operations

| Operation | n8n Node | Use Case |
|-----------|----------|----------|
| **Database CRUD** | Supabase Node | Query, insert, update, delete rows |
| **Edge Function Calls** | HTTP Request | Invoke serverless functions |
| **Realtime Subscriptions** | Supabase Trigger | Listen to database changes |
| **Storage Operations** | Supabase Node | Upload/download files |
| **Auth Management** | HTTP Request | User management, JWT verification |
| **PostgREST API** | HTTP Request | Direct database access via REST |

### Strategic Use Cases

1. **Event-Driven Architecture**:
   - Supabase Realtime → n8n → Multi-system propagation
   - Example: `ops.work_items` insert → notify Slack + update GitHub

2. **Audit Trail**:
   - All n8n workflows log to `ops.platform_events`
   - Provides complete cross-system activity history

3. **Task Queue**:
   - `ops.taskbus_intents` for async Odoo operations
   - n8n polls queue, Odoo cron processes

4. **Edge Function Orchestration**:
   - n8n calls Edge Functions for complex operations
   - Example: `plane-sync`, `github-webhook-handler`, `bir-compliance-check`

---

## n8n Deployment Strategy

### Self-Hosted on DigitalOcean

**Infrastructure**:
- **App**: n8n on DigitalOcean App Platform
- **Database**: PostgreSQL managed database (separate from Odoo)
- **Redis**: For queue management and session storage
- **Backups**: Daily automated backups to Spaces

**Configuration**:
```yaml
# DigitalOcean App Spec
name: n8n-insightpulseai
services:
  - name: n8n
    image:
      registry_type: DOCKER_HUB
      repository: n8nio/n8n
      tag: latest
    envs:
      - key: N8N_HOST
        value: n8n.insightpulseai.com
      - key: N8N_PROTOCOL
        value: https
      - key: WEBHOOK_URL
        value: https://n8n.insightpulseai.com/
      - key: DB_TYPE
        value: postgresdb
      - key: DB_POSTGRESDB_HOST
        value: ${db.HOSTNAME}
      - key: DB_POSTGRESDB_PORT
        value: ${db.PORT}
      - key: DB_POSTGRESDB_DATABASE
        value: ${db.DATABASE}
      - key: DB_POSTGRESDB_USER
        value: ${db.USERNAME}
      - key: DB_POSTGRESDB_PASSWORD
        value: ${db.PASSWORD}
    http_port: 5678
    instance_count: 1
    instance_size_slug: basic-xs
```

### Security Best Practices

1. **Credential Management**:
   - All API keys stored in n8n encrypted credentials store
   - Never hardcode secrets in workflow JSON
   - Use environment variables for infrastructure values

2. **Webhook Security**:
   - HMAC signature verification for GitHub/Plane webhooks
   - IP allowlisting for sensitive webhooks
   - Rate limiting via DigitalOcean App Platform

3. **Access Control**:
   - n8n Basic Auth or OAuth for UI access
   - Role-based workflow execution permissions
   - Audit logs for all workflow executions

---

## Integration Workflow Gallery

### 1. GitHub PR → Plane Sprint → Odoo Timesheet

**File**: `automations/n8n/workflows/github-pr-tracking.json`

**Flow**:
```
PR Opened → Extract estimate from description → Create Plane issue in current sprint
         → Create Odoo timesheet entry → Link all three → Notify Slack
```

### 2. Odoo Invoice → Supabase → Plane → Client Notification

**File**: `automations/n8n/workflows/odoo-invoice-client-notify.json`

**Flow**:
```
Odoo Invoice Created → Log to Supabase ops.accounting_events
                    → Create Plane issue (if milestone payment)
                    → Send Slack DM to account manager
                    → Email client via Mailgun (via Supabase Edge Function)
```

### 3. Figma Component Update → Design System Sync

**File**: `automations/n8n/workflows/figma-design-tokens-sync.json`

**Flow**:
```
Figma Webhook → Extract component tokens → Commit to GitHub design-system repo
             → Trigger Vercel deploy → Update Plane design backlog
             → Notify Slack #design-system
```

### 4. BIR Deadline Approaching → Multi-Channel Alert

**File**: `automations/n8n/workflows/bir-deadline-alerts.json`

**Flow**:
```
Daily Cron → Query Odoo for deadlines (2 days) → For each:
          → Update Plane issue priority to "urgent"
          → Add Plane comment with deadline reminder
          → Slack DM to finance team
          → GitHub issue if missing documentation
          → Supabase log alert event
```

### 5. GitHub Security Alert → Cross-Team Escalation

**File**: `automations/n8n/workflows/github-security-escalation.json`

**Flow**:
```
GitHub Security Advisory → Parse CVE details → Create Plane issue (security backlog)
                        → Slack #security channel (urgent)
                        → Odoo: Create project task for remediation
                        → Supabase: Log security event
                        → Email CTO via Mailgun
```

---

## Environment Variables Reference

All n8n workflows use environment variables for configuration:

```bash
# Odoo Integration
ODOO_URL=https://erp.insightpulseai.com
ODOO_DB=odoo
ODOO_USERNAME=admin
ODOO_PASSWORD=[from vault]
ODOO_PLANE_PROJECT_ID=1  # Odoo project.project ID for Plane tasks

# Plane Integration
PLANE_API_URL=https://plane.insightpulseai.com/api/v1
PLANE_API_KEY=plane_api_ec7bbd295de445518bca2c8788d5e941
PLANE_WORKSPACE_SLUG=fin-ops
PLANE_BIR_PROJECT_ID=dd0b3bd5-43e8-47ab-b3ad-279bb15d4778

# Supabase Integration
SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
SUPABASE_SERVICE_ROLE_KEY=[from vault]
SUPABASE_ANON_KEY=[from vault]

# GitHub Enterprise
GITHUB_API_URL=https://api.github.com
GITHUB_TOKEN=[from vault]
GITHUB_WEBHOOK_SECRET=[from vault]

# Slack Workspace
SLACK_BOT_TOKEN=[from vault]
SLACK_SIGNING_SECRET=[from vault]

# Figma
FIGMA_ACCESS_TOKEN=[from vault]

# Vercel
VERCEL_TOKEN=[from vault]
VERCEL_PROJECT_ID=[from Vercel dashboard]

# DigitalOcean
DIGITALOCEAN_TOKEN=[from vault]

# Mailgun (via Zoho Mail SMTP)
MAILGUN_API_KEY=[deprecated - use Zoho SMTP]
ZOHO_MAIL_SMTP_HOST=smtp.zoho.com
ZOHO_MAIL_SMTP_USER=no-reply@insightpulseai.com
ZOHO_MAIL_SMTP_PASSWORD=[from vault]
```

---

## Monitoring & Observability

### n8n Execution Dashboard

**Metrics Tracked**:
- Workflow execution count (success/failure)
- Average execution time per workflow
- Error rate by workflow
- Webhook response times

### Supabase Audit Trail

**Tables**:
- `ops.platform_events`: All cross-system events
- `ops.work_items`: Cross-platform entity linkage
- `ops.taskbus_intents`: Async task queue activity

**Query Example**:
```sql
-- Cross-platform task sync activity (last 24 hours)
SELECT
  pe.event_type,
  pe.source_system,
  wi.github_issue_id,
  wi.plane_issue_id,
  wi.odoo_task_id,
  pe.timestamp
FROM ops.platform_events pe
LEFT JOIN ops.work_items wi ON pe.event_data->>'work_item_id' = wi.id::text
WHERE pe.event_type = 'workflow.plane_odoo_github_sync'
  AND pe.timestamp > NOW() - INTERVAL '24 hours'
ORDER BY pe.timestamp DESC;
```

### Slack Alerting

**Channels**:
- `#n8n-alerts`: Workflow failures and errors
- `#deployments`: Deployment notifications
- `#compliance`: BIR deadline alerts
- `#security`: Security advisories and incidents

---

## Next Steps

1. ✅ **Review setup guide**: [`ODOO_PLANE_N8N_SETUP.md`](./ODOO_PLANE_N8N_SETUP.md)
2. ✅ **Deploy n8n on DigitalOcean**: Use App Platform 1-Click
3. ✅ **Import workflow**: [`plane-odoo-github-sync.json`](../../automations/n8n/workflows/plane-odoo-github-sync.json)
4. ✅ **Configure credentials**: Add all API tokens to n8n credentials store
5. ✅ **Test webhook**: Trigger GitHub issue creation → verify cross-system sync
6. ✅ **Monitor execution**: Check n8n execution dashboard + Supabase logs
7. ⏳ **Scale workflows**: Add additional patterns from workflow gallery

---

## Resources

| Resource | URL |
|----------|-----|
| n8n Documentation | https://docs.n8n.io/ |
| Supabase Integrations | https://supabase.com/partners/integrations |
| n8n Community Workflows | https://n8n.io/workflows/ |
| DigitalOcean App Platform | https://www.digitalocean.com/products/app-platform |
| Plane API Reference | https://developers.plane.so/api-reference/introduction |
| Odoo XML-RPC Guide | https://www.odoo.com/documentation/19.0/developer/reference/external_api.html |

---

**Last Updated**: 2026-03-05
**Status**: Architecture documented, workflows ready for deployment
**Next Action**: Deploy n8n on DigitalOcean and import first workflow
