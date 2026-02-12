# Process Layer

**Purpose**: Define how work gets done - governance, operations, controls, and business processes

**Layer Position**: Layer 3 of 7 (Strategy → Portfolio → **Process** → Execution → Control → Evidence → Integration)

---

## Purpose & Scope

This layer documents **how the organization operates** through:

- **Governance**: Policies, decision rights, escalation paths
- **Operations**: Day-to-day workflows and runbooks
- **Process Hierarchy**: L4 (core) → L5 (operations) → L6 (controls)
- **SIPOC**: Supplier-Input-Process-Output-Customer diagrams
- **RACI**: Responsibility Assignment Matrix

---

## ID Convention

**Format**: `PROC-<DOMAIN>-<NUMBER>`

**Examples**:
- `PROC-DEV-001` - Software development process
- `PROC-QA-002` - Quality assurance process
- `PROC-DEPLOY-001` - Deployment process
- `PROC-AR-012` - Accounts Receivable process

---

## Directory Structure

```
process/
├── README.md                    # This file
├── hierarchy.yaml               # Machine-readable process hierarchy
├── governance/                  # Policies, decision rights (migrated from /docs/governance)
│   └── BUGBOT_REVIEW.md
├── operations/                  # Day-to-day workflows (consolidated from /docs/operations + /docs/ops)
│   ├── main/                    # Current operational docs
│   └── legacy/                  # Deprecated ops docs
├── runbooks/                    # Procedural guides (migrated from /docs/runbooks)
├── l4-core/                     # Core business processes (BPMN-compatible)
│   ├── order-to-cash.md
│   ├── procure-to-pay.md
│   └── record-to-report.md
├── l5-operations/               # Operational processes
│   ├── incident-response.md
│   └── change-management.md
├── l6-controls/                 # Control processes
│   ├── code-review.md
│   └── deployment-approval.md
├── sipoc/                       # Supplier-Input-Process-Output-Customer diagrams
│   └── dev-process-sipoc.md
└── raci/                        # Responsibility Assignment Matrices
    └── deployment-raci.md
```

---

## Process Hierarchy (SAP Signavio-inspired)

### Level 4: Core Business Processes (Strategic)

- **Order-to-Cash**: Customer acquisition → order fulfillment → payment collection
- **Procure-to-Pay**: Vendor selection → purchase → payment processing
- **Record-to-Report**: Transaction recording → financial close → reporting
- **Hire-to-Retire**: Recruitment → onboarding → offboarding

### Level 5: Operational Processes (Tactical)

- **Incident Response**: Alert → triage → resolution → post-mortem
- **Change Management**: Request → approval → implementation → validation
- **Release Management**: Build → test → deploy → monitor
- **Vendor Management**: Onboarding → performance review → contract renewal

### Level 6: Control Processes (Detailed)

- **Code Review**: PR submission → automated checks → peer review → approval
- **Deployment Approval**: Build → security scan → approval gate → production deploy
- **Access Control**: Request → approval → provisioning → audit
- **Risk Assessment**: Identify → analyze → mitigate → monitor

---

## Connections to Other Layers

### Upstream (Process supports these layers)

- **Strategy** (`docs/strategy/`): Processes enable strategic capabilities
  - Example: `STRAT-CAP-AI` enabled by `PROC-AI-001`

- **Portfolio** (`docs/portfolio/`): Initiatives execute through processes
  - Example: `PORT-2026-007` → `PROC-DEV-001` + `PROC-QA-002` + `PROC-DEPLOY-001`

### Downstream (Process requires these layers)

- **Execution** (code, scripts, workflows): Processes automated through code
  - Example: `PROC-DEPLOY-001` → `.github/workflows/deploy-production.yml`

- **Control** (`docs/control/`): Processes enforced through controls
  - Example: `PROC-DEV-001` → `CTRL-GATE-001` (Architecture review gate)

### Validation (Process verified by these layers)

- **Evidence** (`docs/evidence/`): Process execution leaves audit trail
  - Example: `PROC-DEPLOY-001` → `EVID-20260212-001` (Deployment evidence)

---

## Document Format

All process documents must include frontmatter:

```yaml
---
id: PROC-DEV-001
type: process
name: Software Development Process
level: L5
status: active
owner: engineering_team
strategy_link: STRAT-CAP-AI
portfolio_initiatives: [PORT-2026-007, PORT-2026-008]
controls: [CTRL-GATE-001, CTRL-SEC-004]
execution:
  - .github/workflows/ci.yml
  - scripts/gates/run_parity_gates.sh
evidence_requirements:
  - git_commit_history
  - pr_reviews
  - test_results
---
```

