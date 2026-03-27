---
paths:
  - "apps/**/vercel*"
---

> **ARCHIVED — Vercel fully deprecated 2026-03-11. All deployments moved to Azure Container Apps. The Vercel sections below are historical only. The Figma Dev Mode section remains current.**

# Vercel Observability & Figma Dev Mode (ARCHIVED — Vercel Section Only)

> Vercel observability plus integration and Figma dev mode access.

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

*Last updated: 2026-03-16*
