# Plane Integration Guide

> Complete integration setup for self-hosted Plane instance at `plane.insightpulseai.com`

## Overview

This guide covers the complete integration stack connecting:
- **Plane** (self-hosted project management)
- **GitHub** (code repositories)
- **Slack** (team communication)
- **n8n** (workflow automation)
- **Supabase** (event ledger and audit trail)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Integration Hub                              │
│                                                                  │
│  GitHub ←→ Plane ←→ Slack                                       │
│     ↓         ↓        ↓                                         │
│     └──── n8n (Orchestration) ────┘                             │
│              ↓                                                   │
│         Supabase (Event Ledger + Audit)                         │
│              ↓                                                   │
│         Claude Code (MCP Access)                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. Plane MCP Server

**Status**: ✅ Configured and Ready

**Purpose**: Agentic access to Plane for Claude Code and VS Code

**Configuration**:
- Location: `mcp/servers/plane/`
- Registry: `.claude/mcp-servers.json`
- Status: `source_only` (requires npm build)

**Tools Available**:
- `create_issue` - Create Plane issues with idempotency
- `update_issue` - Update issue state, priority, assignees
- `get_issue` - Fetch single issue by ID
- `list_issues` - Query issues with filters
- `list_projects` - List all workspace projects
- `list_cycles` - List sprints/cycles
- `list_modules` - List epics/modules
- `search_pages` - Search Plane Pages

**Environment Variables**:
```bash
export PLANE_API_URL="https://plane.insightpulseai.com/api/v1"
export PLANE_API_KEY="<your_api_key>"
export PLANE_WORKSPACE_SLUG="fin-ops"
```

**Setup**:
1. Get API key: `https://plane.insightpulseai.com/profile` → API Tokens
2. Set environment variables in `~/.zshrc`
3. Restart Claude Code
4. Test: "List all Plane projects"

**Verification**:
```bash
./scripts/verify_plane_mcp.sh
```

---

### 2. Plane ↔ GitHub Integration

**Options**:

#### A. Marketplace Integration (Recommended)

**URL**: https://plane.so/marketplace/github

**Setup**:
1. Go to: `https://plane.insightpulseai.com/settings/integrations`
2. Click: "Connect GitHub"
3. OAuth: Authorize `Insightpulseai` organization
4. Map repositories to Plane projects:
   - `Insightpulseai/odoo` → `fin-ops` project
   - Configure sync direction (one-way or bidirectional)
5. Configure label mapping:
   - GitHub `bug` → Plane `bug`
   - GitHub `enhancement` → Plane `feature`

**Features**:
- ✅ Automatic issue sync (GitHub → Plane)
- ✅ PR notifications in Plane
- ✅ Status synchronization
- ✅ Comment sync
- ⚠️ UI-based configuration (not SSOT)

#### B. Custom SSOT Integration

**Status**: Planned (see `spec/plane-github-sync/`)

**Architecture**:
```
GitHub → pulser-hub App → Supabase Edge Function
                           ↓
                   ops.github_webhook_deliveries
                           ↓
                   plane-github-sync worker
                           ↓
                   Plane API + work_plane.* mirror
```

**Advantages**:
- Full control over sync logic
- SSOT governance (`ssot/mappings/plane_github.yaml`)
- Custom mapping rules
- Audit trail in `ops.run_events`

**Implementation**: See `/Users/tbwa/.claude/plans/shimmering-dazzling-allen.md`

---

### 3. Plane ↔ Slack Integration

**URL**: https://docs.plane.so/integrations/slack

**Setup**:
1. Go to: `https://plane.insightpulseai.com/settings/integrations`
2. Click: "Connect Slack"
3. Install: Plane Slack App to workspace
4. Configure notifications:
   - Issue created → Slack channel
   - Issue updated → Thread reply
   - State changes → Notifications
5. Set up `/plane` commands

**Features**:
- Create issues from Slack: `/plane create`
- Update issues: `/plane update <issue-id>`
- Search issues: `/plane search <query>`
- Real-time notifications for Plane activity

---

### 4. GitHub ↔ Slack Integration

**URL**: https://docs.github.com/en/integrations/how-tos/slack/integrate-github-with-slack

**Setup**:
1. In Slack: `/github install`
2. Install: https://github.com/integrations/slack
3. Subscribe to repos:
   ```
   /github subscribe Insightpulseai/odoo issues pulls commits
   ```
4. Configure notifications per channel

**Features**:
- PR/issue notifications
- Unfurl GitHub links
- `/github` commands for repo management

---

### 5. n8n GitHub App

**URL**: https://github.com/marketplace/n8n-cloud

**Setup**:
1. Install GitHub App: n8n Cloud
2. Configure webhook URL: `https://n8n.insightpulseai.com/webhook/github`
3. Enable events: `push`, `pull_request`, `issues`, `issue_comment`

**Sample Workflows**:

#### Workflow 1: PR Merged → Create Plane Issue
```
Trigger: GitHub PR merged
↓
Filter: Only main branch
↓
Create Plane Issue: "Deployed: {PR title}"
↓
Notify Slack: #deployments channel
```

#### Workflow 2: Slack Command → Query Plane
```
Trigger: Slack slash command /plane-status
↓
Query Plane API: Get issues by state
↓
Format response
↓
Post to Slack thread
```

#### Workflow 3: Scheduled Sync
```
Trigger: Cron (every 15 min)
↓
Query GitHub: Get recent issues
↓
Check Plane: Find missing issues
↓
Create Plane issues for missing
↓
Log to Supabase: ops.work_items
```

---

## Environment Variables Reference

### Required for Plane MCP

