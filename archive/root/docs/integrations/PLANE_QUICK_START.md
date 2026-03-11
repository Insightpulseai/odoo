# Plane Integration - Quick Start

> 5-minute setup for Plane MCP + Marketplace integrations

## ⚡ Quick Setup (5 minutes)

### Step 1: Set Environment Variables

```bash
# Get your API key from: https://plane.insightpulseai.com/profile
export PLANE_API_KEY="your_plane_api_key"
export PLANE_WORKSPACE_SLUG="fin-ops"
export PLANE_API_URL="https://plane.insightpulseai.com/api/v1"

# Add to ~/.zshrc for persistence
echo 'export PLANE_API_KEY="your_plane_api_key"' >> ~/.zshrc
echo 'export PLANE_WORKSPACE_SLUG="fin-ops"' >> ~/.zshrc
echo 'export PLANE_API_URL="https://plane.insightpulseai.com/api/v1"' >> ~/.zshrc
```

### Step 2: Verify MCP Server

```bash
cd /Users/tbwa/Documents/GitHub/Insightpulseai/odoo
./scripts/verify_plane_mcp.sh
```

**Expected Output**:
```
✅ Environment variables set
✅ Plane MCP server built
✅ MCP server registered
✅ Plane API accessible (HTTP 200)
✅ Successfully fetched N projects
```

### Step 3: Restart Claude Code

Restart Claude Code to load the Plane MCP server.

### Step 4: Test MCP Access

In Claude Code, run:
```
"List all Plane projects"
```

Expected: JSON response with `fin-ops` project details.

---

## 📱 Marketplace Integrations (15 minutes)

### Plane ↔ Slack

1. Visit: `https://plane.insightpulseai.com/settings/integrations`
2. Click: **Connect Slack**
3. Install Plane Slack App
4. Configure notification channels
5. Test: `/plane help` in Slack

### GitHub ↔ Slack

1. In Slack: `/github install`
2. Authorize: https://github.com/integrations/slack
3. Subscribe: `/github subscribe Insightpulseai/odoo issues pulls`
4. Test: Create GitHub issue → verify Slack notification

### GitHub ↔ Plane

1. Visit: `https://plane.insightpulseai.com/settings/integrations`
2. Click: **Connect GitHub**
3. Authorize `Insightpulseai` organization
4. Map: `Insightpulseai/odoo` → `fin-ops` project
5. Test: Create GitHub issue → verify in Plane

---

## ✅ Verification Checklist

- [ ] `PLANE_API_KEY` environment variable set
- [ ] `./scripts/verify_plane_mcp.sh` passes all checks
- [ ] Claude Code MCP responds to "List all Plane projects"
- [ ] Plane Slack App installed and notifications working
- [ ] GitHub Slack App installed and subscribed to repos
- [ ] GitHub → Plane sync configured and tested

---

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| MCP not responding | `./scripts/verify_plane_mcp.sh` → check env vars |
| API key invalid | Get new key from `plane.insightpulseai.com/profile` |
| No projects found | Check `PLANE_WORKSPACE_SLUG="fin-ops"` |
| Build errors | `cd mcp/servers/plane && npm install && npm run build` |

---

## 📚 Full Documentation

See: `docs/integrations/PLANE_INTEGRATION_GUIDE.md`

---

**Status**: Ready to use ✅
