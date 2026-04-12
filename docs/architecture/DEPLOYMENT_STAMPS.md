# Deployment Stamp Architecture — Pulser for Odoo

This document formalizes the Deployment Stamp as the canonical unit of scale, isolation, and blast-radius control for the Pulser for Odoo platform.

---

## 1. The Scaling Unit (BOM 8)

A **Deployment Stamp** is a self-contained, independently deployable and recoverable slice of the platform.
- **Isolation Boundary**: Each stamp resides in a dedicated Azure Resource Group (`rg-ipai-stamp-<id>-prod`).
- **Blast Radius**: Failure of a stamp (e.g., database corruption, regional outage) must not affect the availability or data integrity of other stamps.

### Stamp Composition
Every physical Pulser stamp contains:
1. **Odoo Runtime**: ACA services for Web, Worker, and Cron.
2. **Agent Runtime**: ACA services for the reasoning/retrieval plane.
3. **Database**: Dedicated PostgreSQL database (Flexible Server instance per stamp or shard).
4. **Evidence Vault**: Azure Files / Storage Account for Odoo Documents.
5. **Ingress**: Map to Global Azure Front Door via the **Service Control Plane**.

## 2. Rollout Groups and Promotion

Stamps are organized into groups to support progressive, production-only validation (Shift-Right).

| Group | Stamps | Tenant Profiles | Rollout Trigger |
|-------|--------|-----------------|-----------------|
| **Canary** | `stamp-00` | Internal IPAI, Platform Admins | Pipeline direct deploy |
| **Early Adopter (EA)** | `stamp-01`, `stamp-02` | Registered beta/pilot customers | Automated gate pass |
| **General Availability (GA)**| `stamp-03`+ | Production fleet | Manual/Timed approval |

## 3. Progressive Rollout Mechanism

All stamp updates must use **ACA Revision Labels** and **Traffic Splitting**.

### The "Stable" Label
- Each Container App maintains a revision labeled `stable`.
- 100% of traffic routes to `stable` by default.

### The "Latest" Rollout
1. Deploy new code as a new revision.
2. Verify health in isolation via the unique revision URL.
3. Shift traffic 10% to the new revision (Canary).
4. monitor telemetry (Error rates, latency).
5. If clean, shift 50% -> 100%.
6. Update the `stable` label to the new revision.
7. Decommission the previous `stable` revision.

---

## 4. Resource Group Isolation

To prevent accidental resource sharing:
- No resource in a stamp RG may reference a resource in another stamp RG (except for the shared Control Plane / Front Door).
- All stamp-local secrets must be stored in the **Tenant Registry** or a stamp-scoped Key Vault secrets set.

---

*Last updated: 2026-04-11*
