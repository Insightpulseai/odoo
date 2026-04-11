# Go-Live Factory Methodology — Pulser for Odoo

The Go-Live Factory is the productized methodology for implementing and activating new Pulser SaaS tenants. It ensures that every production tenant is activated with a verified security posture, reconciled data, and scenario-based UAT sign-off.

---

## 1. The 4-Phase Activation Lifecycle (BOM 12, 13)

Every tenant implementation must progress through the following lifecycle stages, governed by the **Service Control Plane (SCP)**.

### Phase 1: Bootstrap (Project Initiation)
- **Goal**: Establish the implementation workspace and tenant goals.
- **Actions**:
    - Instantiate the Tenant Implementation Project.
    - Select the primary scenario (Project to Profit or Record to Report).
    - Map implementation team roles (Sponsor, Process Owner, Technical Lead).
    - Baseline success metrics (KPIs).

### Phase 2: Ingestion (Technical Linkage)
- **Goal**: Complete technical integration and initial data migration.
- **Actions**:
    - Configure the Hub-and-Spoke shell connectivity (OIDC handoff).
    - Execute initial data ingestion (Odoo sub-ledgers, GL, Employee records).
    - Execute the **Security Gate (FACT-SG-01)**: Least-privilege and Managed Identity validation.

### Phase 3: Validation (Quality Gate)
- **Goal**: Verify system integrity and user readiness.
- **Actions**:
    - Execute scenario-based UAT with tenant process owners.
    - Execute the **Data Reconciliation Gate (FACT-DG-01)**: Mandatory AR, AP, and Trial Balance reconciliation.
    - Verify specialist agent performance (Accruals, Tax, PPM).

### Phase 4: Live Site (Cutover & Stabilization)
- **Goal**: Transition to production and stabilize the environment.
- **Actions**:
    - Execute the production cutover checklist (Freeze -> Sync -> Unlock).
    - Enter the 30-day "Stabilization Window".
    - Reconcile the first-month close in the new system (First-Close Review).

## 2. Mandatory Activation Gates

Activation of the "Live Site" status is blocked until the following gates are satisfied:

| Gate ID | Area | Success Criteria | Authority |
|---------|------|------------------|-----------|
| **FACT-SG-01** | Security | Zero unknown Owners; Managed Identity only; PIM enabled. | Platform Admin |
| **FACT-DG-01** | Data | AR/AP/TB balance variance < 0.01% vs Legacy. | Finance Director |
| **FACT-UG-01** | Scenario | 100% of P1 user stories in scenario UAT marked "Done". | Process Owner |

## 3. Implementation Playbooks

Pulser provide standardized playbooks to guide the Factory execution:
- **Playbook-80**: Focus on WBS creation, Resource planning, and Profitability lifecycle.
- **Playbook-90**: Focus on Month-End close tasks, Reconciliation, and BIR compliance.

---

*Last updated: 2026-04-11*
