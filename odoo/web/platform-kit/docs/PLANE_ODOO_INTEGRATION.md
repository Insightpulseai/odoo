# Plane ↔ Odoo Integration

> Bidirectional sync between Plane CE (project management) and Odoo (ERP) via Supabase Edge Functions.

---

## Overview

This integration enables:

- **Plane → Odoo**: Issues become Odoo tasks, projects sync to Odoo projects
- **Odoo → Plane**: Sales orders and invoices create visibility issues in Plane
- **Audit Trail**: All sync operations logged to `ops.events`
- **Conflict Resolution**: Configurable per entity type

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Plane CE   │────▶│  Supabase Edge   │────▶│      Odoo       │
│  (Issues)   │◀────│   (plane-sync)   │◀────│    (Tasks)      │
└─────────────┘     └──────────────────┘     └─────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  ops.events  │
                    │  plane.*     │
                    └──────────────┘
```

---

## Components

### 1. Edge Function: `plane-sync`

Location: `supabase/functions/plane-sync/index.ts`

**Endpoints:**

| Method | Query Params | Description |
|--------|-------------|-------------|
| POST | `?source=plane` | Handle Plane webhooks |
| POST | `?source=odoo` | Handle Odoo webhooks |
| GET | `?action=status` | Get sync status and recent activity |
| POST | `?action=sync` | Manual sync trigger |

### 2. Database Schema: `plane.*`

Location: `supabase/migrations/20260131002000_plane_sync_schema.sql`

**Tables:**

| Table | Purpose |
|-------|---------|
| `plane.sync_mappings` | Maps entities between Plane and Odoo |
| `plane.sync_queue` | Queue for pending/retry operations |
| `plane.sync_config` | Configuration per entity type |
| `plane.sync_log` | Detailed operation log |

### 3. n8n Workflow (Optional)

Location: `infra/n8n/plane-odoo-sync.workflow.json`

Provides:
- Webhook receivers for Plane and Odoo
- Status monitoring every 5 minutes
- Slack alerts for sync errors

---

## Setup

### 1. Deploy Database Migration

```bash
supabase db push
```

### 2. Configure Environment Variables

Set in Supabase Dashboard or via CLI:

```bash
supabase secrets set \
  PLANE_API_URL="https://plane.your-domain.com" \
  PLANE_API_KEY="your-plane-api-key" \
  PLANE_WEBHOOK_SECRET="your-webhook-secret" \
  ODOO_WEBHOOK_SECRET="your-odoo-webhook-secret"
```

### 3. Deploy Edge Function

```bash
supabase functions deploy plane-sync
```

### 4. Configure Plane Webhooks

In Plane CE admin:

1. Go to **Settings → Webhooks**
2. Add webhook URL: `https://<project>.supabase.co/functions/v1/plane-sync?source=plane`
3. Select events: `issue.created`, `issue.updated`, `issue.deleted`, `project.created`, `project.updated`
4. Set secret key matching `PLANE_WEBHOOK_SECRET`

### 5. Configure Odoo Webhooks

In Odoo (via custom module or automation):

```python
# Example Odoo webhook trigger
import requests
import hmac
import hashlib

def trigger_sync(model, action, data):
    url = "https://<project>.supabase.co/functions/v1/plane-sync?source=odoo"
    payload = {"model": model, "action": action, "data": data}
    body = json.dumps(payload)

    signature = hmac.new(
        ODOO_WEBHOOK_SECRET.encode(),
        body.encode(),
        hashlib.sha256
    ).hexdigest()

    requests.post(url, json=payload, headers={
        "X-Odoo-Signature": signature,
        "Content-Type": "application/json"
    })
```

---

## Entity Mappings

### Plane → Odoo

| Plane Entity | Odoo Model | Notes |
|--------------|------------|-------|
| `issue` | `project.task` | Bidirectional |
| `project` | `project.project` | Bidirectional |
| `cycle` | `project.milestone` | One-way |
| `module` | `project.project` | Maps to sub-project |

### Odoo → Plane

