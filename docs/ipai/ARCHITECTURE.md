# IPAI Module Suite - System Architecture

## Overview

The IPAI module suite implements a **five-layer architecture** designed for enterprise financial management, project portfolio management, and operational governance on Odoo 18 CE.

**Design Principles**:
- **Separation of Concerns**: Each layer has distinct responsibilities
- **Dependency Hierarchy**: Higher layers depend on lower layers only (no circular dependencies)
- **OCA Compliance**: Full AGPL-3 compliance with standard Odoo/OCA patterns
- **Data Integrity**: Strong referential integrity with cascade rules
- **Performance**: Optimized queries with proper indexing and caching

## Architectural Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│  ┌────────────────┐  ┌────────────────┐  ┌─────────────┐   │
│  │   Finance (14) │  │   Industry (2) │  │   Other (11) │   │
│  │   PPM, BIR,    │  │   Accounting   │  │   Advisor,   │   │
│  │   Month-End    │  │   Marketing    │  │   Assets, SRM│   │
│  └────────────────┘  └────────────────┘  └─────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           ↓ depends on
┌─────────────────────────────────────────────────────────────┐
│                      WorkOS Layer (1)                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  ipai_workspace_core: Notion/AFFiNE parity             │ │
│  │  Blocks, Pages, Databases, Collaboration               │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                           ↓ depends on
┌─────────────────────────────────────────────────────────────┐
│                  Platform/Utilities Layer (2)                │
│  ┌────────────────┐  ┌────────────────────────────────────┐ │
│  │ ipai_ce_cleaner│  │  ipai_ce_branding                  │ │
│  │ Enterprise deps│  │  InsightPulse AI branding          │ │
│  └────────────────┘  └────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                           ↓ depends on
┌─────────────────────────────────────────────────────────────┐
│                    Odoo Core Modules                         │
│  base, mail, project, hr, account, stock, barcodes          │
└─────────────────────────────────────────────────────────────┘
```

### Layer 1: Odoo Core (Foundation)
**Provided by Odoo CE 18.0**:
- `base` - Core framework (models, fields, ORM, security)
- `mail` - Mail threading, activities, followers
- `project` - Projects, tasks, stages
- `hr` - Employees, departments, contracts
- `account` - Chart of accounts, journal entries, invoices
- `stock` - Warehouses, locations, inventory
- `barcodes` - Barcode scanning infrastructure

### Layer 2: Platform/Utilities
**Purpose**: Foundation utilities and branding

**Modules**:
- **ipai_ce_cleaner** (CRITICAL): Removes Enterprise/IAP dependencies
  - Patches `web.assets_backend` to remove Enterprise JS
  - Disables IAP (In-App Purchases) modules
  - Ensures CE-only deployment

- **ipai_ce_branding**: InsightPulse AI branding
  - Logo replacement
  - CSS theming
  - Favicon customization

**Dependencies**: Odoo core only (base, web)

### Layer 3: WorkOS (Collaboration Platform)
**Purpose**: Notion/AFFiNE-style workspace collaboration

**Module**:
- **ipai_workspace_core**: Workspace engine
  - **Models**: `ipai.workspace`, `ipai.workspace.page`, `ipai.workspace.block`, `ipai.workspace.database`
  - **Features**: Real-time collaboration, block-based editing, database views, templates
  - **Integration**: Mail threading for comments, followers for sharing

**Dependencies**: base, mail, portal

### Layer 4: Finance (Business Logic)
**Purpose**: Financial operations, PPM, BIR compliance, month-end closing

**Core Modules** (install order):
1. **ipai_finance_ppm** - Finance PPM foundation
   - Models: `ipai.finance.logframe`, `ipai.finance.bir_schedule`, `ipai.finance.person`, `ipai.finance.task`
   - BIR schedule with internal deadlines (prep/review/approval)
   - Logframe tracking (Goal → Outcome → IM1/IM2 → Outputs → Activities)
   - Task automation (3 tasks per BIR form)

2. **ipai_bir_compliance** - Tax Shield (Philippines)
   - Models: `ipai.bir.form`, `ipai.bir.attachment`
   - 8 BIR forms: 1601-C, 2550Q, 1702-RT, 0619-E, 1601-EQ, 1601-FQ
   - Validation rules, filing deadlines, penalty tracking

3. **ipai_ppm_a1** - A1 Control Center
   - Extends `ipai.finance.logframe` with A1 workflow
   - Workstream management (AFC, STC, FPA)
   - RACI assignment automation

4. **ipai_close_orchestration** - Close Cycle Engine
   - Models: `ipai.close.cycle`, `ipai.close.task`
   - Multi-stage execution: planning → execution → review → close
   - Dependency management, gate enforcement

5. **ipai_finance_bir_compliance** - BIR Compliance (Schedule + Generator)
   - Seed data: BIR calendar for 2025-2026
   - Auto-task generation from schedule
   - Multi-employee support (8 employees)

**Advanced Modules** (depends on core):
6. **ipai_finance_month_end** - Month-End Templates
   - W101 snapshot (101-day look-back)
   - Template library for recurring tasks
   - Approval workflow (Supervisor → Manager → Director)

7. **ipai_finance_ppm_dashboard** - ECharts Dashboards
   - Controller: `/ipai/finance/ppm`
   - Visualizations: BIR deadline timeline, completion tracking, status distribution, logframe overview
   - KPI cards: Total forms, on-time filings, at risk, late filings

8. **ipai_finance_ppm_tdi** - Transaction Data Ingestion
   - ETL pipeline: Bronze → Silver → Gold
   - Column mapping with fuzzy matching
   - Data quality metrics

9. **ipai_finance_ppm_closing** - PPM Closing Generator
   - Auto-generate closing tasks from templates
   - Period rollover automation
   - Historical tracking

10. **ipai_finance_project_hybrid** - Finance/Project Hybrid
    - IM1/IM2 logic integration
    - Project task synchronization
    - Unified reporting

11. **ipai_finance_monthly_closing** - Monthly Closing Workflows
    - Bank reconciliation automation
    - GL reconciliation checklists
    - Journal entry templates

12. **ipai_clarity_ppm_parity** - Clarity PPM Parity
    - Feature-for-feature Clarity PPM replication
    - Resource allocation views
    - Portfolio dashboards

13. **ipai_ppm** - Portfolio & Program Management
    - Program hierarchy
    - Resource pooling
    - Cross-project reporting

14. **ipai_ppm_monthly_close** - Monthly Close Scheduler
    - Cron-based close cycle triggers
    - Email notifications
    - Close status dashboard

**Dependencies**: base, mail, project, account

### Layer 5: Industry (Vertical Specializations)
**Purpose**: Industry-specific configurations

**Modules**:
- **ipai_industry_accounting_firm**: Accounting firm operations
  - Client project templates
  - Time tracking by client
  - Audit workflow automation

- **ipai_industry_marketing_agency**: Marketing agency operations
  - Campaign project templates
  - Creative asset management
  - Client approval workflows

**Dependencies**: base, project, sale (optional)

### Layer 6: Other/Operations (Horizontal Tools)
**Purpose**: Cross-functional operational tools

**Key Modules**:
- **ipai_advisor**: Azure Advisor-style recommendations
  - Models: `ipai.advisor.category`, `ipai.advisor.recommendation`, `ipai.advisor.playbook`, `ipai.advisor.score`
  - Webhook integration for external advisors
  - Playbook automation

- **ipai_assets**: Cheqroom-parity asset management
  - Models: `ipai.asset`, `ipai.asset.checkout`, `ipai.asset.reservation`
  - Barcode scanning
  - QR code generation
  - Reservation calendar

- **ipai_expense**: Expense & Travel (PH tax rules)
  - Philippine tax withholding
  - Per diem calculations
  - Mileage tracking

- **ipai_master_control**: Work intake management
  - Request forms
  - Triage workflows
  - SLA tracking

- **ipai_srm**: Supplier Relationship Management
  - Supplier onboarding
  - Performance scoring
  - Contract management

- **ipai_equipment**: Equipment management
  - Maintenance schedules
  - Service history
  - Warranty tracking

- **ipai_project_program**: Program + IM Projects
  - Program hierarchy
  - IM project templates
  - Cross-program resource allocation

**Dependencies**: base, mail, hr (for assets), account (for expenses)

## Data Model Architecture

### Core Entity Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                     Finance PPM Domain                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ipai.finance.logframe (1)                                   │
│    ↓ o2m                                                     │
│  ipai.finance.bir_schedule (*)                               │
│    ↓ o2m                                                     │
│  project.task (*)  ←──┐                                      │
│    ↑ m2o            │                                        │
│  ipai.finance.task (*)  ←─ extends project.task             │
│    ↓ m2o            │                                        │
│  ipai.finance.person (*)                                     │
│                     │                                        │
│  ipai.finance.bir_schedule (*) ──→ ipai.finance.person (*)   │
│                (responsible_id)                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      WorkOS Domain                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ipai.workspace (1)                                          │
│    ↓ o2m                                                     │
│  ipai.workspace.page (*)                                     │
│    ↓ o2m                                                     │
│  ipai.workspace.block (*)                                    │
│    ↑ m2o (parent_id - self-referential tree)                │
│                                                              │
│  ipai.workspace.database (*)                                 │
│    ↓ o2m                                                     │
│  ipai.workspace.database.row (*)                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                       Asset Domain                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ipai.asset (*)                                              │
│    ↓ o2m                                                     │
│  ipai.asset.checkout (*)                                     │
│    ↑ m2o (asset_id)                                          │
│    ↓ m2o                                                     │
│  hr.employee (*)                                             │
│                                                              │
│  ipai.asset.reservation (*)  ←─ m2o ─→ ipai.asset (*)       │
│                              ←─ m2o ─→ hr.employee (*)       │
└─────────────────────────────────────────────────────────────┘
```

