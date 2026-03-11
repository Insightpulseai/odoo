# Evidence Layer

**Purpose**: Immutable audit trail of decisions, approvals, deployments, and outcomes

**Layer Position**: Layer 6 of 7 (Strategy → Portfolio → Process → Execution → Control → **Evidence** → Integration)

---

## Purpose & Scope

This layer provides **audit-grade evidence** that validates:

- **Decisions**: Architecture Decision Records (ADRs) with rationale
- **Approvals**: Gate approvals and policy exceptions
- **Releases**: Deployment artifacts and validation evidence
- **Incidents**: Post-mortems and corrective actions
- **Timestamped Artifacts**: Immutable snapshots organized by YYYYMMDD-HHMM

**Inspired by**: SOC 2 audit requirements, ISO 9001 quality records, FDA 21 CFR Part 11 (pharma)

---

## ID Convention

**Format**: `EVID-<YYYYMMDD>-<NUMBER>`

**Examples**:
- `EVID-20260212-001` - Mailgun deprecation evidence
- `EVID-20260212-002` - Odoo.sh-grade parity gate evidence
- `EVID-20260212-003` - BIR compliance test results

---

## Directory Structure

```
evidence/
├── README.md                    # This file
├── index.yaml                   # Machine-readable evidence index
├── decisions/                   # Architecture Decision Records (ADRs)
│   ├── ADR-001-zoho-mail.md
│   ├── ADR-002-oca-parity-strategy.md
│   └── ADR-003-supabase-choice.md
├── approvals/                   # Gate approvals and exceptions
│   ├── APPR-001-architecture-review.md
│   └── APPR-002-security-exception.md
├── releases/                    # Deployment and release evidence
│   ├── RELEASE-2026-02-12-v1.2.0.md
│   └── RELEASE-2026-02-10-hotfix.md
├── incidents/                   # Incident post-mortems
│   ├── INC-001-database-outage.md
│   └── INC-002-security-breach.md
└── YYYYMMDD-HHMM/               # Timestamped evidence snapshots (existing)
    ├── mailgun-cleanup/
    │   ├── verification.md
    │   ├── before-state.txt
    │   └── after-state.txt
    └── alpha-browser-gate/
        └── gate_run_summary.json
```

---

## Evidence Types

### 1. Architecture Decision Records (ADRs)

**Purpose**: Document significant architectural decisions with context and consequences

