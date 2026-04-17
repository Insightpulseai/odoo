# MCP Gap Remediation Runbook

**Rev:** 2026-04-16
**Authority:** `ssot/tooling/mcp-runtime-state.yaml`, `ssot/tooling/mcp-tooling-policy.yaml`

---

## Priority 1 — Wire `foundry` MCP (5 min)

```bash
# In .mcp.json, the foundry server already exists.
# Set the env var in your shell profile (~/.zshrc or ~/.zprofile):
export AZURE_AI_FOUNDRY_ENDPOINT="https://ipai-copilot-resource.services.ai.azure.com"

# Restart Claude Code to pick up the new env var.
# Verify: foundry MCP tools should appear in deferred tool list.
```

## Priority 2 — Wire `databricks-genie` MCP (5 min)

```bash
# In .mcp.json, the databricks-genie server already exists.
# Set env vars:
export DATABRICKS_HOST="https://adb-7405608559466577.17.azuredatabricks.net"
export DATABRICKS_SQL_WAREHOUSE_ID="e7d89eabce4c330c"

# DATABRICKS_GENIE_SPACE_ID — set if you have a Genie space configured.
# Restart Claude Code.
```

## Priority 3 — Remove deprecated integrations (10 min, portal clicks)

### Claude.ai integrations (Settings → Connected apps)
1. **Cloudflare Developer Platform** → Disconnect (x2 if both appear)
2. **Supabase** → Disconnect
3. **Vercel** → Disconnect
4. **Netlify** → Disconnect

### GitHub org installed apps (github.com/organizations/Insightpulseai/settings/installations)
5. **Vercel** → Uninstall
6. **Cloudflare Workers and Pages** → Uninstall
7. **Supabase** → Uninstall

### Vercel project
8. **vercel.com** → project `insightpulseai-web` → Settings → Delete Project

## Priority 4 — Add Chrome DevTools MCP (when needed)

Only add when actively debugging browser rendering/performance issues.

```bash
# Not in .mcp.json yet. Add when needed:
# npx @anthropic-ai/chrome-devtools-mcp@latest
```

## Priority 5 — Future MCP additions (R3 scope)

| MCP | Purpose | When to add |
|---|---|---|
| `azure-managed-grafana` | Monitoring dashboards | When Grafana is provisioned |
| `fabric-data-agent` | BI/Fabric consumption | When Fabric mirroring is active |
| `google-workspace-ops` | Collaboration ops | Only if GWS integration needed |
| `entra-enterprise` | Dedicated identity investigation | When identity audit scope exceeds `az ad` |

---

## Verification after remediation

```bash
# In Claude Code, after env vars set + deprecated removed:
# 1. Check foundry: invoke any mcp__foundry__* tool
# 2. Check databricks-genie: invoke mcp__databricks_genie__* tool
# 3. Confirm deprecated tools no longer appear in deferred list
# 4. Run: /mcp to see active MCP servers
```

## State after full remediation

| Metric | Before | After |
|---|---|---|
| Active | 8 | 10 (+foundry, +databricks-genie) |
| Needs config | 2 | 0 |
| Deprecated | 4 | 0 |
| Total (cleaned) | 21 | 17 (4 removed) |
