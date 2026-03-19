# Plane Finance PPM Template

SSOT-driven Plane template system for Finance PPM execution tracking.

## Overview

This directory contains the canonical template definition for the Finance PPM Plane project, which tracks month-end close and BIR tax filing execution. The project is **owned in Odoo** (master) and **tracked in Plane** (sync target), with bidirectional sync via PPM Clarity workflows.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SSOT Source of Truth                         │
├─────────────────────────────────────────────────────────────────┤
│  addons/ipai/ipai_finance_close_seed/data/06_tasks_month_end.xml│  ← Canonical
│           ↓ (extract metadata)                                  │
│  ssot/plane/templates/finops_month_end.yaml                     │  ← Template
│           ↓ (seed via API)                                      │
│  scripts/plane/seed_finops_from_xlsx.py                         │  ← Seeder
│           ↓ (creates in Plane)                                  │
│  Plane Workspace: fin-ops / Project: FINOPS                     │  ← Live
│           ↕ (bidirectional sync)                                │
│  automations/n8n/workflows/ppm-clarity-*.json                   │  ← Sync
│           ↕                                                      │
│  Odoo Project: Finance PPM - Month-End Close                    │  ← Master
└─────────────────────────────────────────────────────────────────┘
```

## Files

| File | Purpose |
|------|---------|
| `finops_month_end.yaml` | SSOT template definition (workflow states, labels, modules, field ownership) |
| `README.md` | This documentation file |

## Workflow

### 1. Template Definition (SSOT)

Edit `finops_month_end.yaml` to define:
- Workspace and project configuration
- Workflow states (Backlog, Planned, Committed, In Progress, Blocked, Done)
- Labels (25 task categories + 5 phase labels)
- Modules (5 phases: Initial, Accruals, WIP, Final Adjustments, Sign-off)
- Field ownership contract (Plane-owned vs Odoo-owned fields)
- Sync configuration (bidirectional, conflict resolution via field ownership)

### 2. Data Preparation

Prepare task data in one of two formats:

**Option A: Excel File**
```bash
# Create Excel with columns:
# - Task Category (e.g., "Payroll & Personnel")
# - Detailed Monthly Tasks (task title)
# - Phase (e.g., "Phase I")
# - Prep By (employee code, e.g., "RIM")
# - Review By (employee code, e.g., "CKVC")
# - Approve By (employee code, e.g., "CKVC")
# - Planned Hours (effort estimate, default: 16.0)
```

**Option B: Canonical XML** (fallback)
```bash
# Seeder will parse directly from:
# addons/ipai/ipai_finance_close_seed/data/06_tasks_month_end.xml
```

### 3. Seeding via API

```bash
# Set environment variables
export PLANE_API_KEY=<your_api_key>               # Required
export PLANE_WORKSPACE_SLUG=fin-ops               # Default: fin-ops
export FINOPS_XLSX_PATH=/path/to/tasks.xlsx       # Optional (fallback to XML)
export PLANE_BASE_URL=https://api.plane.so        # Default

# Dry run (no API calls)
export DRY_RUN=true
python scripts/plane/seed_finops_from_xlsx.py

