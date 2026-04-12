# SaaS Control Plane Architecture — Pulser for Odoo

This document formalizes the architecture of the Pulser SaaS Control Plane, ensuring a clear separation between Service operations and Tenant administration.

---

## 1. Plane Responsibility Matrix (BOM 6, 7)

Pulser is governed by two distinct control planes to ensure isolation, security, and scalability.

### Service Control Plane (SCP)
The SCP owns the platform and its global infrastructure.
- **Global Tenant Registry**: Authoritative list of all Pulser tenants (metadata, status, contract level).
- **Stamp Placement Engine**: Logic for assigning a tenant to a specific **Deployment Stamp** (BOM 8).
- **Fleet Rollout Controller**: Manages progressive rollout sequences across stamps (Canary -> EA -> GA).
- **Global Feature Flagging**: Enables/disables capabilities across the entire platform.

### Tenant Management Plane (TMP)
The TMP owns the customer instance and its configuration.
- **Tenant Registry (Local)**: Local metadata specific to the tenant's Odoo/Entra setup.
- **Onboarding Milestone Tracker**: Tracks the tenant's progress through the **Onboarding Protocol** (BOM 12).
- **Tenant User Management**: Manages tenant admins and users within the tenant boundary.
- **Tenant Feature Enablement**: Manages tenant-specific feature flags and integration settings.

## 2. Global Tenant Registry Schema

| Field | Description | Scope |
|-------|-------------|-------|
| `tenant_id` | Unique UUID for the customer organization | Global |
| `tenant_name` | Humman-readable customer name | Global |
| `stamp_id` | Pointer to the assigned Deployment Stamp | Global |
| `status` | Onboarding, Active, Suspended, Decommissioned | Global |
| `release_group` | Canary, Early Adopter, General Availability | Global |
| `entra_tenant_id` | Customer's Entra ID for auth mapping | Global |

## 3. Fleet-Wide Rollout Strategy (BOM 8)

Pulser releases are promoted through a tiered sequence of deployment stamps to minimize blast radius.

1. **Canary Stamp**: Internal test tenants and internal IPAI orgs.
2. **Early Adopter (EA) Stamp**: Selected "Beta" customers and low-risk production instances.
3. **General Availability (GA) Stamps**: The bulk of the production fleet.

**Rule**: All stamp updates must use **ACA Revision Labels** and traffic splitting to allow for instant rollback and hitless deployment.

---

## 4. Administrative Auth Handoff

- **Service Admins**: Authenticate against the Pulser Service Entra Tenant.
- **Tenant Admins**: Authenticate against their own Customer Entra Tenant.
- **Service-to-Tenant Support**: Support access must use JIT (Just-In-Time) elevation with tenant-level approval or logging.

---

*Last updated: 2026-04-11*
