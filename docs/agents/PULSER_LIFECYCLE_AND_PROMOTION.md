# Pulser Lifecycle and Promotion

## Purpose

This document defines the canonical lifecycle, promotion stages, and publish gates for **Pulser** assistant variants.

It answers three questions:

1. What lifecycle stage is a Pulser variant in?
2. What evidence is required to move forward?
3. What must be true before a Pulser variant is promoted to a stable endpoint?

This document is about **readiness and promotion**.
It complements `docs/agents/PULSER_TAXONOMY.md`, which defines classification and naming.

---

## Scope

This lifecycle applies to:
- Pulser for Odoo
- Ask Pulser
- Pulser consulting / RAG surfaces
- messaging add-on assistant surfaces
- future Microsoft 365 / Outlook Pulser variants
- Pulser operational modes that require governed promotion

It does not redefine the broader internal agent factory lifecycle except where those controls are inherited by Pulser deployments.

---

## Relationship to taxonomy

Use `PULSER_TAXONOMY.md` to answer:
- what class of assistant this is
- what mode it runs in
- what access posture it has
- what capabilities it exposes

Use this document to answer:
- whether it is still in design/build
- whether it is safe to promote
- what evidence is missing
- what approvals are required

---

## Canonical lifecycle model

Pulser variants move through a governed stage model from intake to maturity.

### Stage progression

| Stage ID | Name | Meaning | Typical evidence |
|---|---|---|---|
| S01 | Intake | Assistant concept / blueprint submitted | Passport exists |
| S02 | Design | Contract and interface defined | Contract/manifest exists |
| S03 | Build | Implementation complete | Code/config present |
| S04 | Unit Test | Core evals and unit checks pass | Eval threshold met |
| S05 | Integration Test | Cross-system integration validated | Integration evidence |
| S06 | Eval Sandbox | Sandbox evaluation executed | Sandbox eval results |
| S07 | Judge Review | Judge agent / governance review signed | Judge sign-off |
| S08 | Canary | Shadow or limited exposure verified | Canary metrics |
| S09 | Staging | Pre-production verification complete | Staging evidence |
| S10 | Production | Live production task processing enabled | Production deployment |
| S11 | Scaling | Stable production behavior sustained | 7-day stability |
| S12 | Hardening | Security and edge-case hardening complete | Hardening evidence |
| S13 | Mature | Final stable operating state | 30-day incident-free evidence |
| S14 | Deprecation Notice | Sunset lifecycle begins | Deprecation record |

---

## Stage intent

### S01 Intake
Used when a Pulser variant is proposed but not yet formally defined.

Minimum expectation:
- identity of the variant is known
- intended surface is known
- owner is known

### S02 Design
Used when the variant has a formal contract.

Minimum expectation:
- interface and runtime contract defined
- tools and knowledge bindings identified
- public naming aligned to Pulser policy

### S03 Build
Used when implementation exists but promotion evidence is incomplete.

Minimum expectation:
- runtime configuration exists
- tool bindings exist
- surface wiring exists where applicable

### S04 Unit Test
Used when the variant has a deterministic baseline.

Minimum expectation:
- evaluation baseline exists
- core task adherence is measurable
- failing behavior is visible and actionable

### S05 Integration Test
Used when the variant interacts with external systems and those interactions are validated.

Examples:
- Odoo runtime calls
- knowledge retrieval
- identity integration
- add-on bridge behavior

### S06 Eval Sandbox
Used for isolated evaluation before broader exposure.

Typical purpose:
- catch regression or unsafe behavior
- validate grounding behavior
- validate tool routing

### S07 Judge Review
Used when governance sign-off is required before traffic expansion.

Typical reviewers:
- platform
- security
- domain owner
- judge agent layer

### S08 Canary
Used for low-risk limited rollout or shadow validation.

Typical purpose:
- observe real-world performance
- confirm no major drift from eval expectations

### S09 Staging
Used for pre-production verification under production-like conditions.

### S10 Production
Used when the assistant variant is approved for live use.

### S11 Scaling
Used when the variant demonstrates stable live behavior across a sustained period.

### S12 Hardening
Used to close remaining security, abuse, safety, observability, or reliability gaps.

### S13 Mature
Used for long-running stable assistants with bounded incident risk.

### S14 Deprecation Notice
Used when a Pulser variant is being sunset, replaced, or migrated.

---

## Exit criteria model

Each stage should have explicit exit evidence before promotion.

### Required artifacts by early stage

| Stage | Required artifact / evidence |
|---|---|
| S01 Intake | Passport or equivalent blueprint artifact |
| S02 Design | Contract / manifest exists |
| S03 Build | Implemented runtime/config/tool wiring |
| S04 Unit Test | Eval passes threshold (baseline: 0.8) |
| S07 Judge Review | Judge sign-off recorded |

---

## Publish gates

No Pulser variant should be promoted to a stable endpoint unless the publish gates are satisfied.

### 1. Evaluation gates

| Gate | Requirement |
|---|---|
| Eval dataset | Required |
| Minimum test cases | At least 10 |
| Task adherence | Must pass |
| Safety eval | Must pass |
| Groundedness eval | Required when grounding is used |
| Model pinning | Required for deterministic baselines |
| Router avoidance in eval baseline | Required where deterministic baseline is expected |

