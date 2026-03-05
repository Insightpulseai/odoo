# PPM Clarity — Product Requirements Document

> Clean Portfolio/Program/Project Management using Plane.so templates + Odoo execution tracking.

**Version**: 1.0.0
**Status**: Draft
**Last Updated**: 2026-03-05
**Deployment**: Self-hosted Plane + Self-hosted Odoo

---

## Vision

Enable portfolio/program/project planning in Plane.so templates with operational execution and costing tracked in Odoo, connected via deterministic field-ownership-based sync contract enforced by Supabase SSOT and n8n orchestration.

**Target Users**:
- Portfolio Managers (strategic planning visibility)
- Delivery Leads (execution tracking + resource allocation)
- Finance Controllers (cost tracking + invoicing)

---

## User Stories

### US1: Portfolio Manager — Strategic Planning View

**As a** Portfolio Manager
**I want** to plan initiatives and projects in Plane using templates
**So that** I can visualize strategic priorities across the portfolio

**Acceptance Criteria**:
- Create Plane projects from Portfolio template with predefined states/labels
- Assign work items to cycles (quarterly planning)
- View dashboard showing initiative progress and project health
- Drill down from portfolio → program → project hierarchy
- Export portfolio analytics to Tableau via SSOT aggregation

**Plane Features Used**:
- Project templates with custom states and labels
- Cycles for quarterly planning sprints
- Initiatives for workspace-level strategic goals
- Dashboards with custom widgets (bar charts, pie charts, number widgets)

### US2: Delivery Lead — Execution Tracking

**As a** Delivery Lead
**I want** Odoo to mirror committed Plane work items as tasks with timesheets
**So that** I can track actual hours, assign resources, and measure delivery performance

**Acceptance Criteria**:
- Plane work item with state="Planned" → auto-creates Odoo task with stage="Backlog"
- Odoo task shows Plane metadata: priority, labels, cycle name
- Assign Odoo users to tasks (independent of Plane assignments)
- Log timesheets against tasks with billable/non-billable flags
- Odoo completion (stage="Done") → updates Plane state with facts-only writeback

**Odoo Modules Used**:
- `project` (core project management)
- `hr_timesheet` (time tracking)
- `project_forecast` (resource allocation, OCA module)

### US3: Finance Controller — Cost Tracking & Invoicing

**As a** Finance Controller
**I want** Odoo to capture actual costs from timesheets
**So that** I can invoice clients and track project profitability

**Acceptance Criteria**:
- Timesheet entries calculate costs using employee hourly rates
- View project profitability report: budgeted vs. actual hours
- Mark timesheet lines as billable/non-billable
- Generate invoices from billable timesheet lines
- Export cost analytics to Superset for BI dashboards

**Odoo Modules Used**:
- `hr_timesheet` (timesheet costing)
- `sale_timesheet` (billable hours → invoices)
- `project_budget` (budget vs. actual tracking, OCA module)

### US4: Analytics Engineer — Portfolio Analytics Rollup

**As an** Analytics Engineer
**I want** Odoo operational data aggregated to Plane dashboards
**So that** stakeholders see real-time execution progress in Plane's analytics UI

**Acceptance Criteria**:
- Supabase SSOT table joins Plane work items + Odoo timesheet data
- Scheduled aggregation job (hourly) computes: actual hours, costs, completion %
- Plane dashboard widgets display Odoo metrics via SSOT analytics view
- Superset dashboards show cross-system analytics (Plane planning + Odoo execution)

**Integration Pattern**:
```sql
-- SSOT analytics view
CREATE VIEW ops.work_item_analytics AS
SELECT
  wil.plane_project_id,
  wil.plane_issue_id,
  wil.odoo_task_id,
  SUM(COALESCE(aal.unit_amount, 0)) as actual_hours,
  SUM(COALESCE(aal.amount, 0)) as actual_cost,
  CASE WHEN pt.stage_id = done_stage THEN 1.0 ELSE 0.0 END as completion_pct
FROM ops.work_item_links wil
LEFT JOIN odoo.account_analytic_line aal ON aal.task_id = wil.odoo_task_id
LEFT JOIN odoo.project_task pt ON pt.id = wil.odoo_task_id
GROUP BY wil.plane_project_id, wil.plane_issue_id, wil.odoo_task_id, pt.stage_id;
```

---

## Plane Template Structure

### Portfolio Template

**States** (workflow):
```yaml
states:
  - name: "Ideation"
    type: "backlog"
    description: "Initial concept, not yet committed"
  - name: "Planned"
    type: "started"
    description: "Committed to cycle, ready for execution"
    trigger: "Creates Odoo task when work item enters this state"
  - name: "In Progress"
    type: "started"
    description: "Active work happening"
  - name: "Done"
    type: "completed"
    description: "Work completed and accepted"
```

