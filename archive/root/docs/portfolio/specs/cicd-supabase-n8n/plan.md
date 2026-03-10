# CI/CD with Supabase + n8n — Implementation Plan

## Phase 1: Core Workflows

### 1.1 Supabase CI/CD Workflow

**File**: `.github/workflows/supabase-deploy.yml`

**Triggers**:
- Push to `main` or `develop` with changes in `supabase/**`
- Pull request validation for `supabase/**` changes
- Manual dispatch with environment selection

**Jobs**:
1. `detect-changes` - Path filtering for migrations/functions
2. `validate-migrations` - Syntax check for PRs
3. `deploy-migrations` - Push migrations to Supabase
4. `deploy-functions` - Deploy Edge Functions
5. `notify-n8n` - Send deployment event to n8n

### 1.2 n8n Orchestrator Workflow

**File**: `.github/workflows/n8n-orchestrator.yml`

**Triggers**:
- Push to `main` or `develop` with changes in `n8n/**`
- Manual dispatch for workflow sync/trigger

**Jobs**:
1. `validate-workflows` - JSON syntax and structure validation
2. `sync-workflows` - API-based sync to n8n instance
3. `trigger-workflow` - Manual n8n webhook trigger
4. `notify-status` - Send status to n8n

### 1.3 Unified CI/CD Workflow

**File**: `.github/workflows/insightpulse-cicd.yml`

**Triggers**:
- Push to `main` or `develop` with any stack changes
- Manual dispatch with component/environment selection

**Jobs**:
1. `detect-changes` - Multi-component path detection
2. `deploy-supabase` - Conditional Supabase deployment
3. `deploy-odoo` - Conditional Odoo deployment
4. `sync-n8n` - Conditional n8n sync
5. `notify` - Unified notification to all channels

## Phase 2: n8n Workflows

### 2.1 Deployment Notification Workflow

**File**: `n8n/workflows/deployment-notify.json`

**Trigger**: Webhook at `/deployment`

**Flow**:
```
Webhook → Parse Event → Check Environment
    ↓                         ↓ (production)
Log to Supabase ←───────────────┤
    ↓                           ↓ (staging)
Notify Slack (Production) ←────→ Notify Slack (Staging)
    ↓
Check Failures → Alert Mattermost (if failed)
    ↓
Respond to Webhook
```

### 2.2 GitHub Deploy Trigger Workflow

**File**: `n8n/workflows/github-deploy-trigger.json`

**Trigger**: Authenticated webhook at `/deploy/trigger`

**Flow**:
```
Webhook → Validate Request → Check Production?
                                ↓ (yes)
                      Log Request → Request Approval → Respond Pending
                                ↓ (no)
                      Trigger GitHub Workflow → Log → Notify → Respond Success
```

## Phase 3: Configuration

### 3.1 Required GitHub Secrets

```
SUPABASE_ACCESS_TOKEN    # From Supabase Dashboard → Settings → API
SUPABASE_DB_PASSWORD     # From project settings
SUPABASE_PROJECT_ID      # spdtwktxdalcfigzeqrz (production)
N8N_API_URL              # https://n8n.insightpulseai.com
N8N_API_KEY              # From n8n Settings → API
N8N_WEBHOOK_URL          # https://n8n.insightpulseai.com/webhook/deployment
SSH_PRIVATE_KEY          # For Odoo server access
SSH_HOST                 # 178.128.112.214
SSH_USER                 # deploy
```

### 3.2 n8n Credentials

| Credential Type | ID | Purpose |
|-----------------|-----|---------|
| Supabase API | `supabase-api` | Database logging |
| Slack OAuth | `slack-bot` | Notifications |
| GitHub Token | `github-token` | Workflow dispatch |
| HTTP Header Auth | Various | Webhook auth |

### 3.3 Supabase Tables

```sql
-- Deployment logs table
CREATE TABLE IF NOT EXISTS deployment_logs (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  event_type text NOT NULL,
  environment text NOT NULL,
  commit_sha text,
  branch text,
  triggered_by text,
  status text NOT NULL,
  components jsonb,
  run_url text,
  deployed_at timestamptz NOT NULL,
  created_at timestamptz DEFAULT now()
);

-- Deployment requests (for approval workflow)
CREATE TABLE IF NOT EXISTS deployment_requests (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  environment text NOT NULL,
  component text NOT NULL,
  ref text NOT NULL,
  requested_by text NOT NULL,
  status text NOT NULL DEFAULT 'pending',
  requested_at timestamptz NOT NULL,
  approved_by text,
  approved_at timestamptz,
  triggered_at timestamptz,
  created_at timestamptz DEFAULT now()
);
```

## Verification Steps

### Post-Implementation Checks

1. **Supabase Workflow**:
   ```bash
   # Trigger with test migration
   git commit --allow-empty -m "test: trigger supabase workflow"
   git push origin develop
   # Verify: Check workflow run in Actions tab
   ```

2. **n8n Webhook**:
   ```bash
   # Test webhook endpoint
   curl -X POST "https://n8n.insightpulseai.com/webhook/deployment" \
     -H "Content-Type: application/json" \
     -d '{"event":"test","environment":"staging","commit":"abc123"}'
   ```

3. **Unified Workflow**:
   ```bash
   # Trigger via workflow_dispatch
   gh workflow run insightpulse-cicd.yml \
     --ref develop \
     -f component=all \
     -f environment=staging
   ```

## Rollout Plan

1. **Merge to develop first** — Test all workflows in staging
2. **Verify n8n connectivity** — Ensure webhooks work
3. **Test path detection** — Confirm selective deployments
4. **Enable production** — Merge to main after validation
