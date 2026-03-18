# PRD: Azure-Native OdooOps Pipeline Baseline

## 1. Summary

Build a clean baseline Azure DevOps pipeline system for an Azure-native Odoo operations platform.

The product is not "just CI/CD."
It is the delivery and operations control plane for:

- shared platform services
- Odoo runtime delivery
- deployment stamps
- staging and promotion
- backups and recovery validation
- Git-based module delivery
- controlled analytics/reporting access
- quality governance for AI and tax/compliance specialist agents

This baseline must support both:
- SMB multitenant deployment stamps
- more isolated enterprise or regulated deployment stamps

---

## 2. Problem

Current pipeline behavior is not trustworthy as a release system.

Observed issues:
- pipeline definitions and YAML bindings are unclear
- bootstrap failures can invalidate run results across unrelated commits
- infra delivery and runtime delivery concerns are mixed
- hosted vs self-hosted agent policy is not clearly encoded
- quality/eval gates are not yet first-class release controls
- staging, promotion, and backup/restore validation are not yet expressed as product-grade pipeline capabilities

Meanwhile, market benchmarks in managed Odoo operations make these capabilities first-class:
- create instance
- create staging instance
- deploy from Git
- backup and recovery operations
- server access lockdown
- read-only reporting access
- migration workflows

The target system needs a cleaner baseline than generic YAML sprawl.

---

## 3. Goals

### Primary goals

1. Establish a clean, deterministic Azure DevOps pipeline topology.
2. Separate PR validation, infrastructure delivery, runtime delivery, and quality governance.
3. Support shared control plane plus deployment stamp rollout.
4. Make staging, promotion, backup validation, and Git-based module rollout first-class pipeline surfaces.
5. Encode hosted-first agent policy with self-hosted only where private reachability is required.
6. Provide a baseline that can later support Odoo, Databricks, Foundry, Power BI, and TaxPulse quality gates without re-architecture.

### Secondary goals

1. Reduce pipeline ambiguity and bootstrap drift.
2. Make production changes environment-gated and auditable.
3. Support progressive rollout with rings and feature flags.
4. Produce machine-readable evidence for runtime and release health.

---

## 4. Non-Goals

1. This PRD does not redesign the full Azure landing zone.
2. This PRD does not define tenant business logic or billing.
3. This PRD does not implement autonomous tax/compliance decisioning.
4. This PRD does not replace application-specific test suites.
5. This PRD does not require every workload to use self-hosted runners.

---

## 5. Users

### Primary users

- platform operator
- release operator
- Odoo runtime owner
- infrastructure owner
- AI/agent quality owner

### Secondary users

- implementation partner
- analytics/reporting integrator
- tenant operations lead

---

## 6. Product Principles

1. **Hosted by default**
   Use Microsoft-hosted agents unless a job explicitly requires private reachability or custom image/tooling.

2. **Pipelines reflect operating planes, not repo accidents**
   Shared platform, stamp delivery, runtime delivery, and quality governance are separate concerns.

3. **One deployment unit at a time**
   Stamp delivery targets one stamp or one bounded stamp batch, never all stamps by default.

4. **Promotion is a product capability**
   Staging, smoke validation, backup verification, and environment promotion are baseline surfaces.

5. **Git is the delivery source of truth**
   Module rollout, spec changes, and infrastructure changes are repo-driven.

6. **Evidence over intuition**
   Deployments, benchmarks, and health validation must emit auditable artifacts.

---

## 7. Target Product Surface

The baseline product must support these operator-facing capabilities:

1. Create shared platform release
2. Create or update one deployment stamp
3. Build and promote Odoo runtime artifacts
4. Create staging clone / staging rollout
5. Deploy modules from Git-controlled source
6. Run backup and restore validation
7. Lock down runtime/server access policy
8. Provision read-only analytics/reporting access
9. Migrate workload from legacy/on-prem/Odoo.sh-like sources
10. Run benchmark/eval governance before protected releases

---

## 8. Pipeline Topology

The baseline consists of five top-level pipelines.

### 8.1 `ci-validation`

Purpose:
- PR validation only

Responsibilities:
- YAML/template validation
- docs/spec/SSOT validation
- lint
- unit tests
- Odoo module tests that do not require private-network execution
- benchmark smoke tests
- artifact publication for validation

### 8.2 `platform-shared-delivery`

Purpose:
- deploy shared control-plane and shared platform services

Responsibilities:
- shared network edge
- shared WAF/front door surfaces
- shared identity/config foundations
- shared observability
- shared service connections/config references
- shared platform infra rollout

### 8.3 `stamp-delivery`

Purpose:
- deploy or update one deployment stamp

Responsibilities:
- stamp infra
- stamp-scoped runtime resources
- stamp routing metadata
- stamp health validation
- stamp evidence publication

Inputs:
- `stamp_id`
- `environment`
- `region`
- `ring`
- optional `tenant_segment`

### 8.4 `runtime-delivery`

Purpose:
- build, publish, migrate, and deploy runtime artifacts

Responsibilities:
- Odoo image build
- package/runtime tests
- push image/artifact
- migration job execution
- ACA runtime rollout
- smoke checks
- rollback metadata

### 8.5 `quality-governance`

Purpose:
- non-release quality control

Responsibilities:
- benchmark runs
- Foundry evals
- tax/compliance custom evaluators
- red-team/adversarial runs
- production trace replay
- regression scorecards
- evidence-pack publication

---

## 9. Functional Requirements

### FR-001 Pipeline separation
The system shall separate PR validation, shared platform delivery, stamp delivery, runtime delivery, and quality governance into distinct Azure DevOps pipelines.

