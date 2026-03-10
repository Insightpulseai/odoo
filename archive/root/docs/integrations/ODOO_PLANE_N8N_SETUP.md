# Odoo ↔ Plane ↔ n8n Integration Setup

> Complete configuration guide for integrating Odoo ERP with Plane project management via n8n workflows and Supabase Edge Functions.

## Prerequisites

- ✅ Plane API credentials configured (already done: `PLANE_API_KEY`, `PLANE_WORKSPACE_SLUG`)
- ✅ Plane MCP server registered (already done: `.claude/mcp-servers.json`)
- ⏳ Supabase Edge Function deployment
- ⏳ Odoo module activation
- ⏳ n8n workflow creation

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Integration Stack                            │
│                                                                  │
│  Odoo ERP ←→ Supabase Edge Functions ←→ Plane API              │
│      ↑              ↓                         ↓                  │
│      │      ops.taskbus_intents          fin-ops project         │
│      │              ↓                                            │
│      └──────── n8n Workflows ─────────────────┘                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Part 1: Activate ipai_bir_plane_sync Module

### Step 1: Update Module Manifest

**File**: `addons/ipai/ipai_bir_plane_sync/__manifest__.py`

Change `"installable": False` to `"installable": True`:

```python
{
    "name": "IPAI BIR Plane Sync",
    # ...
    "installable": True,  # ← Change this
    # ...
}
```

### Step 2: Configure Odoo System Parameters

Add these parameters to Odoo via Settings → Technical → Parameters → System Parameters:

| Key | Value | Description |
|-----|-------|-------------|
| `supabase.url` | `https://spdtwktxdalcfigzeqrz.supabase.co` | Supabase project URL |
| `supabase.service_role_key` | `[from Supabase Vault]` | Service role key for Edge Functions |
| `plane.workspace_slug` | `fin-ops` | Plane workspace slug |
| `plane.bir_project_id` | `dd0b3bd5-43e8-47ab-b3ad-279bb15d4778` | Plane project UUID for BIR tracking |

**Security Note**: Store `supabase.service_role_key` in Supabase Vault, retrieve via Edge Function.

### Step 3: Install Module

```bash
# Via Odoo CLI
./scripts/odoo_update.sh -d odoo -i ipai_bir_plane_sync

# Or via Odoo UI
# Apps → Update Apps List → Search "IPAI BIR Plane Sync" → Install
```

### Step 4: Verify Installation

```python
# Test in Odoo shell
./scripts/odoo_shell.sh -d odoo

>>> env['bir.filing.deadline']._is_plane_sync_enabled()
True  # Should return True if configured correctly
```

---

## Part 2: Deploy Supabase Edge Function

### Create Edge Function: plane-sync

**File**: `supabase/functions/plane-sync/index.ts`

```typescript
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

serve(async (req) => {
  try {
    const { action, entity_type, entity_id, plane_issue_id, data } = await req.json()

    // Get Plane API credentials from environment
    const PLANE_API_URL = Deno.env.get("PLANE_API_URL") || "https://plane.insightpulseai.com/api/v1"
    const PLANE_API_KEY = Deno.env.get("PLANE_API_KEY")
    const PLANE_WORKSPACE_SLUG = Deno.env.get("PLANE_WORKSPACE_SLUG") || "fin-ops"
    const PLANE_PROJECT_ID = Deno.env.get("PLANE_BIR_PROJECT_ID")

    if (!PLANE_API_KEY || !PLANE_PROJECT_ID) {
      throw new Error("Missing Plane API credentials")
    }

    let planeResponse
    if (action === "create") {
      // Create new Plane issue
      const url = `${PLANE_API_URL}/workspaces/${PLANE_WORKSPACE_SLUG}/projects/${PLANE_PROJECT_ID}/issues/`
      planeResponse = await fetch(url, {
        method: "POST",
        headers: {
          "X-API-Key": PLANE_API_KEY,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      })
    } else if (action === "update" && plane_issue_id) {
      // Update existing Plane issue
      const url = `${PLANE_API_URL}/workspaces/${PLANE_WORKSPACE_SLUG}/projects/${PLANE_PROJECT_ID}/issues/${plane_issue_id}/`
      planeResponse = await fetch(url, {
        method: "PATCH",
        headers: {
          "X-API-Key": PLANE_API_KEY,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      })
    }

    if (!planeResponse.ok) {
      const errorText = await planeResponse.text()
      throw new Error(`Plane API error: ${planeResponse.status} ${errorText}`)
    }

    const result = await planeResponse.json()

    return new Response(
      JSON.stringify({
        success: true,
        plane_issue_id: result.id,
        plane_issue_url: `https://plane.insightpulseai.com/${PLANE_WORKSPACE_SLUG}/projects/${PLANE_PROJECT_ID}/issues/${result.id}`,
      }),
      {
        headers: { "Content-Type": "application/json" },
      }
    )
  } catch (error) {
    return new Response(
      JSON.stringify({ success: false, error: error.message }),
      {
        status: 500,
        headers: { "Content-Type": "application/json" },
      }
    )
  }
})
```

### Deploy Edge Function

```bash
# Deploy to Supabase
supabase functions deploy plane-sync --project-ref spdtwktxdalcfigzeqrz

