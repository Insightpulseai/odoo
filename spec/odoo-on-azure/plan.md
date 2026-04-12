# Implementation Plan — Odoo on Azure: Best Practices Reference Platform

## Status

Active

---

## Technical summary

Formalize the operating model for running Odoo CE + extensions + AI copilots on Azure using
Microsoft's own reference patterns as the benchmark. The platform is organized into five
product lanes: runtime foundation, center for ERP solutions, deployment automation, monitoring,
and integration extensions.

---

## Architecture decisions

### AD-001 — Benchmark against control objectives, not SAP product shape

The reference platform benchmarks against Azure architecture best practices, Well-Architected
guidance, and Foundry/Container Apps patterns — not SAP deployment topology or naming.

### AD-002 — Five-lane product model

The platform is organized into: runtime foundation, center for ERP solutions, deployment
automation framework, monitoring and insights, and AI/integration extensions.

### AD-003 — Odoo is the transactional system of record

Odoo remains the sole business SoR. Platform services orchestrate around Odoo but do not
replace its transactional authority.

### AD-004 — Azure-managed controls are the security baseline

Entra ID, Key Vault, managed identities, private endpoints, Azure Monitor, and WAF are the
default security and operations controls. Application-embedded credentials and ad hoc
networking are not acceptable in production.

### AD-005 — YAML-first delivery

All deployment automation is repo-defined YAML. Azure DevOps pipeline state is a control
surface, not the definition surface.

### AD-006 — Foundry-first AI

All AI/agent/grounding capabilities route through Microsoft Foundry. Foundry Agent Service
is the managed agent runtime. Foundry IQ / RAG is the default grounding pattern.

### AD-007 — Identity governance is a core platform plane

Identity governance is a first-class platform concern alongside runtime, networking,
deployment, and monitoring.

### AD-008 — Least privilege is the default access model

Administrative and workload access must be granted at the minimum level necessary, with
standing privilege minimized.

### AD-009 — JIT privileged access for platform administration

Privileged administrative operations should use eligible/activated access patterns instead
of permanent assignment where supported.

### AD-010 — Access lifecycle is policy-driven

Access to applications, groups, roles, and protected resources must be governed through
lifecycle-aware assignment, review, and expiration rules.

### AD-011 — Agent identities are governed subjects

AI agents are treated as governed identities with accountable human sponsors/owners and
reviewable access boundaries.

### AD-012 — SaaS and multitenancy are distinct design concerns

The platform must distinguish SaaS business-model decisions from multitenancy architecture
decisions.

### AD-013 — Tenant definition is explicit

Every supported workload pattern must explicitly define what constitutes a tenant and what
resources are shared versus isolated.

### AD-014 — Tenant isolation over maximal consolidation

Where ERP trust, compliance, or recovery requirements are high, stronger tenant isolation is
preferred over aggressive consolidation.

### AD-015 — Deployment stamps bound scale and blast radius

The platform should use deployment stamps or equivalent bounded fleet partitions to support
scale, safe rollout, regional growth, and fault isolation.

### AD-016 — Control plane is first-class

The platform requires a resilient service-level control plane and a tenant-level
administrative control plane.

### AD-017 — Telemetry-first SaaS operations

Telemetry, usage insight, and live-site observability must be designed into the platform
from the start.

### AD-018 — Feature flags and safe deployment are mandatory

New capabilities, behavior changes, and mitigations must support staged rollout and rollback
through safe deployment and feature-flag controls.

### AD-019 — Standardization over tenant-specific drift

The platform should avoid one-off customer-specific code paths, settings, and configuration
unless explicitly justified and governed.

### AD-020 — Treat the platform as an internal product

The ERP-on-Azure platform must be managed with a product mindset, with internal engineering
teams as customers.

### AD-021 — Self-service with guardrails is the default operating model

Common platform tasks must be self-service where feasible, with policy and automation
enforcing security, compliance, and cost controls.