### Shared Patterns & Mixins

**mail.thread Mixin** (used by most IPAI models):
- Provides: `message_ids`, `message_follower_ids`, `activity_ids`
- Features: Comments, followers, activities, notifications
- Usage: Finance tasks, assets, workspaces, advisories

**mail.activity.mixin** (used for workflow tracking):
- Provides: `activity_ids`, `activity_state`, `activity_user_id`
- Features: To-do lists, reminders, escalations
- Usage: BIR tasks, month-end tasks, asset checkout reminders

**portal.mixin** (used for external access):
- Provides: `access_url`, `access_token`
- Features: Share links, external collaboration
- Usage: Workspace pages, advisories, project reports

**Custom IPAI Mixins**:
- `ipai.finance.mixin` - Common finance fields (period, amount, currency)
- `ipai.audit.mixin` - Audit trail (created_by, modified_by, timestamps)
- `ipai.approval.mixin` - Approval workflow (state, approver, approval_date)

## Integration Architecture

### n8n Workflow Integration

**Communication Pattern**: Webhook → n8n → Odoo XML-RPC → PostgreSQL

**Key n8n Workflows** (`workflows/finance_ppm/*.json`):
1. **bir_deadline_alert.json** - Daily scan at 8 AM
   - Query: `SELECT * FROM ipai_finance_bir_schedule WHERE filing_deadline - INTERVAL '7 days' <= CURRENT_DATE AND status != 'filed'`
   - Action: POST to Mattermost webhook

