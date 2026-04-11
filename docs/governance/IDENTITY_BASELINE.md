# Identity Governance Baseline — Pulser for Odoo

This document defines the mandatory identity governance policies for the Pulser for Odoo platform. All infrastructure and operational changes must adhere to these baselines.

---

## 1. Least Privilege Principle

- **Standing Access**: Permanent "Active" roles must be restricted to the absolute minimum required for automated runtime operations.
- **Admin Elevation**: Human administrators must use **Eligible** assignments via Microsoft Entra Privileged Identity Management (PIM).
- **Time-Bound**: Admin elevation is restricted to a maximum of **4 hours** for Owner/Security roles and **8 hours** for Contributor/Maintenance roles.
- **Approval**: Elevation to **Owner** requires explicit approval from a secondary platform administrator.

## 2. Root-Scope Governance

- **Zero Tolerance**: No standing privileged assignments (Owner, Contributor, User Access Administrator) are permitted at the **Root (/)** scope.
- **Remediation**: Any root-scope assignment found during audit must be remediated immediately.

## 3. Agent and Service Identity

- **Managed Identities**: All Pulser runtime services (Odoo, Gateway, Agents) must use **User-Assigned Managed Identities** for service-to-service authentication.
- **Key-Based Auth**: The use of client secrets or account keys is restricted to secondary/internal adapters where Entra ID is not supported. All secrets must be stored in Azure Key Vault.
- **Accountability**: Every production agent identity must have a defined **Sponsor** (Human) and **Operational Owner** (System/Team).

## 4. Environment-First RBAC

- **Separation of Scope**: Roles should be assigned at the **Resource Group** level rather than Subscription level wherever practical.
- **Deployment Automation**: The DevOps Service Principal must be restricted to **Contributor** at individual deployment resource groups. Subscription-level Owner is prohibited for service principals.
- **Production Isolation**: Production identities must have zero access to developer or sandbox environments, and vice versa.

## 5. Audit and Compliance

- **Assignment Reviews**: Role assignments must be reviewed quarterly.
- **Telemetry**: All PIM activations and role assignment changes must emit actionable alerts to the platform-admins group.
- **Orphaned Principals**: Unknown or orphaned principals (those with no resolvable Entra identity) must be removed within 24 hours of discovery.

---

## Controlled Documents
- **RBAC Matrix**: [`ssot/governance/azure-rbac-remediation.yaml`](../../ssot/governance/azure-rbac-remediation.yaml)
- **Remediation Ticket**: [`docs/governance/AZURE_IAM_REMEDIATION.md`](AZURE_IAM_REMEDIATION.md)
- **Target IaC**: [`infra/azure/identity/rbac-governance.bicep`](../../infra/azure/identity/rbac-governance.bicep)

---

*Last updated: 2026-04-11*
