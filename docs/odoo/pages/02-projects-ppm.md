# Projects & Portfolio Management – InsightPulseAI Edition

**Module:** `project`, `hr_timesheet`, `ipai_ppm_portfolio`, `ipai_finance_ppm`
**Domain:** PPM (Project Portfolio Management)
**Owner Engine:** PPM Engine
**Last Updated:** 2025-12-07

---

## 1. Overview & Purpose

The Projects & PPM workspace provides Clarity PPM-style project portfolio management capabilities on Odoo 18 CE. This module handles:

- **Portfolio → Program → Project hierarchy** for enterprise project management
- **WBS (Work Breakdown Structure)** task management
- **Timesheet capture** and approval workflows
- **Budget tracking** with rate cards
- **Resource capacity planning**
- **Stage-gate approvals** for investment decisions

### Key Differentiators from Stock Odoo

| Feature | Stock Odoo CE | InsightPulseAI Stack |
|---------|---------------|----------------------|
| Portfolio Hierarchy | Not available | `ipai_ppm_portfolio` module |
| WBS Structure | Flat tasks | Hierarchical WBS with codes |
| Resource Planning | Basic | `projects.resources` in Supabase + Superset |
| Rate Cards | Not available | `rates.*` schema + `ipai_rate_card` |
| Stage Gates | Not available | `wf_gate_approval` via n8n |
| Analytics | Basic | Superset dashboards |
| Forecasting | Not available | E3 Intelligence Engine |

---

## 2. Related Domain Engine(s)

| Engine | Role |
|--------|------|
| **PPM Engine** | Primary owner - portfolio/project management |
| **SRM** | Rate card management for vendor resources |
| **E3 Intelligence** | Budget forecasting and variance analysis |

---

## 3. Data Models

### 3.1 Core Odoo Models

| Model | Description | Key Fields |
|-------|-------------|------------|
| `project.project` | Project records | `name`, `partner_id`, `user_id`, `date_start`, `date` |
| `project.task` | Tasks within projects | `project_id`, `parent_id`, `stage_id`, `assigned_ids` |
| `project.task.type` | Task stages | `name`, `sequence`, `fold` |
| `account.analytic.account` | Analytic accounts | `name`, `code`, `company_id` |
| `account.analytic.line` | Timesheet entries | `project_id`, `task_id`, `employee_id`, `unit_amount` |
| `resource.resource` | Resources (people, equipment) | `name`, `resource_type`, `time_efficiency` |
| `resource.calendar` | Working calendars | `name`, `attendance_ids` |

### 3.2 Custom IPAI Models

| Model | Module | Description |
|-------|--------|-------------|
| `ipai.portfolio` | `ipai_ppm_portfolio` | Portfolio container (highest level) |
| `ipai.program` | `ipai_ppm_portfolio` | Program grouping projects |
| `ipai.project.wbs` | `ipai_ppm_portfolio` | WBS code structure |
| `ipai.project.gate` | `ipai_ppm_gates` | Stage-gate milestones |
| `ipai.rate.card` | `ipai_rate_card` | Rate card definitions |
| `ipai.rate.entry` | `ipai_rate_card` | Rate entries by role/skill |
| `ipai.project.budget` | `ipai_finance_ppm` | Budget allocations |

### 3.3 Supabase Schema

