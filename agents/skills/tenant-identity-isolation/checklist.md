# Checklist: Tenant Identity Isolation

## Pre-flight

- [ ] Identity provider selected (Entra ID, Entra External ID)
- [ ] Tenant isolation requirements classified (shared, dedicated, hybrid)
- [ ] Existing identity system documented (Keycloak migration path if applicable)
- [ ] Compliance requirements for identity data residency identified

## App Registration

- [ ] App registration model selected and documented with rationale
- [ ] App registrations created with correct audience and sign-in settings
- [ ] Reply URLs configured per environment (dev, staging, prod)
- [ ] API permissions follow least-privilege (no broad Graph permissions)
- [ ] Client secrets rotated on schedule or replaced with certificates/managed identities

## Token Claims

- [ ] Custom claims schema defined (tenant_id, tier, roles)
- [ ] Claims mapping policy configured in Entra ID
- [ ] Token includes tenant_id on every authentication — no fallback to header/query
- [ ] Claims transformation tested for all tenant tiers
- [ ] Token lifetime appropriate for use case (access: short, refresh: longer)

## Per-Tenant RBAC

- [ ] Roles defined per tenant (admin, member, viewer at minimum)
- [ ] Role assignments use Entra ID groups or app roles
- [ ] No role grants cross-tenant access
- [ ] Privileged roles require PIM activation
- [ ] Role changes audited in Entra ID sign-in logs

## Cross-Tenant Prevention

- [ ] Token validation middleware rejects requests without tenant_id claim
- [ ] Database queries always include tenant_id filter (defense-in-depth)
- [ ] API gateway validates tenant scope before routing
- [ ] Penetration test scenarios for cross-tenant access documented
- [ ] Security event logging for suspected cross-tenant attempts

## Managed Identities

- [ ] User-assigned managed identities created per service (not system-assigned for portability)
- [ ] Each managed identity scoped to minimum required resources
- [ ] No shared managed identities across tenant boundaries
- [ ] Managed identity used instead of connection strings where possible

## Post-flight

- [ ] End-to-end authentication tested for each tenant tier
- [ ] Cross-tenant access attempt tested and confirmed blocked
- [ ] Token tampering tested (modified tenant_id) and confirmed rejected
- [ ] Managed identity access verified — correct resources only
- [ ] Identity audit trail complete and queryable