# Set environment variables in Supabase Dashboard
# Functions → plane-sync → Settings → Environment Variables:
# - PLANE_API_URL=https://plane.insightpulseai.com/api/v1
# - PLANE_API_KEY=plane_api_ec7bbd295de445518bca2c8788d5e941
# - PLANE_WORKSPACE_SLUG=fin-ops
# - PLANE_BIR_PROJECT_ID=dd0b3bd5-43e8-47ab-b3ad-279bb15d4778
```

### Test Edge Function

```bash
curl -X POST \
  "https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/plane-sync?source=odoo" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "create",
    "entity_type": "bir.filing.deadline",
    "entity_id": 123,
    "data": {
      "name": "[1601-C] Test Filing",
      "description": "Test sync from Odoo",
      "state": "backlog",
      "priority": "high",
      "labels": ["area:compliance", "form:1601-c"],
      "due_date": "2026-03-10"
    }
  }'
```

---

## Part 3: Configure Plane Webhooks (Bidirectional Sync)

### Create Plane Webhook

1. Go to Plane: `https://plane.insightpulseai.com/fin-ops/settings/webhooks`
2. Click **Create Webhook**
3. Configure:
   - **Name**: Odoo BIR Sync Webhook
   - **URL**: `https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/plane-webhook-odoo`
   - **Events**: Issue Updated, Issue State Changed
   - **Secret**: Generate random secret, store in Supabase Vault

### Create Webhook Handler Edge Function

**File**: `supabase/functions/plane-webhook-odoo/index.ts`

```typescript
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

serve(async (req) => {
  try {
    const payload = await req.json()

    // Verify webhook signature (optional but recommended)
    const signature = req.headers.get("X-Plane-Signature")
    // ... signature verification logic

    // Extract issue data
    const issueId = payload.issue?.id
    const state = payload.issue?.state?.name

    if (!issueId) {
      throw new Error("Missing issue ID")
    }

    // Call Odoo XML-RPC to update deadline
    const ODOO_URL = Deno.env.get("ODOO_URL") || "https://erp.insightpulseai.com"
    const ODOO_DB = Deno.env.get("ODOO_DB") || "odoo"
    const ODOO_USERNAME = Deno.env.get("ODOO_USERNAME")
    const ODOO_PASSWORD = Deno.env.get("ODOO_PASSWORD")

    // Authenticate with Odoo
    // ... Odoo XML-RPC authentication
    // Call bir.filing.deadline.handle_plane_webhook method
    // ... method call

    return new Response(
      JSON.stringify({ success: true }),
      { headers: { "Content-Type": "application/json" } }
    )
  } catch (error) {
    return new Response(
      JSON.stringify({ success: false, error: error.message }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    )
  }
})
```

---

## Part 4: Create n8n Workflows

### Workflow 1: GitHub Issue → Odoo BIR Deadline + Plane Issue

**Use Case**: When GitHub issue with label `bir:filing` is created, auto-create BIR deadline in Odoo and sync to Plane.

**File**: `automations/n8n/workflows/github-bir-plane-sync.json`

**Nodes**:
1. **Webhook Trigger**: GitHub issue created
2. **Filter**: Check if issue has `bir:filing` label
3. **Extract Data**: Parse issue title for form type (1601-C, 2550Q, etc.)
4. **Odoo XML-RPC**: Create `bir.filing.deadline` record
5. **Wait**: Wait for Odoo → Plane sync (5 seconds)
6. **Plane API**: Verify issue created in Plane
7. **Supabase**: Log to `ops.work_items` for audit trail
8. **Slack**: Send notification to #compliance channel

### Workflow 2: Scheduled BIR Deadline Reminder → Plane Comments

**Use Case**: Daily check for upcoming BIR deadlines (within 3 days), add comments to Plane issues.

**Nodes**:
1. **Cron Trigger**: Daily at 9 AM Manila time
2. **Odoo XML-RPC**: Query deadlines due within 3 days
3. **Loop**: For each deadline
4. **Plane API**: Add comment to linked Plane issue
5. **Slack**: Send reminder to #compliance channel

### Workflow 3: Pulser Task Bus Orchestration

**Use Case**: External system requests Odoo data via task bus, results returned to Plane.