---

## SIPOC Format

**Supplier-Input-Process-Output-Customer** diagrams clarify process boundaries:

```yaml
sipoc:
  process_name: Software Development
  process_id: PROC-DEV-001
  suppliers:
    - Product team (requirements)
    - Design team (UI specs)
  inputs:
    - User stories with acceptance criteria
    - Design mockups and tokens
  process_steps:
    - Requirements analysis
    - Technical design
    - Implementation
    - Testing
    - Code review
    - Deployment
  outputs:
    - Working software
    - Documentation
    - Test evidence
  customers:
    - End users
    - Product team (feedback loop)
```

---

## RACI Matrix Format

**Responsible-Accountable-Consulted-Informed** clarifies decision rights:

```yaml
raci:
  process_name: Deployment Process
  process_id: PROC-DEPLOY-001
  activities:
    - activity: Build artifact
      responsible: CI/CD system
      accountable: Engineering lead
      consulted: [DevOps team]
      informed: [Product team]
    - activity: Security scan
      responsible: Security scanner
      accountable: Security team
      consulted: [Engineering lead]
      informed: [Compliance team]
    - activity: Production deploy
      responsible: DevOps engineer
      accountable: Engineering lead
      consulted: [Product team]
      informed: [Executive team]
```

---

## How to Contribute

### Creating New Process Documentation

1. **Identify level**: L4 (core), L5 (operations), L6 (controls)
2. **Generate unique ID**: Use `PROC-<DOMAIN>-<NUMBER>` format
3. **Add frontmatter**: Include all required metadata
4. **Create SIPOC**: Define process boundaries clearly
5. **Create RACI**: Clarify decision rights
6. **Link to portfolio**: Reference initiatives that use this process
7. **Document automation**: Reference execution artifacts (scripts, workflows)
8. **Update traceability index**: Add to `docs/TRACEABILITY_INDEX.yaml`

### Reviewing Process Documentation

- **Clarity**: Can someone unfamiliar execute this process?
- **Completeness**: Are all decision points and escalation paths documented?
- **Automation**: What can be automated vs must remain manual?
- **Controls**: What gates/checkpoints enforce process compliance?
- **Evidence**: What audit trail does this process produce?

---

## Key Processes (Current State)

### L4 Core Processes

- **Order-to-Cash**: Customer inquiry → quote → order → fulfillment → invoice → payment
- **Procure-to-Pay**: Requisition → approval → PO → receipt → invoice → payment
- **Record-to-Report**: Transaction entry → reconciliation → close → financial statements

### L5 Operational Processes

- **Software Development** (`PROC-DEV-001`): Requirements → design → implementation → testing → deployment
- **Quality Assurance** (`PROC-QA-002`): Test planning → execution → defect tracking → validation
- **Deployment** (`PROC-DEPLOY-001`): Build → security scan → approval → production deploy → monitoring

### L6 Control Processes

- **Code Review** (`PROC-CTRL-001`): PR submission → automated checks → peer review → approval
- **Architecture Review** (`PROC-CTRL-002`): Design proposal → review gate → approval/rejection
- **Security Approval** (`PROC-CTRL-003`): Security scan → vulnerability assessment → remediation/approval

---

## Governance Framework

### Decision Rights

| Decision Type | Accountable | Consulted | Informed |
|--------------|-------------|-----------|----------|
| Strategic direction | Leadership team | All teams | Company-wide |
| Portfolio prioritization | Product team | Engineering, Finance | All teams |
| Technical architecture | Engineering lead | Architects, DevOps | Product team |
| Process changes | Process owner | Affected teams | All teams |

### Escalation Paths

1. **Operational issues**: Team lead → Department head → Executive team
2. **Technical blockers**: Engineer → Tech lead → Engineering lead → CTO
3. **Process exceptions**: Process owner → Governance committee → Executive sponsor

---

## Success Metrics

Process layer effectiveness measured by:

1. **Process Compliance**: % of activities following documented process (Target: 95%)
2. **Automation Rate**: % of process steps automated (Target: 70%)
3. **Cycle Time**: Average time from start to completion (varies by process)
4. **Defect Escape Rate**: Issues found in production vs testing (Target: <5%)

---

## References

- **Strategy Layer**: `docs/strategy/README.md`
- **Portfolio Layer**: `docs/portfolio/README.md`
- **Control Layer**: `docs/control/README.md`
- **Evidence Layer**: `docs/evidence/README.md`
- **Traceability Index**: `docs/TRACEABILITY_INDEX.yaml`
- **Process Hierarchy**: `docs/process/hierarchy.yaml`

---

*Last updated: 2026-02-12*
