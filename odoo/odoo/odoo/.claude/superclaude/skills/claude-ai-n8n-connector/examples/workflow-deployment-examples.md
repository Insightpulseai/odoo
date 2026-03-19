# Workflow Deployment Examples

> **Tools**: `workflow_manager`, `github_ops`, `artifact_deployer`
> **Access Level**: Admin only (restricted bearer token)

---

## Workflow Manager Examples

### 1. Create New n8n Workflow

**Natural language**:
```
Create a new n8n workflow that sends Slack notifications when Odoo invoices are posted
```

**Tool call**:
```json
{
  "action": "create",
  "workflow_json": {
    "name": "Invoice Posted → Slack Notification",
    "nodes": [
      {
        "type": "n8n-nodes-base.webhook",
        "name": "Webhook Trigger",
        "parameters": {
          "path": "invoice-posted",
          "responseMode": "onReceived"
        },
        "position": [250, 300]
      },
      {
        "type": "n8n-nodes-base.function",
        "name": "Format Message",
        "parameters": {
          "functionCode": "return [{json: {text: `New invoice ${$input.first().json.name} posted for ${$input.first().json.partner_name}`}}];"
        },
        "position": [450, 300]
      },
      {
        "type": "n8n-nodes-base.slack",
        "name": "Send to Slack",
        "parameters": {
          "channel": "#finance-notifications",
          "text": "={{ $json.text }}"
        },
        "credentials": {
          "slackApi": "slack-insightpulse"
        },
        "position": [650, 300]
      }
    ],
    "connections": {
      "Webhook Trigger": {
        "main": [[{"node": "Format Message", "type": "main", "index": 0}]]
      },
      "Format Message": {
        "main": [[{"node": "Send to Slack", "type": "main", "index": 0}]]
      }
    },
    "active": true,
    "settings": {
      "saveExecutionProgress": true,
      "saveDataSuccessExecution": "all"
    }
  }
}
```

**Expected response**:
```json
{
  "workflow_id": "wf_abc123xyz",
  "name": "Invoice Posted → Slack Notification",
  "webhook_url": "https://n8n.insightpulseai.com/webhook/invoice-posted",
  "status": "active"
}
```

---

### 2. Update Existing Workflow

**Natural language**:
```
Update workflow wf_abc123xyz to also send email notifications
```

**Tool call**:
```json
{
  "action": "update",
  "workflow_id": "wf_abc123xyz",
  "workflow_json": {
    "nodes": [
      {
        "type": "n8n-nodes-base.emailSend",
        "name": "Send Email",
        "parameters": {
          "fromEmail": "finance@insightpulseai.com",
          "toEmail": "finance-team@insightpulseai.com",
          "subject": "New Invoice Posted: {{ $node['Webhook Trigger'].json.name }}",
          "text": "{{ $json.text }}"
        },
        "position": [650, 450]
      }
    ],
    "connections": {
      "Format Message": {
        "main": [
          [{"node": "Send to Slack", "type": "main", "index": 0}],
          [{"node": "Send Email", "type": "main", "index": 0}]
        ]
      }
    }
  }
}
```

---

### 3. Activate/Deactivate Workflow

**Natural language**:
```
Deactivate workflow wf_abc123xyz for maintenance
```

**Tool call**:
```json
{
  "action": "deactivate",
  "workflow_id": "wf_abc123xyz"
}
```

**Later**:
```
Reactivate workflow wf_abc123xyz
```

**Tool call**:
```json
{
  "action": "activate",
  "workflow_id": "wf_abc123xyz"
}
```

---

### 4. Delete Workflow

**Natural language**:
```
Delete test workflow wf_test456
```

**Tool call**:
```json
{
  "action": "delete",
  "workflow_id": "wf_test456"
}
```

**Warning**: Deletion is permanent. Workflows should be deactivated first for testing.

---

## GitHub Operations Examples

### 1. Create GitHub Issue

**Natural language**:
```
Create a GitHub issue in Insightpulseai/odoo for missing RLS policies in Supabase
```

