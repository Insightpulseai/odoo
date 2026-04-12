# PRD — Odoo on Azure: Best Practices Reference Platform

## Status

Active

## Feature Branch

`odoo-on-azure`

---

## Name

Odoo on Azure — Best Practices Reference Platform

## One-line positioning

A Microsoft-style ERP-on-Azure operating model built from Azure best practices, not a SAP clone.

## Problem

Running Odoo CE as a production ERP on Azure requires decisions across identity, networking,
secrets, monitoring, deployment automation, AI integration, and lifecycle management. Without
a reference platform, these decisions are made ad hoc, resulting in inconsistent security
posture, manual operations, poor observability, and fragile delivery.

## Why now

- Azure Container Apps, Foundry, and Azure Pipelines are mature enough to compose a governed
  ERP hosting model without enterprise middleware
- The SAP-on-Azure program proves Microsoft packages this guidance for ERP workloads, but no
  equivalent exists for non-SAP ERPs
- InsightPulseAI already runs Odoo + Pulser on Azure — this spec formalizes the operating model

## Target users

- Platform administrator
- DevOps / release engineer
- Finance / operations user (indirect — benefits from reliability and observability)
- AI copilot developer (Pulser)

---

## Benchmark authority

This product is benchmarked against Azure and enterprise platform best practices, not SAP
product topology.

Primary benchmark sources:

- Azure architecture and Well-Architected guidance
- Azure-native identity, networking, secret, monitoring, and deployment controls
- YAML-first Azure Pipelines delivery patterns
- Foundry-first enterprise AI application patterns
- Odoo/ERP-specific runtime and operational requirements

## Product objective

Provide a best-practice reference platform for running Odoo/ERP workloads on Azure with:

- governed deployment automation
- runtime observability
- lifecycle management
- quality checks
- cost analysis
- secure AI/agent integration
- governed identity and access lifecycle for people, apps, and agents

---

## Identity governance model

The platform must include an identity-governance control model based on least privilege and
lifecycle-based access, not static administrator assignment.

### Governance domains

- Employee identity lifecycle
- Guest / partner identity lifecycle
- Application access lifecycle
- Privileged access lifecycle
- Agent identity lifecycle

### Required governance capabilities

- Lifecycle-based onboarding, mover, and offboarding controls
- Entitlement-based access assignment with approval policies
- Recurring access reviews for sensitive access
- Just-in-time privileged access for administrative roles
- Explicit human accountability for governed nonhuman identities

## Agent identity governance

AI agents are first-class governed identities.

Pulser and other platform agents must not rely solely on shared application credentials or
unmanaged service identities. Where supported, agent execution should use governed agent
identities with:

- Scoped access rights
- Accountable human sponsor/owner
- Access-package based assignment where appropriate
- Lifecycle review and removal when no longer required

Human accountability for agent access is required even when the agent acts autonomously
within approved bounds.

## SaaS and multitenancy model

This product is a SaaS platform with a multitenant architecture.

Definitions:

- SaaS is the business model under which the platform is delivered and operated.
- Multitenancy is the architectural approach used to share some platform components across
  multiple tenants.
- A tenant represents a customer organization, business unit, or equivalent governed boundary
  within the service.

Multitenancy does not require that every component be shared. The platform may selectively
isolate critical components while sharing control-plane or application-layer services where
appropriate.

## Tenant definition and isolation strategy

The platform must explicitly define what a tenant is for each supported deployment model.

Default assumption:

- In B2B ERP/SaaS scenarios, a tenant maps to a customer organization or controlled
  organizational boundary.

Isolation strategy:

- Share platform services where cost and operational efficiency justify it
- Isolate tenant-critical data and high-risk resources where trust, compliance, or recovery
  requirements justify stronger separation

For transactional ERP data, the preferred model is to optimize for tenant isolation first
and shared efficiency second.

## Control plane model

The platform must provide two control-plane layers:

1. **Service-level control plane**
   - Onboarding tenants
   - Provisioning environments and dependencies
   - Rollout coordination
   - Fleet health and quality checks
   - Cost, capacity, and deployment management

2. **Tenant-level control plane**
   - Tenant administration
   - Configuration changes
   - Maintenance initiation where allowed
   - Tenant-scoped visibility and operational controls

The control plane is a production-critical subsystem and must not be treated as an
afterthought.