# Production run
unset DRY_RUN
python scripts/plane/seed_finops_from_xlsx.py
```

**Expected Output:**
```
============================================================
Plane Finance PPM Template Seeder
============================================================
Workspace: fin-ops
Base URL: https://api.plane.so
Rate limit: 60 req/min (1.1s sleep)
Dry run: false
============================================================
[INFO] Reading Excel file: /path/to/tasks.xlsx
[INFO] Parsed 39 tasks from Excel
[INFO] Checking for existing project in workspace: fin-ops
[INFO] Creating new project: Finance PPM — Month-end Close
[INFO] Created project: <project_id>
[INFO] Creating 30 unique labels...
[INFO] Creating label: Payroll & Personnel (#f56565)
...
[INFO] Creating 39 work items...
[INFO] Created work item: [I.1] Process and record Payroll... (ID: <item_id>)
[INFO] Progress: 1/39 (1/39)
...
============================================================
Seeding complete!
Project ID: <project_id>
Labels created: 30
Work items created: 39/39
API requests: 72
Total time: 79.2s
============================================================
```

### 4. Verification

Run verification checks from template YAML:

```bash
# Check workspace exists
curl -H "X-API-Key: $PLANE_API_KEY" \
  https://api.plane.so/api/v1/workspaces/$PLANE_WORKSPACE_SLUG/ | jq .

# Check project created
curl -H "X-API-Key: $PLANE_API_KEY" \
  https://api.plane.so/api/v1/workspaces/$PLANE_WORKSPACE_SLUG/projects/ \
  | jq '.[] | select(.name=="Finance PPM — Month-end Close")'

# Check labels seeded (expected: 30)
curl -H "X-API-Key: $PLANE_API_KEY" \
  https://api.plane.so/api/v1/workspaces/$PLANE_WORKSPACE_SLUG/projects/$PROJECT_ID/labels/ \
  | jq 'length'

# Check work items seeded (expected: 39 for month-end, 48 if including BIR)
curl -H "X-API-Key: $PLANE_API_KEY" \
  https://api.plane.so/api/v1/workspaces/$PLANE_WORKSPACE_SLUG/work-items/ \
  | jq 'length'
```

### 5. Sync Activation

Once seeded, activate bidirectional sync:

```bash
# Deploy n8n workflows (if not already deployed)
cd automations/n8n
n8n import:workflow --input=workflows/ppm-clarity-plane-to-odoo.json
n8n import:workflow --input=workflows/ppm-clarity-odoo-to-plane.json
n8n import:workflow --input=workflows/ppm-clarity-reconciliation.json
n8n import:workflow --input=workflows/ppm-clarity-slack-commands.json

# Configure webhooks
# - Plane: Settings → Integrations → Webhooks → Add webhook
#   URL: https://n8n.insightpulseai.com/webhook/plane-to-odoo
#   Events: issue.created, issue.updated, issue.deleted
```

## Field Ownership Contract

From `finops_month_end.yaml`:

| Field Category | Owning System | Sync Direction |
|----------------|---------------|----------------|
| **Plane-Owned** | Plane (authoritative) | Plane → Odoo |
| `name`, `description`, `labels` | Plane | One-way |
| `estimate_point`, `priority` | Plane | One-way |
| `start_date`, `target_date` | Plane | One-way |
| **Odoo-Owned** | Odoo (authoritative) | Odoo → Plane |
| `stage_id` (workflow state) | Odoo | One-way |
| `user_ids` (assignees) | Odoo | One-way |
| `date_deadline` | Odoo | Odoo wins on conflict |
| `planned_hours`, `effective_hours` | Odoo | One-way |
| `progress` | Odoo | One-way (no Plane equivalent) |
| **Shared** | Both | Conflict resolution |
| `state` | Both | Reconciliation workflow |

## Rate Limiting

Plane API: **60 requests/minute**

Seeder configuration:
- Sleep: `1.1s` between requests
- Effective rate: `54.5 req/min` (safe margin)
- Total time for 39 tasks: `~79s` (72 API calls × 1.1s)

## Slack Notifications

Sync events are logged to:
- Success: `#ppm-clarity-logs`
- Failure: `#ppm-clarity-alerts`
- Conflicts: `#ppm-clarity-conflicts`

## Troubleshooting

**Error: `openpyxl not installed`**
```bash
pip install openpyxl
```

**Error: `PLANE_API_KEY environment variable not set`**
```bash
# Get API key from Plane:
# Settings → Account → API Tokens → Create Token
export PLANE_API_KEY=<your_key>
```

**Error: Rate limit exceeded (429)**
```bash
# Increase sleep time in seeder script
# Edit: scripts/plane/seed_finops_from_xlsx.py
# Change: rate_limit_sleep: float = 1.5  # Increase to 1.5s (40 req/min)
```

**Dry-run mode for testing**
```bash
export DRY_RUN=true
python scripts/plane/seed_finops_from_xlsx.py
# No API calls will be made, only validation and logging
```

## References

- **SSOT Template**: `ssot/plane/templates/finops_month_end.yaml`
- **Seeder Script**: `scripts/plane/seed_finops_from_xlsx.py`
- **Canonical Seed**: `addons/ipai/ipai_finance_close_seed/data/06_tasks_month_end.xml`
- **PPM Clarity Spec**: `spec/ppm-clarity-plane-odoo/plan.md`
- **n8n Workflows**: `automations/n8n/workflows/ppm-clarity-*.json`
- **Plane API Docs**: https://docs.plane.so/api-reference

## Maintenance

**Update labels:**
1. Edit `finops_month_end.yaml` → `labels_from_seed` section
2. Re-run seeder script (will create only new labels)

**Add new tasks:**
1. Add rows to Excel file or update canonical XML
2. Re-run seeder script (work items are idempotent by title)

**Modify field ownership:**
1. Edit `finops_month_end.yaml` → `field_ownership` section
2. Update n8n reconciliation workflow logic
3. Redeploy workflows

**Change sync configuration:**
1. Edit `finops_month_end.yaml` → `sync` section
2. Update n8n workflow parameters
3. Redeploy workflows
