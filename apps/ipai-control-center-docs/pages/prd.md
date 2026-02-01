# Product Requirements Document — IPAI Control Center

## Executive Summary

**Product Name**: IPAI Control Center
**Version**: 1.0.0
**Status**: Planning Phase
**Owner**: Platform Engineering Team
**Last Updated**: 2025-12-19

The IPAI Control Center is an Azure Advisor-inspired unified operations platform for Odoo CE 18.0 + Supabase environments. It provides actionable recommendations across five operational categories (Cost, Security, Reliability, Operational Excellence, Performance), integrates Portfolio/Program Management (PPM) with OCA modules, and automates workflows via n8n + Mattermost.

---

## Problem Statement

### Current State
Organizations running Odoo CE 18.0 + Supabase face fragmented operational visibility:
- **No unified health dashboard** – Cost, security, reliability, and performance insights scattered across tools
- **Manual PPM tracking** – Portfolio/program/risk management requires manual Excel reports
- **Reactive operations** – Issues discovered after impact rather than proactively surfaced
- **Siloed analytics** – Superset dashboards exist but lack unified access and governance
- **Alert fatigue** – Critical issues buried in notification noise

### Target State
A single operational control center that:
1. **Surfaces actionable recommendations** with evidence, impact, and remediation playbooks
2. **Provides portfolio-level visibility** into program health, budget variance, and risk exposure
3. **Automates intelligence workflows** via n8n for proactive issue detection
4. **Curates analytics workbooks** with drill-down capabilities in Superset
5. **Delivers notifications** to Mattermost with clear ownership and prioritization

---

## Goals and Success Metrics

### Business Goals
- **Operational Excellence**: 95% of critical recommendations resolved within 30 days
- **Cost Optimization**: Identify 15%+ cost savings opportunities annually
- **Risk Mitigation**: Zero-penalty compliance with security and reliability standards
- **Portfolio Visibility**: Real-time program health tracking for 100% of active projects
- **Time Savings**: 70% reduction in manual reporting and investigation time

### Technical Goals
- **Performance**: Recommendation ingestion API <2s p95 latency
- **Scale**: Support 1000+ recommendations with <30s score recomputation
- **Reliability**: 95%+ uptime for advisor overview dashboard
- **Idempotency**: Zero duplicate recommendations (deterministic key enforcement)
- **Security**: RLS policies enforce category + owner-based access control

### User Success Metrics
- **Ops Lead**: Average time-to-remediation reduced by 50%
- **Finance Owner**: Cost recommendations drive measurable savings
- **PMO Lead**: Portfolio dashboard replaces manual weekly reports
- **Executives**: Single pane of glass for operational health across categories

---

## User Personas

### 1. Platform Owner
**Role**: Approves architecture changes, sets category weights, owns roadmap
**Pain Points**: Lacks unified view of operational health, manual report generation
**Success**: Dashboard shows category scores, top recommendations, and portfolio health at a glance

### 2. Ops Lead
**Role**: Manages reliability/performance recommendations, owns playbook quality
**Pain Points**: Reactive firefighting, scattered metrics, unclear ownership
**Success**: Proactive alerts with clear remediation steps, automated playbook execution

### 3. Security Owner
**Role**: Manages security recommendations, approves risk acceptance
**Pain Points**: Manual vulnerability tracking, compliance gaps discovered late
**Success**: Security scorecard with evidence-based risk assessments and remediation tracking

### 4. Finance Owner
**Role**: Manages cost recommendations, tracks savings impact
**Pain Points**: Manual cost analysis, lack of optimization visibility
**Success**: Cost dashboard with savings projections and realized impact tracking

### 5. PMO Lead
**Role**: Manages PPM hierarchy, risk register, resource allocation
**Pain Points**: Excel-based portfolio tracking, disconnected risk management
**Success**: Real-time portfolio rollups with risk exposure and resource utilization