```sql
-- Portfolio hierarchy
CREATE TABLE projects.portfolios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50),
    owner_id UUID,
    status VARCHAR(20) DEFAULT 'active',
    budget_total DECIMAL(15,2),
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE projects.programs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    portfolio_id UUID REFERENCES projects.portfolios(id),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50),
    manager_id UUID,
    status VARCHAR(20) DEFAULT 'active'
);

CREATE TABLE projects.projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    odoo_id INTEGER,
    program_id UUID REFERENCES projects.programs(id),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50),
    pm_id UUID,
    status VARCHAR(20),
    budget_allocated DECIMAL(15,2),
    budget_consumed DECIMAL(15,2),
    start_date DATE,
    end_date DATE
);

CREATE TABLE projects.wbs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    project_id UUID REFERENCES projects.projects(id),
    odoo_task_id INTEGER,
    wbs_code VARCHAR(50) NOT NULL,
    name VARCHAR(255),
    parent_wbs_id UUID REFERENCES projects.wbs(id),
    level INTEGER,
    budget DECIMAL(15,2)
);

CREATE TABLE projects.timesheets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    odoo_id INTEGER,
    employee_id UUID,
    project_id UUID REFERENCES projects.projects(id),
    task_id UUID REFERENCES projects.wbs(id),
    date DATE NOT NULL,
    hours DECIMAL(5,2) NOT NULL,
    rate DECIMAL(10,2),
    cost DECIMAL(15,2) GENERATED ALWAYS AS (hours * COALESCE(rate, 0)) STORED,
    status VARCHAR(20) DEFAULT 'draft'
);

-- Rate cards
CREATE TABLE rates.rate_cards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    vendor_id UUID,
    name VARCHAR(255) NOT NULL,
    currency VARCHAR(3) DEFAULT 'PHP',
    valid_from DATE,
    valid_to DATE,
    status VARCHAR(20) DEFAULT 'active'
);

CREATE TABLE rates.rate_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    rate_card_id UUID REFERENCES rates.rate_cards(id),
    role VARCHAR(100) NOT NULL,
    skill_level VARCHAR(50),
    hourly_rate DECIMAL(10,2),
    daily_rate DECIMAL(10,2),
    monthly_rate DECIMAL(15,2)
);
```

---

## 4. User Roles & Permissions

| Role | Odoo Group | Supabase Role | Permissions |
|------|------------|---------------|-------------|
| Portfolio Manager | `project.group_project_manager` | `ppm_portfolio_mgr` | Full portfolio access |
| Program Manager | `project.group_project_manager` | `ppm_program_mgr` | Program and project access |
| Project Manager | `project.group_project_manager` | `ppm_project_mgr` | Own projects only |
| Team Member | `project.group_project_user` | `ppm_team_member` | Assigned tasks, own timesheets |
| Finance Analyst | `project.group_project_user` | `ppm_analyst` | Read-only + reports |
| Resource Manager | `hr.group_hr_manager` | `ppm_resource_mgr` | Resource allocation |

---

## 5. Key Workflows

### 5.1 Portfolio → Program → Project Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         PORTFOLIO                                        │
│  (Strategic Investment Theme)                                           │
│  e.g., "Digital Transformation 2025"                                    │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────┐     ┌──────────────────────┐                  │
│  │      PROGRAM A       │     │      PROGRAM B       │                  │
│  │  (Initiative Group)  │     │  (Initiative Group)  │                  │
│  │  e.g., "ERP Upgrade" │     │  e.g., "AI Enablement│                  │
│  ├──────────────────────┤     ├──────────────────────┤                  │
│  │  ┌────────────────┐  │     │  ┌────────────────┐  │                  │
│  │  │   PROJECT 1    │  │     │  │   PROJECT 3    │  │                  │
│  │  │ "Odoo 18 Impl" │  │     │  │ "RAG Pipeline" │  │                  │
│  │  └────────────────┘  │     │  └────────────────┘  │                  │
│  │  ┌────────────────┐  │     │  ┌────────────────┐  │                  │
│  │  │   PROJECT 2    │  │     │  │   PROJECT 4    │  │                  │
│  │  │ "Data Migration│  │     │  │ "Agent Deploy" │  │                  │
│  │  └────────────────┘  │     │  └────────────────┘  │                  │
│  └──────────────────────┘     └──────────────────────┘                  │
└─────────────────────────────────────────────────────────────────────────┘
```

**Setup Steps:**

1. **Create Portfolio** (Odoo)
   - Navigate to: Projects > Configuration > Portfolios > Create
   - Enter name, code, owner, strategic objectives
   - Set overall budget envelope

2. **Create Program** (Odoo)
   - Navigate to: Projects > Configuration > Programs > Create
   - Link to portfolio
   - Assign program manager
   - Define program-level budget

3. **Create Project** (Odoo)
   - Navigate to: Projects > Projects > Create
   - Link to program
   - Configure project settings
   - **Triggers:** `wf_project_sync` (n8n → Supabase)

### 5.2 WBS (Work Breakdown Structure)

```
PROJECT: Odoo 18 Implementation
├── 1.0 Project Management
│   ├── 1.1 Planning
│   ├── 1.2 Status Reporting
│   └── 1.3 Change Management
├── 2.0 Analysis & Design
│   ├── 2.1 Requirements Gathering
│   ├── 2.2 Gap Analysis
│   └── 2.3 Solution Design
├── 3.0 Build & Configure
│   ├── 3.1 Module Configuration
│   ├── 3.2 Custom Development
│   └── 3.3 Integration Build
├── 4.0 Testing
│   ├── 4.1 Unit Testing
│   ├── 4.2 Integration Testing
│   └── 4.3 UAT
└── 5.0 Deployment
    ├── 5.1 Data Migration
    ├── 5.2 Training
    └── 5.3 Go-Live Support
