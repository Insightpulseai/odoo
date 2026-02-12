# Control Layer

**Purpose**: Enforce policies, manage risk, and ensure compliance through gates and controls

**Layer Position**: Layer 5 of 7 (Strategy → Portfolio → Process → Execution → **Control** → Evidence → Integration)

---

## Purpose & Scope

This layer defines **governance mechanisms** that enforce quality, security, and compliance:

- **Policies**: SOPs, standards, and operating procedures
- **Gates**: Approval checkpoints that block progress until criteria met
- **Risk**: Risk and issue registers with mitigation strategies
- **Access**: Role-based access control (RBAC) and segregation of duties (SOD)

**Inspired by**: Master Control (compliance software), ISO 9001 (quality), SOC 2 (security)

---

## ID Convention

**Format**: `CTRL-<DOMAIN>-<NUMBER>`

**Examples**:
- `CTRL-GATE-001` - Architecture review gate
- `CTRL-SEC-004` - Security approval gate
- `CTRL-FIN-001` - Financial approval control
- `CTRL-DOC-001` - Documentation completeness control

---

## Directory Structure

```
control/
├── README.md                    # This file
├── policies/                    # Standard Operating Procedures (SOPs)
│   ├── SOP-001-code-review.md
│   ├── SOP-002-deployment.md
│   └── SOP-003-access-management.md
├── gates/                       # Approval gates and criteria
│   ├── GATE-001-architecture-review.md
│   ├── GATE-002-security-approval.md
│   ├── GATE-003-compliance-check.md
│   └── tier-0-gates.md          # Reference to scripts/gates/
├── risk/                        # Risk and issue management
│   ├── risk-register.yaml
│   └── issue-register.yaml
├── access/                      # Access control
│   └── access-matrix.yaml
└── segregation-of-duties.yaml   # SOD matrix
```

---

## Gate Architecture

**Gates are blocking checkpoints** that enforce quality standards before work proceeds.

### Gate Lifecycle

```
Request → Automated Checks → Manual Review (if needed) → Approval/Rejection → Evidence Collection
```

### Gate Types

1. **Automated Gates**: Fully automated, no manual intervention
   - Example: CI/CD quality gates (lint, test, security scan)
   - Implementation: GitHub Actions workflows

2. **Semi-Automated Gates**: Automated checks + manual approval
   - Example: Architecture review (automated scoring + human review)
   - Implementation: Bot checks + GitHub approval workflow

3. **Manual Gates**: Human approval required
   - Example: Production deployment approval
   - Implementation: GitHub required reviewers

---

## Connections to Other Layers

### Upstream (Controls enforce these layers)

- **Strategy** (`docs/strategy/`): Controls ensure strategic objectives are met with quality
  - Example: `STRAT-PARITY-001` → `CTRL-GATE-001` (Architecture must support parity goals)

- **Portfolio** (`docs/portfolio/`): Controls gate portfolio initiative progression
  - Example: `PORT-2026-007` → `CTRL-SEC-004` (Security approval before production)

- **Process** (`docs/process/`): Controls enforce process compliance
  - Example: `PROC-DEV-001` → `CTRL-GATE-001` (Code review gate in dev process)

### Downstream (Controls implemented through these layers)

- **Execution** (code, scripts, workflows): Controls automated through CI/CD
  - Example: `CTRL-GATE-001` → `.github/workflows/architecture-gate.yml`

### Validation (Controls verified by these layers)

- **Evidence** (`docs/evidence/`): Controls produce audit trail
  - Example: `CTRL-GATE-001` → `EVID-20260212-001` (Architecture review evidence)

---

## Document Format

All control documents must include frontmatter:

```yaml
---
id: CTRL-GATE-001
type: gate
name: Architecture Review Gate
category: quality
trigger: portfolio_initiative_phase == "design"
approvers: [architect_role, tech_lead_role]
criteria:
  - scalability_assessed
  - security_reviewed
  - cost_estimated
  - documentation_complete
enforced_by: .github/workflows/architecture-gate.yml
bypass_allowed: false
bypass_approver: cto_role
evidence_required: [architecture_diagram, cost_analysis, security_assessment]
---
```