### 6. Executives (CTO/CFO)
**Role**: Strategic oversight, budget approval, risk governance
**Pain Points**: Delayed visibility into operational issues, manual quarterly reviews
**Success**: Executive dashboard with trend analysis and actionable insights

---

## Architecture Overview

### Layered Approach
```
Native CE (foundation)
  ↓
OCA Modules (gap-fill for PPM)
  ↓
IPAI Custom Modules (governance + advisor + integration)
```

### Module Structure
All IPAI custom modules live in `addons/ipai/` namespace:

**1. ipai_workspace_core** (Shared Foundation)
- **Depends on**: `base`, `mail`
- **Purpose**: Shared mixins, base configuration, common security groups
- **Key Features**: Base models, utility functions, RBAC groups

**2. ipai_ppm** (Portfolio/Program Management)
- **Depends on**: `project`, `account`, `hr`, `resource`, OCA modules (project_portfolio, project_risk)
- **Purpose**: PPM core entities (portfolio, program, risk, resource allocation)
- **Key Features**:
  - Portfolio/program hierarchy
  - Risk register with likelihood/impact scoring
  - Resource allocation tracking
  - Budget variance reporting
  - Integration with OCA project modules

**3. ipai_advisor** (Recommendation Workflow)
- **Depends on**: `mail`, `ipai_workspace_core`
- **Purpose**: Advisor categories, recommendations, playbooks, scoring
- **Key Features**:
  - 5 category models (Cost, Security, Reliability, OpsEx, Performance)
  - Recommendation lifecycle (new → assigned → in_progress → resolved)
  - Playbook versioning and approval workflow
  - Category score calculation with confidence weighting
  - Evidence attachment (logs, metrics, screenshots)

**4. ipai_workbooks** (Analytics Registry)
- **Depends on**: `ipai_workspace_core`
- **Purpose**: Workbook registry with links to Superset dashboards
- **Key Features**:
  - Curated workbook metadata (name, description, owner, tags)
  - Drill-through link generation to Superset
  - Access control integration (view permissions)
  - CSV export capability for offline analysis

**5. ipai_connectors** (Integration Layer)
- **Depends on**: `ipai_advisor`, `ipai_ppm`
- **Purpose**: API endpoints + sync jobs for external integrations
- **Key Features**:
  - Webhook endpoints for n8n workflows
  - Recommendation ingestion API (idempotent)
  - Portfolio sync with external tools
  - Health check endpoints for monitoring

---

## Functional Requirements

### FR-1: Advisor Overview Dashboard

**Description**: Single pane of glass showing category health scores and top recommendations

**User Stories**:
- As an **Ops Lead**, I want to see the top 5 reliability recommendations so I can prioritize remediation
- As a **Finance Owner**, I want to see the cost optimization score trend over 30 days
- As a **Platform Owner**, I want to filter recommendations by owner and severity

**Acceptance Criteria**:
- ✅ Dashboard loads in <3s with 1000+ recommendations
- ✅ Category scores (0-100) displayed with color-coded status (red <60, yellow 60-79, green 80+)
- ✅ Top 5 recommendations per category with severity badges
- ✅ Drill-down to full recommendation list with filters (owner, status, category, severity)
- ✅ Score trend chart (30-day lookback)
- ✅ Responsive design (mobile + desktop)

**Dependencies**:
- `ipai_advisor` module for recommendation models
- Supabase `ops_advisor.recommendations` table
- Odoo views: list, kanban, graph

---

### FR-2: Recommendation Lifecycle Management

**Description**: Full CRUD workflow for recommendations with assignment, tracking, and closure

**User Stories**:
- As an **Ops Lead**, I want to assign recommendations to team members so ownership is clear
- As a **Security Owner**, I want to update recommendation status and add resolution notes
- As a **Platform Owner**, I want to track time-to-resolution metrics for SLA compliance

**Acceptance Criteria**:
- ✅ Recommendations have lifecycle states: `new` → `assigned` → `in_progress` → `resolved` → `closed`
- ✅ Assignment workflow with email notifications via Odoo mail integration
- ✅ Due date setting with escalation logic (overdue → auto-notify manager)
- ✅ Resolution notes with rich text editor (evidence documentation)
- ✅ Activity log tracking all status changes and assignments
- ✅ Bulk actions: assign, update status, set due dates