**Labels** (categorization):
```yaml
labels:
  - name: "Strategic"
    color: "#FF6B6B"
    description: "Strategic initiatives with long-term impact"
  - name: "Operational"
    color: "#4ECDC4"
    description: "Operational improvements and optimizations"
  - name: "Committed"
    color: "#95E1D3"
    description: "Work item committed to Odoo execution"
```

**Work Item Types**:
```yaml
work_item_types:
  - name: "Initiative"
    icon: "target"
    description: "Strategic multi-quarter initiative"
  - name: "Program"
    icon: "layers"
    description: "Set of related projects with shared goals"
  - name: "Project"
    icon: "folder"
    description: "Discrete deliverable with defined scope"
  - name: "Task"
    icon: "check-square"
    description: "Granular work item for execution tracking"
```

### Odoo Project Mapping

**Project Structure**:
```python
# Plane Project → Odoo Project
odoo_project = {
    'name': plane_project['name'],
    'description': plane_project['description'],
    'type_ids': [
        (0, 0, {'name': 'Draft', 'sequence': 1}),      # Maps to Plane "Ideation"
        (0, 0, {'name': 'Backlog', 'sequence': 2}),    # Maps to Plane "Planned"
        (0, 0, {'name': 'In Progress', 'sequence': 3}), # Maps to Plane "In Progress"
        (0, 0, {'name': 'Done', 'sequence': 4})        # Maps to Plane "Done"
    ],
    'allow_timesheets': True,
    'allow_billable': True
}
```

**Task Structure**:
```python
# Plane Work Item → Odoo Task
odoo_task = {
    'name': plane_issue['name'],
    'description': plane_issue['description_html'],
    'project_id': odoo_project_id,
    'stage_id': stage_mapping[plane_issue['state']['name']],
    'priority': priority_mapping[plane_issue['priority']],
    'planned_hours': plane_issue.get('estimate_point', 0) * 8,  # Story points × 8 hours
    # Odoo-only fields (not synced from Plane)
    'user_ids': [],  # Assigned users (managed in Odoo)
    'timesheet_ids': [],  # Time entries (Odoo-only)
    'attachment_ids': []  # Files (Odoo-only)
}
```

---

## Sync Contract

### Commitment Signal (Plane → Odoo)

**Trigger**: Plane work item state changes to "Planned" OR label "Committed" added

**Workflow**:
1. Plane webhook fires with `event: "issue"`, `action: "update"`
2. n8n workflow `ppm-clarity-plane-to-odoo` receives webhook
3. Validate HMAC-SHA256 signature
4. Check commitment signal: `state === "Planned"` OR `"Committed" in labels`
5. Query `ops.work_item_links` for existing mapping
6. If no mapping: Create Odoo task + insert link record
7. If mapping exists: Update Odoo task with Plane-owned fields
8. Calculate Plane hash, update `last_plane_hash` in link record
9. Append event to `ops.work_item_events` with `event_type: 'plane_to_odoo'`

**Plane-Owned Fields Synced**:
- `name` → `title`
- `description_html` → `description`
- `priority` → `priority` (enum mapping)
- `label_ids` → stored in `ops.work_item_links.event_data` (informational)
- `state_id` → `stage_id` (state→stage mapping)
- `estimate_point` → `planned_hours` (story points × 8)

### Completion Signal (Odoo → Plane)

**Trigger**: Odoo task stage changes to "Done"

**Workflow**:
1. n8n cron (every 10 minutes) queries Odoo tasks with `stage_id = done_stage` AND `write_date > last_sync`
2. For each completed task: Query `ops.work_item_links` for Plane mapping
3. If mapping exists: Call Plane MCP `update_work_item` with `state: completed_state_id`
4. Append comment to Plane issue: "Task completed in Odoo. Actual hours: X, Cost: $Y"
5. Calculate Odoo hash, update `last_odoo_hash` in link record
6. Append event to `ops.work_item_events` with `event_type: 'odoo_to_plane'`

**Facts-Only Writeback** (Odoo → Plane):
- Completion status (state change to "Done")
- Summary metrics in comment: actual hours, cost, completion date
- **Never** write back: assigned users, timesheet details, attachments (Odoo-owned)

### Conflict Reconciliation (Nightly)

**Trigger**: Cron at 2 AM daily

**Workflow**:
1. Query `ops.work_item_links` WHERE `last_plane_hash` AND `last_odoo_hash` both changed since `last_synced_at`
2. For each conflict: Fetch current Plane issue via MCP, current Odoo task via RPC
3. Apply field ownership rules:
   - Plane-owned fields: Update Odoo with Plane values
   - Odoo-owned fields: Update Plane comment with Odoo facts