### FR-002 Hosted-first execution
The system shall use Microsoft-hosted `ubuntu-latest` by default for validation and non-private jobs.

### FR-003 Exception-based self-hosted execution
The system shall allow self-hosted or Managed DevOps Pool execution only for stages/jobs that require:
- private endpoint reachability
- internal-only validation targets
- custom runner image/tooling
- VNet-constrained resources

### FR-004 Environment-gated deployments
The system shall use Azure DevOps Environments for protected deployments with approvals/checks.

### FR-005 Deployment locking
The system shall support exclusive lock or sequential deployment behavior for protected environments where overlapping runs are unsafe.

### FR-006 Stamp-scoped rollout
The system shall model deployment stamps as first-class deployment units.

### FR-007 Staging support
The system shall support staging rollout and staged validation before protected promotion.

### FR-008 Git-based module delivery
The system shall support Git-native delivery of Odoo addons/modules as part of runtime delivery.

### FR-009 Backup/restore validation
The system shall support backup creation, restore validation, and release evidence for protected environments.

### FR-010 Runtime smoke validation
The system shall perform post-deploy smoke checks for runtime and route health.

### FR-011 Reporting access provisioning
The system shall support a controlled read-only reporting access path for analytics consumers.

### FR-012 Migration support
The system shall support migration workflows from legacy/self-hosted/Odoo.sh-like estates into the target platform.

### FR-013 Evidence publication
Each pipeline shall publish machine-readable and human-readable evidence sufficient for audit and rollback analysis.

### FR-014 Quality gates
Protected releases for AI/tax/compliance features shall be blocked if benchmark or evaluator thresholds are not met.

---

## 10. Non-Functional Requirements

### NFR-001 Determinism
Pipeline topology, template paths, and environment bindings must be deterministic and version-controlled.

### NFR-002 Auditability
Every protected deployment must produce sufficient logs, artifacts, and status evidence for later inspection.

### NFR-003 Isolation
The pipeline system must support both shared and selectively isolated deployment models.

### NFR-004 Scalability
The design must support growth from shared SMB stamps to more isolated enterprise stamps.

### NFR-005 Operability
Pipeline failures must be diagnosable at the stage/job/task level without relying on tribal knowledge.

### NFR-006 Security
Secrets must be sourced from controlled secret surfaces, not hardcoded pipeline values.

### NFR-007 Recoverability
Protected rollout must support rollback-safe behavior and validated recovery paths.

---

## 11. Environment Model

### Shared environments
- shared-dev
- shared-staging
- shared-prod

### Stamp environments
- stamp-dev
- stamp-staging
- stamp-prod

Policy:
- dev: no manual approval by default
- staging: optional approval/checks
- prod: required approval/checks and protected deployment behavior

---

## 12. Agent Pool Policy

### Default
- `ubuntu-latest`

### Exceptions
Use self-hosted or Managed DevOps Pool only where justified by:
- private networking
- internal-only endpoints
- custom image/tooling
- restricted deployment access patterns

This decision must be stage/job-specific, not assumed pipeline-wide.

---

## 13. Release Flow

### Standard PR flow
1. `ci-validation`
2. merge after policy checks pass

### Shared platform release flow
1. validate
2. deploy shared-dev
3. validate
4. deploy shared-staging
5. validate
6. deploy shared-prod
7. validate

### Stamp release flow
1. resolve target stamp metadata
2. validate stamp
3. deploy infra
4. validate infra
5. deploy runtime
6. validate runtime
7. publish evidence

### Runtime release flow
1. build
2. test
3. push artifact
4. migrate
5. deploy
6. smoke
7. publish rollback metadata

### Quality flow
1. load dataset
2. deterministic eval
3. model/agent eval
4. domain-specific eval
5. scorecard
6. evidence pack
7. alert or block on regression

---

## 14. Success Metrics

### Pipeline health
- docs-only PR validation becomes a reliable fast signal
- no recurring blanket fast-fail bootstrap pattern across unrelated commits
- protected deployments have deterministic approval/check behavior

### Delivery health
- shared platform and stamp deployments are independently runnable
- runtime delivery can proceed without coupling to unrelated infra rollout
- staging and promotion are validated, not implied

### Quality health
- benchmark/eval artifacts are emitted for protected AI/tax releases
- regression can block promotion where policy requires it

---

## 15. Risks

1. Pipeline definitions in Azure DevOps may still point to unexpected YAML files.
2. Variable groups or service connections may fail before job logic executes.
3. A blanket hosted-agent migration may be invalid for stages requiring private reachability.
4. Overloading one pipeline with both infra and runtime responsibilities will recreate ambiguity.
5. Tax/compliance quality gates can become performative unless backed by deterministic evaluators and evidence packs.

---

## 16. Open Questions

1. Which YAML file is currently bound to `ci-validation`?
2. Which deploy stages genuinely require self-hosted/private runner reachability?
3. Which environments already exist in Azure DevOps and which still need to be created?
4. What is the canonical metadata contract for tenant-to-stamp routing?
5. Which runtime smoke checks are mandatory before promotion?

---

## 17. MVP Scope

### Include in baseline MVP
- `ci-validation`
- `platform-shared-delivery`
- `stamp-delivery`
- `runtime-delivery`
- `quality-governance`
- hosted-first policy
- environment-gated deploys
- deterministic template structure
- stamp metadata contract
- evidence publication

### Exclude from baseline MVP
- autonomous tenant-by-tenant rollout optimization
- advanced tenant billing orchestration
- fully automated tax/compliance decision execution
- broad marketplace-style commercial packaging
