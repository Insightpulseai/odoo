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
- Requiring integrated-services maturity across every interface in the first release
- Leaving provisioning at coordinated/ticket-driven maturity for core workflows
- Naming Viva Goals or any specific retired OKR tool as a future operating surface

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

### FR-41: Interface maturity target
The platform must provide standardized interfaces for development-environment setup and application diagnosis, with self-service introduced first for the highest-frequency workflows.

### FR-42: Discoverability
Users must be able to identify available capabilities and request what they need through consistent affordances rather than person-to-person tribal knowledge.

### FR-43: Diagnostic affordances
The platform must provide a standard path for observing deployed resources and diagnostic data; later, observability should be increasingly integrated into normal engineering tools and workflows.

### FR-44: Paved provisioning
Provisioning must use IaC templates and formalized organization-wide provisioning processes for core platform capabilities.

### FR-45: Automated provisioning workflow
Core environment/resource provisioning must be automated and integrated into CI/CD with embedded governance and compliance checks.

### FR-46: Controlled self-service creation
Authorized users must be able to provision standardized, preconfigured dedicated or shared environments independently within platform-defined guardrails.

### FR-47: Allocation visibility
The platform must expose centralized metrics and dashboards for resource allocation and utilization across services.

### FR-48: Allocation automation roadmap
The roadmap must include automated scaling based on usage patterns and later predictive allocation, but those are not required for TVP acceptance.

### FR-49: Source classification
The platform documentation must distinguish normative doctrine from implementation exemplars and explicitly mark unrelated naming-collision repos as out of scope.

### FR-50: MCP/provider pattern
The platform must support an MCP/provider-style extension model for AI capabilities, informed by Microsoft Foundry examples such as mcp-foundry.

### FR-51: Local AI development option
The platform may offer a local/offline developer path for AI-assisted workflows using OpenAI-compatible local endpoints, informed by Foundry Local.

### FR-52: Production AI reference path
Any production-grade AI extension path must align to hardened reference architecture patterns (network isolation, controlled dependencies, security controls) as shown by the Azure AI Foundry baseline reference implementation.

### FR-53: Bootstrap templates are non-production by default
Starter/bootstrap templates may accelerate onboarding, but they must be marked as non-production baselines unless hardened.

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