---

## Gate Definition Format

**File**: `docs/control/gates/GATE-001-architecture-review.md`

**Structure**:
```markdown
---
id: CTRL-GATE-001
type: gate
name: Architecture Review Gate
---

# Architecture Review Gate

## Purpose
Ensure technical designs meet scalability, security, and cost requirements before implementation.

## Trigger
- Portfolio initiative phase changes to "design"
- Major architectural change proposed

## Automated Criteria (Must Pass)
- [ ] Architecture diagram exists in spec bundle
- [ ] Cost analysis completed (infrastructure + operational)
- [ ] Security threat model documented
- [ ] Scalability assessment for 3x growth

## Manual Review Criteria
- [ ] Architect approves design approach
- [ ] Tech lead confirms implementation feasibility
- [ ] Security team validates threat model

## Approval Flow
1. Automated checks run (GitHub Actions)
2. If all automated checks pass → Manual review requested
3. Assigned approvers review design docs
4. Approval requires 2/2 (Architect + Tech Lead)
5. Evidence artifacts archived in docs/evidence/

## Bypass Procedure
- Allowed: No (critical quality gate)
- Exception: CTO approval required with documented justification
- Post-bypass: Mandatory architectural review within 1 sprint

## Evidence Requirements
- Architecture diagram (PNG/SVG)
- Cost analysis spreadsheet
- Security threat model document
- Scalability assessment report

## Related
- Process: PROC-DEV-001 (Software Development)
- Portfolio: All PORT-* initiatives at design phase
- Evidence: EVID-*/architecture-review/
```

---

## Policy (SOP) Format

**File**: `docs/control/policies/SOP-001-code-review.md`

**Structure**:
```markdown
---
id: CTRL-SOP-001
type: policy
name: Code Review Standard Operating Procedure
status: active
version: 1.2
owner: engineering_team
last_review: 2026-02-01
next_review: 2026-05-01
---

# SOP-001: Code Review

## Purpose
Ensure code quality, knowledge sharing, and defect prevention through peer review.

## Scope
- Applies to: All code changes in production repositories
- Excludes: Markdown documentation (unless process-critical)

## Procedure

### Before Review
- [ ] Automated checks pass (lint, test, security scan)
- [ ] PR description includes context and testing evidence
- [ ] Commits follow conventional commit format

### During Review
- [ ] Reviewer has <24h to respond or reassign
- [ ] Focus areas: correctness, maintainability, security, performance
- [ ] Minimum 1 approval required; 2 for critical changes

### After Review
- [ ] All review comments addressed or explicitly acknowledged
- [ ] Final approval recorded
- [ ] PR merged (squash merge preferred)

## Roles & Responsibilities
- **Author**: Write clear code, provide context, address feedback
- **Reviewer**: Review within SLA, provide constructive feedback, approve/reject
- **Tech Lead**: Ensure SOP compliance, resolve conflicts

## Enforcement
- Automated: GitHub branch protection rules
- Manual: Tech lead reviews compliance monthly

## Exceptions
- Hot fixes: 1 approval sufficient (post-mortem required)
- Documentation: Self-merge allowed for typos
```

---

## Risk Register Format

**File**: `docs/control/risk/risk-register.yaml`

