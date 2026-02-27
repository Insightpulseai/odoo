---
name: github-well-architected
description: Community-driven standards for designing, deploying, and optimizing resilient GitHub solutions.
---

# GitHub Well-Architected Framework

This skill encapsulates opinionated best practices for managing GitHub organizations and repositories at scale, focused on productivity, security, and governance.

## Key Pillars

### 1. Productivity & Velocity (The Developer Tools Equivalent)

Streamline workflows and accelerate team output. This pillar serves as the equivalent to **Azure Developer Tools**.

- **GitHub Actions (Azure Pipelines Equivalent)**: Automate CI/CD; use reusable workflows and composite actions.
- **GitHub Projects + Issues (Azure Boards Equivalent)**: Projects for planning views; Issues for work items to plan, track, and discuss work.
- **GitHub Codespaces (Azure DevTest Labs / Dev Box Equivalent)**: Ephemeral dev/test environments via Codespaces + prebuilds/devcontainers, and CI-provisioned preview environments.
- **Environments & Secrets/Variables (Azure App Configuration Equivalent)**:
  - _Mapping_: GitHub Environments (deployment gates) + Secrets/Variables (static config).
  - _Note_: An external config plane (e.g., OpenFeature provider) is required for runtime flagging/dynamic config.
  - _Start_: Identify repetitive manual tasks suitable for automation.
  - _Mature_: Standardize automation patterns across teams.
  - _Advance_: Use autonomous agents and self-healing pipelines.
- **Design for Engineering System Success**:
  - _Advance_: Focus on a "golden path" for developers—paved roads that minimize cognitive load while enforcing standards.

### 2. Collaboration & Inner-sourcing

Foster open knowledge sharing and transparent management.

- **CODEOWNERS**: Define clear ownership for specific paths to ensure quality reviews.
- **Discussions**: Use GitHub Discussions for RFCs, Q&A, and community building.
- **Transparency**: Favor internal/public visibility for shared tools and libraries.

### 3. Application Security (AppSec)

Embed security into every stage of the development lifecycle.

- **GitHub Advanced Security (GHAS)**: Enable CodeQL, Secret Scanning, and Dependency Review.
- **Dependabot**: Automate dependency updates and security patch management.
- **Branch Protection**: Enforce signed commits, PR reviews, and passing status checks.

### 4. Governance & Compliance

Balance innovation with oversight and accountability.

- **Enterprise Policies**: Enforce enterprise-wide rules for repo visibility and runner usage.
- **Audit Logs**: Monitor audit logs for sensitive actions and external access.
- **Custom Roles**: Use fine-grained permissions for least privilege access.
- **Identity Federation**: Integrate with Entra ID (SAML/SCIM) for automated user lifecycle.

## Golden Path Contract (Engineering System Success)

A repository is “on the Golden Path” if it has:

- A build pipeline (Actions) with deterministic steps + cached dependencies.
- A test gate (unit + lint; optional E2E) that blocks merges.
- Deployment environments (dev/stage/prod) with protected approvals where needed.
- Secrets/variables owned by environments (no repo-wide secret sprawl).
- A documented “how to ship” runbook (`docs/` + CI references).
- Policy gates for architectural SSOT artifacts (e.g., diagram export drift gates, allowlists).

### Golden Path Outputs (Required Artifacts)

- `.github/workflows/*` (CI/CD)
- `docs/architecture/*` (SSOT + runtime snapshot + diagrams)
- `scripts/ci/*` (policy enforcement)

### 5. Resilient Architecture

Design scalable, resilient, and efficient GitHub environments.

- **Design for Scalability**:
  - Implement dynamic scaling for self-hosted runners and automate capacity planning.
- **Design for Resiliency**:
  - Establish reference architecture blueprints with explicit redundancy and failover mechanisms.
- **Design for Observability**:
  - Proactively detect issues via Distributed Tracing, Error Tracking (equivalent to Azure Managed Grafana/App Insights), and AI-powered feedback tools.
- **Design for Interoperability**:
  - Use standard data formats and real-time Webhook updates for seamless system-to-system integration.
