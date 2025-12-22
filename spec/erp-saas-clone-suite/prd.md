# ERP SaaS Clone Suite — Product Requirements Document

## 1. Executive Summary

Build an **Odoo CE/OCA 18–based platform** that delivers **best-of-breed SaaS experiences** (Salesforce, ServiceNow, Notion, Cheqroom, Clarity PPM) through a catalog-driven, parity-enforced development process.

### Value Proposition

* **For developers**: Spec-driven workflow with clear capability mapping and automated quality gates.
* **For operators**: Enterprise-grade ERP features without Enterprise Edition licensing costs.
* **For users**: Modern SaaS UX on familiar Odoo backbone.

## 2. Target Users

| Persona | Description | Key Needs |
|---------|-------------|-----------|
| Platform Dev | Builds and maintains ipai_* modules | Clear specs, parity rubrics, fast feedback loops |
| Domain Admin | Configures tenant workspaces | Preset bundles, SSO, role dashboards |
| End User | Uses ERP features daily | Modern UX, quick actions, activity timelines |

## 3. Feature Requirements

### 3.1 Spec Kit Infrastructure (P0)

**FR-001**: Spec Kit Validation

* Every `spec/<slug>/` must contain: `constitution.md`, `prd.md`, `plan.md`, `tasks.md`
* CI fails on missing files
* Minimum content threshold enforced (10+ non-empty lines per file)

**FR-002**: Capability Catalog

* `catalog/best_of_breed.yaml` lists clone targets with hero flows
* `catalog/equivalence_matrix.csv` maps capability IDs to modules
* All development tasks reference a `capability_id`

### 3.2 Parity Enforcement (P0)

**FR-003**: Parity Scoring

* Six dimensions: workflow (30%), UX (25%), data (15%), permissions (15%), reporting (10%), performance (5%)
* Scores tracked per capability in equivalence matrix
* Baseline file locks P0 scores to prevent regression

**FR-004**: Parity CI Gate

* `tools/parity/parity_audit.py` runs on every PR
* Fails if any P0 capability score drops below baseline
* Uploads parity report as artifact

### 3.3 Platform Primitives (P1)

**FR-005**: Platform Workflow Module (`ipai_platform_workflow`)

* Generic approval workflow engine
* State machine with configurable transitions
* Email/Mattermost notifications on state changes

**FR-006**: Platform Approvals Module (`ipai_platform_approvals`)

* Role-based approval chains
* Delegation and escalation rules
* Audit trail for all approval actions

**FR-007**: Platform Audit Module (`ipai_platform_audit`)

* Field-level change tracking
* Configurable audit policies per model
* Retention and archival rules

**FR-008**: Platform Theme Module (`ipai_platform_theme`)

* SCSS token system (spacing, colors, typography)
* Fiori-inspired design system
* Dark mode support (P2)

### 3.4 CRM Pipeline (P0)

**FR-009**: Pipeline Board View

* Kanban with drag-and-drop stage transitions
* Stage rules with required fields per stage
* Quick actions (log call, schedule meeting, send email)

**FR-010**: Activity Timeline

* Unified activity feed on lead/opportunity
* Inline activity logging
* @mentions and notifications

**FR-011**: Role Dashboards

* Sales Manager: pipeline value, win rate, forecast
* Sales Rep: my opportunities, overdue activities
* Executive: revenue trends, top accounts

### 3.5 Additional Verticals (P1)

**FR-012**: ITSM Incident Module (`ipai_itsm_incident`)

* Incident intake and triage
* Assignment rules with SLA
* Escalation workflows

**FR-013**: WorkOS Pages Module (`ipai_workos_pages`)

* Wiki-style pages with database views
* Templates for common page types
* Full-text search

**FR-014**: Assets Checkout Module (`ipai_assets_checkout`)

* Reserve, checkout, custody, return workflow
* Asset tracking with barcode/QR
* Maintenance scheduling integration

**FR-015**: PPM Portfolio Module (`ipai_ppm_portfolio`)

* Portfolio-level project grouping
* Capacity planning (lite)
* Budget control (lite)

## 4. Non-Functional Requirements

### 4.1 Performance

* Page load < 2s for standard views
* Kanban board drag-drop < 500ms response
* Search results < 1s for typical queries

### 4.2 Security

* SSO via Keycloak (SAML/OIDC)
* Tenant data isolation (DB-level)
* Field-level access control where needed

### 4.3 Scalability

* Support 10+ concurrent tenants
* 1000+ users per tenant
* 100k+ records per major model

## 5. Acceptance Criteria

### 5.1 Spec Kit Gate

* Given any PR touching spec/
* When CI runs validate_spec_kit.py
* Then merge is blocked if any required file missing

### 5.2 Parity Gate

* Given a PR changing a P0 capability
* When CI runs parity_audit.py
* Then merge is blocked if capability score regresses

### 5.3 CRM Pipeline Demo

* Given a new opportunity
* When user drags to "Qualified" stage
* Then required fields validation triggers
* And activity is logged
* And pipeline dashboard updates

## 6. Out of Scope (v1)

* Mobile native apps (web responsive only)
* Advanced AI features (basic agent hooks only)
* Multi-currency (single currency per tenant)
* Custom report builder (use Superset)

## 7. Dependencies

* Odoo 18 CE stable release
* OCA modules: `crm`, `sale`, `project`, `helpdesk` (community ports)
* Infrastructure: PostgreSQL 15, n8n, Keycloak, Mattermost

## 8. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Spec Kit compliance | 100% | All bundles pass validation |
| P0 parity score | ≥ 70/100 average | parity_report.json |
| Module test coverage | ≥ 80% | pytest coverage |
| Demo time | < 15 min | Recorded walkthrough |