**Format**: See [ADR template](https://github.com/joelparkerhenderson/architecture-decision-record)

**Structure**:
```markdown
---
id: ADR-001
title: Migrate from Mailgun to Zoho Mail
status: accepted
date: 2026-02-12
deciders: [platform_team, cto]
consulted: [finance_team]
informed: [all_teams]
---

# ADR-001: Migrate from Mailgun to Zoho Mail

## Context
Mailgun costs $35/month for minimal usage. Zoho Mail offers better value at $1/user/month with 5GB storage and better deliverability.

## Decision
Migrate all transactional email to Zoho Mail SMTP (smtp.zoho.com:587).

## Consequences
**Positive**:
- Cost reduction: $35/mo → $1/mo (97% savings)
- Better deliverability rates
- Unified email management

**Negative**:
- Migration effort: ~4 hours
- Requires DNS changes
- Legacy Mailgun module deprecated

## Implementation
- Portfolio initiative: PORT-2026-007
- Process: PROC-EMAIL-001
- Control: CTRL-DOC-001
- Evidence: EVID-20260212-001
```

### 2. Approval Records

**Purpose**: Document gate approvals, policy exceptions, and decision rationale

**Structure**:
```markdown
---
id: APPR-001
type: gate_approval
gate_id: CTRL-GATE-001
portfolio_initiative: PORT-2026-007
date: 2026-02-12
status: approved
approvers:
  - name: Senior Architect
    role: architect_role
    decision: approved
    timestamp: 2026-02-12T14:30:00Z
  - name: Tech Lead
    role: tech_lead_role
    decision: approved
    timestamp: 2026-02-12T15:15:00Z
---

# Architecture Review Approval: Odoo.sh-Grade Parity

## Review Summary
Architecture reviewed for scalability, security, and cost efficiency.

## Criteria Met
- ✅ Scalability: Supports 100+ concurrent users
- ✅ Security: Threat model reviewed, no critical risks
- ✅ Cost: $50/month infrastructure (within budget)
- ✅ Documentation: Architecture diagram and deployment plan complete

## Approver Comments
**Senior Architect**: "Design is solid. Recommend load testing before production."
**Tech Lead**: "Implementation plan is clear. Team has capacity."

## Conditions
- Complete load testing with 100 concurrent users
- Final security scan before production deployment
```

### 3. Release Evidence

**Purpose**: Document deployments, validation, and rollback procedures

**Structure**:
```markdown
---
id: RELEASE-2026-02-12-v1.2.0
type: release
version: v1.2.0
date: 2026-02-12
portfolio_initiatives: [PORT-2026-007, PORT-2026-008]
deployed_by: devops_engineer
validated_by: qa_team
---

# Release v1.2.0: Odoo.sh-Grade Parity Features

## Deployment Summary
- **Date**: 2026-02-12 16:00 UTC
- **Environment**: Production
- **Downtime**: 0 minutes (rolling deployment)

## Changes Included
- Feature: Alpha browser automation integration
- Feature: Odoo.sh-grade parity gates
- Fix: Email configuration migration to Zoho Mail

## Validation Results
- ✅ Smoke tests: All passed
- ✅ Integration tests: 98% passed (2 known issues in non-critical flows)
- ✅ Performance tests: Response time <200ms (p95)
- ✅ Security scan: No critical vulnerabilities

## Rollback Procedure
If issues detected:
1. Execute: `scripts/rollback.sh v1.1.5`
2. Notify: All stakeholders via Slack #incidents
3. Post-mortem: Within 48 hours

## Evidence Artifacts
- Deployment logs: `logs/deploy-20260212-1600.log`
- Test results: `docs/evidence/20260212-1600/test-results/`
- Performance metrics: `docs/evidence/20260212-1600/performance/`
```

### 4. Incident Post-Mortems

**Purpose**: Learn from failures and prevent recurrence

**Structure**:
```markdown
---
id: INC-001
type: incident
severity: critical
date_occurred: 2026-02-10T03:45:00Z
date_resolved: 2026-02-10T05:30:00Z
duration_minutes: 105
impact: Production database unavailable
affected_users: ~200
---

# INC-001: Production Database Outage

## Summary
Production database became unavailable due to disk space exhaustion.

## Timeline
- **03:45 UTC**: Monitoring alert triggered (database connection errors)
- **03:50 UTC**: On-call engineer paged
- **04:00 UTC**: Root cause identified (disk 100% full)
- **04:15 UTC**: Temporary mitigation (deleted old logs)
- **04:30 UTC**: Database service restored
- **05:30 UTC**: Full resolution (disk space monitoring implemented)

## Root Cause
Log rotation was not configured on production database server. Logs accumulated over 6 months, consuming all available disk space.

## Impact
- 200 users unable to access system for 105 minutes
- No data loss occurred
- Revenue impact: ~$500 (estimated)

## Resolution
1. Immediate: Deleted old logs, freed 20GB disk space
2. Short-term: Configured log rotation (daily, keep 7 days)
3. Long-term: Implemented disk space monitoring (alert at 80%)

## Preventive Actions
- [ ] Add disk space monitoring to all servers (Due: 2026-02-15)
- [ ] Automated log cleanup script (Due: 2026-02-17)
- [ ] Runbook: Disk space incident response (Due: 2026-02-20)
- [ ] Quarterly capacity planning review (Due: 2026-03-01)

## Lessons Learned
- **What went well**: Fast incident response, clear communication
- **What went wrong**: No disk space monitoring, manual log cleanup required
- **What we'll do differently**: Proactive monitoring, automated maintenance
```

---

## Connections to Other Layers

### Upstream (Evidence validates these layers)

- **Strategy** (`docs/strategy/`): Evidence validates strategic outcomes achieved
  - Example: `STRAT-PARITY-001` validated by `EVID-20260212-001` (80% parity achieved)

- **Portfolio** (`docs/portfolio/`): Evidence proves initiative completion
  - Example: `PORT-2026-007` validated by `EVID-20260212-002` (feature delivered)

- **Process** (`docs/process/`): Evidence shows process execution
  - Example: `PROC-DEV-001` validated by `EVID-20260212-003` (code review evidence)

- **Control** (`docs/control/`): Evidence proves control compliance
  - Example: `CTRL-GATE-001` validated by `APPR-001` (gate approval record)

### No Downstream

Evidence layer is terminal - it validates all other layers but requires none.

---

## Document Format

All evidence documents must include frontmatter:

```yaml
---
id: EVID-20260212-001
type: migration
scope: mailgun-cleanup
date: 2026-02-12
portfolio_initiative: PORT-2026-007
process_id: PROC-EMAIL-001
controls: [CTRL-DOC-001]
artifacts:
  - verification.md
  - before-state.txt
  - after-state.txt
status: complete
verified_by: platform_team
---
```

---

## Evidence Index Format

**File**: `docs/evidence/index.yaml`

**Purpose**: Machine-readable cross-reference of all evidence artifacts

**Structure**:
```yaml
evidence_records:
  - id: EVID-20260212-001
    timestamp: "20260212-1844"
    type: migration
    scope: mailgun-cleanup
    portfolio_initiative: PORT-2026-007
    process_id: PROC-EMAIL-001
    controls: [CTRL-DOC-001]
    artifacts:
      - path: docs/evidence/20260212-1844/mailgun-cleanup/
        files: [verification.md, before-state.txt, after-state.txt]
    status: complete
    verified_by: platform_team

  - id: EVID-20260212-002
    timestamp: "20260212-1848"
    type: gate_execution
    scope: alpha-browser-gate
    portfolio_initiative: PORT-2026-007
    process_id: PROC-DEV-001
    controls: [CTRL-GATE-001]
    artifacts:
      - path: docs/evidence/20260212-1848/alpha-browser-gate/
        files: [gate_run_summary.json, gate_results.txt]
    status: complete
    verified_by: qa_team
```

---

## How to Contribute

### Creating Evidence Artifacts

1. **Generate unique ID**: Use `EVID-YYYYMMDD-NNN` format
2. **Choose evidence type**: ADR, Approval, Release, Incident, or Timestamped
3. **Add frontmatter**: Include all required metadata
4. **Link to upstream layers**: Reference portfolio initiative, process, controls
5. **Preserve immutability**: Never modify evidence once created (create new version instead)
6. **Update evidence index**: Add to `docs/evidence/index.yaml`

### Evidence Best Practices

- **Immutability**: Evidence is append-only, never modified after creation
- **Completeness**: Include all artifacts needed to validate the event
- **Traceability**: Link to all upstream artifacts (portfolio, process, control)
- **Timeliness**: Create evidence artifacts immediately after event occurrence
- **Accessibility**: Store in version-controlled repository for audit access

---

## Timestamped Evidence Format

**Purpose**: Organize implementation evidence by timestamp for easy chronological access

**Naming Convention**: `YYYYMMDD-HHMM/<scope>/`

**Example**:
```
evidence/20260212-1844/
├── mailgun-cleanup/
│   ├── verification.md          # What was verified and how
│   ├── before-state.txt         # System state before change
│   ├── after-state.txt          # System state after change
│   └── screenshots/             # Visual evidence
```

**When to Use**:
- Implementation evidence (migrations, deployments)
- Gate execution results
- Test results and validation
- Configuration changes
- Any event requiring timestamped proof

---

## Success Metrics

Evidence layer effectiveness measured by:

1. **Audit Readiness**: Time to produce evidence for audit request (Target: <1 hour)
2. **Completeness**: % of portfolio initiatives with complete evidence trail (Target: 100%)
3. **Traceability**: % of evidence linked to upstream artifacts (Target: 100%)
4. **Accessibility**: % of evidence requests fulfilled from repository (Target: 100%)

---

## References

- **Strategy Layer**: `docs/strategy/README.md`
- **Portfolio Layer**: `docs/portfolio/README.md`
- **Process Layer**: `docs/process/README.md`
- **Control Layer**: `docs/control/README.md`
- **Integration Layer**: `docs/integration/README.md`
- **Traceability Index**: `docs/TRACEABILITY_INDEX.yaml`
- **Evidence Index**: `docs/evidence/index.yaml`

---

*Last updated: 2026-02-12*
