# AZ-400 + Platform Engineering — Boards-Ready Learning Backlog

> **Source:** AZ-400 (Secure Continuous Deployment + IaC with Azure & DSC) + "Design and Implement Platform Engineering" learning paths.
> **Doctrine alignment:** Azure Pipelines only. Bicep + VS Code authoring. Azure CLI local validation. Managed identity first. **No GitHub Actions. No Vercel.**
> **Filed:** 2026-04-15.
> **Authority:** ADO Boards portfolio hierarchy (`ipai-platform`).

---

## Initiative

**Azure-native delivery hardening — Secure CD + IaC + Platform Engineering**

Rolls up three Microsoft Learn paths into one execution program:

- **AZ-400: Implement a secure continuous deployment using Azure Pipelines** — deployment patterns, blue-green, canary, identity, config/secrets
- **AZ-400: Manage infrastructure as code using Azure and DSC** — IaC, ARM/Bicep, CLI, automation, DSC
- **Design and Implement Platform Engineering** — platform foundations, secure/scalable architecture, self-service, observability, roadmapping

---

## Epic 1 — Secure continuous deployment patterns `[P0]`

### Feature 1.1 — deployment strategy baseline

- **ISSUE-001** Define supported deployment patterns for IPAI workloads
- **ISSUE-002** Map classical vs modern deployment patterns to ACA / Odoo / web / services
- **ISSUE-003** Define workload-by-workload deployment strategy matrix
- **ISSUE-004** Define rollback criteria per deployment pattern
- **ISSUE-005** Define release evidence required before promotion

### Feature 1.2 — blue-green and feature toggles

- **ISSUE-006** Define blue-green eligibility for web and API surfaces
- **ISSUE-007** Define deployment slot / traffic-switch contract where applicable
- **ISSUE-008** Define feature-flag ownership and lifecycle policy
- **ISSUE-009** Define toggle cleanup and expiry rules
- **ISSUE-010** Add feature-gate checklist to release workflow

### Feature 1.3 — canary, dark launch, and progressive exposure

- **ISSUE-011** Define canary rollout policy for selected workloads
- **ISSUE-012** Define dark-launch policy for agent and UI features
- **ISSUE-013** Define ring-based rollout model
- **ISSUE-014** Define A/B or progressive exposure decision criteria
- **ISSUE-015** Define telemetry needed to approve or abort progressive rollout

---

## Epic 2 — Identity, secrets, and configuration `[P0]`

### Feature 2.1 — workload identity baseline

- **ISSUE-016** Define Entra workload identity standard for pipelines and services
- **ISSUE-017** Define managed identity-first policy for Azure-hosted apps
- **ISSUE-018** Define service principal exception process
- **ISSUE-019** Define GitHub SSO and ADO permission boundary model
- **ISSUE-020** Audit current pipeline identities and missing role assignments

### Feature 2.2 — configuration and secret management

- **ISSUE-021** Define externalized configuration standard
- **ISSUE-022** Define Azure App Configuration adoption boundary
- **ISSUE-023** Define Key Vault integration standard for pipelines
- **ISSUE-024** Define secure files / certificates / token handling standard
- **ISSUE-025** Define dynamic config and feature flag governance

### Feature 2.3 — release gates and notifications

- **ISSUE-026** Define automated release gates for deployment approval
- **ISSUE-027** Define alerting and service-hook notification flows
- **ISSUE-028** Define quality reporting for deployment decisions
- **ISSUE-029** Define incident-response signal routing from pipelines
- **ISSUE-030** Define secrets-rotation checks in deployment workflows

---

## Epic 3 — Infrastructure as code foundation `[P0]`

### Feature 3.1 — IaC doctrine

- **ISSUE-031** Define declarative IaC standard across Azure estate
- **ISSUE-032** Define imperative-vs-declarative exception policy
- **ISSUE-033** Define idempotency rules for infra changes
- **ISSUE-034** Define environment parity requirements across dev / staging / prod
- **ISSUE-035** Define infra evidence requirements after deployment

### Feature 3.2 — Bicep standard

- **ISSUE-036** Make Bicep the default Azure IaC authoring path
- **ISSUE-037** Define `main.bicep` and module structure standard
- **ISSUE-038** Define `.bicepparam` usage standard
- **ISSUE-039** Define Bicep + VS Code authoring standard
- **ISSUE-040** Define Bicep MCP assistive-authoring boundary