## Continuous SaaS operations principles

The platform follows these SaaS operating principles:

- Telemetry must be designed early and treated as core platform capability
- Customer satisfaction and usage are leading indicators; cost optimization follows after
  service usefulness and trust
- Safe deployment applies to both code and configuration
- Feature flags are required for controlled rollout, preview, mitigation, and deprecation
- One-off tenant divergence should be minimized to preserve operability at scale

---

## Product surfaces

### 1. Runtime foundation

Odoo app + PostgreSQL + storage + ingress + backup + HA/DR.

Supported deployment archetypes:

- Single-instance dev
- Staging / rehearsal
- Production single-region
- HA production
- ERP + AI copilot sidecar
- ERP + document processing
- ERP + analytics / lakehouse integration

### 2. Center for ERP solutions

System registration, inventory, lifecycle operations, health, quality checks, and cost views.

Capabilities:

- Register existing ERP systems
- Inventory instances and environments
- Start / stop systems
- Lifecycle state view
- Health checks
- Quality checks
- Configuration drift detection
- Cost analysis
- Environment metadata
- Release state visibility

### 3. Deployment automation framework

Bootstrap, deploy, promote, rollback, and environment registration flows.

Capabilities:

- Bootstrap new environments
- Provision runtime + DB + storage + secrets
- Register service connections
- Deploy app/runtime revisions
- Support rollback/recovery
- Encode approvals/checks and protected branches

### 4. Monitoring and quality insights

Runtime, database, worker, deployment, and AI telemetry surfaces.

Capabilities:

- Runtime health
- Job/worker health
- Queue backlog / reconciliation backlog
- App traces
- AI traces (token / model consumption)
- DB health
- Storage/filestore health
- Deployment events
- Security/compliance signals

### 5. Integration patterns

Foundry/Pulser, M365, Power Platform, Document Intelligence, analytics.

Covered integrations:

- Microsoft 365 / Teams / Outlook
- Power Platform
- Foundry / Agent Service / Foundry IQ
- Azure AI Search / Document Intelligence / Content Understanding
- Databricks / Fabric / Power BI
- Identity and SSO patterns (Entra ID)
- Mail / comms / notification integrations (Zoho SMTP)

### 6. Identity governance and access control

Governed identity lifecycle, access assignment, reviews, and privileged access management.

Covered identity types:

- Employees
- Guests / partners
- Service / application identities
- AI agent identities (Pulser, platform agents)

---

## Platform benchmark layers

### A. Platform benchmark

Azure-native best-practice controls:

- Entra ID / RBAC / managed identity
- Key Vault
- Private endpoints / internal-first connectivity
- Azure Monitor / App Insights / Log Analytics
- WAF / protected ingress
- Branch-gated, approval-gated delivery
- Backup / restore / DR
- Cost visibility and operational tagging

### B. Application runtime benchmark

- Odoo as transactional system of record
- Containerized sidecars/workers for non-core services
- Separate interactive vs batch workloads
- Internal services private by default
- Revision-aware deployments
- Multi-stage promotion path

### C. Delivery benchmark

Azure Pipelines best practices:

- Repo-defined YAML
- Build / test / staging / production stages
- Manual validation for protected deploys
- Branch-gated production
- Non-skippable required gates
- CLI/REST operational control

### D. AI benchmark

Pulser / copilots / agents:

- Foundry is canonical AI platform
- Foundry Agent Service is managed runtime
- Foundry IQ / RAG is default grounding
- Tool-use before model-only generation
- Fine-tuning only when justified
- Evaluation/monitoring are part of runtime

---

## Non-functional requirements (identity)

- Privileged administrative access must prefer just-in-time activation over standing privilege
- Access to sensitive resources must support periodic recertification
- Guest, partner, and agent access must expire or be reviewed rather than persist indefinitely
- Least-privilege role assignment is the default administrative model
- Access policies must be auditable for compliance and review

## Platform engineering model

The platform is not only an application runtime and control plane. It is also an internal
developer platform for teams that build, extend, operate, and govern ERP workloads on Azure.

Principles:

- Treat developers, operators, ML/AI builders, and platform consumers as customers
- Adopt a product mindset for platform capabilities
- Provide self-service with guardrails
- Expose paved/golden paths rather than forcing every team to build from scratch
- Use inventories and catalogs to manage assets, templates, services, and approved paths
- Measure adoption, speed, quality, and ease of use