### 2. Tracing gates

| Gate | Requirement |
|---|---|
| Trace enabled | Required |
| Application Insights connected | Required |
| Span naming convention | Required |

### 3. Tool compliance gates

| Gate | Requirement |
|---|---|
| Allowlist compliance | All tools must be allowlisted |
| Auth mode declaration | Required per tool |
| Approval mode declaration | Required |

### 4. Identity gates

| Gate | Requirement |
|---|---|
| Entra agent identity | Required |
| Least-privilege RBAC | Required |
| Identity reassignment on publish | Required when moving from shared/dev to promoted runtime |

### 5. Knowledge gates

| Gate | Requirement |
|---|---|
| KB binding declared | Required when knowledge grounding is used |
| ACL enforcement | Required for permission-aware retrieval |

### 6. Ownership gates

| Gate | Requirement |
|---|---|
| Owner declared | Required |
| Owner repo declared | Required |
| Version pinned | Required |

---

## Promotion flow by environment

### Dev

| Environment | Required gates | Auto-promote | Approval |
|---|---|---|---|
| Dev | Eval dataset exists; trace enabled | Yes | None |

### Staging

| Environment | Required gates | Auto-promote | Approval |
|---|---|---|---|
| Staging | Eval pass; tools allowlist pass; identity configured | No | Platform team |

### Production

| Environment | Required gates | Auto-promote | Approval |
|---|---|---|---|
| Production | All gates pass; safety eval pass; groundedness pass | No | Platform + Security team |

### Approval model

At minimum:
- staging requires platform approval
- production requires platform and security approval

If future governance docs define a stricter approval matrix, that stricter matrix wins.

---

## Pulser-specific promotion interpretation

Not all Pulser variants need the same depth of promotion evidence.

### Public advisory surfaces

Examples: Ask Pulser, public docs-grounded assistants

Priority gates:
- safety
- grounding quality
- traceability
- public-safe branding
- explicit exclusion of sensitive tools

### Authenticated operational surfaces

Examples: Pulser for Odoo

Priority gates:
- identity
- tool allowlist
- confirmation-before-mutation behavior
- auditability
- Odoo/live-data integration quality

### Messaging add-on surfaces

Examples: Gmail / Outlook assistant surfaces

Priority gates:
- identity and account binding
- least privilege
- narrow scope of actions
- connector/bridge reliability
- tenant-safe data handling

### Consulting / RAG surfaces

Examples: PrismaLab Pulser

Priority gates:
- knowledge quality
- grounding fidelity
- routing / CTA correctness
- public-safe answer boundaries

---

## Current Pulser variant readiness

| Variant | Current stage | Next gate | Key blocker |
|---------|--------------|-----------|-------------|
| Pulser ERP (Foundry) | S03 Build | S04 Unit Test | Eval dataset + `ipai_mail_plugin` backend |
| Ask Pulser (public) | S10 Production | S11 Scaling | Operational — monitor stability |
| Pulser PrismaLab | S10 Production | S11 Scaling | Operational — deployed to ACA |
| Pulser Gmail | S03 Build | S04 Unit Test | Backend bridge + GCP project |
| Pulser Outlook | S01 Intake | S02 Design | Billing role + M365 subscription |
| Pulser M365 | S01 Intake | Deferred | Package type unresolved |

---

## Recommended status language

| Status phrase | Meaning |
|---|---|
| Concept | Intake not yet promoted beyond S01 |
| Defined | Design complete, not yet production-ready |
| Build lane | Implemented but missing full eval/promotion evidence |
| Validation lane | In test, sandbox, judge review, or canary |
| Production | Live and approved |
| Mature | Stable and hardened |
| Deprecated | Sunset path has begun |

Avoid vague labels like "almost done", "basically prod", "ready-ish". Prefer explicit stage references.

---

## Operational rules

1. **No stable publish without gates** — No Pulser variant should be treated as stably published unless the publish gates are satisfied.

2. **Taxonomy and lifecycle are separate** — A variant can be clearly classified even if it is still early-stage.

3. **Public brand does not override readiness** — A Pulser-branded assistant is not automatically production-ready.

4. **Higher authority surfaces require stronger evidence** — Public advisory assistants need strong safety/grounding. Authenticated operational assistants need even stronger identity, tool, and audit controls.

5. **Promotion state should be explicit in docs** — Any architecture or launch doc referencing a Pulser variant should state its lifecycle stage.

---

## Required references for each Pulser variant

Each Pulser variant should have a documented linkage to:
- taxonomy entry (`PULSER_TAXONOMY.md`)
- owning runtime/config or workflow anchor
- current stage
- missing gates
- approval owner
- latest validation evidence location

---

## Canonical summary

Pulser readiness is governed by:
- a 14-stage lifecycle (S01–S14)
- explicit publish gates (evaluation, tracing, tools, identity, knowledge, ownership)
- environment-specific promotion controls (dev → staging → production)
- approval requirements for staging and production

Taxonomy answers **what Pulser is**.
Lifecycle and promotion answer **whether a Pulser variant is ready to trust, promote, and scale**.