**Dependencies**:
- `ipai_advisor` module with `mail.thread` inheritance
- Odoo activity tracking (`mail.activity`)
- n8n workflow for due date reminders

---

### FR-3: Category-Specific Scorecards

**Description**: Dedicated dashboards for each advisor category with specialized metrics

**Categories**:
1. **Cost Optimization**: Savings projections, realized impact, cost trends
2. **Security**: Vulnerability counts, compliance status, risk acceptance register
3. **Reliability**: Uptime metrics, incident frequency, MTTR trends
4. **Operational Excellence**: Automation coverage, runbook completeness, manual toil reduction
5. **Performance**: Response time trends, resource utilization, optimization opportunities

**Acceptance Criteria**:
- ✅ Each category has a dedicated Odoo view with category-specific KPIs
- ✅ Scorecard shows current score + 30-day trend
- ✅ Drill-down to recommendations filtered by category
- ✅ Export to CSV for offline analysis
- ✅ Integration with Superset workbooks for advanced analytics

**Dependencies**:
- `ipai_advisor` category models
- `ipai_workbooks` for Superset links
- Supabase `ops_advisor.category_scores` table

---

### FR-4: Portfolio/Program Management (PPM) Extensions

**Description**: OCA-based PPM with risk register and resource allocation tracking

**User Stories**:
- As a **PMO Lead**, I want to see portfolio health rollups so I can report to executives
- As a **Finance Owner**, I want to track budget variance across programs
- As a **Platform Owner**, I want to link recommendations to affected programs

**Acceptance Criteria**:
- ✅ Portfolio hierarchy: Portfolio → Programs → Projects (OCA `project_portfolio`)
- ✅ Risk register with likelihood/impact scoring (OCA `project_risk`)
- ✅ Resource allocation tracking with overload detection
- ✅ Budget variance reporting (planned vs. actual)
- ✅ Recommendations can be linked to programs (many-to-many relationship)
- ✅ Portfolio dashboard with health indicators (green/yellow/red)

**Dependencies**:
- OCA modules: `project_portfolio`, `project_risk`, `resource_allocation`
- `ipai_ppm` module for custom extensions
- `ipai_advisor` for recommendation linking

---

### FR-5: Workbooks Registry

**Description**: Curated catalog of Superset dashboards with metadata and access control

**User Stories**:
- As an **Analyst**, I want to browse available workbooks by category and tags
- As a **Platform Owner**, I want to control workbook access based on user roles
- As a **Finance Owner**, I want to drill through from Odoo to Superset cost dashboards

**Acceptance Criteria**:
- ✅ Workbook registry model with fields: name, description, category, owner, tags, superset_url
- ✅ Odoo kanban view grouped by category
- ✅ Click-through to Superset dashboard (opens in new tab with SSO)
- ✅ Access control: Only show workbooks user has permission to view
- ✅ CSV export capability with workbook metadata

**Dependencies**:
- `ipai_workbooks` module
- Superset API integration (optional for SSO)
- Supabase `ops_advisor.workbooks` table

---

### FR-6: Automation Workflows (n8n Integration)

**Description**: Event-driven automation for recommendation ingestion, alerts, and notifications

**Workflows**:
1. **Recommendation Ingestion**: External sources → n8n → Odoo API (idempotent)
2. **Due Date Reminders**: Daily cron → Check overdue → Mattermost notify
3. **Score Refresh**: Nightly cron → Recalculate category scores → Update dashboard
4. **Monthly Report**: End-of-month → Generate PDF summary → Email stakeholders

**Acceptance Criteria**:
- ✅ n8n webhooks integrated with `ipai_connectors` endpoints
- ✅ Idempotent recommendation creation (deterministic keys prevent duplicates)
- ✅ Mattermost notifications for high/critical recommendations (real-time)
- ✅ Error handling with retry logic (3 attempts with exponential backoff)
- ✅ Workflow execution logs stored in Supabase for debugging

