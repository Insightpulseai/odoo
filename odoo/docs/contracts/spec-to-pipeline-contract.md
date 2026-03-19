# Spec-to-Pipeline Contract

## Purpose

Define what must exist before a spec bundle can enter the governed CI/CD lane.

## Source and target

**Source:** `spec/<slug>/` bundle
**Target:** PR + Azure Pipeline execution

## Required inputs

Before pipeline execution is considered valid, the spec bundle must define:

- delivery unit slug
- deploy target (`azure_runtime` or `odoo_sh`)
- whether AI evaluation is required
- acceptance criteria
- test strategy
- rollout strategy
- rollback expectation
- marketplace intent (yes/no)

## Required repo cross-links

Each PR must reference: Azure Boards Issue ID, spec slug, `plan.md`, `tasks.md`.

## Required pipeline metadata

Each pipeline run must resolve: work item ID, spec slug, module/app identifier, deploy target, release class, environment target.

## Minimum pipeline stages

Every releaseable unit must have stages for:

1. Validate metadata
2. Lint / static checks
3. Test
4. Package / build
5. Staging deployment
6. Evaluation gate (if required)
7. Production approval / deploy
8. Evidence publication

## Test-level contract

Use the explicit quality taxonomy:

- **L0/L1** = unit / local low-dependency tests
- **L2** = bounded functional tests
- **L3** = deployed service tests
- **L4** = restricted production-integrated tests

Minimum rule: most quality signal must happen before merge. Lowest-level tests should be preferred first.

## Required evidence outputs

Pipeline must emit or link: test summary, package/build artifact, deployment logs, staging validation result, eval result (if AI-enabled), production deployment record, rollback reference, release notes artifact.

## AI-enabled release rule

If `ai_enabled: true`, production promotion is blocked until: eval threshold file exists, eval run completes, traces are available, monitoring path is defined.

## Production promotion preconditions

Promotion is allowed only if:

- required tests passed
- required approvals/checks passed
- staging validation passed
- rollout strategy exists
- rollback path exists
- bake time policy exists
- eval gate passed (if required)

## Failure conditions

This contract fails if: PR has no linked work item/spec, pipeline runs without deploy target metadata, AI-enabled feature skips eval gate, required evidence artifacts are missing, or production deploy occurs without rollback definition.

---

*Last updated: 2026-03-17*