```

**WBS Task Creation:**

1. **Create Parent Task** (Odoo)
   - Navigate to: Projects > [Project] > Tasks > Create
   - Enter WBS code (e.g., "1.0")
   - Set as parent level

2. **Create Child Tasks** (Odoo)
   - Create task with parent reference
   - Auto-generates WBS code (e.g., "1.1")
   - **Triggers:** `wf_task_sync` (n8n → Supabase)

3. **View WBS** (Superset)
   - Dashboard shows hierarchical WBS view
   - Budget rollup from children to parents

### 5.3 Timesheet Workflow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  1. Enter   │────▶│  2. Submit  │────▶│  3. Approve │────▶│  4. Bill    │
│   Hours     │     │   Week      │     │   (PM)      │     │   Client    │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
     Draft            Submitted          Approved           Invoiced
```

**Step-by-Step:**

1. **Enter Timesheets** (Odoo)
   - Navigate to: Timesheets > My Timesheets
   - Select date, project, task
   - Enter hours and description
   - Save (auto-saves in CE)

2. **Submit Timesheet** (Odoo + n8n)
   - Weekly submission via timesheet sheet (OCA `hr_timesheet_sheet`)
   - Click "Submit to Manager"
   - **Triggers:** `wf_timesheet_submitted` (n8n)

3. **Manager Approval** (Mattermost + n8n)
   - PM receives notification in Mattermost
   - Approve/Reject with comments
   - n8n updates Odoo
   - **Triggers:** `wf_timesheet_approval`

4. **Cost Calculation** (Supabase)
   - Approved timesheets sync to Supabase
   - Rate applied from rate card
   - Cost calculated: `hours * rate`

