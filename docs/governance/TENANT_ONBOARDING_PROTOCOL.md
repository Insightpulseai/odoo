# Tenant Onboarding Protocol — Pulser for Odoo

This protocol defines the mandatory 4-Phase lifecycle for onboarding new production tenants to the Pulser platform. Compliance with this protocol is required to satisfy **SC-PH-16** through **SC-PH-22**.

---

## Phase A: Bootstrap (Planning & Resource Mapping)

**Goal**: Establish the technical and business foundation for the tenant.
- **Resource Mapping**: Identify and map the Customer Entra Tenant and assign a Deployment Stamp.
- **Goal Alignment**: Document the tenant's primary KPIs (e.g., "Reduce month-end close by 3 days").
- **Identity Setup**: Configure Managed Identities and RBAC for the Odoo/Pulser bridge.

## Phase B: Ingestion (Data & Integration)

**Goal**: Ingest legacy data and establish source-of-truth connectivity.
- **Legacy Migration**: Execute the structured data import for Open AR/AP, Trial Balances, and Project WBS.
- **Integration Test**: Verify connectivity between Odoo and the Pulser Agent Runtime.
- **Grounding Setup**: Index the tenant's Odoo Documents vault into Azure AI Search.

## Phase C: Validation (UAT & Cutover)

**Goal**: Verify system correctness and execute the final cutover.
- **Scenario UAT**: Tenant sign-off on critical business scenarios (Project-to-Profit, Record-to-Report).
- **Balance Reconciliation**: Mandatory check of AR/AP aging and Trial Balance vs. legacy system.
- **Go-Live Gate**: Final check of the "Feature Ship-Readiness Checklist" (BOM 11).

## Phase D: Live Site (Stabilization & First-Close)

**Goal**: Stabilize operations and align with the first monthly close cycle.
- **Stabilization Window**: 30-day "Hyper-care" window with daily status reviews.
- **First-Close Alignment**: Formal audit of the first month-end close using Pulser Close Packs.
- **Performance Review**: Baseline check of transaction processing times and agent grounded-answer quality.

---

## 2. Activation State Management

A tenant's status in the **Global Tenant Registry** must be updated at each milestone:
1. `onboarding`: Phase A to C.
2. `active`: Phase D completion.
3. `suspended`: Emergency isolation or contract termination.
4. `decommissioned`: Data purge and resource release.

---

*Last updated: 2026-04-11*
