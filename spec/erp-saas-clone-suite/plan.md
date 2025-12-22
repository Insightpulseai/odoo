# ERP SaaS Clone Suite — Implementation Plan

## Phase 0: Foundation (Week 1)

### 0.1 Spec Kit + Catalog Infrastructure

**Objective**: Establish catalog-driven development process with CI gates.

**Deliverables**:

1. Create directory structure:
   ```
   catalog/
   ├── best_of_breed.yaml
   └── equivalence_matrix.csv
   kb/
   ├── parity/
   │   ├── rubric.json
   │   └── baseline.json
   └── design_system/
       └── tokens.yaml
   tools/parity/
   ├── validate_spec_kit.py
   └── parity_audit.py
   ```

2. Implement CI workflow `.github/workflows/spec-and-parity.yml`:
   - Spec Kit validation job
   - Parity audit job with artifact upload
   - Merge blocking on failures

3. Seed initial capability catalog:
   - 2 P0 capabilities: `crm.pipeline.board`, `itsm.incident.queue`
   - 3 P1 capabilities: `workos.pages.db`, `assets.checkout.reserve`, `ppm.portfolio.lite`

**Exit Criteria**:

- [ ] `python3 tools/parity/validate_spec_kit.py` passes
- [ ] `python3 tools/parity/parity_audit.py` runs without error
- [ ] CI workflow triggers on PR

### 0.2 Platform Module Scaffolds

**Objective**: Create empty module structures for platform primitives.

**Deliverables**:

1. Scaffold modules:
   - `addons/ipai_platform_workflow/`
   - `addons/ipai_platform_approvals/`
   - `addons/ipai_platform_audit/`
   - `addons/ipai_platform_theme/`

2. Each module contains:
   - `__manifest__.py` with correct dependencies
   - `__init__.py` with standard imports
   - `models/`, `security/`, `views/`, `tests/` directories
   - Minimal `ir.model.access.csv`

**Exit Criteria**:

- [ ] All modules installable (no syntax errors)
- [ ] Theme module loads SCSS tokens

## Phase 1: First P0 Vertical — CRM Pipeline (Week 2-3)

### 1.1 Pipeline Board Enhancement

**Objective**: Deliver Salesforce-like pipeline experience on Odoo CRM.

**Capability ID**: `crm.pipeline.board`

**Implementation**:

1. Create `addons/ipai_crm_pipeline/`:
   - Inherit `crm.lead` with additional fields
   - Add stage validation rules
   - Implement quick action buttons

2. View customizations:
   - Enhanced kanban with stage rules indicator
   - Quick actions panel (log call, schedule, email)
   - Activity timeline widget

3. Dashboard views:
   - Pipeline by stage (stacked bar)
   - Win/loss ratio trending
   - Activity metrics

**Exit Criteria**:

- [ ] Parity score ≥ 50 for `crm.pipeline.board`
- [ ] Demo flow recorded
- [ ] Unit tests pass

### 1.2 Activity Timeline

**Objective**: Unified activity feed with @mentions.

**Implementation**:

1. Extend `mail.message` display
2. Add inline activity creation
3. Implement @mention notification routing

**Exit Criteria**:

- [ ] Activities visible in timeline
- [ ] @mentions trigger notifications
- [ ] Performance < 500ms for 100 activities

## Phase 2: Platform Primitives Implementation (Week 4-5)

### 2.1 Workflow Engine

**Capability ID**: Platform-level (not in matrix)

**Implementation**:

1. Generic state machine model
2. Transition rules with conditions
3. Notification hooks (email, Mattermost)

### 2.2 Approval Chains

**Implementation**:

1. Role-based approver lookup
2. Delegation configuration
3. Escalation timer

### 2.3 Audit Trail

**Implementation**:

1. Model mixin for audited fields
2. Change event capture
3. Audit log viewer

### 2.4 Theme Tokens

**Implementation**:

1. SCSS variable system
2. Component token mapping
3. Theme switcher (light/dark preparation)

## Phase 3: Second P0 Vertical — ITSM (Week 6-7)

**Capability ID**: `itsm.incident.queue`

### 3.1 Incident Module

1. Create `addons/ipai_itsm_incident/`
2. Incident intake form with auto-categorization
3. Queue views with assignment rules
4. SLA configuration and tracking
5. Escalation workflow

**Exit Criteria**:

- [ ] Parity score ≥ 50 for `itsm.incident.queue`
- [ ] SLA violations flagged correctly
- [ ] Demo flow recorded

## Phase 4: P1 Verticals (Week 8-10)

### 4.1 WorkOS Pages

**Capability ID**: `workos.pages.db`

- Wiki pages with rich editor
- Database views (table, board, gallery)
- Templates and cloning

### 4.2 Assets Checkout

**Capability ID**: `assets.checkout.reserve`

- Reservation workflow
- Custody tracking
- Return processing

### 4.3 PPM Portfolio

**Capability ID**: `ppm.portfolio.lite`

- Portfolio grouping
- Resource capacity view
- Budget summary

## Phase 5: Hardening + Launch Prep (Week 11-12)

### 5.1 Performance Optimization

- Query optimization
- Caching strategy
- Load testing

### 5.2 Security Audit

- Permission review
- Penetration testing
- Compliance checklist

### 5.3 Documentation

- User guides per vertical
- Admin configuration docs
- API documentation

### 5.4 Demo Environment

- Seed data scripts
- Reset automation
- Recording studio setup

## Dependencies Graph

```
Phase 0 (Foundation)
    ├── Spec Kit + Catalog
    └── Platform Scaffolds
          │
          v
Phase 1 (CRM)
    ├── Pipeline Board
    └── Activity Timeline
          │
          v
Phase 2 (Platform)
    ├── Workflow Engine ─────┐
    ├── Approval Chains      │
    ├── Audit Trail          │
    └── Theme Tokens         │
          │                  │
          v                  v
Phase 3 (ITSM) <────────────┘
    └── Incident Module
          │
          v
Phase 4 (P1 Verticals)
    ├── WorkOS Pages
    ├── Assets Checkout
    └── PPM Portfolio
          │
          v
Phase 5 (Launch)
```

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| OCA module gaps | Early evaluation, budget for custom dev |
| Performance issues | Continuous profiling, baseline thresholds |
| Scope creep | Strict parity gate enforcement |
| Resource constraints | P0 focus, defer P1/P2 as needed |

## Checkpoints

| Milestone | Exit Criteria |
|-----------|---------------|
| M0: Foundation | CI gates operational |
| M1: CRM MVP | Pipeline demo complete |
| M2: Platform | All primitives functional |
| M3: ITSM MVP | Incident demo complete |
| M4: P1 Complete | All verticals at baseline |
| M5: Launch | All P0 at ≥70 score |