2. **task_escalation.json** - Overdue task alerts
   - Query: `SELECT * FROM project_task WHERE is_finance_ppm = true AND date_deadline < CURRENT_DATE AND stage_id.is_closed = false`
   - Action: Email + Mattermost notification

3. **monthly_report.json** - End-of-month summary
   - Trigger: Cron (last day of month at 11:59 PM)
   - Generate: Finance PPM completion report
   - Send: Email to Finance Director + Mattermost summary

**n8n Environment Variables** (required):
```bash
N8N_API_KEY=<n8n-api-key>
N8N_BASE_URL=https://ipa.insightpulseai.net
ODOO_URL=https://odoo.insightpulseai.net
ODOO_DB=odoo
ODOO_USERNAME=admin
ODOO_PASSWORD=<odoo-admin-password>
MATTERMOST_WEBHOOK_URL=<mattermost-webhook-url>
```

### Supabase Integration

**Purpose**: Analytics, task bus, external ETL

**Schema** (`finance_ppm` schema):
```sql
-- Task queue for async operations
CREATE TABLE finance_ppm.task_queue (
  id SERIAL PRIMARY KEY,
  kind TEXT NOT NULL,
  status TEXT DEFAULT 'pending',
  payload JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Monthly reports (for BI dashboards)
CREATE TABLE finance_ppm.monthly_reports (
  id SERIAL PRIMARY KEY,
  period DATE NOT NULL,
  total_forms INT,
  filed_on_time INT,
  late_filings INT,
  completion_pct NUMERIC(5,2),
  report_data JSONB,
  generated_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS policies (Row-Level Security)
ALTER TABLE finance_ppm.task_queue ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow authenticated users" ON finance_ppm.task_queue
  FOR ALL USING (auth.role() = 'authenticated');
```