### 5.4 Budget Management

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      BUDGET STRUCTURE                                    │
├─────────────────────────────────────────────────────────────────────────┤
│  Portfolio Budget: P10,000,000                                          │
│  ├── Program A Budget: P6,000,000                                       │
│  │   ├── Project 1: P3,000,000 (Consumed: P1,500,000 = 50%)            │
│  │   └── Project 2: P3,000,000 (Consumed: P750,000 = 25%)              │
│  └── Program B Budget: P4,000,000                                       │
│      ├── Project 3: P2,500,000 (Consumed: P500,000 = 20%)              │
│      └── Project 4: P1,500,000 (Consumed: P0 = 0%)                      │
└─────────────────────────────────────────────────────────────────────────┘
```

**Budget Workflow:**

1. **Set Portfolio Budget** (Odoo)
   - Define overall investment envelope
   - Allocate to programs

2. **Allocate to Projects** (Odoo)
   - Program manager allocates to projects
   - Set budget by WBS element

3. **Track Consumption** (Supabase + Superset)
   - Timesheet costs roll up
   - Variance calculated automatically
   - **Triggers:** `wf_budget_alert` (>80%, >90%, >100%)

### 5.5 Stage-Gate Workflow

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ Gate 0  │────▶│ Gate 1  │────▶│ Gate 2  │────▶│ Gate 3  │────▶│ Gate 4  │────▶│ Gate 5  │
│ Ideation│     │ Scoping │     │ Business│     │ Develop │     │ Testing │     │ Launch  │
│         │     │         │     │  Case   │     │         │     │  & Val  │     │         │
└─────────┘     └─────────┘     └─────────┘     └─────────┘     └─────────┘     └─────────┘
    ↓               ↓               ↓               ↓               ↓               ↓
  Go/Kill       Go/Kill/Hold    Go/Kill/Hold    Go/Kill/Hold    Go/Kill/Hold      Go
```

**Gate Approval Process:**

1. **Request Gate Review** (Odoo)
   - PM completes gate deliverables
   - Creates gate review request
   - **Triggers:** `wf_gate_request`

2. **Gate Committee Review** (Mattermost + n8n)
   - Committee notified
   - Schedule review meeting
   - Document decision

3. **Gate Decision** (n8n)
   - **Go**: Proceed to next phase
   - **Kill**: Terminate project
   - **Hold**: Pause for more info
   - Update project status in Odoo

---

## 6. Integrations

### 6.1 Supabase Tables/Views

| Supabase Table | Source | Sync Direction | Frequency |
|----------------|--------|----------------|-----------|
| `projects.portfolios` | `ipai.portfolio` | Odoo → Supabase | Real-time |
| `projects.programs` | `ipai.program` | Odoo → Supabase | Real-time |
| `projects.projects` | `project.project` | Bi-directional | Real-time |
| `projects.wbs` | `project.task` | Odoo → Supabase | Real-time |
| `projects.timesheets` | `account.analytic.line` | Odoo → Supabase | Real-time |
| `projects.budgets` | `ipai.project.budget` | Odoo → Supabase | Real-time |
| `projects.gates` | `ipai.project.gate` | Odoo → Supabase | On change |
| `rates.rate_cards` | `ipai.rate.card` | Supabase → Odoo | On change |
| `rates.rate_entries` | `ipai.rate.entry` | Supabase → Odoo | On change |

### 6.2 n8n Workflows

| Workflow ID | Trigger | Action | Target |
|-------------|---------|--------|--------|
| `wf_project_sync` | Project created/updated | Sync to Supabase | `projects.projects` |
| `wf_task_sync` | Task created/updated | Sync WBS | `projects.wbs` |
| `wf_timesheet_submitted` | Timesheet submitted | Notify PM | Mattermost |
| `wf_timesheet_approval` | Mattermost action | Update status | Odoo + Supabase |
| `wf_budget_alert` | Consumption threshold | Alert PM/Finance | Mattermost |
| `wf_gate_request` | Gate review requested | Notify committee | Mattermost |
| `wf_gate_approval` | Gate decision made | Update project | Odoo |
| `wf_rate_card_sync` | Rate card updated | Sync to Odoo | `ipai.rate.card` |

### 6.3 AI Agents/Tools

| Agent | Capability | Use Case |
|-------|------------|----------|
| **PPM Coach** | Project health analysis | "Is Project X on track?" |
| **Budget Forecaster** | Predict budget consumption | "When will we hit 100%?" |
| **Resource Optimizer** | Skill-based matching | "Who's available with Python skills?" |
| **Risk Analyst** | Risk identification | "What risks should we monitor?" |

---

## 7. Configuration Guide

### 7.1 Project Stages

