# Azure Boards Structure — Task Checklist

> Granular task checklist for the Azure Boards 3-project rollout.
> Plan: `spec/azure-boards-structure/plan.md`

---

## T0 — Prerequisites

- [ ] Verify Azure DevOps organization `insightpulseai` exists and is accessible
- [ ] Verify admin permissions for project creation in the org
- [ ] Verify GitHub org `Insightpulseai` has Azure Boards app available
- [ ] Confirm list of GitHub repos: `odoo`, `odoo-modules`, `lakehouse`, `platform`, `boards-automation`, `agents`, `infra`, `web`
- [ ] Review and approve constitution (`spec/azure-boards-structure/constitution.md`)
- [ ] Review and approve PRD (`spec/azure-boards-structure/prd.md`)
- [ ] Identify pilot team and pilot repo for agent-assisted PR creation
- [ ] Confirm sprint start date and 2-week cadence alignment

---

## T1 — Project Creation (Week 1)

### T1.1 — Create Projects

- [ ] Create `erp-saas` project in Azure DevOps org `insightpulseai`
  - Process template: Agile
  - Version control: None (Boards only)
  - Description: "Odoo ERP SaaS runtime, modules, integrations, and release engineering"
- [ ] Create `platform` project in Azure DevOps org `insightpulseai`
  - Process template: Agile
  - Version control: None (Boards only)
  - Description: "Control plane, Azure runtime, boards automation, agents, shared services"
- [ ] Verify or create `lakehouse` project in Azure DevOps org `insightpulseai`
  - Process template: Agile
  - Version control: None (Boards only)
  - Description: "Databricks lakehouse, data pipelines, customer 360, marketing intelligence, ML/AI"

### T1.2 — Disable Prohibited Services

- [ ] Disable Repos service for `erp-saas`
- [ ] Disable Pipelines service for `erp-saas`
- [ ] Disable Artifacts service for `erp-saas`
- [ ] Disable Test Plans service for `erp-saas`
- [ ] Disable Wiki service for `erp-saas`
- [ ] Disable Repos service for `lakehouse`
- [ ] Disable Pipelines service for `lakehouse`
- [ ] Disable Artifacts service for `lakehouse`
- [ ] Disable Test Plans service for `lakehouse`
- [ ] Disable Wiki service for `lakehouse`
- [ ] Disable Repos service for `platform`
- [ ] Disable Pipelines service for `platform`
- [ ] Disable Artifacts service for `platform`
- [ ] Disable Test Plans service for `platform`
- [ ] Disable Wiki service for `platform`

### T1.3 — Create Epic Shells

#### `erp-saas` Epics
- [ ] Create epic: `[ERP] ERP Runtime`
- [ ] Create epic: `[ERP] Tenant & Environment Management`
- [ ] Create epic: `[ERP] Business Modules`
- [ ] Create epic: `[ERP] Integration Layer`
- [ ] Create epic: `[ERP] Security & Compliance`
- [ ] Create epic: `[ERP] Release Engineering`
- [ ] Create epic: `[ERP] Observability & Support`

#### `lakehouse` Epics
- [ ] Create epic: `[DATA] Data Foundation`
- [ ] Create epic: `[DATA] Ingestion & Pipelines`
- [ ] Create epic: `[DATA] Customer 360`
- [ ] Create epic: `[DATA] Marketing Intelligence`
- [ ] Create epic: `[DATA] AI / ML / Agents`
- [ ] Create epic: `[DATA] Serving & Activation`
- [ ] Create epic: `[DATA] Governance & Quality`

#### `platform` Epics
- [ ] Create epic: `[PLAT] Control Plane`
- [ ] Create epic: `[PLAT] Boards Automation`
- [ ] Create epic: `[PLAT] Agent Platform`
- [ ] Create epic: `[PLAT] Azure Runtime Platform`
- [ ] Create epic: `[PLAT] Shared Services`
- [ ] Create epic: `[PLAT] Developer Experience`
- [ ] Create epic: `[PLAT] Observability & FinOps`

### T1.4 — Week 1 Validation
- [ ] Verify all 3 projects visible in Azure DevOps org
- [ ] Verify prohibited services are disabled for all projects
- [ ] Verify 7 epics exist in each project (21 total)
- [ ] Screenshot evidence saved to `docs/evidence/`

