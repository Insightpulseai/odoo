# Integrations
> Extracted from root CLAUDE.md. See [CLAUDE.md](../../CLAUDE.md) for authoritative rules.

---

## n8n Workflows

- Located in `n8n/` directory
- Deploy with: `./scripts/deploy-n8n-workflows.sh`
- Activate with: `./scripts/activate-n8n-workflows.sh`

## Slack ChatOps

- Slack workspace for team communication
- Claude installed in Slack for AI assistance
- Webhooks for alerts and notifications
- AI assistant integrations

## Figma Dev Mode Access

**Prerequisites:**
- Dev seat or Full seat on a paid Figma plan (Collab/View-only seats do NOT include Dev Mode)
- Personal Access Token with required scopes

**Seat Comparison:**

| Seat Type | Dev Mode | Variables API | Code Connect |
|-----------|----------|---------------|--------------|
| Full      | Yes      | Enterprise    | Yes          |
| Dev       | Yes      | Enterprise    | Yes          |
| Collab    | No       | No            | No           |
| View-only | No       | No            | No           |

**Setup Commands:**

```bash
# 1. Set environment variables
export FIGMA_ACCESS_TOKEN=figd_xxxxxxxxxxxxx
export FIGMA_FILE_KEY=your_file_key_here

# 2. Verify access
./scripts/figma/verify_dev_mode_access.sh

# 3. Install Code Connect CLI
npm install --global @figma/code-connect@latest

# 4. Publish component mappings
npx figma connect publish --token="$FIGMA_ACCESS_TOKEN"

# 5. Export variables (Enterprise only)
./scripts/figma/figma_export_variables.sh
```

**Hotkey:** Toggle Dev Mode in Figma with `Shift + D`

**Note:** The Variables REST API is only available to full members of Enterprise orgs. For non-Enterprise plans, use Code Connect or Figma Tokens Studio plugin.

---

## n8n Automation Layer

### GitHub Events Handler

```
+---------------------------------------------------------------------+
|                    n8n.insightpulseai.com                            |
+---------------------------------------------------------------------+
|  GitHub Webhooks (via pulser-hub app)                                |
|  |-- Push to main -> Deploy to erp.insightpulseai.com               |
|  |-- PR opened -> Odoo task + Slack notification                    |
|  |-- Issue labeled "ai" -> Claude Code agent workflow               |
|  |-- @claude comment -> Queue for AI processing                     |
|  +-- CI failure -> Immediate Slack alert                            |
|                                                                      |
|  Scheduled Jobs                                                      |
|  |-- Daily: Export Actions logs -> Supabase audit_logs              |
|  |-- Weekly: Dependency update digest -> Email                      |
|  +-- Monthly: Compliance report -> Superset snapshot                |
+---------------------------------------------------------------------+
```

### Event Routing

```javascript
// n8n webhook receives GitHub events
const event = headers['x-github-event'];
const payload = body;

switch(event) {
  case 'push':
    if (payload.ref === 'refs/heads/main') {
      return { action: 'deploy', branch: payload.ref };
    }
    break;
  case 'pull_request':
    return { action: 'create_odoo_task', pr: payload.pull_request };
  case 'issue_comment':
    if (payload.comment.body.includes('@claude')) {
      return { action: 'queue_claude', issue: payload.issue };
    }
    break;
}
```

---

## Vercel Observability Plus Integration

**Cost**: $10/mo + usage
**Module**: `ipai_connector_vercel`

### What You Get

| Feature | Value |
|---------|-------|
| 30-day retention | Historical data access |
| Function latency (p75) | Performance metrics |
| Path breakdown | Per-route analytics |
| External API metrics | Third-party call tracking |
| Runtime logs (30d) | Error debugging |

### Integration Pattern

```python
# ipai_connector_vercel/models/vercel_sync.py
class VercelConfig(models.Model):
    _name = "ipai.vercel.config"

    workspace_url = fields.Char(required=True)
    api_token = fields.Char(required=True)
    error_rate_threshold = fields.Float(default=5.0)
    latency_p75_threshold = fields.Integer(default=3000)

    def _cron_sync_metrics(self):
        """Sync Vercel metrics -> create Odoo tasks for alerts"""
        # Fetch from Vercel API
        # Create project.task if threshold exceeded
```

---

## Claude Integration

### Claude in Slack

Claude is installed in Slack workspace. Usage:
- Direct chat: Message Claude in Apps section
- Channel mentions: @Claude in channels
- Combined with GitHub: @claude in PR comments -> n8n -> processing

### Claude Code MCP

```bash
# Add GitHub MCP to Claude Code
claude mcp add github \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxx \
  -- npx -y @anthropic-ai/mcp-server-github
```

### Claude as PR Agent

```bash
#!/bin/bash
# ~/bin/claude-pr - Automated PR generation
ISSUE_NUM=$1
gh issue view "$ISSUE_NUM" --json title,body > /tmp/issue.json

claude --print "Implement this GitHub issue:
$(cat /tmp/issue.json)
Repository: Odoo 18 CE, ipai_* conventions, OCA style."

gh pr create --title "$(jq -r .title /tmp/issue.json)" \
  --body "Closes #$ISSUE_NUM - Generated by Claude Code"
```
