# Epic 04 — Pulser for Odoo: Azure Pipelines and GitHub Delivery Integration

> Delivery-plane / CI-CD / release-governance backlog. **Not** an Odoo business-module backlog.

**Success criteria:** canonical GitHub ↔ Azure Pipelines integration model approved; PR validation + branch policy model defined; pipeline template baseline established; environment promotion + release controls defined; GitHub Actions vs Azure Pipelines boundary documented.

**Doctrine anchor:** GitHub remains code and pull-request truth. Azure Pipelines is used as a governed validation and release surface where it adds value for PR validation, environment promotion, enterprise controls, or cross-platform execution. Must not create duplicate or conflicting automation with GitHub Actions.

**Reference repos:**
- Microsoft Learn: "Build GitHub repositories" (Azure Pipelines + GitHub)
- `microsoft/azure-pipelines-yaml` — official YAML examples + templates
- `Azure/pipelines` — GitHub Action to trigger Azure Pipelines from workflows
- `microsoft/azure-pipelines-agent` — official agent/runtime repo for runner behavior

---

## Feature 1 — Plan GitHub and Azure Pipelines Integration Model

Tags: `pulser-odoo`, `azure-pipelines`, `github`, `ci-cd`

### Story 1.1 — Define canonical GitHub-to-Azure-Pipelines operating model
GitHub source-of-truth role. Azure Pipelines role. Trigger model (PRs, commits, promotions). Ownership + access boundaries.

### Story 1.2 — Define PR validation strategy for GitHub repositories
Required PR validation pipeline classes. Trigger conditions (PRs + branch pushes). Required status checks. Failure handling + rerun policy.

### Story 1.3 — Define coexistence strategy for GitHub Actions and Azure Pipelines
Responsibilities split: GH Actions vs AzDO. Duplication rules. Trigger chaining/handoff model. Exception policy. (Aligns with `ssot/governance/platform-authority-split.yaml`: GH Actions = CI + docs/web deploy; AzDO = Odoo/Databricks/infra deploy.)

---

## Feature 2 — Create Azure Pipelines Template Baseline

Tags: `pulser-odoo`, `azure-pipelines`, `ci-cd`

### Story 2.1 — Define canonical Azure Pipelines YAML structure
Canonical file layout. Template layering. Stage/job/step naming. Variable + parameter conventions.

### Story 2.2 — Create reusable CI pipeline templates
Templates for lint/test/build. Odoo-specific validation. Infra/config validation. Template input contract.

### Story 2.3 — Create reusable release and promotion templates
Promotion stages standardized. Environment approval points. Artifact/version handoff. Rollback hooks.

---

## Feature 3 — Implement PR, Branch, and Environment Controls

Tags: `pulser-odoo`, `azure-pipelines`, `governance`

### Story 3.1 — Define branch protection and pipeline-required checks
Required checks per branch class. Merge-blocking conditions. Solo-maintainer exception policy. Auto-merge posture.

### Story 3.2 — Define environment promotion model
Dev → staging → prod promotion path. Manual vs automated approval points. Artifact immutability. Audit trail requirements.

### Story 3.3 — Define release evidence and traceability model
Required evidence per release. PR/build/artifact/environment traceability. Evidence retention + location. Exception handling.

---

## Feature 4 — Integrate Azure Pipelines with GitHub Workflows and Events

Tags: `pulser-odoo`, `azure-pipelines`, `github`

### Story 4.1 — Define when GitHub should trigger Azure Pipelines
Trigger events. Supported handoff patterns. Secret/token boundary. Non-approved chaining patterns.

### Story 4.2 — Assess Azure/pipelines GitHub Action for controlled handoff
Applicable vs non-applicable use cases. Required inputs/secrets/controls. Governance implications.

### Story 4.3 — Define webhook/API integration posture for pipeline orchestration
API/webhook-trigger posture. Auth model. Retry/idempotency. Auditability.

---

## Feature 5 — Standardize Agents, Runners, and Execution Surfaces

Tags: `pulser-odoo`, `azure-pipelines`, `runners`

### Story 5.1 — Define hosted vs self-hosted runner strategy
Hosted vs self-hosted selection rules. Sensitive workload rules. Capacity + concurrency expectations. OS/runtime coverage.

### Story 5.2 — Define agent and worker lifecycle management
Update policy. Registration/de-registration. Health monitoring. Failure/replacement procedures.

### Story 5.3 — Define containerized build/test execution posture
Container vs non-container use cases. Image provenance rules. Cache/artifact strategy.

---

## Feature 6 — Implement Security, Governance, and Cost Controls

Tags: `pulser-odoo`, `azure-pipelines`, `security`, `governance`

### Story 6.1 — Define identity and secret model for Azure Pipelines
Secret source-of-truth (Azure Key Vault). Pipeline identity (service connections / managed identity). Rotation posture. Least-privilege expectations.

### Story 6.2 — Define pipeline governance and change-control policy
Who can change shared templates. Review requirements. Policy enforcement. Exception procedure.

### Story 6.3 — Define cost and capacity optimization policy
Cost drivers. Concurrency policy. Optimization rules. Reporting/visibility.

---

## Feature 7 — Benchmark and Adapt Official Azure Pipeline References

Tags: `pulser-odoo`, `azure-pipelines`, `benchmark`

### Story 7.1 — Assess Microsoft Learn GitHub repository integration guidance
Relevant guidance summarized. Repo-specific adaptation notes. Trigger + validation implications. Gaps → follow-up tasks.

### Story 7.2 — Assess microsoft/azure-pipelines-yaml as template reference
Reusable template concepts identified. Repo-specific adaptations. Anti-patterns to avoid. Template follow-ups.

### Story 7.3 — Assess microsoft/azure-pipelines-agent for runner operations baseline
Runner operational considerations. Update + compatibility concerns. Self-hosted applicability. Hardening follow-ups.

---

## Priority sequencing

**P0:** 1.1, 1.2, 1.3, 2.1, 3.1, 6.1
**P1:** 2.2, 2.3, 3.2, 3.3, 5.1, 7.1
**P2:** 4.1, 4.2, 4.3, 5.2, 5.3, 6.2, 6.3, 7.2, 7.3