| Stage | Sequence | Description |
|-------|----------|-------------|
| Backlog | 1 | Not yet started |
| In Progress | 2 | Active work |
| Review | 3 | Pending review |
| Done | 4 | Completed |
| Cancelled | 5 | Terminated |

### 7.2 Analytic Accounts

```
Chart of Analytic Accounts:
├── INTERNAL
│   ├── INT-001 Administrative
│   ├── INT-002 R&D
│   └── INT-003 Sales & Marketing
├── BILLABLE
│   ├── CLT-001 Client A
│   │   ├── CLT-001-P01 Project 1
│   │   └── CLT-001-P02 Project 2
│   └── CLT-002 Client B
│       └── CLT-002-P01 Project 1
└── NON-BILLABLE
    ├── NB-001 Training
    └── NB-002 Leave
```

### 7.3 Rate Card Configuration

| Role | Junior | Mid | Senior | Principal |
|------|--------|-----|--------|-----------|
| Developer | 500 | 750 | 1,000 | 1,500 |
| Designer | 400 | 600 | 900 | 1,300 |
| PM | 600 | 900 | 1,200 | 1,800 |
| Analyst | 450 | 700 | 1,000 | 1,400 |

*Rates in PHP per hour*

---

## 8. Reports & Analytics

### 8.1 Standard Odoo Reports

- Project Overview
- Timesheet Analysis
- Task Burndown
- Employee Productivity

### 8.2 Superset Dashboards

| Dashboard | Location | Key Metrics |
|-----------|----------|-------------|
| Portfolio Overview | `/superset/dashboard/ppm-portfolio` | Health, budget, timeline |
| Project Status | `/superset/dashboard/ppm-project` | Tasks, WBS progress, burn rate |
| Timesheet Analysis | `/superset/dashboard/ppm-timesheets` | Hours, utilization, cost |
| Budget Variance | `/superset/dashboard/ppm-budget` | Planned vs actual, forecasts |
| Resource Capacity | `/superset/dashboard/ppm-resources` | Allocation, availability |

---

## 9. Delta from Official Odoo Docs

| Topic | Official Odoo Docs | InsightPulseAI Differences |
|-------|-------------------|---------------------------|
| Project Hierarchy | Flat projects only | Portfolio → Program → Project via `ipai_ppm_portfolio` |
| WBS | Basic subtasks | Full WBS codes and hierarchy |
| Rate Cards | Not available | Custom `ipai_rate_card` module |
| Resource Planning | Enterprise Planning app | Supabase + Superset |
| Stage Gates | Not available | `ipai_ppm_gates` + n8n workflows |
| Forecasting | Not available | E3 Intelligence Engine |
| Timesheet Approval | Basic | n8n + Mattermost workflow |

---

## 10. Known Limitations & Phase 2+ Items

### Current Limitations

- **No drag-drop resource calendar**: Use manual allocation
- **Limited mobile timesheet**: Web-based only
- **No Gantt chart**: Use Superset timeline visualization

### Phase 2 Roadmap

- [ ] Gantt chart view (OCA or custom)
- [ ] Mobile timesheet app
- [ ] Automatic resource leveling
- [ ] AI-powered schedule optimization
- [ ] Integration with MS Project import/export

---

> **InsightPulseAI Integration:**
> - **Data flows to:** `projects.*`, `rates.*`, `finance.*`
> - **Used by engines:** PPM Engine, SRM, E3 Intelligence
> - **Triggered automations:** `wf_project_sync`, `wf_timesheet_*`, `wf_budget_alert`, `wf_gate_*`
> - **AI agents:** PPM Coach, Budget Forecaster, Resource Optimizer

---

## References

- [Odoo 18 Project Documentation](https://www.odoo.com/documentation/18.0/applications/services/project.html)
- [OCA project modules](https://github.com/OCA/project)
- [InsightPulseAI CE/OCA Mapping](../ODOO18_ENTERPRISE_TO_CE_OCA_MAPPING.md)
