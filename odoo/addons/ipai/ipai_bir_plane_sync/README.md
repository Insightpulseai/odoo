# IPAI BIR Plane Sync

**Version**: 19.0.1.0.0
**Author**: InsightPulseAI
**License**: AGPL-3

## Purpose

Bidirectional synchronization between BIR tax filing deadlines (Odoo) and Plane issues for OKR tracking and work management.

## Features

- **Automatic Sync**: Deadlines sync to Plane on create/update
- **Bidirectional**: Plane issue updates trigger Odoo status changes
- **OKR Integration**: Issues tagged with OKR labels (objective, key-result, initiative)
- **Rich Context**: Issue descriptions include deadline details and Odoo links
- **Error Tracking**: Sync failures logged with error messages
- **Manual Sync**: Button to force sync for individual deadlines
- **Batch Sync**: Action to sync all deadlines at once

## Installation

### Prerequisites

1. **Plane Project Setup**: Create BIR project in Plane manually
   - Follow steps in `scripts/plane_bir_bootstrap.sql`
   - Create project: "bir-compliance-automation"
   - Create 3 modules: bir-eservices-integration, bir-form-generation, bir-audit-trail
   - Create labels: okr:*, area:*, risk:*, form:*, status:*

2. **Supabase Edge Function**: Existing `plane-sync` function must be deployed
   - Location: `.gemini/tmp/odoo-kit/supabase/functions/plane-sync/index.ts`
   - Already production-ready (939 lines)

3. **Plane API Token**: Generate in Plane settings
   - Go to: Plane → Settings → API Tokens
   - Create token with workspace access
   - Store in Supabase Vault as `PLANE_API_TOKEN`

### Module Installation

1. Install module:
   ```bash
   odoo-bin -u ipai_bir_plane_sync
   ```

2. Configure system parameters (Settings → Technical → System Parameters):
   - `plane.workspace_slug`: Your Plane workspace slug (e.g., "insightpulseai")
   - `plane.bir_project_id`: BIR project UUID from Plane (get from project URL)
   - `supabase.url`: `https://spdtwktxdalcfigzeqrz.supabase.co`
   - `supabase.service_role_key`: Supabase service role key (from Vault)

3. Initial sync (one-time):
   ```python
   # Odoo shell
   env['bir.filing.deadline'].sync_all_to_plane()
   ```

## Usage

### Automatic Sync (Default Behavior)

Once configured, sync happens automatically:

**Odoo → Plane**:
- New deadline created → Plane issue created
- Deadline status changed → Plane issue state updated
- Deadline date changed → Plane issue due_date updated
- Priority changed → Plane issue priority updated

**Plane → Odoo** (via webhook):
- Plane issue state changed → Odoo status updated
- Plane issue assigned → Odoo responsible_user_id updated

### Manual Sync

**Single Deadline**:
1. Open BIR Filing Deadline form
2. Go to "Plane Sync" tab
3. Click "Sync to Plane" button

**Batch Sync**:
1. Go to BIR Filing Deadlines list
2. Select deadlines
3. Action → "Sync All to Plane"

### Monitoring Sync Status

**List View**:
- Column: "Plane Sync Status"
- Filters: "Synced to Plane", "Not Synced", "Sync Error"

**Form View**:
- Tab: "Plane Sync"
- Fields: Sync status, last sync time, issue ID, issue URL, error message

**Sync Statuses**:
- **Not Synced**: Deadline not yet synced to Plane
- **Synced**: Successfully synced, issue exists in Plane
- **Pending**: Sync queued but not yet processed
- **Error**: Sync failed (see error message)

## Field Mapping

### Odoo → Plane

| Odoo Field | Plane Field | Transformation |
|------------|-------------|----------------|
| `form_type` + `description` | `issue.name` | "[1601-C] Withholding Tax Return" |
| `description` + details | `issue.description` | Markdown with links |
| `status` | `issue.state` | pending→backlog, in_progress→started, filed→completed |
| `priority` | `issue.priority` | 0→low, 1→medium, 2→high, 3→urgent |
| `deadline_date` | `issue.due_date` | ISO 8601 date |
| Form + status | `issue.labels` | ["form:1601c", "status:in-progress", "area:compliance"] |

### Plane → Odoo (Webhook)

| Plane Field | Odoo Field | Transformation |
|-------------|------------|----------------|
| `issue.state` | `status` | backlog→pending, started→in_progress, completed→filed |
| `issue.assignees` | `responsible_user_id` | Map by email (if user exists) |

## OKR Structure in Plane

### Project Structure
```
Project: bir-compliance-automation
├── Module: bir-eservices-integration (eBIRForms/eFPS API)
├── Module: bir-form-generation (36 form computation engines)
└── Module: bir-audit-trail (10-year immutable evidence)
```

### Issue Hierarchy
```
Objective: All statutory filings on-time with audit-ready evidence
├── Key Result 1.1: 100% filings submitted by deadline (0 late)
│   ├── Initiative 1.1.1: eBIRForms API integration
│   ├── Initiative 1.1.2: eFPS API integration
│   └── [All BIR deadline issues]
├── Key Result 1.2: 100% filings have BIR acknowledgement receipts
│   └── Initiative 1.2.1: 36 BIR form computation engines
└── Key Result 1.3: 10-year audit trail operational
    └── Initiative 1.3.1: Immutable audit trail system
```

### Labels Usage

**OKR Labels** (manual assignment):
- `okr:objective` - Top-level business objective
- `okr:key-result` - Measurable key result
- `okr:initiative` - Tactical initiative

