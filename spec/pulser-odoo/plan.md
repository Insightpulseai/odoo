# Implementation Plan — Pulser for Odoo

This plan defines the implementation roadmap for the Pulser for Odoo SaaS platform, organized across core runtime, delivery shells, and the go-live factory.

---

## 1. SaaS Platform Foundation (BOM 1, 6, 7, 8)

### Control Plane Implementation
Establish the dual control-plane model for resilient multitenancy:
- **Service Control Plane**: Implement onboarding wizards, stamp placement logic, and fleet-wide monitoring in `agent-platform`.
- **Tenant Admin Plane**: Implement tenant-scoped settings and feature flags.

## 46. Umbrella / child-bundle operating model

### Goal
Make `spec/pulser-odoo/` the platform umbrella while keeping business capability design bounded in child bundles.

### Bundle layout
- `pulser-odoo` = platform and cross-cutting authority
- `pulser-project-to-profit` = project/delivery/profitability authority
- `pulser-record-to-report` = finance-control/close/reporting authority

### Design rule
Future major business capabilities should be introduced as bounded child bundles rather than expanding the umbrella PRD indefinitely.

## 47. Cross-bundle implementation dependencies

### Project-to-Profit outputs required by Record-to-Report
- billing-readiness signals
- project budget/forecast/actual signals
- profitability and margin summaries
- accrual-relevant delivery signals
- evidence-linked project-finance artifacts

### Record-to-Report outputs required by umbrella platform
- finance control status
- close readiness
- publishable finance/reporting packs
- tax/compliance support outputs
- audit-safe evidence views

## 48. Microsoft 365 channel-surface plan

### Goal
Enable optional Teams / Outlook / Word / Excel channel delivery using the canonical **Microsoft 365 Copilot Extensibility** model.

### Design rules
- treat M365 Agents Toolkit as scaffolding and channel packaging only
- implement **Declarative Agents** for P2P and RTR personas
- expose Pulser actions via **API Plugins**
- preserve canonical business logic and policy resolution in Pulser
- require the same RBAC, evidence, and mutation controls as native Pulser surfaces

### Deployment Stamp Topology
Scale and isolate tenants via independent capacity slices using Azure Container Apps:
- **Composition**: Scoped Odoo runtime, Pulser gateway, and agent services.
- **Rollout**: Promote releases stamp-by-stamp via Revision Labels and traffic splitting.
- **Decision (Locked)**: **Dedicated PostgreSQL Flexible Server per stamp** is mandatory for blast-radius control and performance isolation.
- **Decision (Locked)**: **Azure Pipelines** is the canonical release and promotion authority.

## 2. Layered Delivery Model: Core and Shells (BOM 3, 4, 5)

### Authority and Orchestration
Keep the reasoning authority in the **Pulser Core Hub** (Foundry + Odoo) while delivery reach is handled through stateless spoke adapters:
- **Enterprise Shell (M365)**: Teams and Outlook delivery via Microsoft Agents SDK.
- **Engineering Shell (DevOps)**: Operator and release-management assistants via GitHub Copilot SDK.
- **Office Studios**: High-fidelity Excel (ODATA reconciliation) and Outlook (Collections sidebar) adapters.

## 3. Go-Live Factory (BOM 12, 13)

### Implementation Lifecycle (Ph 41)
Adopt a structured 4-phase progression from initiation to stabilization:
- **Phase 1: Bootstrap (Initiation)**: Implementation wizard instance, goal mapping, and role assignment.
- **Phase 2: Ingestion (Technical)**: Identity handoff, technical integration, **Migration Intensity** (Master, Open Items, 24m TB), and **Security Gate** validation.
- **Phase 3: Validation (Quality)**: **Scenario-based UAT** (100% P1 sign-off) and **Data Reconciliation Gate** (AR/AP/Trial Balance variance reporting).
- **Phase 4: Live Site (Cutover)**: **T-minus Cutover Checklist** execution, enter 30-day stabilization window, and perform **First-Close Review**.

## 4. Live-Site Operations Model (BOM 16)

### Operational Posture
- **Engineering Ownership**: Build-it-own-it culture for production reliability.
- **Telemetry**: actionable alerting tied to customer impact.
- **Verification**: Shift-right validation for production-only behavior (chaos, failover).

### Integration and Connectivity
- **Data Mobility**: Implement ODATA v4 read/write-proposal bridges for **Excel Studio** reconciliation workbooks.
- **Event-Driven**: Enable business-event handling via Azure Service Bus for cross-app orchestration.
- **Contextual Sidebars**: Implement context-aware session providers for **Outlook Studio** collections.

### Performance and Scalability Review
- **Batch Processing**: Implement and verify idempotent asynchronous batch execution for high-volume reconciliations.
- **Close Cycle Load**: Baseline system performance against a simulated 100k-transaction month-end close.

### E2E Business Scenarios (Ph 39-40)
- **Scenario Mapping**: Map all specialists (AP, Tax, Close, PPM) to Project to Profit or Record to Report scenarios.
- **Accrual Visibility**: Implement query-based "Outstanding Liability" (recorded vs. paid) detection.
- **Card Hygiene**: Implement query-based "Unassigned/Unsubmitted" card transaction detection.

## 5. Persona and Governance (Ph 45-47)
- **Finance RBAC Model**: Implement the 5-layer architecture (Role, Band, Evidence, Action, UI).
- **Cockpit Specialization**: Adapt delivery shells into persona-based "Cockpits" (Close, Source-to-Pay, BIR, Treasury) based on high-density UI requirements.
- **Interaction Logic**: **Action pills** (e.g., Approve, View, Schedule) are the primary interactions for approvals and queues. Chat is secondary for nuance.
- **Action Guard**: Implement granular tool-call interception and authorization based on Agent Action Scopes.
- **Evidence Scoping**: Enforce retrieval boundaries (Self, Team, Entity, Consolidated) within the reasoning hub.

---

## 41. Normalized Delivery Model
Pulser follows a productized delivery model:
- **Git Authority**: Version control is the source of truth for code, config, and infrastructure (IaC).
- **Pipeline Gates**: All production changes are policy-gated and executed via Azure Pipelines or GitHub Actions.
- **Audit Trails**: Every release must produce an **Evidence Pack** (Stage 4 of the pipeline).

## 42. Estate Convergence
Unify the current Azure estate into the canonical model:
- **Shared Prod**: Resource group for global services (Front Door, Key Vault, Log Analytics).
- **Environment Stamps**: Environment-specific resource groups (dev, staging, prod) containing the deployment stamps.
- **Foundry Hook**: Deep integration of Azure AI Foundry as the shared reasoning backbone across all stamps.

---

*Last updated: 2026-04-11*