**Structure**:
```yaml
risk_register:
  - id: RISK-001
    title: Production database backup failure
    category: availability
    probability: low
    impact: critical
    risk_score: 12  # probability * impact
    status: active
    owner: devops_team
    mitigation:
      - Automated daily backups to 3 separate locations
      - Weekly backup restoration drill
      - Monitoring alert on backup failure
    contingency:
      - Restore from most recent successful backup
      - Notify stakeholders within 1 hour
      - Incident post-mortem within 48 hours
    last_review: 2026-02-01
    next_review: 2026-05-01

  - id: RISK-002
    title: Unauthorized access to production environment
    category: security
    probability: medium
    impact: critical
    risk_score: 18
    status: active
    owner: security_team
    mitigation:
      - Multi-factor authentication enforced
      - Role-based access control (RBAC)
      - Access audit log monitoring
      - Quarterly access review
    contingency:
      - Immediate account suspension
      - Security incident response team activation
      - Forensic investigation
    last_review: 2026-02-01
    next_review: 2026-03-01
```

---

## Access Control Matrix Format

**File**: `docs/control/access/access-matrix.yaml`

**Structure**:
```yaml
access_matrix:
  systems:
    - name: Production Database
      system_id: PROD-DB-001
      access_levels:
        - role: database_admin
          permissions: [read, write, delete, backup, restore]
          approval_required: cto
        - role: application
          permissions: [read, write]
          approval_required: tech_lead
        - role: analyst
          permissions: [read]
          approval_required: data_team_lead

    - name: GitHub Repository (Main Branch)
      system_id: GITHUB-MAIN
      access_levels:
        - role: maintainer
          permissions: [read, write, merge, admin]
          approval_required: cto
        - role: contributor
          permissions: [read, write]
          approval_required: tech_lead
        - role: viewer
          permissions: [read]
          approval_required: self_service

  segregation_of_duties:
    - rule: Code author cannot approve their own PR
      enforcement: GitHub branch protection
    - rule: Deployment approver cannot be the same as code author
      enforcement: GitHub required reviewers
    - rule: Financial approver cannot process their own expense
      enforcement: Odoo workflow rules
```

---

## How to Contribute

### Creating New Control

1. **Choose control type**: Policy, Gate, Risk, Access
2. **Generate unique ID**: Use `CTRL-<DOMAIN>-<NUMBER>` format
3. **Define criteria**: Automated checks + manual approval steps
4. **Document enforcement**: How is this control automated?
5. **Specify evidence**: What audit trail is produced?
6. **Link to processes**: Which processes does this control enforce?
7. **Update traceability index**: Add to `docs/TRACEABILITY_INDEX.yaml`

### Reviewing Controls

- **Enforceability**: Can this be automated or must it remain manual?
- **Necessity**: Is this control essential or bureaucratic overhead?
- **Evidence**: Does this produce auditable evidence?
- **Bypass**: Under what circumstances (if any) can this be bypassed?
- **Review Cycle**: How often should this control be reviewed for relevance?

---

## Tier-0 Gates (Current Implementation)

**Reference**: `scripts/gates/run_parity_gates.sh`

**Purpose**: Block work if foundational parity criteria not met

**Gates**:
1. **Architecture Parity Gate**: EE vs CE feature coverage >= 80%
2. **Security Baseline Gate**: No critical vulnerabilities in dependencies
3. **Performance Baseline Gate**: Response time <= 200ms (p95)
4. **Documentation Gate**: README + CHANGELOG + API docs exist

**Enforcement**: GitHub Actions workflow blocks merge if gates fail

---

## Success Metrics

Control layer effectiveness measured by:

1. **Gate Compliance**: % of work passing all gates without bypass (Target: 98%)
2. **Risk Mitigation**: % of identified risks with active mitigation (Target: 100%)
3. **Access Violations**: Unauthorized access attempts detected and blocked (Target: 0)
4. **Policy Adherence**: % of activities compliant with SOPs (Target: 95%)

---

## References

- **Strategy Layer**: `docs/strategy/README.md`
- **Portfolio Layer**: `docs/portfolio/README.md`
- **Process Layer**: `docs/process/README.md`
- **Evidence Layer**: `docs/evidence/README.md`
- **Traceability Index**: `docs/TRACEABILITY_INDEX.yaml`
- **Current Gates**: `scripts/gates/run_parity_gates.sh`

---

*Last updated: 2026-02-12*