### AD-022 — Paved paths over ad hoc enablement

The platform should define and iteratively improve paved/golden paths for the most important
routes to production.

### AD-023 — API-first, portal-second interface strategy

The platform should prefer reusable APIs, YAML/IaC/EaC artifacts, CLI flows, and integrations
with existing engineering tools before building large custom portal surfaces.

### AD-024 — Everything as code is the preferred control surface

Infrastructure, policy, security, configuration, and workflow definitions should be expressed
through versioned code or declarative artifacts where possible.

### AD-025 — Platform maturity is measured across six capabilities

Platform evolution should be assessed and prioritized across: investment, adoption,
governance, provisioning and management, interfaces, and measurement and feedback.

### AD-026 — GitHub-native repo automation is a first-class path

The platform must support repository-local workflow automation through GitHub Actions for
build, test, packaging, and Azure deployment scenarios where local ownership and speed
are important.

### AD-027 — OIDC-first GitHub-to-Azure authentication

Authentication from GitHub workflows to Azure must prefer OpenID Connect or managed identity.
Client-secret-based authentication is an exception path only.

### AD-028 — Key Vault-backed secret retrieval

Sensitive values needed by workflows should be retrieved from Azure Key Vault or equivalent
managed secret stores rather than stored directly in workflow code.

### AD-029 — GitHub Actions and Azure Pipelines have distinct roles

GitHub Actions should handle repo-native workflow automation and local developer/product flows.
Azure Pipelines should handle governed multi-stage release flows, shared enterprise controls,
or central orchestration requirements.

### AD-030 — Policy and infrastructure are code-defined

Azure deployment templates, IaC artifacts, and policy/compliance definitions should be managed
as code and executable from GitHub-integrated workflows.

---

## Workstreams

### WS1 — Reference architecture and benchmark model

Deliver:

- benchmark layers and control objectives
- supported deployment archetypes
- target-state architecture diagram
- mapping from Azure best-practice controls to Odoo workload requirements

### WS2 — Center for ERP solutions

Deliver:

- system registration and inventory
- lifecycle operations (start/stop, environment management)
- health check framework
- quality check framework
- configuration drift detection
- cost analysis and operational tagging

### WS3 — Deployment automation framework

Deliver:

- environment bootstrap automation
- runtime + DB + storage + secrets provisioning
- service connection registration
- app/runtime revision deployment
- rollback/recovery procedures
- approval/check and branch protection encoding

### WS4 — Monitoring and insights

Deliver:

- runtime health dashboards
- database health monitoring
- worker/job health monitoring
- deployment event tracking
- AI telemetry (token consumption, model usage, agent behavior)
- alert definitions and escalation paths
- App Insights / Log Analytics integration

### WS5 — AI and integration extensions

Deliver:

- Pulser/Foundry integration patterns
- RAG boundaries between Odoo data and enterprise knowledge
- Document Intelligence integration
- M365 / Teams integration patterns
- Power BI / Databricks analytics integration
- identity and SSO patterns

### WS6 — Identity governance foundation

Deliver:

- employee / guest / partner lifecycle model
- privileged access model (PIM / JIT elevation)
- approval and entitlement model
- access review cadence for sensitive surfaces
- least-privilege admin role matrix

### WS7 — Agent identity governance

Deliver:

- identity model for Pulser and related agents
- sponsor / owner accountability model
- access package and approval pathways for agents where supported
- lifecycle review / disable / decommission procedures for agents

### WS8 — Tenancy and isolation architecture

Deliver:

- tenant boundary definition for each workload model
- shared vs isolated component map
- data isolation posture for transactional ERP data
- recovery and blast-radius boundaries

### WS9 — Control plane and fleet operations

Deliver:

- service-level control plane capabilities
- tenant-level admin/control capabilities
- onboarding, provisioning, rollout, and maintenance orchestration
- quality checks and cost/capacity visibility

