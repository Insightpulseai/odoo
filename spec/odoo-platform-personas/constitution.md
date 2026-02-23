# Constitution — Odoo Platform Personas & Expertise Model

## Purpose
Define the canonical role/persona and expertise model for operating the Odoo platform stack across development, QA, release management, and platform operations.

This specification establishes:
- role boundaries
- decision rights
- evidence requirements
- environment safety controls
- automation hooks
- promotion gates

It is intended to standardize both human and agent execution across the InsightPulseAI Odoo platform ecosystem.

---

## Scope

### In Scope
- Persona definitions for:
  - Developer
  - QA / Release Tester
  - Release Manager
  - Platform SRE / System Administrator
- Shared governance requirements across dev/staging/prod
- Expertise taxonomy for registry/skills mapping
- Required evidence artifacts for delivery, release, and ops
- CI/CD and promotion gate expectations
- Environment safety rules (mail catcher, staging data policy, TTL, access control)
- Agent persona alignment (human-equivalent operating contracts)

### Out of Scope
- Low-level implementation details of individual CI providers
- Vendor-specific lock-in (Odoo.sh, GitHub Actions, GitLab, etc.)
- UI workflows as the canonical process definition
- Replacing OCA parity strategy or Supabase SSOT strategy
- Runtime-specific deployment scripts (covered in implementation specs)

---

## Foundational Principles

### 1. Role Clarity over Tool Access
Personas are defined by **outcomes and decision rights**, not by who can click a button or access a UI.

### 2. Evidence-Backed Operations
Every critical activity (build, test, promotion, restore, recovery, rollback, incident response) must produce auditable evidence.

### 3. Environment Safety by Default
Non-production environments must be guarded by default-safe behavior:
- mail capture / mail suppression
- production data controls
- scoped access
- expiry / lifecycle policies

### 4. Promotion Discipline
All production promotions require explicit readiness signals:
- test results
- release validation evidence
- rollback criteria
- accountable role signoff

### 5. Automation-First, Human-Reviewable
Processes should be automatable end-to-end, while remaining understandable and reviewable by humans and agents.

### 6. Vendor-Agnostic Capability Model
The persona/expertise model must remain valid whether capabilities are delivered by Odoo.sh-like platforms or self-hosted stacks.

### 7. Supabase-First Control Plane Alignment
Where orchestration metadata, approvals, and operational state are persisted, prefer Supabase-native primitives as the control-plane SSOT.

---

## Canonical Personas

### A. Odoo Platform Developer
**Mission:** Ship code and configuration changes safely with rapid feedback loops.

**Primary Outcomes**
- Merge-ready changes with passing checks
- Deterministic dependency updates
- Debuggable builds and deployments
- Migration-safe module changes

**Decision Rights**
- Feature branch implementation changes
- Non-prod debug actions within approved scope
- Dependency proposals and compatibility fixes

**Must Not**
- Promote to production without release governance
- Bypass evidence requirements
- Alter environment safety policies unilaterally

---

### B. Odoo QA / Release Tester
**Mission:** Validate readiness of feature/staging builds under production-like conditions.

**Primary Outcomes**
- Verified acceptance criteria
- Regression risk visibility
- Reproducible defect reports
- UAT evidence and signoff recommendations

**Decision Rights**
- Test pass/fail recommendations
- Defect severity classification (per policy)
- UAT readiness recommendation for release gate

**Must Not**
- Override release approvals
- Modify production data policies
- Convert unverified observations into signoff

---

### C. Odoo Release Manager
**Mission:** Orchestrate safe promotion across environments and enforce release discipline.

**Primary Outcomes**
- Controlled dev → staging → production promotion
- Clear go/no-go decisions
- Rollback readiness
- Stakeholder communication and release traceability

**Decision Rights**
- Promotion sequencing
- Release scheduling
- Go/no-go recommendations (or decisions, per org policy)
- Rollback initiation per approved criteria

**Must Not**
- Ignore failed mandatory gates
- Promote without evidence package
- Collapse role separation where policy requires independence

---

### D. Odoo Platform SRE / System Administrator
**Mission:** Maintain platform availability, performance, recoverability, and operational safety.

**Primary Outcomes**
- Healthy runtime and infrastructure posture
- Verified backups and restores
- Monitoring/alerting coverage
- Recovery and incident response readiness

**Decision Rights**
- Runtime operational changes under ops policy
- Backup/restore drills
- Performance tuning actions
- Incident mitigation actions

**Must Not**
- Deploy application changes outside release governance
- Skip recovery validation
- Disable controls without documented exception

---

## Shared Governance Layer (Applies to All Personas)

### Environment Categories
- **Development**: fast feedback, isolated work, default-safe external effects disabled or sandboxed
- **Staging**: production-like validation, controlled data use, time-bounded lifecycle
- **Production**: highest control level, strict promotion gates, auditability required

### Mandatory Safety Controls
- Non-prod email suppression or catcher
- Non-prod external integration safeguards (sandbox endpoints / blocked sends)
- Least-privilege access to logs, shell, and runtime controls
- Branch/environment lifecycle and TTL policies
- Documented data refresh and masking rules for staging (if using prod-derived data)

### Evidence Requirements (Minimum)
- Build/test results
- Validation summary (QA/UAT)
- Promotion approval records
- Rollback plan / criteria
- Ops health signals for production change windows

---

## Canonical Expertise Taxonomy

### Core Expertise Domains
- `odoo.devx.ci_cd`
- `odoo.devx.debugging`
- `odoo.qa.automation`
- `odoo.qa.staging_validation`
- `odoo.release.orchestration`
- `odoo.release.governance`
- `odoo.sre.backup_recovery`
- `odoo.sre.monitoring_performance`
- `odoo.sre.network_dns_mail`
- `odoo.platform.environment_governance`

### Taxonomy Rules
- Persona ≠ Expertise
- A persona may require multiple expertise domains
- A single expertise domain may be shared across multiple personas
- Skills/agents should map to expertise domains, then to persona-operating contracts

---

## Control Gates (Normative)

### Gate G1 — Build Integrity
Required before QA validation:
- branch build succeeds
- required automated checks pass
- logs are retained and inspectable

### Gate G2 — Validation Readiness
Required before staging acceptance:
- acceptance criteria mapped
- known defects documented
- test evidence attached

### Gate G3 — Promotion Readiness
Required before production promotion:
- test evidence package complete
- rollback criteria and rollback path confirmed
- release notes / impact summary prepared
- accountable signoff recorded

### Gate G4 — Post-Deploy Operational Confirmation
Required after production promotion:
- health checks / runtime checks green
- key monitoring signals normal
- incident fallback/rollback timer defined (per policy)

---

## Exceptions and Escalation
Any deviation from this constitution requires:
1. documented exception
2. accountable approver
3. risk statement
4. expiry/rollback of exception
5. post-event review

---

## Success Criteria
This constitution is successful when:
- persona responsibilities are unambiguous
- releases become more predictable
- evidence exists for every critical step
- environment incidents decrease from policy violations
- agent automations align to explicit role contracts