```bash
# Plane Self-Hosted Instance
export PLANE_API_URL="https://plane.insightpulseai.com/api/v1"
export PLANE_API_KEY="<get from Plane profile>"
export PLANE_WORKSPACE_SLUG="fin-ops"

# Supabase (for audit trail)
export SUPABASE_URL="https://spdtwktxdalcfigzeqrz.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="<your key>"
```

### Optional for Custom GitHub Integration

```bash
# GitHub App (pulser-hub or ipai-plane-bridge)
export GITHUB_APP_ID="<from GitHub App settings>"
export GITHUB_APP_PRIVATE_KEY="<base64-encoded PEM>"
export GITHUB_APP_WEBHOOK_SECRET="<HMAC secret>"
```

---

## Integration Patterns

### Pattern 1: Marketplace (Quick Setup)

**Timeline**: 30 minutes

**Steps**:
1. ✅ Plane MCP (already done)
2. Plane → Slack (marketplace)
3. GitHub → Slack (official app)
4. GitHub → Plane (marketplace)

**Result**: Basic integration with minimal code

---

### Pattern 2: Hybrid (Recommended)

**Timeline**: 2-4 hours

**Steps**:
1. ✅ Plane MCP (already done)
2. Marketplace integrations (Plane→Slack, GitHub→Slack)
3. GitHub → Plane (marketplace)
4. n8n workflows for custom automation
5. Supabase for event ledger

**Result**: Marketplace ease + custom automation

---

### Pattern 3: Full SSOT (Advanced)

**Timeline**: 1-2 days

**Steps**:
1. ✅ Plane MCP (already done)
2. Custom GitHub → Plane sync worker
3. n8n orchestration
4. Complete SSOT governance
5. Full audit trail

**Result**: Complete control + SSOT compliance

---

## Testing & Verification

### 1. Plane MCP Verification

```bash
# Run verification script
./scripts/verify_plane_mcp.sh

# Expected output:
# ✅ Environment variables set
# ✅ Plane MCP server built
# ✅ Plane API accessible (HTTP 200)
# ✅ Successfully fetched N projects
```

### 2. Integration Tests

**Test Case 1: GitHub → Plane**
1. Create issue in GitHub: `Insightpulseai/odoo`
2. Verify issue appears in Plane `fin-ops` project
3. Confirm labels and state are synced

**Test Case 2: Plane → Slack**
1. Create issue in Plane
2. Verify notification in Slack channel
3. Test `/plane` commands

**Test Case 3: GitHub → Slack**
1. Open PR in GitHub
2. Verify notification in Slack
3. Test link unfurling

**Test Case 4: MCP Access**
1. In Claude Code: "List all Plane projects"
2. Expected: JSON response with projects
3. Test: "Create a test issue in project X"

---

## Troubleshooting

### Plane MCP Not Working

**Symptom**: MCP server not responding

**Solutions**:
1. Check environment variables: `echo $PLANE_API_KEY`
2. Verify API connectivity:
   ```bash
   curl -H "X-API-Key: $PLANE_API_KEY" \
     "$PLANE_API_URL/workspaces/$PLANE_WORKSPACE_SLUG/projects/"
   ```
3. Rebuild MCP server: `cd mcp/servers/plane && npm run build`
4. Restart Claude Code

---

### GitHub Integration Not Syncing

**Symptom**: Issues not appearing in Plane

**Check**:
1. Verify OAuth connection in Plane settings
2. Check repo mappings are correct
3. Test with manual issue creation
4. Review Plane integration logs

---

### Slack Notifications Missing

**Symptom**: No Slack notifications

**Solutions**:
1. Verify Plane Slack App installed
2. Check notification channel settings
3. Test with manual issue update
4. Review Slack App permissions

---

## Next Steps

### Immediate (Today)

1. **Set Plane API Key**:
   ```bash
   # Get from: https://plane.insightpulseai.com/profile
   export PLANE_API_KEY="your_key_here"
   echo 'export PLANE_API_KEY="your_key_here"' >> ~/.zshrc
   ```

2. **Verify MCP**:
   ```bash
   ./scripts/verify_plane_mcp.sh
   ```

3. **Test in Claude Code**:
   - Restart Claude Code
   - Run: "List all Plane projects"
   - Verify: Should return fin-ops project

### Short-term (This Week)

1. **Install Marketplace Integrations**:
   - Plane → Slack
   - GitHub → Slack
   - GitHub → Plane

2. **Configure n8n GitHub App**:
   - Install app
   - Setup webhook
   - Create first workflow

3. **Test End-to-End**:
   - Create GitHub issue
   - Verify in Plane and Slack
   - Test MCP access

### Long-term (Next Sprint)

1. **Build Custom Sync Worker** (if needed)
2. **Implement SSOT Governance**
3. **Add Advanced n8n Workflows**
4. **Complete Audit Trail**

---

## Resources

### Official Documentation

- Plane Integrations: https://docs.plane.so/integrations/about
- Plane API: https://developers.plane.so/api-reference/introduction
- GitHub Slack: https://docs.github.com/en/integrations/how-tos/slack/integrate-github-with-slack
- n8n GitHub App: https://github.com/marketplace/n8n-cloud

### Internal Documentation

- Plan File: `/Users/tbwa/.claude/plans/shimmering-dazzling-allen.md`
- SSOT Config: `ssot/integrations/plane_mcp.yaml`
- MCP Server: `mcp/servers/plane/index.ts`
- Verification: `scripts/verify_plane_mcp.sh`

---

**Last Updated**: 2026-03-05
**Status**: Plane MCP ready, marketplace integrations pending
**Next Action**: Set PLANE_API_KEY and verify MCP server