4. Recalculate both hashes, update link record
5. Append event with `event_type: 'reconciliation'`

---

## Analytics Integration

### Plane Dashboards

**Dashboard Types** (available in Plane):
- **Overview**: Workspace-level metrics (work item counts, user activity, project health)
- **Projects Analysis**: Project lifecycle, team composition, resource allocation
- **Work Items Analysis**: Task distribution by state with "created vs resolved" trends
- **Cycles Analysis**: Sprint progress with completion percentages

**Custom Widgets**:
```yaml
widgets:
  - type: "bar_chart"
    title: "Actual Hours by Project"
    data_source: "ops.work_item_analytics"
    x_axis: "plane_project_id"
    y_axis: "SUM(actual_hours)"
    grouping: "plane_project_id"

  - type: "donut_chart"
    title: "Cost Breakdown by Priority"
    data_source: "ops.work_item_analytics"
    metric: "SUM(actual_cost)"
    grouping: "priority"

  - type: "number_widget"
    title: "Total Actual Cost (Month)"
    data_source: "ops.work_item_analytics"
    metric: "SUM(actual_cost)"
    filter: "created_at >= date_trunc('month', now())"
```

### Superset Integration

**Data Pipeline**:
1. Supabase SSOT view `ops.work_item_analytics` joins Plane + Odoo data
2. Superset connects to Supabase PostgreSQL (read-only user)
3. Create Superset dataset from `ops.work_item_analytics` view
4. Build dashboards with charts:
   - Portfolio health: Planned vs. Actual hours
   - Project profitability: Budgeted cost vs. Actual cost
   - Resource utilization: User timesheet totals

**Superset Charts**:
```yaml
charts:
  - type: "bar"
    title: "Planned vs. Actual Hours by Project"
    dataset: "ops.work_item_analytics"
    metrics:
      - "SUM(planned_hours)"
      - "SUM(actual_hours)"
    groupby: ["plane_project_id"]

  - type: "line"
    title: "Actual Cost Trend (Weekly)"
    dataset: "ops.work_item_analytics"
    metrics: ["SUM(actual_cost)"]
    time_grain: "week"
    time_column: "created_at"
```

---

## Self-Hosted Deployment

### Plane Self-Hosted Setup

**Installation** (Docker Compose):
```yaml
# docker-compose.plane.yml
version: '3.8'
services:
  plane-web:
    image: makeplane/plane-frontend:latest
    environment:
      NEXT_PUBLIC_API_BASE_URL: https://plane-api.insightpulseai.com
      NEXT_PUBLIC_WEB_BASE_URL: https://plane.insightpulseai.com
    ports:
      - "3000:3000"

  plane-api:
    image: makeplane/plane-backend:latest
    environment:
      DATABASE_URL: postgresql://plane:${PLANE_DB_PASSWORD}@postgres:5432/plane
      REDIS_URL: redis://redis:6379
      SECRET_KEY: ${PLANE_SECRET_KEY}
      PLANE_BASE_URL: https://plane.insightpulseai.com
    ports:
      - "8000:8000"

  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: plane
      POSTGRES_USER: plane
      POSTGRES_PASSWORD: ${PLANE_DB_PASSWORD}
    volumes:
      - plane-postgres:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - plane-redis:/data

volumes:
  plane-postgres:
  plane-redis:
```

**DNS Configuration**:
```yaml
# infra/dns/subdomain-registry.yaml
subdomains:
  - name: plane
    type: A
    target: 178.128.112.214  # DigitalOcean droplet
    ttl: 300
    description: "Plane.so self-hosted (frontend)"

  - name: plane-api
    type: A
    target: 178.128.112.214
    ttl: 300
    description: "Plane.so API (backend)"
```

### Plane MCP Server Configuration (Self-Hosted)

**Environment Variables**:
```bash
# ~/.zshrc or .env
export PLANE_API_KEY=<your-workspace-api-key>
export PLANE_WORKSPACE_SLUG=insightpulseai
export PLANE_BASE_URL=https://plane-api.insightpulseai.com  # Self-hosted API URL
```

**MCP Server Setup** (Claude Code):
```json
{
  "plane": {
    "command": "uvx",
    "args": ["plane-mcp-server"],
    "env": {
      "PLANE_API_KEY": "$PLANE_API_KEY",
      "PLANE_WORKSPACE_SLUG": "$PLANE_WORKSPACE_SLUG",
      "PLANE_BASE_URL": "https://plane-api.insightpulseai.com"
    }
  }
}
```

**Verification**:
```bash
# Test MCP server connectivity
curl -X POST http://localhost:8765/mcp/plane/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "list_projects",
    "arguments": {}
  }'
```