**Dependencies**:
- `ipai_connectors` for webhook endpoints
- n8n workflows (JSON definitions stored in Git)
- Mattermost webhook URLs (stored in Supabase Vault)

---

### FR-7: Mattermost Notifications

**Description**: Actionable notifications in Mattermost with recommendation context and links

**Notification Types**:
- **New Critical Recommendation**: Immediate alert with severity badge
- **Due Date Approaching**: 7-day and 3-day warnings
- **Overdue Assignment**: Daily escalation to owner + manager
- **Score Threshold Breach**: Alert when category score drops below 60
- **Monthly Summary**: End-of-month digest with top issues and trends

**Acceptance Criteria**:
- ✅ Notifications include: recommendation title, category, severity, owner, due date, Odoo link
- ✅ Severity color-coding: Critical (red), High (orange), Medium (yellow), Low (blue)
- ✅ Clickable links to Odoo recommendation detail view
- ✅ Notification frequency controls (no spam: max 1 alert per recommendation per day)
- ✅ Channel routing: Critical → #ops-critical, Overdue → #ops-overdue, Summary → #ops-summary

**Dependencies**:
- n8n workflows for notification logic
- Mattermost webhook integration
- `ipai_advisor` recommendation models

---

### FR-8: Explainability and Evidence

**Description**: Every recommendation includes evidence, impact, remediation, owner, and confidence

**Required Fields**:
- **Evidence**: Concrete data/metrics supporting the recommendation (JSON field)
- **Impact**: Quantified business impact (cost savings, risk reduction, performance gain)
- **Remediation**: Step-by-step playbook with validation criteria
- **Owner**: Assigned person/team responsible for resolution
- **Confidence**: Algorithm confidence score (0.0-1.0)

**Acceptance Criteria**:
- ✅ All recommendations must have non-null evidence and remediation before activation
- ✅ Playbook versioning: Track changes to remediation steps over time
- ✅ Evidence attachments: Support logs, screenshots, metrics exports (Odoo attachments)
- ✅ Confidence scoring: Algorithm must return 0.0-1.0 float (displayed as percentage)
- ✅ Impact quantification: Cost (USD), Risk (CVSS score), Performance (latency ms)

**Dependencies**:
- `ipai_advisor` recommendation model with JSON fields
- Odoo attachment system (`ir.attachment`)
- Playbook approval workflow (optional: require manager approval for playbook edits)

---

## Data Requirements

### Supabase Schema: `ops_advisor`

**Tables**:

1. **recommendations**
   ```sql
   CREATE TABLE ops_advisor.recommendations (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       category TEXT NOT NULL CHECK (category IN ('cost', 'security', 'reliability', 'opex', 'performance')),
       title TEXT NOT NULL,
       description TEXT,
       severity TEXT NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low')),
       status TEXT NOT NULL DEFAULT 'new' CHECK (status IN ('new', 'assigned', 'in_progress', 'resolved', 'closed')),
       owner_id INTEGER REFERENCES res_users(id),
       evidence JSONB NOT NULL,
       impact JSONB NOT NULL,
       remediation JSONB NOT NULL,
       confidence NUMERIC(3,2) CHECK (confidence BETWEEN 0.00 AND 1.00),
       due_date DATE,
       created_at TIMESTAMPTZ DEFAULT NOW(),
       updated_at TIMESTAMPTZ DEFAULT NOW(),
       UNIQUE (category, title, evidence->>'resource_id')  -- Idempotency key
   );
   ```

2. **category_scores**
   ```sql
   CREATE TABLE ops_advisor.category_scores (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       category TEXT NOT NULL,
       score NUMERIC(5,2) NOT NULL CHECK (score BETWEEN 0.00 AND 100.00),
       calculated_at TIMESTAMPTZ DEFAULT NOW(),
       recommendation_count INTEGER NOT NULL,
       critical_count INTEGER NOT NULL,
       high_count INTEGER NOT NULL
   );
   ```