### Feature 3.3 — Azure CLI and validation path

- **ISSUE-041** Define Azure CLI as default local infra validation path
- **ISSUE-042** Define `az bicep build` / validation / what-if workflow
- **ISSUE-043** Define resource-group vs subscription deployment boundaries
- **ISSUE-044** Define local auth standard for infra operators
- **ISSUE-045** Define pre-merge infra validation requirements

---

## Epic 4 — Azure automation and drift control `[P1]`

### Feature 4.1 — automation accounts and runbooks

- **ISSUE-046** Define Azure Automation adoption boundary
- **ISSUE-047** Define when to use runbooks vs pipelines vs jobs
- **ISSUE-048** Define webhook-triggered automation policy
- **ISSUE-049** Define automation shared-resource governance
- **ISSUE-050** Define source-control integration rules for automation assets

### Feature 4.2 — configuration drift and DSC

- **ISSUE-051** Assess DSC relevance for current IPAI footprint
- **ISSUE-052** Define drift-detection standard for infra and config
- **ISSUE-053** Define hybrid-management exception policy
- **ISSUE-054** Define checkpoint / retry model for configuration remediation
- **ISSUE-055** Decide keep / adopt / skip posture for DSC in current Azure estate

---

## Epic 5 — Platform engineering foundation `[P0]`

### Feature 5.1 — platform capability model

- **ISSUE-056** Define IPAI platform engineering capability model
- **ISSUE-057** Map repos to platform capabilities and ownership boundaries
- **ISSUE-058** Define internal platform products and supported consumers
- **ISSUE-059** Define platform SLO / SLA-lite expectations
- **ISSUE-060** Define business-alignment success metrics for platform work

### Feature 5.2 — secure and scalable architecture

- **ISSUE-061** Define secure / scalable platform architecture principles
- **ISSUE-062** Define capacity-planning review for core workloads
- **ISSUE-063** Define automation and resiliency baseline
- **ISSUE-064** Define compliance / governance review for new platform components
- **ISSUE-065** Define cost-optimization checkpoints in platform design

---

## Epic 6 — Developer self-service `[P1]`

### Feature 6.1 — self-service platform surface

- **ISSUE-066** Define self-service platform architecture for developers
- **ISSUE-067** Define what can be self-served vs centrally controlled
- **ISSUE-068** Define guardrails for secure self-service workflows
- **ISSUE-069** Define developer coding environment baseline
- **ISSUE-070** Define audit trail for self-service actions

### Feature 6.2 — self-service infrastructure with Bicep

- **ISSUE-071** Define self-service Bicep module catalog
- **ISSUE-072** Define approved module input / output contract
- **ISSUE-073** Define onboarding flow for new workloads using Bicep
- **ISSUE-074** Define quota / policy constraints for self-service provisioning
- **ISSUE-075** Define validation / promotion path from self-service to managed estate

---

## Epic 7 — Observability and continuous improvement `[P0]`

### Feature 7.1 — platform observability

- **ISSUE-076** Define observability baseline for platform workloads
- **ISSUE-077** Define metrics, logs, traces, and alert minimums
- **ISSUE-078** Define Azure Monitor usage standard
- **ISSUE-079** Define incident-detection automation baseline
- **ISSUE-080** Define telemetry review cadence for platform health

### Feature 7.2 — feedback loops and improvement

- **ISSUE-081** Define continuous-improvement loop for platform services
- **ISSUE-082** Define deployment feedback capture and review
- **ISSUE-083** Define developer-experience feedback mechanism
- **ISSUE-084** Define market / architecture change review cadence
- **ISSUE-085** Define backlog refresh process from observability insights

---

## Epic 8 — Strategic platform roadmapping `[P1]`

### Feature 8.1 — roadmap process

- **ISSUE-086** Define platform roadmap governance
- **ISSUE-087** Define risk management for platform initiatives
- **ISSUE-088** Define stakeholder communication model
- **ISSUE-089** Define future-proofing review for core platform choices
- **ISSUE-090** Define roadmap artifact format and update cadence

### Feature 8.2 — execution alignment

- **ISSUE-091** Align platform roadmap with Azure Boards portfolio hierarchy
- **ISSUE-092** Align roadmap with Azure Pipelines delivery gates
- **ISSUE-093** Align roadmap with FinOps and workload onboarding
- **ISSUE-094** Align roadmap with agent / runtime evolution
- **ISSUE-095** Define quarterly platform review pack