## Internal platform users

Primary platform customers include:

- ERP application teams
- Extension/integration teams
- AI/agent teams
- Operations/SRE/release teams
- Security/governance stakeholders

The platform must optimize for reducing cognitive load while preserving required governance,
security, and cost controls.

## Self-service and paved paths

The platform should provide self-service workflows for common tasks, including:

- Starting a new workload or extension
- Provisioning approved infrastructure and secrets
- Deploying through governed pipelines
- Accessing observability and operational diagnostics
- Requesting approved tools, capabilities, and integrations

These self-service workflows must follow paved/golden paths that encode recommended and
supported patterns, while still allowing controlled extensibility where justified.

## Interfaces strategy

The platform should meet users where they already work.

Preferred interface order:

1. Existing engineering surfaces such as GitHub, Azure DevOps, CLI, IDE extensions, and
   chat/collaboration surfaces
2. APIs and automation entrypoints
3. Portal experiences only where they clearly reduce friction or aggregate otherwise
   fragmented workflows

Do not assume a greenfield portal is the first or primary interface for the platform.

## GitHub and Azure integration model

The platform must support a GitHub-native path for engineering workflows on Azure.

### Principles

- Source code and workflow definitions should live with the repository
- Repository-local automation should be supported through GitHub Actions where appropriate
- Azure authentication from GitHub should prefer federated identity / OIDC over long-lived
  client secrets
- Secrets required at runtime should be retrieved from managed secret stores rather than
  embedded into workflows

### Supported delivery surfaces

- GitHub Actions for repo-local build, test, package, and Azure deployment workflows
- Azure Pipelines for governed, multi-stage, organization-level release flows where those
  controls are required
- Explicit interop between GitHub and Azure DevOps when a repository-local workflow needs
  to trigger a governed Azure Pipelines flow

## Repository-native workflow definition

Workflow automation should be versioned with the application or platform code.

Examples include:

- GitHub Actions workflow files under `.github/workflows/`
- YAML pipeline definitions for governed Azure Pipelines flows
- Policy-as-code artifacts
- Infrastructure and deployment templates

The platform should treat workflow definitions as part of the product and platform source
of truth.

## Non-functional requirements (GitHub/Azure integration)

- GitHub-to-Azure authentication should prefer OIDC or managed identity over stored client secrets
- Workflows must support secure secret retrieval from Azure Key Vault where sensitive values
  are required
- Repo-local workflows and centrally governed release workflows must have clearly defined boundaries
- Policy/compliance automation should be executable from versioned code, not only through portal
  configuration

## Non-functional requirements (platform engineering)

- Platform capabilities must be consumable through self-service with governance guardrails
- Common provisioning and delivery tasks should be represented as reusable templates/building blocks
- Platform interfaces must minimize context switching for engineers
- Platform adoption and experience must be measured, not assumed
- The platform should evolve as a thinnest viable platform first, then expand incrementally

## Non-functional requirements (SaaS operations)

- The platform must bound blast radius for rollout and incident scenarios
- The control plane must be resilient and highly available
- Telemetry, monitoring, and communications are part of the service, not optional accessories
- Tenant-isolation decisions must be explicit per tier: data, app, control plane, and operations
- Near-zero-downtime maintenance is the target operating posture

---

## Non-goals

- Replace SAP or claim SAP feature parity
- Use SAP deployment topology as the normative target
- Use SAP naming as the organizing principle
- Build a generic multi-ERP hosting platform in V1

---

## References

- [Azure Well-Architected Framework](https://learn.microsoft.com/en-us/azure/well-architected/)
- [Azure Container Apps documentation](https://learn.microsoft.com/en-us/azure/container-apps/)
- [Azure AI Foundry documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/)
- [Azure Pipelines documentation](https://learn.microsoft.com/en-us/azure/devops/pipelines/)
- [spec/pulser-odoo-ph/](../pulser-odoo-ph/) — Pulser copilot spec (AI lane)
- [docs/architecture/DELIVERY_GOVERNANCE.md](../../docs/architecture/DELIVERY_GOVERNANCE.md) — delivery operating model
- [docs/architecture/BENCHMARK_MODEL.md](../../docs/architecture/BENCHMARK_MODEL.md) — benchmark doctrine