3. **workbooks**
   ```sql
   CREATE TABLE ops_advisor.workbooks (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       name TEXT NOT NULL,
       description TEXT,
       category TEXT NOT NULL,
       owner_id INTEGER REFERENCES res_users(id),
       superset_url TEXT NOT NULL,
       tags TEXT[],
       created_at TIMESTAMPTZ DEFAULT NOW()
   );
   ```

4. **activity_log**
   ```sql
   CREATE TABLE ops_advisor.activity_log (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       recommendation_id UUID REFERENCES ops_advisor.recommendations(id),
       action TEXT NOT NULL,  -- 'status_change', 'assignment', 'due_date_update', 'closed'
       old_value TEXT,
       new_value TEXT,
       user_id INTEGER REFERENCES res_users(id),
       timestamp TIMESTAMPTZ DEFAULT NOW()
   );
   ```

**RLS Policies**:
- **Category-based access**: Users can only see recommendations for categories they own
- **Owner-based access**: Users can see recommendations assigned to them or their team
- **Admin override**: Platform admins can view all recommendations
- **Audit trail**: All status changes, assignments, and closures logged to `activity_log`

---

## Integration Contracts

### Odoo ↔ Supabase Sync
- **Pattern**: Write to Odoo first, sync to Supabase via scheduled action (hourly)
- **Conflict Resolution**: Odoo is source of truth for recommendation lifecycle
- **Performance**: Batch updates (max 100 records per sync job)
- **Error Handling**: Failed syncs logged to `sync_errors` table, retry with exponential backoff

### Odoo ↔ n8n Webhooks
- **Recommendation Ingestion**: `POST /api/advisor/recommendations` (idempotent)
- **Due Date Reminders**: n8n cron → Query Odoo XML-RPC → Mattermost notify
- **Score Refresh**: n8n cron → Call Supabase RPC `recalculate_category_scores()`

### Odoo ↔ Mattermost
- **Notification Channel**: Webhook URLs stored in Supabase Vault (not Odoo database)
- **Message Format**: JSON payload with recommendation context + Odoo deep link
- **Rate Limiting**: Max 1 notification per recommendation per day (tracked in `activity_log`)

### Odoo ↔ Superset
- **SSO**: Optional Superset OAuth integration (v1.1 roadmap)
- **Drill-through**: Odoo generates Superset URL with filters pre-applied
- **Embedding**: Optional iframe embedding in Odoo (v2.0 roadmap)

---

## Non-Functional Requirements

### Performance
- **Recommendation Ingestion API**: <2s p95 latency for single recommendation
- **Score Recomputation**: <30s for 1000 recommendations (nightly batch job)
- **Dashboard Load Time**: <3s for advisor overview with 1000+ recommendations
- **Webhook Response Time**: <500ms acknowledgment, async processing

### Scalability
- **Recommendation Volume**: Support 10,000+ recommendations across all categories
- **User Concurrency**: 50+ simultaneous users without performance degradation
- **PPM Entities**: 100+ portfolios, 500+ programs, 5000+ projects

### Reliability
- **Uptime**: 95%+ for advisor overview dashboard (monthly measurement)
- **Data Durability**: Supabase automatic backups with 7-day retention
- **Error Recovery**: All n8n workflows have retry logic (3 attempts, exponential backoff)

### Security
- **Access Control**: RLS policies enforce category + owner-based access
- **Audit Trail**: All status changes, assignments, and closures logged
- **Secret Management**: API keys and webhook URLs in Supabase Vault (not Odoo)
- **Authentication**: Odoo session-based auth, Supabase JWT for API calls

### Maintainability
- **Code Quality**: OCA compliance (AGPL-3, proper `__manifest__.py`, README.rst)
- **Documentation**: Comprehensive README per module with installation/configuration/usage
- **Testing**: Unit tests with ≥80% coverage, integration tests for sync jobs
- **Dependency Management**: `oca_dependencies.txt` for vendored OCA modules

