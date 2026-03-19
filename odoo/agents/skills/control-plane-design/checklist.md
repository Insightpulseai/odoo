# Checklist: Control Plane Design

## Pre-flight

- [ ] Tenant count and growth projection documented
- [ ] Required management operations listed
- [ ] Admin personas and access levels defined
- [ ] Integration points identified (provisioning, billing, monitoring)
- [ ] Control plane hosting decided (separate resource group, separate stamp)

## Tenant Catalog

- [ ] Schema defined with all required fields (id, name, tier, state, stamp, config_version)
- [ ] State machine documented (provisioning, active, suspended, deleted)
- [ ] Unique constraints on tenant ID and slug
- [ ] Indexes on frequently queried fields (state, stamp, tier)
- [ ] Soft delete with retention period (not hard delete)
- [ ] Catalog database backed up independently from tenant databases

## Configuration Management

- [ ] Configuration schema defined (JSON Schema)
- [ ] Configuration versioned — each change creates a new version
- [ ] Rollback procedure: revert to previous configuration version
- [ ] Feature flags per tenant supported
- [ ] Resource limits per tenant configurable (users, storage, API calls)
- [ ] Configuration changes applied without tenant restart where possible

## Health Monitoring

- [ ] Per-tenant health check defined (database connectivity, app responsiveness)
- [ ] Per-stamp health aggregated from tenant health checks
- [ ] Platform-wide health dashboard with drill-down
- [ ] Alerting for unhealthy tenants (threshold: N consecutive failures)
- [ ] Health check frequency appropriate (not too aggressive)
- [ ] Control plane health independent of tenant stamp health

## Admin Portal

- [ ] Tenant list with search, filter, and sort
- [ ] Tenant detail view: metadata, configuration, health, activity log
- [ ] Provisioning trigger from portal
- [ ] Suspend/resume actions with confirmation
- [ ] Configuration editor with validation
- [ ] Access restricted to platform admin role with MFA

## Control Plane API

- [ ] OpenAPI specification complete for all endpoints
- [ ] Authentication via Entra ID with admin roles
- [ ] Rate limiting configured (per client, per endpoint)
- [ ] Pagination for list endpoints
- [ ] Error responses follow RFC 7807 (Problem Details)
- [ ] API versioned (URL path or header)

## Audit Logging

- [ ] Audit log captures: who, what, when, which tenant, before/after state
- [ ] Logs are append-only (immutable)
- [ ] Retention policy defined (minimum 1 year for compliance)
- [ ] Query interface for audit log search
- [ ] Audit logs stored separately from tenant data

## Post-flight

- [ ] Control plane operational when a tenant stamp is down
- [ ] Tenant CRUD operations work end-to-end via API
- [ ] Admin portal loads and displays all tenants
- [ ] Audit trail complete for all operations
- [ ] Configuration rollback tested
