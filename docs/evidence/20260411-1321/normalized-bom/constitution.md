# Constitution — Pulser for Odoo

Pulser for PH is the canonical agentic ERP workspace for finance and project operations. This document defines the engineering invariants and architectural constraints for the platform.

---

## 1. SaaS Multitenancy Principle (BOM 1)

Pulser is a B2B multitenant SaaS platform.
- **Tenant Definition**: A tenant is a customer organization.
- **Independence**: Pulser Tenant != Odoo Company != Microsoft Entra Tenant.
- **Isolation**: Tenant-internal structures (branches, projects, business units) must remain within the SaaS tenant boundary.

## 2. Business Process Authority (BOM 2)

Pulser must be architected around formal end-to-end business scenarios:
- **Primary**: Project to Profit (Sales, Resourcing, Finance) and Record to Report (Close, Audit).
- **Supporting**: Source to Pay (AP, Expense), Order to Cash (Billing, Collections), and Administer to Operate (Control Plane).
- **Benchmark**: Dynamics 365 Project Operations is the canonical operating model benchmark.

## 3. Core Reasoning and Action (BOM 3, 4)

Pulser follows a "One Core, Three Shells" invariant.
- **The Core**: Authority resides in Odoo CE/OCA 18 (Action) and Odoo Documents (Evidence), served by Azure AI Foundry/Search (Reasoning).
- **Agentic Retrieval**: Pulser must use agentic retrieval and grounded flows linked to retained evidence.

## 4. Channel Shell Adapters (BOM 5)

- **Microsoft Agents SDK**: The preferred shell for M365, Teams, and enterprise multichannel delivery.
- **GitHub Copilot SDK**: An optional shell for internal developer/operator/release-management lanes.
- **Hierarchy**: No delivery shell may replace or bypass the Pulser Core authority or the SaaS control plane.

## 5. Control Plane Architecture (BOM 6, 7)

Pulser must maintain a productized separation between service operations and tenant administration.
- **Service Control Plane**: Governs onboarding, lifecycle, stamp assignment, and fleet-wide maintenance.
- **Tenant Admin Plane**: Governs tenant-specific settings, feature enablement, and evidence policies.

## 6. Deployment Stamp Invariant (BOM 8)

Pulser scales and isolates risks through deployment stamps.
- **Definition**: An independently deployable/recoverable slice of runtime and platform capacity.
- **Rollout**: Releases must be promoted stamp-by-stamp using ACA revision-based safe rollout (labels, traffic splitting).

## 7. Delivery and Governance (BOM 10, 11, 15)

Pulser follows the Microsoft CAF (Cloud Adoption Framework) and rigorous ALM discipline.
- **Execution**: All production changes flow through policy-gated pipelines (Git + PR).
- **Security**: Lease privilege is a hard production gate. No unknown Owners or unexplained root-scope privileges are permitted.
- **Evidence-First**: Telemetry, logs, and audit trails are first-class product requirements.

## 8. Live-Site-First Operations (BOM 16)

Pulser must be operated as a "live site," not merely deployed software.
- **Culture**: Engineering owns production quality and reliability.
- **Strategy**: Shift-right for production-only validation (canaries, fault-injection).

---

*Last updated: 2026-04-11*
