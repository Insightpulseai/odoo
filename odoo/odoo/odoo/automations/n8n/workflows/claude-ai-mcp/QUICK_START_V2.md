# Quick Start: Claude.ai ↔ n8n MCP Integration (Instance-Level)

> **Updated**: 2026-02-20 - Using n8n's built-in instance-level MCP server (simpler approach)

## ⚡ 3-Minute Setup

### Step 1: Enable MCP in n8n (1 min)

1. **Open n8n**: https://n8n.insightpulseai.com
2. **Go to Settings** → **MCP Access**
3. **Enable** the MCP feature toggle
4. **Enable workflows**:
   - Click "Enable workflows" button
   - Select all 9 "MCP Tool:" workflows
   - Click "Enable selected"
5. **Verify**: All 9 workflows should show "Available in MCP" badge

---

### Step 2: Connect Claude.ai (1 min)

1. **Open Claude.ai** → **Settings** → **Custom Connectors**
2. **Click "Add Connector"**
3. **Paste URL**: `https://n8n.insightpulseai.com` (base URL only!)
4. **Click "Continue"** → OAuth2 authorization will start
5. **Authorize** Claude.ai to access your n8n instance
6. **Verify**: Connection status shows "Connected"

**That's it!** No bearer tokens, no manual configuration needed.

---

### Step 3: Test (1 min)

In Claude.ai chat, try these queries:

```
Query Odoo for invoices posted in February 2026
```

Expected: JSON with invoice records

```
Check InsightPulseAI infrastructure health
```

Expected: Health status for all services

```
Trigger a sync of invoices to Supabase (dry run)
```

Expected: Preview of outbox entry

---

## ✅ Verification Checklist

- [ ] n8n MCP Access feature enabled
- [ ] 9 workflows marked "Available in MCP"
- [ ] Claude.ai connector configured with OAuth2
- [ ] Test query returns actual data
- [ ] n8n execution logs show successful runs

---

## 🔧 Troubleshooting

### "Connection failed"
→ Verify n8n is accessible: `curl https://n8n.insightpulseai.com/healthcheck`

### "Workflow not found"
→ Check workflow has "Available in MCP" toggle ON in n8n

### "Tool execution failed"
→ Check n8n execution logs for detailed error message

### "OAuth2 authorization failed"
→ Check n8n OAuth2 settings in Settings → API

---

## 📋 Workflow List (9 Total)

**Read-Only Tools (6)**:
1. Odoo Query (SOR Read-Only)
2. Supabase Ops (SSOT Query)
3. Finance Summary (Odoo SOR)
4. Infrastructure Health
5. Workflow Monitor
6. Sync Trigger (Outbox Pattern)

**Write-Path Tools (3)**:
7. Workflow Manager (admin only)
8. GitHub Operations (admin only)
9. Artifact Deployer (admin only)

---

## 🎯 Key Differences from Old Approach

**Old Approach** (MCP Server Trigger nodes):
- ❌ Required special trigger nodes per workflow
- ❌ Manual bearer token configuration
- ❌ Complex SSE endpoint setup

**New Approach** (Instance-level MCP):
- ✅ No special nodes needed (use regular triggers)
- ✅ OAuth2 automatic authentication
- ✅ Just toggle workflows on/off in MCP Access

---

## 📚 Full Documentation

- **Complete Guide**: [DEPLOYMENT_GUIDE_V2.md](./DEPLOYMENT_GUIDE_V2.md)
- **n8n MCP Docs**: https://docs.n8n.io/advanced-ai/accessing-n8n-mcp-server/
- **Architecture**: [README.md](./README.md)

---

**Status**: Instance-level MCP (recommended)
**Last Updated**: 2026-02-20
