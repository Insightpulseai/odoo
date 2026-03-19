# PRD — OdooSH Azure Equivalent

## Problem

We need Odoo.sh-like developer and operator ergonomics on Azure, while preserving Odoo operational safety and making staging/prod behaviors explicit and reproducible.

## Goals

1. Push/PR-driven build/test/deploy
2. Ephemeral preview environments per PR
3. Sanitized staging refresh from production
4. Approval-gated production promotion
5. App + DB rollback capability
6. Evidence and observability at every stage

## Non-Goals

- Reproducing Odoo.sh UI exactly (no drag-and-drop branch management)
- Recreating shared-hosting internals (worker recycling, platform API)
- Supporting arbitrary long-lived auxiliary daemons inside the main Odoo web container

## Functional Requirements

### FR-01: Automatic CI on push/PR
Pushes and PRs must trigger CI automatically. Build, lint, test.

### FR-02: Immutable artifact production
CI must produce an immutable deployable container image and publish deployment evidence (digest, test results, lint status).

### FR-03: Environment-targeted deployments
Deployments must target explicit environments (dev/staging/prod) with history, security controls, and traceability.

### FR-04: PR preview environments
Platform must support preview deployments per PR/feature branch with automatic cleanup TTL. Preview URL posted as PR comment.

### FR-05: Staging refresh from production
Staging must be refreshable from production data through restore + sanitize workflow. Azure PG Flexible Server PITR supports the substrate.

### FR-06: Staging integration scrub
Staging refresh must strip or sandbox outbound integrations: mail servers, payment processors, social integrations, calendar/drive tokens, IAP accounts, EDI tokens, cron jobs, robots.txt.

### FR-07: Production approval gates
Production deployment must require resource-level approvals/checks, not YAML-only logic. Environment protection rules with required reviewers.

### FR-08: Zero-downtime production rollout
Production app deploy must support zero-downtime rollout or controlled cutover using ACA revisions, traffic splitting, and labels.

### FR-09: Operator access
Operators must have centralized logs (Log Analytics), health signals (App Insights), and shell access (`az containerapp exec`) to running containers.

### FR-10: Backup and recovery
Production must have documented backup (35-day retention), PITR, and recovery workflows. Read-only reporting access supported through replica or least-privilege path.

### FR-11: Addon management
Addon sources must support multi-folder OCA/custom layout and optionally submodules, but discovery must be explicit and reproducible via `config/addons.manifest.yaml`.

### FR-12: Secret management
Secrets must come from Key Vault-backed variable groups or managed identity-backed runtime resolution. Never hardcoded in YAML or committed to git.

## Non-Functional Requirements

- **Security**: Resource-owned approvals/checks, least-privilege secrets, auditable deploys
- **Reliability**: Production DB HA/PITR, revision-based app rollback
- **Observability**: Logs, traces, deployment history, smoke endpoints
- **Portability**: No assumptions that only exist in Odoo.sh shared hosting

## Acceptance Criteria

- [ ] A PR creates a preview runtime with accessible URL + evidence
- [ ] A staging refresh produces sanitized data with disabled external side effects
- [ ] A prod deploy cannot bypass environment checks unless explicitly bypassed by resource admin
- [ ] A failed prod rollout can return traffic to the prior known-good revision
- [ ] DB restore runbook exists and has been rehearsed
- [ ] Every promotion has an evidence pack (image digest, test results, approvals, health check)