---

## Acceptance Criteria

### Minimum Viable Product (MVP) — v1.0

**Must Have**:
- ✅ Advisor overview dashboard with 5 category scores
- ✅ Recommendation lifecycle (new → assigned → in_progress → resolved → closed)
- ✅ Workbooks registry with Superset links
- ✅ n8n workflows: Recommendation ingestion + Due date reminders
- ✅ Mattermost notifications for critical recommendations
- ✅ OCA PPM integration (portfolio/program/risk models)
- ✅ RLS policies enforced on all public tables
- ✅ Idempotent recommendation creation (no duplicates)

**Nice to Have** (v1.1 Roadmap):
- Resource allocation tracking with overload detection
- Deeper observability inputs (Prometheus/Loki integration)
- Advanced filtering + bulk actions
- PDF export with executive summary

**Out of Scope** (v2.0 Roadmap):
- GitOps integration (ArgoCD/Flux)
- Policy compliance reporting (Kyverno/OPA)
- Drift detection + automated remediation
- Embedded Superset dashboards in Odoo

---

## Dependencies and Risks

### Dependencies
1. **OCA Modules**: `project_portfolio`, `project_risk`, `resource_allocation` (version pinning required)
2. **Supabase Project**: `xkxyvboeubffxxbebsll` (ops_advisor schema)
3. **n8n Instance**: `https://ipa.insightpulseai.com` (workflow orchestration)
4. **Mattermost Instance**: `https://mattermost.insightpulseai.com` (notifications)
5. **Superset Instance**: `https://superset.insightpulseai.com` (workbooks)

### Risks
1. **OCA Module Compatibility**: OCA modules may have breaking changes in future versions
   - **Mitigation**: Pin OCA versions in `oca_dependencies.txt`, test upgrades in staging
2. **Recommendation Volume**: High recommendation count may degrade dashboard performance
   - **Mitigation**: Implement pagination, lazy loading, and database indexing
3. **n8n Workflow Complexity**: Complex workflows may be hard to debug and maintain
   - **Mitigation**: Keep workflows simple, store JSON definitions in Git, add comprehensive logging
4. **Idempotency Enforcement**: External sources may generate duplicate recommendations
   - **Mitigation**: Use deterministic keys (category + title + resource_id), enforce UNIQUE constraint

---

## Success Validation

### Technical Acceptance
- ✅ Recommendation ingestion API <2s p95 latency
- ✅ Score recomputation <30s for 1000 recommendations
- ✅ No duplicate recommendations (idempotency verified)
- ✅ RLS policies prevent unauthorized access (penetration test)
- ✅ 95%+ uptime for advisor overview dashboard (30-day measurement)

### User Acceptance
- ✅ Ops Lead can view top 5 reliability recommendations and assign to team
- ✅ PMO Lead can see portfolio health rollups without manual Excel reports
- ✅ Finance Owner can track cost savings with drill-through to Superset
- ✅ Mattermost notifications arrive within 1 minute of recommendation creation
- ✅ Workbooks registry shows only authorized dashboards for logged-in user

### Business Value
- ✅ 80%+ of critical recommendations resolved within 14 days (month 1)
- ✅ +10 points improvement in any category score over 30 days
- ✅ 90%+ correlation between deployment failures and reliability recommendations
- ✅ 70%+ portfolio health distribution: green (target: 70%, yellow 20%, red 10%)

---

## Appendix: Related Documents

- **Constitution**: `spec/ipai-control-center/constitution.md` (principles, constraints, success criteria)
- **Architecture**: `spec/ipai-control-center/architecture.md` (diagrams, data flows, integration)
- **Plan**: `spec/ipai-control-center/plan.md` (milestones, technical decisions, roadmap)
- **Tasks**: `spec/ipai-control-center/tasks.md` (execution backlog with acceptance criteria)
- **Pulser SDK Integration**: See Constitution Appendix for agent registration and governance automation
