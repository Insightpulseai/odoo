# Azure Boards Structure — Rollout Plan

> Phased implementation plan for the Azure Boards 3-project structure.
> Governance: `spec/azure-boards-structure/constitution.md`
> Requirements: `spec/azure-boards-structure/prd.md`

---

## Week 1 — Foundation

**Objective**: Establish the 3-project structure with correct hierarchy.

### Project Creation
- Create `erp-saas` project in Azure DevOps org `insightpulseai` (Boards-only process template)
- Create `platform` project in Azure DevOps org `insightpulseai` (Boards-only process template)
- Verify or create `lakehouse` project in Azure DevOps org `insightpulseai`
- Disable Repos, Pipelines, Artifacts, Test Plans, and Wiki for all 3 projects

### Work Item Hierarchy
- Verify work item types: Epic, Feature, User Story, Task (standard Agile process)
- Configure work item hierarchy relationships across all projects
- Set up required fields for each work item type

### Initial Epic Shells
- Create 7 epics in `erp-saas`: ERP Runtime, Tenant & Environment Management, Business Modules, Integration Layer, Security & Compliance, Release Engineering, Observability & Support
- Create 7 epics in `lakehouse`: Data Foundation, Ingestion & Pipelines, Customer 360, Marketing Intelligence, AI / ML / Agents, Serving & Activation, Governance & Quality
- Create 7 epics in `platform`: Control Plane, Boards Automation, Agent Platform, Azure Runtime Platform, Shared Services, Developer Experience, Observability & FinOps

### Validation
- Verify all 3 projects are visible in org
- Verify prohibited services are disabled
- Verify epic shells exist in each project
- Document evidence in `docs/evidence/`

---

## Week 2 — Configuration

**Objective**: Configure area paths, iteration paths, board columns, swimlanes, tags, and custom fields.

### Area Paths
- `erp-saas`: Create `Runtime`, `Modules`, `Integrations`, `Security`, `Release`
- `lakehouse`: Create `Foundation`, `Pipelines`, `Customer360`, `Marketing`, `ML-AI`, `Governance`
- `platform`: Create `ControlPlane`, `BoardsAutomation`, `Agents`, `AzureRuntime`, `SharedServices`, `Observability`

### Iteration Paths
- Create `2026` root iteration for each project
- Create `Q1`, `Q2`, `Q3`, `Q4` under `2026`
- Create `Sprint 01` through `Sprint 13` under each quarter (2-week cadence)
- Set sprint start/end dates, synchronized across all projects
- Set current iteration

### Board Columns
- Story board: Configure columns — New, Ready, In Progress, Blocked, In Review, Done
- Task board: Configure columns — To Do, Doing, Review, Done
- Set WIP limits on In Progress (5) and In Review (3) for story boards
- Apply column configuration to all 3 projects

### Swimlanes
- Create swimlanes: Expedite, Standard, Debt / Hardening
- Set Expedite as top lane with visual distinction
- Apply to all 3 projects

### Tags
- Create canonical tag set: `odoo`, `oca`, `ipai`, `azure`, `databricks`, `supabase`, `agent`, `security`, `finops`, `marketing`, `customer360`, `runtime`, `deploy`, `observability`
- Document tag usage guidelines

### Custom Fields
- Create `Primary Repo` field (single select): `odoo`, `lakehouse`, `platform`, `boards-automation`, `agents`, `infra`, `web`
- Create `Deployment Surface` field (single select): `none`, `azure-runtime`, `databricks`, `odoo-runtime`, `web`, `shared-platform`
- Create `Risk Level` field (single select): `low`, `medium`, `high`
- Create `Verification Required` field (single select): `unit`, `integration`, `deploy`, `manual-business-check`
- Add fields to Feature, User Story, and Task work item types as specified in PRD

### Validation
- Verify area paths in each project
- Verify iteration paths with correct dates
- Verify board columns and swimlanes render correctly
- Verify tags are available
- Verify custom fields appear on work item forms

---

## Week 3 — Integration

**Objective**: Connect Azure Boards to GitHub and enable agent-assisted workflows.

### GitHub Integration
- Install Azure Boards app on GitHub org `Insightpulseai`
- Connect `erp-saas` project to `odoo` and `odoo-modules` repos
- Connect `lakehouse` project to `lakehouse` repo
- Connect `platform` project to `platform`, `boards-automation`, `agents`, `infra`, `web` repos
- Verify AB# mention linking works (commit/PR → work item)
- Configure auto-transition: PR merge → work item moves to Done

### PR Link Automation
- Set up branch naming convention enforcement: `<type>/<work-item-id>-<short-description>`
- Configure PR title template to include work item reference
- Test bidirectional linking (work item shows PR, PR shows work item)

### Agent-Assisted PR Creation
- Select pilot repo (recommend `boards-automation` or `platform`)
- Configure agent trigger: work item moves to In Progress → agent creates branch
- Configure agent → PR creation pipeline
- Test end-to-end: Story → Agent → Branch → PR → CI → Merge → Done

### Saved Views and Dashboards
- Create per-project saved views as specified in PRD
- Create cross-project delivery plan
- Create blocked items view
- Create agent activity view
- Create security posture view

### Validation
- Verify AB# linking with test commit
- Verify auto-transition with test PR merge
- Verify agent creates branch and PR on pilot repo
- Verify all dashboard views render correct data

---

## Week 4 — Validation

**Objective**: Populate data, run a pilot sprint, and validate the full workflow.

### Data Population
- Populate initial features under each epic in `erp-saas` (per PRD feature lists)
- Populate initial features under each epic in `lakehouse` (per PRD feature lists)
- Populate initial features under each epic in `platform` (per PRD feature lists)
- Create sample user stories for the pilot sprint
- Assign area paths, tags, and custom field values

### Pilot Sprint
- Select one team for pilot (recommend Platform team)
- Create Sprint 01 backlog with 8-12 stories
- Run daily standup using board views
- Track velocity and burndown

### End-to-End Workflow Validation
- Validate: Create story → Assign → In Progress → Agent creates branch → PR opened → CI passes → Review → Merge → Work item auto-transitions to Done
- Validate: Blocked items surface correctly
- Validate: Cross-project delivery plan shows accurate timeline
- Validate: FinOps tags and views work correctly

### Runbook and Handoff
- Document operational runbook for ongoing Boards management
- Document backlog refinement process
- Document sprint planning ceremony using Boards
- Document agent-assisted workflow for new repos
- Train team leads on dashboard usage

### Validation
- All success metrics from PRD are measured and baselined
- Pilot sprint completed with velocity data
- End-to-end PR/Agent workflow operational
- Runbook reviewed and approved

---

## Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| Azure Boards API rate limits | Automation blocked | Batch operations, exponential backoff |
| GitHub integration token expiry | Linking breaks | Token rotation automation, alerts |
| Custom field schema changes | Data loss | Version custom field schemas in SSOT |
| Agent creates incorrect PRs | Noise, wasted CI | Dry-run mode, human approval gate |
| Sprint cadence misalignment | Confusing metrics | Synchronized sprint dates from day 1 |

---

*Governed by: `spec/azure-boards-structure/constitution.md`*
*Last updated: 2026-03-07*