### Webhook Endpoint (Self-Hosted)

**n8n Webhook Configuration**:
```yaml
# n8n webhook URL
webhook_url: https://n8n.insightpulseai.com/webhook/ppm-clarity/plane

# Plane webhook setup (via UI)
webhook_endpoint: https://n8n.insightpulseai.com/webhook/ppm-clarity/plane
secret_key: ${PLANE_WEBHOOK_SECRET}  # Generate via `openssl rand -hex 32`
events:
  - project.create
  - project.update
  - issue.create
  - issue.update
  - cycle.create
  - cycle.update
```

**nginx Reverse Proxy**:
```nginx
# /etc/nginx/sites-available/n8n
server {
    listen 443 ssl http2;
    server_name n8n.insightpulseai.com;

    ssl_certificate /etc/letsencrypt/live/n8n.insightpulseai.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/n8n.insightpulseai.com/privkey.pem;

    location /webhook/ppm-clarity/plane {
        limit_req zone=webhook_limit burst=10 nodelay;
        proxy_pass http://localhost:5678/webhook/ppm-clarity/plane;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 30s;
    }
}
```

---

## Security & Compliance

### Authentication

**Plane API Key**:
- Generated in Plane workspace settings
- Stored in Supabase Vault: `vault.secrets.plane_api_key`
- Never committed to git or logged in plain text
- Rotate every 90 days

**Odoo Service Account**:
- Dedicated user: `plane_sync@insightpulseai.com`
- Permissions: `project.task` read/write, `account.analytic.line` read-only
- Password stored in Supabase Vault: `vault.secrets.odoo_service_password`

**Webhook Secret**:
- Generate: `openssl rand -hex 32`
- Stored in Supabase Vault: `vault.secrets.plane_webhook_secret`
- Used for HMAC-SHA256 signature verification

### Data Privacy

**PII Handling**:
- User names and emails NOT synced between systems
- Only user IDs referenced in SSOT tables
- Timesheet costs aggregated, individual entries not exposed to Plane
- Attachments remain Odoo-only (never synced to Plane)

**GDPR Compliance**:
- User consent required for cross-system data sync
- Right to erasure: Delete from `ops.work_item_links` + orphan cleanup
- Data retention: 90 days for `ops.work_item_events`, indefinite for links

---

## Success Metrics

### M1: Sync Reliability
- **Target**: ≥99.5% sync success rate
- **Measurement**: `SUM(success) / COUNT(*) FROM ops.work_item_events`
- **Threshold**: Alert if <95% in 24-hour window

### M2: Sync Latency
- **Target**: <5 minutes from Plane change to Odoo update
- **Measurement**: `(odoo_update_time - plane_webhook_time)` from event metadata
- **Threshold**: Alert if median >10 minutes

### M3: Conflict Rate
- **Target**: <1% of syncs trigger conflict reconciliation
- **Measurement**: `COUNT(event_type='conflict') / COUNT(*) FROM ops.work_item_events`
- **Threshold**: Alert if >5% in 7-day window

### M4: Analytics Freshness
- **Target**: Superset dashboards show data <1 hour old
- **Measurement**: `now() - MAX(updated_at) FROM ops.work_item_analytics`
- **Threshold**: Alert if >2 hours stale

### M5: User Adoption
- **Target**: ≥80% of projects use Plane → Odoo sync
- **Measurement**: `COUNT(DISTINCT plane_project_id) / total_projects FROM ops.work_item_links`
- **Threshold**: Review if <50% after 30 days

---

## Non-Goals

### NG1: Real-Time Sync
- Acceptable latency: 10 minutes (cron-based)
- Rationale: Real-time would require complex event streaming infrastructure

### NG2: Bidirectional Timesheet Sync
- Timesheets remain Odoo-only (never write to Plane)
- Rationale: Plane lacks timesheet schema, summary metrics sufficient

### NG3: Plane Agent Integration
- Use n8n orchestration instead of Plane Agents (Beta)
- Rationale: Agents require @mentions, not suitable for automated sync

### NG4: Multi-Workspace Support
- Single Plane workspace (`insightpulseai`)
- Rationale: Multi-workspace adds significant complexity

---

## References

- **Plane Self-Hosted Docs**: https://docs.plane.so/self-hosting
- **Plane API Reference**: https://developers.plane.so/api-reference
- **Plane MCP Server**: https://developers.plane.so/dev-tools/mcp-server-claude-code
- **Odoo Project Management**: https://www.odoo.com/documentation/19.0/applications/services/project.html
- **Supabase RPC Functions**: https://supabase.com/docs/guides/database/functions

---

**Status**: Ready for implementation plan creation (`/speckit.plan`)