| Odoo Model | Plane Entity | Notes |
|------------|--------------|-------|
| `project.task` | `issue` | Bidirectional |
| `project.project` | `project` | Bidirectional |
| `sale.order` | `issue` | Creates visibility issue |
| `account.move` | `issue` | Creates visibility issue |

### Field Mappings

```sql
-- Default field mappings (in plane.sync_config)
{
  "name": "name",
  "description": "description",
  "priority": "priority",
  "state": "stage_id"
}
```

### Priority Mapping

| Plane | Odoo |
|-------|------|
| `urgent` | `3` |
| `high` | `2` |
| `medium` | `1` |
| `low` | `0` |
| `none` | `0` |

---

## Conflict Resolution

Configure in `plane.sync_config`:

| Strategy | Description |
|----------|-------------|
| `latest_wins` | Most recent update wins (default) |
| `plane_wins` | Plane is source of truth |
| `odoo_wins` | Odoo is source of truth |
| `manual` | Create conflict for manual resolution |

---

## Monitoring

### Check Sync Status

```bash
curl -H "Authorization: Bearer $SERVICE_KEY" \
  "https://<project>.supabase.co/functions/v1/plane-sync?action=status"
```

### View Sync Mappings

```sql
SELECT * FROM plane.v_active_syncs;
```

### View Pending Queue

```sql
SELECT * FROM plane.v_pending_queue;
```

### View Sync Statistics

```sql
SELECT * FROM plane.v_sync_stats;
```

### Recent Sync Events

```sql
SELECT * FROM ops.events
WHERE category = 'plane-sync'
ORDER BY created_at DESC
LIMIT 20;
```

---

## Troubleshooting

### Sync Not Working

1. Check Edge Function logs:
   ```bash
   supabase functions logs plane-sync
   ```

2. Verify webhook signatures are correct

3. Check for errors in sync queue:
   ```sql
   SELECT * FROM plane.sync_queue WHERE status = 'failed';
   ```

### Duplicate Records

1. Check for existing mappings:
   ```sql
   SELECT * FROM plane.sync_mappings
   WHERE source_id = 'your-id';
   ```

2. Clear and re-sync if needed:
   ```sql
   DELETE FROM plane.sync_mappings WHERE source_id = 'your-id';
   ```

### Rate Limiting

If hitting Plane or Odoo rate limits:

1. Increase retry backoff in `plane.sync_queue`
2. Reduce sync frequency in n8n workflow

---

## Security

### Webhook Verification

Both Plane and Odoo webhooks are verified using HMAC-SHA256:

- `X-Plane-Signature` header for Plane webhooks
- `X-Odoo-Signature` header for Odoo webhooks

### RLS Policies

- Service role: Full access
- Authenticated users: Read-only access to mappings and config

### Audit Trail

All sync operations are logged to:
- `plane.sync_log` - Detailed sync operations
- `ops.events` - General event stream (category: `plane-sync`)

---

## Advanced Configuration

### Custom Field Mappings

Update `plane.sync_config`:

```sql
UPDATE plane.sync_config
SET field_mappings = '{
  "name": "name",
  "description": "description",
  "priority": "priority",
  "state": "stage_id",
  "x_custom_field": "custom_field_plane"
}'::jsonb
WHERE plane_type = 'issue' AND odoo_model = 'project.task';
```

### Disable Sync for Entity Type

```sql
UPDATE plane.sync_config
SET enabled = false
WHERE plane_type = 'cycle';
```

### Change Sync Direction

```sql
UPDATE plane.sync_config
SET direction = 'plane_to_odoo'  -- or 'odoo_to_plane', 'bidirectional'
WHERE plane_type = 'issue';
```

---

## Related Documentation

- [CANONICAL_ARCHITECTURE.md](./CANONICAL_ARCHITECTURE.md) - Overall system architecture
- [GOVERNANCE.md](./GOVERNANCE.md) - SSOT/SoR boundaries
- [supabase/ARCHITECTURE.md](../supabase/ARCHITECTURE.md) - Schema details
