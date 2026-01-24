# Supabase Integration Architecture

## Overview

Supabase serves as the transactional + auth + realtime backbone for the InsightPulse platform, providing 7 core services that integrate with Odoo CE, Control Room, n8n, and Databricks.

## Supabase Products Mapping

| Product | Purpose | Use in Pipeline |
|---------|---------|-----------------|
| Database | PostgreSQL + Realtime | Control Room schemas, KB, audit trails |
| Auth | Identity management | User auth + RLS enforcement |
| Storage | S3-compatible files | Documents, diagrams, reports |
| Realtime | WebSocket pub/sub | Live dashboards, approval flows |
| Edge Functions | Serverless functions | Webhooks, API middleware |
| AI & Vectors | pgvector embeddings | Semantic KB search |
| Cron & Queues | Scheduled jobs | Medallion refresh, async processing |

## Schema Overview

```sql
-- Core Identity (Supabase Auth)
auth.users (id, email, raw_user_meta_data)

-- Odoo Integration
odoo_users (auth_user_id, odoo_user_id, odoo_login)

-- Control Room
control_room_jobs (id, name, job_type, status, created_by)

-- Knowledge Base
kb_spaces (id, name, description, created_by)
kb_artifacts (id, space_id, kind, title, content, personas, tags)
kb_artifact_relations (source_id, target_id, relation_type)

-- Data Lineage
data_assets (id, catalog, schema_name, table_name, sla_hours)
data_lineage_edges (source_id, target_id, relation_type, job_id)

-- Approvals
approval_requests (id, request_type, ref_id, status, assigned_to)

-- Audit
audit_log (action, table_name, record_id, changed_by, old/new_values)
```

## Row Level Security

```sql
-- Jobs: Only creator sees their jobs
CREATE POLICY job_owner_access ON control_room_jobs
  USING (created_by = auth.uid() OR auth.jwt()->>'role' = 'admin');

-- KB: Only matching personas see artifacts
CREATE POLICY kb_persona_access ON kb_artifacts
  USING (
    (auth.jwt()->>'persona_tags')::TEXT[] && personas::TEXT[]
    OR created_by = auth.uid()
  );

-- Approvals: Manager or creator access
CREATE POLICY approval_access ON approval_requests
  USING (
    assigned_to = auth.uid()
    OR created_by = auth.uid()
    OR auth.jwt()->>'role' = 'manager'
  );
```

## Integration Stack

### Critical Integrations
- **n8n**: Workflow automation hub
- **Prisma**: Type-safe ORM for Node.js
- **Clerk/Auth0**: Enterprise SSO (optional)
- **Vercel**: Control Room deployment

### Data Integrations
- **ClickHouse**: OLAP analytics (optional)
- **BigQuery Wrapper**: Cross-system queries

### Frontend Acceleration
- **Retool/Plasmic**: Low-code dashboards
- **FlutterFlow**: Mobile app builder

## Realtime Subscriptions

```typescript
// Control Room: Live job status updates
import { useRealtimeSubscription } from '@supabase/react'

export function JobDashboard() {
  const { data: jobs } = useRealtimeSubscription(
    'control_room_jobs',
    { event: '*' },
    (payload) => {
      // Update React state on change
    }
  )
  // ...
}
```

## Edge Functions

```typescript
// Webhook handler for n8n
// supabase/functions/n8n-webhook/index.ts

import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'

serve(async (req) => {
  const { job_id, status } = await req.json()

  // Update job record
  await supabase
    .from('control_room_jobs')
    .update({ status, completed_at: new Date() })
    .eq('id', job_id)

  // Broadcast notification
  await supabase.channel('job-notifications').send({
    type: 'broadcast',
    event: 'job_completed',
    payload: { job_id, status }
  })

  return new Response(JSON.stringify({ ok: true }))
})
```

## Deployment Options

### Option 1: Supabase SaaS
- Cost: $25-500/month
- Maintenance: Zero
- Best for: Rapid prototyping

### Option 2: Self-Hosted (Recommended)
- Cost: ~$155/month on DigitalOcean
- Components: PostgreSQL 15, PostgREST, Gotrue, Realtime
- Best for: Enterprise compliance, data sovereignty

## Cost Summary

| Component | SaaS | Self-Hosted |
|-----------|------|-------------|
| Supabase | $25-500/mo | $155/mo |
| n8n | $20-120/mo | $0 |
| Mattermost | $10/user/mo | $0 |
| **Total** | $55-620/mo | **$155/mo** |

## Branching (Preview Environments)

Supabase Branching creates isolated preview environments for each git branch, enabling safe testing of database migrations and Edge Functions before deploying to production.

### How It Works

1. **Create branch**: Push to `feature/*`, `claude/*`, or `fix/*` branches
2. **Preview created**: Supabase automatically creates an isolated environment
3. **Test changes**: Each preview has its own database, Auth, and Edge Functions
4. **Merge to main**: Changes deploy to production automatically
5. **Cleanup**: Preview branch is deleted after PR merge

### Branch Architecture

```
main (Production)
├── feature/add-new-api     → Preview: feature-add-new-api.supabase.co
├── claude/fix-auth-issue   → Preview: claude-fix-auth-issue.supabase.co
└── fix/migration-rollback  → Preview: fix-migration-rollback.supabase.co
```

### Environment Variables for Preview

When working with a preview branch, update environment variables:

```bash
# Production
SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
NEXT_PUBLIC_SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co

# Preview branch (example)
SUPABASE_URL=https://preview-abc123.supabase.co
NEXT_PUBLIC_SUPABASE_URL=https://preview-abc123.supabase.co
```

### Seed Data

Preview branches are seeded automatically using `supabase/seed.sql`:
- Core tenants, roles, and users
- ERP integration demo data
- AI agent configurations
- Sample finance data (expenses, budgets, approvals)

### Workflow Configuration

See `.github/workflows/supabase-branching.yml` for the complete CI/CD pipeline:
- Validates migrations before applying
- Deploys Edge Functions to preview
- Posts preview URLs to PR comments
- Cleans up branches on merge

### Manual Branch Operations

```bash
# List branches
supabase branches list

# Create branch manually
supabase branches create my-feature

# Delete branch
supabase branches delete my-feature --confirm

# Reset branch (re-apply migrations + seed)
supabase db reset
```

### Prerequisites

1. **Enable GitHub Integration**: Dashboard > Project Settings > Integrations
2. **Enable Branching**: Dashboard > Project Settings > Branching
3. **Configure Secrets**: `SUPABASE_ACCESS_TOKEN`, `SUPABASE_PROJECT_REF`

### Limitations

- Preview branches don't include production data (by design)
- Custom database roles created via dashboard aren't captured
- Branches can only merge to main (not between previews)
- Iteration field values require manual UI setup (GitHub API limitation)

### Pricing

Preview branches are billed per hour of compute usage:
- Micro Compute: ~$0.01344/hour ($10/month if always running)
- Preview branches auto-pause after 7 days of inactivity
- Usage counts toward subscription quota

## Related Documentation

- [Supabase Docs](https://supabase.com/docs)
- [Supabase Branching](https://supabase.com/docs/guides/deployment/branching)
- [Migrations](../supabase/migrations/)
- [Control Room API](../apps/control-room/)
- [n8n Workflows](../workflows/n8n/)