### WS10 — Safe deployment and feature management

Deliver:

- deployment-ring or stamp rollout model
- feature-flag lifecycle and governance
- mitigation / fallback patterns
- configuration rollout controls

### WS11 — Telemetry and live-site operations

Deliver:

- telemetry baseline
- operational communications model
- incident detection / isolation / mitigation workflow
- shift-left and self-healing opportunities

### WS12 — Thinnest viable platform

Deliver:

- first high-value paved paths
- identification of existing tools/surfaces to extend before building new interfaces
- minimum reusable catalog of templates, workflows, and approved assets

### WS13 — Self-service foundation

Deliver:

- request/provision/deploy flows for common platform tasks
- mapping of each flow to policy guardrails and fulfillment providers
- inventory/catalog model for templates, services, images, integrations, and environments

### WS14 — Platform interfaces

Deliver:

- API, CLI, pipeline, IDE, and optional portal surfaces
- reduced unnecessary context switching
- prioritized integrations into tools teams already use

### WS15 — Measurement and feedback

Deliver:

- adoption, speed, quality, and ease-of-use metrics
- platform feedback loops
- how platform usage and experience influence prioritization

### WS16 — GitHub-to-Azure federation

Deliver:

- OIDC federation model for GitHub workflows
- allowed auth patterns and exception paths
- runner strategy for hosted vs self-hosted scenarios

### WS17 — GitHub workflow catalog

Deliver:

- approved GitHub Actions patterns for build, deploy, infra, policy, and database updates
- repository-local workflow templates
- when GitHub should directly deploy vs trigger an Azure Pipelines flow

### WS18 — Secret and policy integration

Deliver:

- Key Vault retrieval patterns for GitHub workflows
- policy-as-code / compliance scan flows
- protected environment / approval behavior across GitHub and Azure boundaries

---

## Information architecture

```text
Overview
  What offerings are available?
  Supported deployment archetypes
  Supported runtime topologies
  Security / operations model

Get started
  ERP on Azure workloads
  Choose your deployment pattern
  Quickstart: dev / staging / production
  Register an existing system

Center for ERP solutions
  What is the control plane?
  Register an existing ERP system
  Start / stop systems
  Manage system inventory
  Quality checks and insights
  Cost analysis

Deployment automation framework
  What is the automation framework?
  Supported platform/features
  Plan your deployment
  Configure Azure DevOps services
  Bootstrap runtime / DB / secrets / networking
  Promote through environments

Monitoring
  What is Azure Monitor for ERP solutions?
  Runtime health
  Deployment health
  Database health
  Worker/job health
  AI telemetry
  Alerts / dashboards / traces

Supported workloads
  Supported app/runtime patterns
  Supported DB/storage patterns
  HA / DR reference guidance
  Networking and identity guidance
  Backup / restore / recovery patterns

Integrations
  Foundry / Pulser
  M365 / Teams / Outlook
  Power Platform
  Document intelligence
  Analytics / BI / lakehouse
```

---

## Delivery phasing

### Phase 1 — Runtime baseline

- Document supported deployment archetypes
- Establish ACA + PostgreSQL + storage reference topology
- Establish identity and secret baseline (Entra ID, Key Vault, MI)
- Establish YAML pipeline for build → test → deploy

### Phase 2 — Center for ERP solutions (MVP)

- System registration
- Environment inventory
- Health check framework
- Quality check framework

### Phase 3 — Deployment automation

- Bootstrap automation
- Multi-environment promotion
- Rollback/recovery procedures
- Protected branch/approval gates

### Phase 4 — Monitoring and insights

- Runtime dashboards
- AI telemetry
- Cost analysis
- Alert definitions

### Phase 5 — Integration extensions

- Pulser/Foundry patterns
- Document Intelligence patterns
- M365/Teams patterns
- Analytics/BI patterns

---

## Acceptance gates