---

## T2 — Configuration (Week 2)

### T2.1 — Area Paths

#### `erp-saas`
- [ ] Create area path: `erp-saas\Runtime`
- [ ] Create area path: `erp-saas\Modules`
- [ ] Create area path: `erp-saas\Integrations`
- [ ] Create area path: `erp-saas\Security`
- [ ] Create area path: `erp-saas\Release`

#### `lakehouse`
- [ ] Create area path: `lakehouse\Foundation`
- [ ] Create area path: `lakehouse\Pipelines`
- [ ] Create area path: `lakehouse\Customer360`
- [ ] Create area path: `lakehouse\Marketing`
- [ ] Create area path: `lakehouse\ML-AI`
- [ ] Create area path: `lakehouse\Governance`

#### `platform`
- [ ] Create area path: `platform\ControlPlane`
- [ ] Create area path: `platform\BoardsAutomation`
- [ ] Create area path: `platform\Agents`
- [ ] Create area path: `platform\AzureRuntime`
- [ ] Create area path: `platform\SharedServices`
- [ ] Create area path: `platform\Observability`

### T2.2 — Iteration Paths

For each project (`erp-saas`, `lakehouse`, `platform`):

- [ ] Create root iteration: `2026`
- [ ] Create iteration: `2026\Q1`
- [ ] Create iteration: `2026\Q1\Sprint 01` (dates: TBD based on cadence start)
- [ ] Create iteration: `2026\Q1\Sprint 02`
- [ ] Create iteration: `2026\Q1\Sprint 03`
- [ ] Create iteration: `2026\Q1\Sprint 04`
- [ ] Create iteration: `2026\Q1\Sprint 05`
- [ ] Create iteration: `2026\Q1\Sprint 06`
- [ ] Create iteration: `2026\Q2`
- [ ] Create iterations: `2026\Q2\Sprint 01` through `Sprint 06`
- [ ] Create iteration: `2026\Q3`
- [ ] Create iterations: `2026\Q3\Sprint 01` through `Sprint 07`
- [ ] Create iteration: `2026\Q4`
- [ ] Create iterations: `2026\Q4\Sprint 01` through `Sprint 07`
- [ ] Set current iteration to active sprint
- [ ] Synchronize sprint dates across all 3 projects

### T2.3 — Board Columns

For each project:

- [ ] Configure story board columns: New, Ready, In Progress, Blocked, In Review, Done
- [ ] Set WIP limit on In Progress: 5
- [ ] Set WIP limit on In Review: 3
- [ ] Configure task board columns: To Do, Doing, Review, Done
- [ ] Remove any default columns not in the spec
- [ ] Verify column order matches spec

### T2.4 — Swimlanes

For each project:

- [ ] Create swimlane: `Expedite` (top position, highlighted)
- [ ] Create swimlane: `Standard` (default)
- [ ] Create swimlane: `Debt / Hardening` (bottom position)
- [ ] Set `Standard` as the default swimlane for new items

### T2.5 — Tags

- [ ] Create tag: `odoo`
- [ ] Create tag: `oca`
- [ ] Create tag: `ipai`
- [ ] Create tag: `azure`
- [ ] Create tag: `databricks`
- [ ] Create tag: `supabase`
- [ ] Create tag: `agent`
- [ ] Create tag: `security`
- [ ] Create tag: `finops`
- [ ] Create tag: `marketing`
- [ ] Create tag: `customer360`
- [ ] Create tag: `runtime`
- [ ] Create tag: `deploy`
- [ ] Create tag: `observability`

### T2.6 — Custom Fields

- [ ] Create field `Primary Repo` (single select)
  - Values: `odoo`, `lakehouse`, `platform`, `boards-automation`, `agents`, `infra`, `web`
- [ ] Create field `Deployment Surface` (single select)
  - Values: `none`, `azure-runtime`, `databricks`, `odoo-runtime`, `web`, `shared-platform`
- [ ] Create field `Risk Level` (single select)
  - Values: `low`, `medium`, `high`
