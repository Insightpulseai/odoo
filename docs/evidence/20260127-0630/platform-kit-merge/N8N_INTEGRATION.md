# Platform Kit n8n Integration

**Date:** 2026-01-27 07:00 UTC
**n8n Instance:** https://n8n.insightpulseai.net
**Status:** ✅ API Key Verified, Ready for Workflow Deployment

---

## Current Setup

**Stack:**
- **Mattermost:** `chat.insightpulseai.net` (self-hosted, no tier limits)
- **n8n:** `n8n.insightpulseai.net` (self-hosted Community Edition)
- **GitHub:** jgtolentino/odoo-ce
- **Supabase:** spdtwktxdalcfigzeqrz

**No Tier Blockers:**
- ✅ n8n self-hosted = unlimited executions
- ✅ Public REST API available
- ✅ Full automation capabilities
- ✅ No usage quotas

---

## n8n API Access

**API Key Status:** ✅ Verified and working

**Test Command:**
```bash
export N8N_API_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzNjQ1M2ZhNS0zM2ZiLTQ5MjAtOTIxOS00M2FhYTJiYTg2Y2MiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzY5NDc1MTE0LCJleHAiOjE3NzcyMTkyMDB9.lg1vYem-vyNJex69h1wYoDe-qmtGz_zA11roUU98C78"

curl -H "X-N8N-API-KEY: $N8N_API_KEY" \
  "https://n8n.insightpulseai.net/api/v1/workflows" | jq '.'
```

**Expected:** `{"data": [], "nextCursor": null}` (0 workflows currently)

---

## Platform Kit Orchestrator Workflow

### Purpose
Automate Platform Kit operations via webhook:
1. Receive event from Claude/external trigger
2. Dispatch GitHub Actions
3. Notify Mattermost
4. Return confirmation

### Workflow Definition

**File:** `docs/evidence/20260127-0630/platform-kit-merge/workflows/platform-kit-orchestrator.json`

**Nodes:**
1. **Webhook** - Receives POST requests at `/webhook/platform-kit-trigger`
2. **Extract Event** - Parses event_type and payload
3. **GitHub Dispatch** - Triggers repository_dispatch event
4. **Mattermost Notify** - Posts result to platform-kit channel
5. **Respond to Webhook** - Returns JSON confirmation

**Connections:**
```
Webhook → Extract Event → GitHub Dispatch → Mattermost Notify → Respond
```

### Deployment Options

#### Option 1: Import via n8n UI (Recommended)
1. Navigate to: https://n8n.insightpulseai.net
2. Click "..." menu → "Import from File"
3. Select `platform-kit-orchestrator.json`
4. Configure credentials:
   - GitHub OAuth2
   - Mattermost webhook URL
5. Activate workflow

#### Option 2: Deploy via n8n API
```bash
# Remove read-only fields
jq 'del(.active, .id, .createdAt, .updatedAt)' platform-kit-orchestrator.json > workflow-create.json

# Create workflow
curl -X POST "https://n8n.insightpulseai.net/api/v1/workflows" \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  -H "Content-Type: application/json" \
  -d @workflow-create.json

# Activate workflow (use returned ID)
curl -X PATCH "https://n8n.insightpulseai.net/api/v1/workflows/{workflow_id}" \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"active": true}'
```

---

## Integration Patterns

### Pattern 1: Claude → n8n → GitHub → Mattermost

**Use Case:** Deploy Platform Kit changes via chat command

**Flow:**
```
Claude detects deployment request
  ↓
POST to n8n webhook
  ↓
n8n dispatches GitHub Action (deploy-platform-kit.yml)
  ↓
GitHub runs deployment
  ↓
n8n posts result to Mattermost
  ↓
Claude reads Mattermost confirmation
```

**Implementation:**
```bash
# Claude sends
curl -X POST "https://n8n.insightpulseai.net/webhook/platform-kit-trigger" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "deploy-platform-kit",
    "payload": {
      "component": "edge-function",
      "environment": "production"
    }
  }'
```

### Pattern 2: n8n → Supabase → GitHub → n8n

**Use Case:** Automated Platform Kit inventory scans

**Flow:**
```
n8n Schedule (daily 6AM)
  ↓
Call Supabase Edge Function (platformkit-introspect)
  ↓
Store results in ops.inventory_scans
  ↓
If changes detected, dispatch GitHub Action
  ↓
GitHub creates PR with updated inventory
  ↓
n8n posts PR link to Mattermost
```

