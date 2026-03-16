# Quick Start: Claude.ai ↔ n8n MCP Integration

## ⚡ 5-Minute Setup

### Step 1: Import to n8n (2 min)

1. Open https://n8n.insightpulseai.com
2. Login as `devops@insightpulseai.com`
3. For each workflow in `read-only/` and `write-path/`:
   - Click **"+"** → **"Import from File"**
   - Select the JSON file
   - Click **"Activate"** toggle

**Workflows to Import (9 total)**:
```
read-only/
├── 01_mcp_odoo_query.json
├── 02_mcp_supabase_ops.json
├── 03_mcp_finance_summary.json
├── 04_mcp_infra_health.json
├── 05_mcp_workflow_monitor.json
└── 06_mcp_sync_trigger.json

write-path/
├── 07_mcp_workflow_manager.json
├── 08_mcp_github_ops.json
└── 09_mcp_artifact_deployer.json
```

---

### Step 2: Configure Claude.ai (2 min)

1. **Open Claude.ai** → **Settings** → **Custom Connectors**
2. **Click "Add Connector"**
3. **Paste** configuration from `.claude/superclaude/skills/claude-ai-n8n-connector/connector-config.json`
4. **Set URL**: `https://n8n.insightpulseai.com` (base URL only!)
5. **Add Bearer Token** (get from Supabase Vault or n8n API settings)
6. **Save Connector**

---

### Step 3: Test (1 min)

In Claude.ai chat, try:

```
Query Odoo for recent invoices posted this month
```

Expected: JSON response with invoice records from Odoo SOR

```
Check InsightPulseAI infrastructure health
```

Expected: Health status for Odoo, Supabase, n8n, Superset

```
Trigger a sync of invoices to Supabase (dry run mode)
```

Expected: Preview of outbox entry without executing

---

## ✅ Verification Checklist

- [ ] All 9 workflows imported to n8n
- [ ] All 9 workflows activated (green toggle)
- [ ] Claude.ai connector configured with `https://n8n.insightpulseai.com`
- [ ] Bearer token added to Claude.ai connector
- [ ] Test query returns actual data (not error)
- [ ] n8n execution logs show successful runs

---

## 🔧 Troubleshooting

### "MCP server authorization error"
→ Check Bearer token in Claude.ai connector settings

### "Tool not found"
→ Verify workflow is activated in n8n UI

### "Empty response"
→ Check n8n environment variables (ODOO_URL, SUPABASE_URL, etc.)

### "Workflow execution failed"
→ Check n8n execution logs for detailed error message

---

## 📚 Full Documentation

- **Complete Setup**: [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
- **Architecture**: [README.md](./README.md)
- **Query Examples**: `.claude/superclaude/skills/claude-ai-n8n-connector/examples/`
- **Integration Guide**: `docs/ai/CLAUDE_AI_N8N_CONNECTOR.md`

---

**Status**: Manual import recommended (n8n API authentication pending)
**Last Updated**: 2026-02-20