**RPCs** (Remote Procedure Calls):
- `route_and_enqueue(kind text, payload jsonb)` - Enqueue task to queue
- `rpc_runbot_record(cycle_id int)` - Record runbot execution
- `rpc_enqueue_odoo_visual(route text, odoo_version text)` - Enqueue visual snapshot

### Mattermost Integration

**Communication Pattern**: n8n → Mattermost Webhook

**Webhook URL**: `https://mattermost.insightpulseai.net/hooks/<webhook-id>`

**Message Formats**:
```json
// BIR deadline alert
{
  "text": "⚠️ **BIR 1601-C (Dec 2025)** due in 7 days",
  "username": "Finance PPM Bot",
  "icon_url": "https://insightpulseai.net/logo.png",
  "attachments": [{
    "color": "#ff9900",
    "fields": [
      {"title": "Form", "value": "1601-C", "short": true},
      {"title": "Period", "value": "Dec 2025", "short": true},
      {"title": "Deadline", "value": "2026-01-10", "short": true},
      {"title": "Status", "value": "In Progress (60%)", "short": true}
    ]
  }]
}
```

## Data Flow Diagrams

### BIR Compliance Workflow

```
┌──────────────────────────────────────────────────────────────┐
│  1. BIR Schedule Seed Data Loaded                            │
│     (data/bir_schedule_seed.xml)                             │
└──────────────────────┬───────────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────────┐
│  2. Cron Job Triggers Daily (8 AM)                           │
│     (data/finance_cron.xml → _cron_sync_bir_tasks)           │
└──────────────────────┬───────────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────────┐
│  3. Auto-Create 3 Tasks Per BIR Form                         │
│     - Preparation task (Finance Supervisor)                  │
│     - Review task (Senior Finance Manager)                   │
│     - Approval task (Finance Director)                       │
└──────────────────────┬───────────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────────┐
│  4. n8n Workflow: bir_deadline_alert.json                    │
│     Query: SELECT WHERE filing_deadline - 7 days <= today    │
└──────────────────────┬───────────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────────┐
│  5. Mattermost Notification                                  │
│     Alert Finance team 7 days before deadline                │
└──────────────────────┬───────────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────────┐
│  6. Finance Team Completes Tasks                             │
│     Update task stage → triggers state change                │
└──────────────────────┬───────────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────────┐
│  7. BIR Form Marked as "Filed"                               │
│     action_mark_filed() → updates completion_pct to 100%     │
└──────────────────────────────────────────────────────────────┘
```

### Month-End Closing Workflow

```
┌──────────────────────────────────────────────────────────────┐
│  1. Month-End Template Selection                             │
│     (ipai_finance_month_end → W101 Snapshot)                 │
└──────────────────────┬───────────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────────┐
│  2. Generate Closing Tasks from Template                     │
│     (ipai_finance_ppm_closing → create tasks)                │
└──────────────────────┬───────────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────────┐
│  3. Close Orchestration Engine Execution                     │
│     (ipai_close_orchestration → multi-stage execution)       │
│     Stages: Planning → Execution → Review → Close            │
└──────────────────────┬───────────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────────┐
│  4. Approval Gates Enforced                                  │
│     Supervisor → Manager → Director approvals required       │
└──────────────────────┬───────────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────────┐
│  5. Close Cycle Completion                                   │
│     Generate summary report → Store in Supabase              │
└──────────────────────┬───────────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────────┐
│  6. Monthly Report Generation                                │
│     (n8n workflow → monthly_report.json)                     │
└──────────────────────────────────────────────────────────────┘
```

## Deployment Architecture