**Tool call**:
```json
{
  "operation": "create_issue",
  "repo": "Insightpulseai/odoo",
  "title": "Missing RLS policies for user_tasks table",
  "body": "## Problem\n\nSupabase table `user_tasks` lacks Row-Level Security (RLS) policies.\n\n## Impact\n\nUsers can currently view tasks assigned to other users.\n\n## Proposed Solution\n\n```sql\nCREATE POLICY \"Users can view own tasks\"\n  ON user_tasks\n  FOR SELECT\n  USING (assigned_to = auth.uid());\n```\n\n## Acceptance Criteria\n\n- [ ] RLS policy created\n- [ ] Tested with multiple users\n- [ ] Documentation updated\n\n## Labels\n\nsecurity, database, high-priority"
}
```

**Expected response**:
```json
{
  "issue_number": 456,
  "issue_url": "https://github.com/Insightpulseai/odoo/issues/456",
  "status": "created"
}
```

---

### 2. Create Pull Request

**Natural language**:
```
Create a PR in Insightpulseai/odoo to add the missing RLS policy
```

**Tool call**:
```json
{
  "operation": "create_pr",
  "repo": "Insightpulseai/odoo",
  "title": "feat(supabase): add RLS policy for user_tasks table",
  "body": "## Changes\n\n- Added RLS policy restricting task visibility to assigned users\n- Updated Supabase migration script\n- Added tests for policy enforcement\n\n## Related Issues\n\nCloses #456\n\n## Testing\n\n```bash\n# Run migration\nsupabase db push\n\n# Test policy\npsql $SUPABASE_DB_URL -c \"SELECT * FROM user_tasks WHERE assigned_to != auth.uid();\"\n# Expected: 0 rows\n```",
  "branch": "fix/user-tasks-rls-policy",
  "files": [
    {
      "path": "supabase/migrations/20260220_add_user_tasks_rls.sql",
      "content": "CREATE POLICY \"Users can view own tasks\"\n  ON user_tasks\n  FOR SELECT\n  USING (assigned_to = auth.uid());\n\nCREATE POLICY \"Users can update own tasks\"\n  ON user_tasks\n  FOR UPDATE\n  USING (assigned_to = auth.uid());"
    }
  ]
}
```

**Expected response**:
```json
{
  "pr_number": 789,
  "pr_url": "https://github.com/Insightpulseai/odoo/pull/789",
  "branch": "fix/user-tasks-rls-policy",
  "status": "open"
}
```

---

### 3. Commit Files

**Natural language**:
```
Commit updated n8n workflow JSON to the repository
```

**Tool call**:
```json
{
  "operation": "commit",
  "repo": "Insightpulseai/odoo",
  "branch": "main",
  "files": [
    {
      "path": "automations/n8n/workflows/invoice-posted-notification.json",
      "content": "{\"name\": \"Invoice Posted → Slack Notification\", ...}"
    }
  ]
}
```

**Expected response**:
```json
{
  "commit_sha": "abc123def456",
  "commit_url": "https://github.com/Insightpulseai/odoo/commit/abc123def456",
  "status": "committed"
}
```

---

### 4. Merge Pull Request

**Natural language**:
```
Merge PR #789 after CI passes
```

**Tool call**:
```json
{
  "operation": "merge_pr",
  "repo": "Insightpulseai/odoo",
  "pr_number": 789
}
```

**Expected response**:
```json
{
  "pr_number": 789,
  "merge_commit_sha": "def456ghi789",
  "status": "merged"
}
```

---

## Artifact Deployer Examples

### 1. Deploy Odoo Module to Staging

**Natural language**:
```
Deploy the latest ipai_finance_automation module to staging environment
```

**Tool call**:
```json
{
  "app_id": "odoo-staging",
  "artifact_url": "registry.digitalocean.com/insightpulse/odoo:latest",
  "environment": "staging",
  "force_rebuild": false
}
```

**Expected response**:
```json
{
  "deployment_id": "dep_xyz789",
  "app_url": "https://odoo-staging-abc123.ondigitalocean.app",
  "status": "deploying",
  "estimated_time_minutes": 5
}
```

---

### 2. Deploy to Production with Rebuild

**Natural language**:
```
Deploy to production with force rebuild
```

**Tool call**:
```json
{
  "app_id": "odoo-production",
  "artifact_url": "registry.digitalocean.com/insightpulse/odoo:v1.2.3",
  "environment": "production",
  "force_rebuild": true
}
```

**Expected response**:
```json
{
  "deployment_id": "dep_prod456",
  "app_url": "https://erp.insightpulseai.com",
  "status": "building",
  "estimated_time_minutes": 10
}
```

---

### 3. Deploy from Git Branch

**Natural language**:
```
Deploy feature branch 'ocr-v2' to development environment
```

**Tool call**:
```json
{
  "app_id": "odoo-dev",
  "artifact_url": "git:github.com/Insightpulseai/odoo#ocr-v2",
  "environment": "development",
  "force_rebuild": false
}
```

**Expected response**:
```json
{
  "deployment_id": "dep_dev123",
  "app_url": "https://odoo-dev-xyz.ondigitalocean.app",
  "status": "deploying",
  "git_ref": "ocr-v2",
  "estimated_time_minutes": 7
}
```

---

## Complex Workflow Patterns

### Pattern 1: Deploy → Test → Notify

**Natural language**:
```
Deploy to staging, run tests, and notify team via Slack
```

**Workflow sequence**:
1. Deploy artifact (`artifact_deployer`)
2. Wait for deployment completion
3. Run integration tests (external API call)
4. Send Slack notification with results

**Implementation**: Create n8n workflow with multiple nodes orchestrated via `workflow_manager`.

---

### Pattern 2: Issue → Branch → PR → Deploy

**Natural language**:
```
Automate the workflow: GitHub issue → create branch → implement fix → create PR → deploy after merge
```

**Workflow nodes**:
1. **Webhook Trigger**: GitHub issue created
2. **GitHub Ops**: Create feature branch
3. **Code Generation**: AI-assisted implementation (external)
4. **GitHub Ops**: Commit files to branch
5. **GitHub Ops**: Create pull request
6. **Webhook**: Wait for PR merge event
7. **Artifact Deployer**: Deploy to staging
8. **Slack Notification**: Notify team

---

### Pattern 3: Scheduled Workflow Deployment

**Natural language**:
```
Deploy a new n8n workflow that runs nightly to sync Odoo invoices to Supabase
```

**Tool calls**:

1. **Create workflow**:
```json
{
  "action": "create",
  "workflow_json": {
    "name": "Nightly Invoice Sync",
    "nodes": [
      {
        "type": "n8n-nodes-base.cron",
        "name": "Schedule",
        "parameters": {
          "triggerTimes": {
            "hour": 2,
            "minute": 0
          }
        }
      },
      {
        "type": "n8n-nodes-base.httpRequest",
        "name": "Trigger Sync",
        "parameters": {
          "url": "https://n8n.insightpulseai.com/webhook/sync-trigger",
          "method": "POST",
          "body": {
            "sync_type": "incremental",
            "direction": "sor_to_ssot"
          }
        }
      }
    ]
  }
}
```

2. **Activate workflow**:
```json
{
  "action": "activate",
  "workflow_id": "wf_nightly_sync"
}
```

---

## Security Best Practices

### 1. Workflow Validation

**Before deployment**:
- ✅ Validate JSON syntax
- ✅ Check for hardcoded credentials (use Vault instead)
- ✅ Verify webhook paths don't conflict
- ✅ Test workflow in staging first

### 2. GitHub Operations

**Before creating PRs**:
- ✅ Run linters and tests locally
- ✅ Verify branch protection rules
- ✅ Include comprehensive PR description
- ✅ Request code review from team

### 3. Artifact Deployment

**Before production deploy**:
- ✅ Test in staging environment
- ✅ Verify CI/CD pipeline passes
- ✅ Check database migrations
- ✅ Review deployment logs

---

## Rollback Procedures

### Rollback n8n Workflow

**Natural language**:
```
Rollback workflow wf_abc123xyz to previous version
```

**Steps**:
1. Deactivate current workflow
2. Re-import previous workflow JSON from git history
3. Activate restored workflow

### Rollback GitHub Changes

**Natural language**:
```
Revert PR #789 that was merged earlier
```

**Tool call**:
```json
{
  "operation": "create_pr",
  "repo": "Insightpulseai/odoo",
  "title": "Revert: feat(supabase): add RLS policy for user_tasks table",
  "body": "Reverts PR #789 due to production issues",
  "branch": "revert-789"
}
```

### Rollback DigitalOcean Deployment

**Natural language**:
```
Rollback odoo-production to previous deployment
```

**Tool call**:
```json
{
  "app_id": "odoo-production",
  "artifact_url": "registry.digitalocean.com/insightpulse/odoo:v1.2.2",
  "environment": "production",
  "force_rebuild": false
}
```

---

## Monitoring and Logging

### View Workflow Execution Logs

Use `workflow_monitor` tool:

```json
{
  "action": "list",
  "workflow_id": "wf_abc123xyz",
  "limit": 20
}
```

### Check Deployment Status

Query DigitalOcean API via `artifact_deployer` with status check:

```json
{
  "app_id": "odoo-production",
  "operation": "status"
}
```

---

*For more deployment patterns, see `/odoo/docs/ai/CLAUDE_AI_N8N_CONNECTOR.md`*