**Auto-Generated Labels** (from sync):
- `form:1601c` - Form type (36 forms)
- `status:in-progress` - Current status
- `area:compliance` - Always applied
- `risk:deliverability` - If deadline <3 days or overdue

## Plane Issue Description Format

```markdown
## BIR Tax Filing Deadline

**Form Type**: 1601-C
**Filing Period**: 2026-01-01 to 2026-01-31
**Deadline**: 2026-02-10 (Monday)
**Status**: IN_PROGRESS

## Description
Monthly withholding tax return for regular employees.

## Links
- [View in Odoo ERP](odoo://bir.filing.deadline/123)

---
*Synced from InsightPulseAI Odoo ERP via ipai_bir_plane_sync*
```

## Webhook Configuration

### Plane → Odoo (Webhook)

Configure in Plane project settings:

**Webhook URL**:
```
https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/plane-sync?source=plane
```

**Events**:
- `issue.created`
- `issue.updated`
- `issue.deleted` (optional)

**Secret**: Store in Supabase Vault as `PLANE_WEBHOOK_SECRET`

### Verification

After webhook configured, test by:
1. Change issue state in Plane
2. Check Odoo deadline status updates automatically
3. Review `plane.sync_log` table in Supabase for activity

## Troubleshooting

### No Sync Happening

**Check Configuration**:
```python
# Odoo shell
env['bir.filing.deadline']._is_plane_sync_enabled()
# Should return True
```

**Check System Parameters**:
- Settings → Technical → System Parameters
- Verify all 4 required parameters are set

**Check Supabase Edge Function**:
```bash
# Test Edge Function
curl -X POST https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/plane-sync?action=status \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY"
```

### Sync Errors

**Check Error Message**:
1. Open deadline form
2. Go to "Plane Sync" tab
3. Read "Sync Error Message"

**Common Errors**:
- "PLANE_API_TOKEN not configured" → Set token in Supabase Vault
- "Plane API error: 404" → Verify project ID in system parameters
- "Plane API error: 401" → Check API token validity
- "Missing required environment variable" → Check Supabase Edge Function env vars

**Retry Sync**:
1. Fix configuration issue
2. Click "Sync to Plane" button on deadline form
3. Or run batch sync: `env['bir.filing.deadline'].sync_all_to_plane()`

### Webhook Not Working

**Check Webhook Configuration**:
- Verify webhook URL in Plane project settings
- Ensure events are enabled (issue.created, issue.updated)
- Check webhook secret matches Supabase Vault value

**Check Webhook Logs**:
```sql
-- Supabase SQL Editor
SELECT * FROM plane.sync_log ORDER BY created_at DESC LIMIT 20;
```

**Test Webhook Manually**:
```bash
# Simulate Plane webhook
curl -X POST https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/plane-sync?source=plane \
  -H "Content-Type: application/json" \
  -H "X-Plane-Signature: $WEBHOOK_SECRET" \
  -d '{"issue_id": "uuid", "state": "started"}'
```

## Advanced Usage

### Custom Labels

Modify `_prepare_plane_payload()` in `models/bir_filing_deadline.py`:

```python
# Add custom labels based on business logic
if self.amount_due > 100000:
    labels.append("high-value")

if self.agency_id.name == "BIR RDO 39":
    labels.append("rdo:39")
```

### Custom State Mapping

Modify state mappings in `_prepare_plane_payload()`:

```python
# Custom status mapping
status_map = {
    "pending": "backlog",
    "in_progress": "started",
    "filed": "completed",
    "void": "cancelled",
    "under_review": "in_review",  # Custom state
}
```

### Webhook Extension

Extend `handle_plane_webhook()` for custom webhook processing:

```python
def handle_plane_webhook(self, payload):
    result = super().handle_plane_webhook(payload)

    # Custom logic
    if payload.get("assignee_added"):
        # Notify assignee via email
        self._notify_assignee(payload["assignee_email"])

    return result
```

## Database Schema

### New Fields (bir.filing.deadline)

| Field | Type | Description |
|-------|------|-------------|
| `plane_issue_id` | Char | Plane issue UUID |
| `plane_issue_url` | Char (computed) | Direct link to Plane issue |
| `plane_sync_status` | Selection | Sync status (not_synced, synced, error) |
| `plane_sync_error` | Text | Error message if sync failed |
| `plane_last_sync` | Datetime | Timestamp of last successful sync |

### Supabase Tables (External)

Created by plane-sync Edge Function:
- `plane.sync_mappings` - Entity ID mappings (Odoo ↔ Plane)
- `plane.sync_queue` - Pending sync operations
- `plane.sync_log` - Sync history and errors

## Performance Considerations

- **Sync Overhead**: ~200ms per deadline sync (API call + DB update)
- **Batch Sync**: Processes sequentially to avoid rate limits
- **Webhook Latency**: ~1-2s for Plane → Odoo updates
- **Large Datasets**: For >100 deadlines, use batch sync during off-hours

## Security

- API tokens stored in Supabase Vault (not in Odoo)
- Webhook signatures verified by Edge Function
- Supabase RLS policies protect sync tables
- Odoo access rules apply (manager-only write access)

## Support

For issues or questions:
- GitHub: https://github.com/Insightpulseai/odoo
- Email: business@insightpulseai.com

## References

- Plane API Documentation: https://docs.plane.so/api-reference
- Existing plane-sync function: `.gemini/tmp/odoo-kit/supabase/functions/plane-sync/index.ts`
- Bootstrap script: `scripts/plane_bir_bootstrap.sql`

## License

AGPL-3 - See LICENSE file for details