---

## Epic 9 — Azure Pipelines implementation and hardening `[P0]`

### Feature 9.1 — pipeline templates

- **ISSUE-096** Create secure deployment template baseline for Azure Pipelines
- **ISSUE-097** Create Bicep lint / build / validate pipeline template
- **ISSUE-098** Create environment promotion pipeline template
- **ISSUE-099** Create secret / key-vault integration template
- **ISSUE-100** Create rollout-strategy template hooks for blue-green / canary

### Feature 9.2 — policy and release controls

- **ISSUE-101** Define mandatory checks before deployment
- **ISSUE-102** Define environment approvals and protected resources
- **ISSUE-103** Define deployment freeze / emergency break-glass process
- **ISSUE-104** Define rollback and incident capture standard
- **ISSUE-105** Define service-hook and notification standard for releases

---

## Epic 10 — Current-state remediation `[P0]`

### Feature 10.1 — close known delivery gaps

- **ISSUE-106** Stabilize current Azure Pipelines red / failing paths
- **ISSUE-107** Remove remaining manual-only islands from infra / runtime setup
- **ISSUE-108** Land Bicep and Foundry runtime contract validation in CI / CD
- **ISSUE-109** Land identity hardening for critical agents and pipelines
- **ISSUE-110** Produce release-readiness checklist aligned to secure CD + IaC doctrine

---

## Recommended sprint cut

### Sprint 1

- ISSUE-001 → ISSUE-015 (deployment strategy + blue-green + canary)
- ISSUE-016 → ISSUE-030 (identity, secrets, gates)
- ISSUE-031 → ISSUE-045 (IaC + Bicep + CLI)

### Sprint 2

- ISSUE-056 → ISSUE-065 (platform capability + secure architecture)
- ISSUE-076 → ISSUE-085 (observability + feedback)
- ISSUE-096 → ISSUE-105 (pipeline templates + release controls)

### Sprint 3

- ISSUE-066 → ISSUE-075 (developer self-service + Bicep catalog)
- ISSUE-106 → ISSUE-110 (current-state remediation)
- ISSUE-046 → ISSUE-055 (automation + drift / DSC)

### Sprint 4

- ISSUE-086 → ISSUE-095 (roadmap governance + execution alignment)
- Remaining hardening / cleanup carryover

---

## Azure Boards paste block

```text
Initiative: Azure-native delivery hardening — Secure CD + IaC + Platform Engineering

Epics:
1. Secure continuous deployment patterns
2. Identity, secrets, and configuration
3. Infrastructure as code foundation
4. Azure automation and drift control
5. Platform engineering foundation
6. Developer self-service
7. Observability and continuous improvement
8. Strategic platform roadmapping
9. Azure Pipelines implementation and hardening
10. Current-state remediation
```

---

## Verification checklist

- [x] Azure Boards hierarchy is explicit (Initiative → Epic → Feature → Issue)
- [x] Secure CD topics represented as board work (Epics 1, 2, 9)
- [x] IaC / Bicep / CLI topics represented as board work (Epics 3, 4, 6)
- [x] Platform engineering / self-service / observability / roadmap topics represented (Epics 5, 6, 7, 8)
- [x] All items phrased as executable backlog work, not generic study notes
- [x] Doctrine guardrails enforced: Azure Pipelines only, Bicep + VS Code authoring, Azure CLI validation, managed identity first, no GHA, no Vercel
- [x] Recommended sprint cut included
- [x] Azure Boards short paste block included

---

## Doctrine pointers

- **CI / CD authority**: `CLAUDE.md` §"Engineering & Delivery Authority (REVISED 2026-04-14)" — Azure Pipelines is sole authority. GHA + Vercel forbidden.
- **Identity baseline**: `.claude/rules/security-baseline.md` — Managed Identity first, Key Vault for secrets, no plaintext.
- **IaC standard**: `infra/azure/` Bicep + `azure-pipelines/` deploy lanes.
- **Platform authority split**: `ssot/governance/platform-authority-split.yaml`.
- **CI / CD authority matrix**: `ssot/governance/ci-cd-authority-matrix.yaml`.
- **Repo delivery disposition**: `ssot/governance/repo-delivery-disposition.yaml`.

---

*Last updated: 2026-04-15 — by Claude (Opus 4.6, 1M context)*