### Production Stack (DigitalOcean)

**Host**: 159.223.75.148 (odoo-erp-prod droplet)
**OS**: Ubuntu 22.04 LTS
**RAM**: 4 GB
**Disk**: 80 GB SSD
**Region**: Singapore (SGP1)

**Docker Containers**:
```yaml
services:
  odoo-accounting:
    image: odoo:18.0
    volumes:
      - /opt/odoo-ce/addons/ipai:/mnt/addons/ipai
      - /opt/odoo-ce/deploy/odoo.conf:/etc/odoo/odoo.conf
    environment:
      - HOST=odoo-db-1
      - PORT=5432
      - USER=odoo
    command: ["odoo", "-c", "/etc/odoo/odoo.conf", "-d", "odoo"]

  odoo-db-1:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=odoo
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=${DB_PASSWORD}
```

**Odoo Configuration** (`deploy/odoo.conf`):
```ini
[options]
db_host = odoo-db-1
db_port = 5432
db_user = odoo
db_password = ${DB_PASSWORD}
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/addons/ipai
workers = 4  # 1 worker per CPU core
limit_memory_hard = 2684354560  # 2.5 GB
limit_memory_soft = 2147483648  # 2 GB
max_cron_threads = 2
proxy_mode = True
list_db = False
```

### Scaling Considerations

**Horizontal Scaling**:
- Use HAProxy/nginx load balancer for multiple Odoo workers
- PostgreSQL read replicas for reporting queries
- Redis for session storage (multi-worker environments)

**Vertical Scaling**:
- Current: 4 GB RAM (4 workers)
- Recommended: 8 GB RAM (8 workers) for >100 concurrent users
- Database: Separate droplet for PostgreSQL at >1000 transactions/day

**Caching Strategy**:
- Browser cache: Static assets (365 days)
- Odoo cache: Model/field metadata (in-memory)
- PostgreSQL cache: Frequently accessed tables (via shared_buffers)

## Performance Optimization

### Database Indexing

**Critical Indexes** (auto-created by Odoo ORM):
```sql
-- Finance PPM indexes
CREATE INDEX idx_bir_schedule_filing_deadline ON ipai_finance_bir_schedule(filing_deadline);
CREATE INDEX idx_bir_schedule_status ON ipai_finance_bir_schedule(status);
CREATE INDEX idx_finance_task_bir_schedule ON ipai_finance_task(bir_schedule_id);

-- Project task indexes (extended by IPAI)
CREATE INDEX idx_project_task_finance_ppm ON project_task(is_finance_ppm) WHERE is_finance_ppm = true;
CREATE INDEX idx_project_task_deadline ON project_task(date_deadline);

-- Asset checkout indexes
CREATE INDEX idx_asset_checkout_employee ON ipai_asset_checkout(employee_id);
CREATE INDEX idx_asset_checkout_status ON ipai_asset_checkout(status);
```

### Query Optimization Patterns

**Anti-Pattern**:
```python
# BAD: N+1 query problem
for task in env['project.task'].search([('is_finance_ppm', '=', True)]):
    print(task.bir_schedule_id.form_type)  # Separate query per task
```

**Optimized**:
```python
# GOOD: Single query with prefetch
tasks = env['project.task'].search([('is_finance_ppm', '=', True)])
env['ipai.finance.bir_schedule'].browse([t.bir_schedule_id.id for t in tasks]).read(['form_type'])
```

## Security Architecture

See [SECURITY_MODEL.md](./SECURITY_MODEL.md) for comprehensive security documentation.

**Key Security Principles**:
1. **Role-Based Access Control (RBAC)**: Groups define permissions
2. **Record Rules**: Row-level security based on user attributes
3. **Field-Level Security**: Hide sensitive fields from unauthorized users
4. **Multi-Company**: Isolation between companies (if enabled)
5. **Audit Trail**: Track all create/write/unlink operations

## Next Steps

- **Deployment**: See [OPERATIONS_RUNBOOK.md](./OPERATIONS_RUNBOOK.md) for deployment procedures
- **Security**: See [SECURITY_MODEL.md](./SECURITY_MODEL.md) for access control configuration
- **Module Details**: See [modules/](./modules/) for per-module technical documentation