**Nodes**:
1. **Webhook Trigger**: Receive request from external system
2. **Supabase Insert**: Write intent to `ops.taskbus_intents` with `intent_type: "odoo.bir.status"`
3. **Wait**: Poll Supabase for intent completion (max 2 minutes)
4. **Transform**: Extract result from intent
5. **Plane API**: Create issue with status report
6. **Supabase**: Log to `ops.platform_events`

---

## Part 5: Testing & Verification

### Test 1: Odoo → Plane Sync

```python
# In Odoo shell
./scripts/odoo_shell.sh -d odoo

# Create test BIR filing deadline
deadline = env['bir.filing.deadline'].create({
    'form_type': '1601-C',
    'period_start': '2026-02-01',
    'period_end': '2026-02-28',
    'deadline_date': '2026-03-10',
    'description': 'February 2026 Withholding Tax',
    'status': 'pending',
    'priority': '2',
})

# Check if Plane issue created
print(deadline.plane_issue_id)  # Should have UUID
print(deadline.plane_issue_url)  # Should have URL
print(deadline.plane_sync_status)  # Should be 'synced'
```

### Test 2: Plane → Odoo Sync

1. Go to Plane issue created above
2. Change state from "Backlog" to "In Progress"
3. Wait 30 seconds for webhook processing
4. Check Odoo deadline status (should change to `in_progress`)

### Test 3: n8n Workflow

1. Activate n8n workflow
2. Create GitHub issue with label `bir:filing` and title `[1601-C] March 2026 Filing`
3. Verify:
   - BIR deadline created in Odoo
   - Plane issue created in fin-ops project
   - Slack notification sent
   - `ops.work_items` log entry created

---

## Part 6: Monitoring & Observability

### Supabase Logging

All integration events logged to:
- `ops.platform_events`: High-level integration events
- `ops.task_queue`: Task bus activity (via `ipai_pulser_connector`)
- `ops.work_items`: Cross-system entity linkage

### Odoo Logs

```bash
# Watch Odoo logs for Plane sync activity
tail -f /var/log/odoo/odoo.log | grep -i "plane\|bir_plane_sync"
```

### n8n Execution History

- n8n Dashboard → Executions
- Filter by workflow name
- Check execution logs for errors

### Plane Webhooks Log

- Plane → Settings → Webhooks → View Logs
- Check webhook delivery status and payloads

---

## Troubleshooting

### Issue: Odoo → Plane sync fails with 401 Unauthorized

**Cause**: Invalid or expired Plane API key

**Fix**:
1. Generate new API key in Plane: `https://plane.insightpulseai.com/profile` → API Tokens
2. Update Edge Function environment variable: `PLANE_API_KEY`
3. Redeploy Edge Function: `supabase functions deploy plane-sync`

### Issue: Plane → Odoo webhook not triggering

**Cause**: Webhook signature verification failing or URL unreachable

**Fix**:
1. Check Plane webhook logs for delivery failures
2. Verify Edge Function URL is correct
3. Check Supabase Edge Function logs: `supabase functions logs plane-webhook-odoo`
4. Test webhook manually with curl

### Issue: n8n workflow stuck waiting for Odoo task completion

**Cause**: Odoo cron not running or intent not claimed

**Fix**:
1. Check Odoo cron jobs: Settings → Technical → Automation → Scheduled Actions
2. Verify `ipai_pulser_connector` cron is active
3. Check `ops.taskbus_intents` table for stuck intents
4. Manually trigger cron: `env['ipai.pulser.intent']._pulser_process_intents()`

---

## Next Steps

1. ✅ **Activate ipai_bir_plane_sync module** (change manifest + install)
2. ✅ **Deploy Supabase Edge Functions** (plane-sync + plane-webhook-odoo)
3. ✅ **Configure Plane webhooks** (create webhook for bidirectional sync)
4. ✅ **Create n8n workflows** (GitHub integration, reminders, task bus)
5. ✅ **Test end-to-end** (create test deadline → verify Plane issue)
6. ⏳ **Monitor integration** (check logs, execution history, webhook deliveries)
7. ⏳ **Optimize performance** (batch syncs, rate limiting, error handling)

---

## Reference Documentation

| Resource | URL |
|----------|-----|
| Plane API Docs | https://developers.plane.so/api-reference/introduction |
| Supabase Edge Functions | https://supabase.com/docs/guides/functions |
| n8n Workflow Docs | https://docs.n8n.io/workflows/ |
| Odoo XML-RPC | https://www.odoo.com/documentation/19.0/developer/reference/external_api.html |
| ipai_bir_plane_sync code | `addons/ipai/ipai_bir_plane_sync/models/bir_filing_deadline.py` |
| ipai_pulser_connector code | `addons/ipai/ipai_pulser_connector/models/pulser_intent.py` |

---

**Last Updated**: 2026-03-05
**Status**: Configuration guide complete, awaiting deployment
**Next Action**: Activate ipai_bir_plane_sync module and deploy Edge Functions