- [ ] Create field `Verification Required` (single select)
  - Values: `unit`, `integration`, `deploy`, `manual-business-check`
- [ ] Add `Primary Repo` to Feature form layout
- [ ] Add `Primary Repo` to User Story form layout
- [ ] Add `Deployment Surface` to Feature form layout
- [ ] Add `Deployment Surface` to User Story form layout
- [ ] Add `Risk Level` to Feature form layout
- [ ] Add `Risk Level` to User Story form layout
- [ ] Add `Verification Required` to User Story form layout
- [ ] Add `Verification Required` to Task form layout

### T2.7 — Week 2 Validation
- [ ] Verify area paths in each project (5 + 6 + 6 = 17 total)
- [ ] Verify iteration paths with correct sprint dates
- [ ] Verify board columns render correctly for story and task boards
- [ ] Verify swimlanes appear on boards
- [ ] Verify all 14 tags are available
- [ ] Verify custom fields appear on work item forms
- [ ] Screenshot evidence saved to `docs/evidence/`

---

## T3 — Integration (Week 3)

### T3.1 — GitHub Integration

- [ ] Install Azure Boards app on GitHub org `Insightpulseai`
- [ ] Authorize Azure Boards app with appropriate permissions
- [ ] Connect `erp-saas` to GitHub repo `odoo`
- [ ] Connect `erp-saas` to GitHub repo `odoo-modules`
- [ ] Connect `lakehouse` to GitHub repo `lakehouse`
- [ ] Connect `platform` to GitHub repo `platform`
- [ ] Connect `platform` to GitHub repo `boards-automation`
- [ ] Connect `platform` to GitHub repo `agents`
- [ ] Connect `platform` to GitHub repo `infra`
- [ ] Connect `platform` to GitHub repo `web`
- [ ] Test AB# mention in a commit message links to correct work item
- [ ] Test AB# mention in a PR description links to correct work item

### T3.2 — PR Automation

- [ ] Configure auto-transition rule: merged PR → work item moves to Done
- [ ] Set up branch naming convention: `<type>/<work-item-id>-<short-description>`
- [ ] Configure PR title template with work item reference
- [ ] Test bidirectional linking: work item → PR tab shows linked PR
- [ ] Test bidirectional linking: PR → work item reference resolves

### T3.3 — Agent-Assisted PR Creation

- [ ] Select pilot repo (target: `boards-automation` or `platform`)
- [ ] Configure agent trigger: work item transitions to In Progress
- [ ] Implement agent logic: read work item → create branch → open PR with template
- [ ] Configure CI pipeline on pilot repo to run on agent-created PRs
- [ ] Test end-to-end flow:
  - [ ] Create test user story with Primary Repo set
  - [ ] Move story to In Progress
  - [ ] Verify agent creates branch with correct naming
  - [ ] Verify agent opens PR with work item reference
  - [ ] Verify CI runs on the PR
  - [ ] Merge PR
  - [ ] Verify work item auto-transitions to Done

### T3.4 — Dashboard Views

#### `erp-saas` Views
- [ ] Create saved query: ERP Sprint Board
- [ ] Create saved query: ERP Module Status
- [ ] Create saved query: ERP Release Pipeline
- [ ] Create saved query: ERP Compliance
- [ ] Create saved query: ERP Velocity

#### `lakehouse` Views
- [ ] Create saved query: Data Sprint Board
- [ ] Create saved query: Pipeline Status
- [ ] Create saved query: Customer 360 Progress
- [ ] Create saved query: ML Model Tracker
- [ ] Create saved query: Data Quality Dashboard

#### `platform` Views
- [ ] Create saved query: Platform Sprint Board
- [ ] Create saved query: Agent Operations
- [ ] Create saved query: Infrastructure Status
- [ ] Create saved query: Boards Automation Health
- [ ] Create saved query: FinOps Tracker

#### Cross-Project Views
- [ ] Create delivery plan: Epics across all 3 projects on timeline
- [ ] Create saved query: Blocked Items (all projects)
- [ ] Create saved query: Agent Activity (all projects)
- [ ] Create saved query: Security Posture (all projects)

