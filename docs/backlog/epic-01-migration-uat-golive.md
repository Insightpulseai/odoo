# Epic 01 — Pulser for Odoo: Migration, UAT, and Go-Live Readiness

> Translates the D365 F&O migration/go-live learning path into **Odoo-on-Azure parity and delivery work**, not D365 implementation work.

**Success criteria:** canonical migration strategy approved; target data model and import/export contract defined; UAT suite executable in CI/sandbox; go-live checklist, cutover, rollback, and readiness gates approved.

---

## Feature 1 — Migration Strategy and Data Readiness

Tags: `pulser-odoo`, `migration`, `data-management`

### Story 1.1 — Define migration strategy by source and scenario
Source systems classified by migration type (master, transactional open items, historical, reference, attachment/document); each has migration path (import/sync/staged load/archive-only), wave assignment (mock/rehearsal/cutover), owner, validation rule, rollback posture.

### Story 1.2 — Define canonical migration entity inventory
Canonical inventory for finance, project ops, CRM handoff, users/security, attachments. Each entity: source, target model, required fields, keys, dependencies, load sequence. Open-item vs historical policy explicit. Cross-company/legal-entity behavior documented.

### Story 1.3 — Define import/export strategy and tooling doctrine
Default pathways for CSV/XLSX/API/staged-DB/object-storage. Validation/staging/error-handling pattern. Retry/idempotency. Production-safe import policy.

### Story 1.4 — Define migration reconciliation and signoff model
Record-count reconciliation; control-total reconciliation for finance; sampling + exception review; signoff roles for business and technical.

---

## Feature 2 — Data Management Framework for Pulser/Odoo

Tags: `pulser-odoo`, `data-management`

### Story 2.1 — Define target data-management framework
Packages, templates, staging, validation, apply, audit steps. Entity dependency order. Partial-failure re-run. Environment-specific differences.

### Story 2.2 — Create import templates for priority entities
Templates for priority finance and project-ops entities. Required columns/keys/formats/lookups. Validation + known-failure examples.

### Story 2.3 — Support legal-entity / company-aware data movement
Company/legal-entity routing (per `docs/tenants/TENANCY_MODEL.md`). Shared vs company-specific entity behavior. Multi-company load sequencing. Cross-company misload validation.

### Story 2.4 — Define database movement and environment refresh policy
Dev/staging/prod movement. Sanitization/masking. Refresh ownership + cadence. Refresh validation checklist.

---

## Feature 3 — User Acceptance Testing and Automation

Tags: `pulser-odoo`, `testing`

### Story 3.1 — Define UAT scope and test library
Covers finance core flows + project-ops core flows + Pulser assistive flows. Each test: owner, preconditions, expected results, evidence.

### Story 3.2 — Map test library to business process model
Each major process linked to test cases. Classification: manual/semi-automated/automated. Critical-path scenarios identified. Coverage gaps listed + prioritized.

### Story 3.3 — Automate regression suite for critical scenarios
Smoke regression for critical finance + project-ops flows. Pulser role-based prompt/action smoke tests. CI can run + publish results.

### Story 3.4 — Create UAT exit criteria and defect governance
Exit criteria (severity, open defects, coverage thresholds). Defect triage. Business signoff. UAT completion evidence pack.

---

## Feature 4 — Go-Live Readiness, Cutover, and Production Controls

Tags: `pulser-odoo`, `release`

### Story 4.1 — Define go-live checklist and readiness gates
Checklist covers platform, data, app, security, AI, reporting, support readiness. Mandatory approvals. Blocking vs non-blocking explicit. Versioned.

### Story 4.2 — Define cutover plan and mock rehearsal
Cutover runbook with timeline + owners. Mock cutover completed. Timed durations captured. Lessons learned fed back.

### Story 4.3 — Define rollback and business continuity model
Rollback triggers. Rollback method by component. Business continuity fallback for finance/project workflows. Decision owner for invoke/abort named.

### Story 4.4 — Define post-go-live hypercare and stabilization
Hypercare window. Triage SLAs. Daily/weekly stabilization reporting. Exit-from-hypercare criteria.

---

## Feature 5 — Benchmark and Agent Governance

Tags: `pulser-odoo`, `benchmark`, `governance`

### Story 5.1 — Benchmark D365 F&O migration/go-live concepts to Pulser/Odoo equivalents
D365 concept → Pulser/Odoo equivalent matrix. Explicit "not applicable / substitute pattern" notes. Attached to spec bundle / SSOT.

### Story 5.2 — Define agent-aware go-live controls for Pulser
Read/recommend/draft/act capability matrix. Approval requirements. Agent logging + traceability. Disablement/fallback plan during incidents.

---

## Priority sequencing

**P0:** 1.1, 1.2, 3.1, 4.1
**P1:** 2.1, 2.2, 3.3, 4.2, 5.1
**P2:** 2.4, 4.3, 4.4, 5.2
