# Prompt: Control Plane Design

## Context

You are the SaaS Platform Architect designing the control plane for a multi-tenant platform on Azure.

## Task

Given the tenant count, management operations, and admin personas, produce a control plane design covering:

1. **Tenant catalog**: Database schema storing tenant metadata — ID, name, tier, state (active, suspended, provisioning, deleted), stamp assignment, creation date, configuration version. This is the single source of truth for tenant state.
2. **Configuration management**: How tenant-specific settings are stored, versioned, and applied. Cover feature flags, resource limits, branding overrides, and module selections. Include rollback for configuration changes.
3. **Health monitoring**: How the control plane aggregates health from tenant stamps. Per-tenant health status, stamp-level health, and platform-wide dashboard. Alerting for unhealthy tenants.
4. **Admin portal**: UI for platform operators — tenant list with search/filter, tenant detail view, provisioning trigger, suspend/resume, configuration editor, health dashboard.
5. **Control plane API**: OpenAPI specification for tenant CRUD, configuration management, health queries, and administrative actions. Authentication via Entra ID with admin roles. Rate limiting to protect the control plane.
6. **Audit logging**: Immutable audit trail for all control plane operations — who did what, when, to which tenant. Retention policy and query interface.

## Constraints

- Control plane must run in a separate fault domain from tenant workloads
- Tenant catalog is the authoritative source — no shadow state in other systems
- All mutations must go through the API (no direct database edits)
- Admin portal access requires MFA
- Audit logs must be immutable (append-only, no delete capability)

## Output Format

Produce a structured document with:
- Tenant catalog ERD
- Configuration schema (JSON Schema)
- Health aggregation architecture diagram
- Admin portal wireframes (text-based)
- OpenAPI spec skeleton
- Audit log schema