### T3.5 — Week 3 Validation
- [ ] Verify AB# linking works for all connected repos
- [ ] Verify auto-transition on PR merge
- [ ] Verify agent-assisted PR creation on pilot repo
- [ ] Verify all dashboard views return correct results
- [ ] Screenshot evidence saved to `docs/evidence/`

---

## T4 — Validation (Week 4)

### T4.1 — Data Population

#### `erp-saas` Features
- [ ] Populate features under `[ERP] ERP Runtime` (8 features)
- [ ] Populate features under `[ERP] Tenant & Environment Management` (6 features)
- [ ] Populate features under `[ERP] Business Modules` (9 features)
- [ ] Populate features under `[ERP] Integration Layer` (7 features)
- [ ] Populate features under `[ERP] Security & Compliance` (7 features)
- [ ] Populate features under `[ERP] Release Engineering` (6 features)
- [ ] Populate features under `[ERP] Observability & Support` (6 features)

#### `lakehouse` Features
- [ ] Populate features under `[DATA] Data Foundation` (7 features)
- [ ] Populate features under `[DATA] Ingestion & Pipelines` (7 features)
- [ ] Populate features under `[DATA] Customer 360` (7 features)
- [ ] Populate features under `[DATA] Marketing Intelligence` (7 features)
- [ ] Populate features under `[DATA] AI / ML / Agents` (7 features)
- [ ] Populate features under `[DATA] Serving & Activation` (7 features)
- [ ] Populate features under `[DATA] Governance & Quality` (7 features)

#### `platform` Features
- [ ] Populate features under `[PLAT] Control Plane` (7 features)
- [ ] Populate features under `[PLAT] Boards Automation` (7 features)
- [ ] Populate features under `[PLAT] Agent Platform` (7 features)
- [ ] Populate features under `[PLAT] Azure Runtime Platform` (7 features)
- [ ] Populate features under `[PLAT] Shared Services` (7 features)
- [ ] Populate features under `[PLAT] Developer Experience` (7 features)
- [ ] Populate features under `[PLAT] Observability & FinOps` (7 features)

#### Sample Stories
- [ ] Create 8-12 user stories for pilot sprint
- [ ] Assign area paths to all stories
- [ ] Set tags on all stories
- [ ] Set custom field values (Primary Repo, Deployment Surface, Risk Level, Verification Required)

### T4.2 — Pilot Sprint

- [ ] Select pilot team (recommend: Platform team)
- [ ] Populate Sprint 01 backlog (current iteration)
- [ ] Run daily standup using board views for 1 week minimum
- [ ] Track burndown chart
- [ ] Measure velocity at sprint end
- [ ] Capture retrospective notes

### T4.3 — End-to-End Workflow Validation

- [ ] Validate full workflow: Create story → Assign → In Progress → Agent → Branch → PR → CI → Review → Merge → Done
- [ ] Validate blocked item visibility and escalation
- [ ] Validate cross-project delivery plan accuracy
- [ ] Validate FinOps tag and view functionality
- [ ] Validate naming convention compliance across all work items

### T4.4 — Success Metrics Check

- [ ] Measure: % of code-triggering work items linked to GitHub repos (target: 100%)
- [ ] Verify: Zero work items exist in Azure repos/pipelines (target: 0)
- [ ] Verify: Agent-assisted PR creation operational for pilot repo
- [ ] Measure: Sprint velocity data available for all 3 projects
- [ ] Measure: Board compliance rate (target: 100% constitution conformance)

### T4.5 — Runbook and Documentation

- [ ] Document operational runbook for ongoing Boards management
- [ ] Document backlog refinement process using Boards
- [ ] Document sprint planning ceremony using Boards
- [ ] Document agent-assisted workflow for onboarding new repos
- [ ] Train team leads on dashboard usage
- [ ] Archive rollout evidence in `docs/evidence/`

### T4.6 — Week 4 Validation
- [ ] All success metrics baselined
- [ ] Pilot sprint completed with velocity data
- [ ] End-to-end PR/Agent workflow validated
- [ ] Runbook reviewed and approved by Engineering Manager
- [ ] Final screenshot evidence saved to `docs/evidence/`

---

*Total tasks: ~180+*
*Governed by: `spec/azure-boards-structure/constitution.md`*
*Last updated: 2026-03-07*