### Pattern 3: GitHub → n8n → Mattermost

**Use Case:** PR notifications for Platform Kit changes

**Flow:**
```
GitHub PR opened/merged (webhook)
  ↓
n8n receives webhook
  ↓
Filter: only platform-kit/* paths
  ↓
Extract PR metadata (title, author, files changed)
  ↓
Post formatted message to Mattermost
```

---

## Required Workflows (Priority Order)

### 1. Platform Kit Deployment Orchestrator (P0)
**Status:** Workflow JSON created, ready to import
**Purpose:** Automate Supabase deployments (migrations + Edge Functions)

**Trigger:** Webhook or manual
**Actions:**
- Deploy migration via psql
- Deploy Edge Function via Supabase CLI
- Test endpoint health
- Post results to Mattermost

### 2. Daily Platform Inventory Scan (P1)
**Purpose:** Automated introspection runs

**Trigger:** Cron (daily 6AM UTC)
**Actions:**
- Call platformkit-introspect Edge Function
- Compare with previous scan
- If changes >5%, create GitHub issue
- Post summary to Mattermost

### 3. BIR Deadline Alerts (P1)
**Purpose:** Finance PPM compliance notifications

**Trigger:** Cron (daily 8AM PHT)
**Actions:**
- Query Supabase for upcoming BIR deadlines (7 days)
- Post alerts to Mattermost finance-ppm channel
- Escalate overdue tasks to Finance Director

### 4. PR Automation (P2)
**Purpose:** Automated PR creation for inventory updates

**Trigger:** Inventory scan detects changes
**Actions:**
- Generate PR with diff
- Assign reviewers
- Apply labels
- Post PR link to Mattermost

---

## Credentials Setup

### GitHub OAuth2 (for repository_dispatch)
1. Go to: https://github.com/settings/developers
2. New OAuth App:
   - Name: "n8n Platform Kit Orchestrator"
   - Homepage: https://n8n.insightpulseai.net
   - Callback: https://n8n.insightpulseai.net/rest/oauth2-credential/callback
3. Generate client secret
4. Add to n8n credentials

### Mattermost Webhook
1. Go to: https://chat.insightpulseai.net/admin_console/integrations/incoming_webhooks
2. Create webhook for `platform-kit` channel
3. Copy webhook URL
4. Add to n8n credentials

### Supabase Service Role (for Edge Function calls)
```bash
# Already in environment
echo $SUPABASE_SERVICE_ROLE_KEY
```

---

## Testing

### Test Workflow Creation
```bash
# List current workflows (should be 0)
curl -H "X-N8N-API-KEY: $N8N_API_KEY" \
  "https://n8n.insightpulseai.net/api/v1/workflows" | jq '.data | length'

# After import, verify
curl -H "X-N8N-API-KEY: $N8N_API_KEY" \
  "https://n8n.insightpulseai.net/api/v1/workflows" | jq '.data[] | {id, name, active}'
```

### Test Webhook Endpoint
```bash
# Get webhook URL from n8n UI or API
WEBHOOK_URL="https://n8n.insightpulseai.net/webhook/platform-kit-trigger"

# Send test event
curl -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "test",
    "payload": {"message": "Hello from Platform Kit"}
  }'

# Expected: {"ok": true, "event": "test", "dispatched_at": "..."}
```

---

## Next Steps

1. **Import Workflow** (choose Option 1 or 2 above)
2. **Configure Credentials** (GitHub + Mattermost)
3. **Activate Workflow**
4. **Test Webhook**
5. **Create Remaining Workflows** (inventory scan, BIR alerts, PR automation)

---

## Documentation

**This Document:** `docs/evidence/20260127-0630/platform-kit-merge/N8N_INTEGRATION.md`

**Related:**
- Platform Kit spec: `spec/platform-kit/`
- Deployment status: `docs/evidence/20260127-0630/platform-kit-merge/DEPLOYMENT_STATUS.md`
- Merge evidence: `docs/evidence/20260127-0630/platform-kit-merge/MERGE_EVIDENCE.md`

---

**Status:** n8n API verified, workflows ready for deployment.
**Next:** Import workflow via n8n UI and configure credentials.