- Each deployment archetype has a documented topology
- Platform security controls are mapped to Azure-managed services
- YAML pipeline covers build/test/staging/production with approval gates
- Monitoring covers runtime, DB, worker, deployment, and AI telemetry
- Center for ERP solutions provides inventory, health, and quality views
- Cost analysis is available for each registered environment
- Integration patterns are documented for each supported lane
- Each protected surface has an access model
- Privileged roles are identified and minimized
- Recurring review requirements are defined for sensitive access
- Guest / partner / nonhuman access has expiration or recertification rules
- Agent identities have named human accountability
- No critical workflow depends on long-lived shared credentials without explicit exception documentation
- Tenant definition is explicit for every supported architecture pattern
- Shared and isolated components are documented by tier
- Blast-radius boundary is defined for deployment and failure scenarios
- Service-level and tenant-level control-plane responsibilities are defined
- Telemetry baseline exists before production launch
- Safe deployment and feature-flag controls exist for code and configuration changes
- No undocumented tenant-specific exceptions exist in the happy-path operating model
- At least one high-value paved path is explicitly defined
- Self-service tasks map to approved automation and policy controls
- Platform interfaces are documented in priority order: API/CLI/integration/portal
- Reusable templates or catalog assets exist for common tasks
- Platform success metrics include adoption and developer-experience measures
- Feedback collection and prioritization are defined
- GitHub repository workflows are versioned in-repo where applicable
- Azure authentication from GitHub uses OIDC or documented managed-identity pattern
- Workflows that require secrets have a managed secret retrieval path
- The boundary between GitHub Actions and Azure Pipelines is documented
- Policy/compliance automation is represented as code and executable through workflow automation

---

## Anti-goals

- Do not clone SAP deployment topology or naming
- Do not build a generic multi-ERP platform in the first iteration
- Do not treat manual Azure portal operations as the primary management surface
- Do not embed credentials in application code or pipeline definitions
- Do not expose internal services publicly without explicit justification
- Do not treat monitoring and quality checks as optional post-launch additions
- Do not rely on permanent broad administrator access where JIT patterns are feasible
- Do not leave guest or external access open-ended by default
- Do not treat AI agents as ungoverned service actors
- Do not make shared static credentials the default identity model for agents
- Do not treat multitenancy as equivalent to sharing everything
- Do not optimize cost ahead of tenant trust, isolation, and service usefulness
- Do not treat the control plane as noncritical support tooling
- Do not rely on ad hoc customer-specific configuration as a default scaling strategy
- Do not introduce new capabilities directly to the whole fleet without safe rollout controls
- Do not build a large portal first if existing engineering surfaces can be improved instead
- Do not treat platform governance as separate from developer experience
- Do not require manual ticket-driven fulfillment for common repeatable platform tasks by default
- Do not build everything from scratch when existing Microsoft/open-source building blocks are sufficient
- Do not mandate platform usage without making the paved path genuinely better
- Do not default to client-secret-based GitHub authentication when OIDC is available
- Do not embed sensitive values directly in workflow YAML
- Do not duplicate the same delivery responsibility in both GitHub Actions and Azure Pipelines
  without a clear ownership boundary
- Do not rely on portal-only deployment logic when workflow-as-code can represent the same behavior

---

## Touch points

### Repo paths

- `spec/odoo-on-azure/` — this spec bundle
- `docs/architecture/BENCHMARK_MODEL.md` — benchmark doctrine
- `docs/architecture/DELIVERY_GOVERNANCE.md` — delivery operating model
- `odoo/.azure-pipelines/` — YAML pipeline definitions
- `infra/` — infrastructure as code
- `ssot/` — intended-state truth

### Related specs

- `spec/pulser-odoo-ph/` — Pulser copilot (AI lane)
- `spec/close-orchestration/` — month-end close (finance workload)
- `spec/bir-tax-compliance/` — BIR compliance (PH workload)
