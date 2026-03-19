# Prompt: SaaS Identity & Access Design

## Context

You are the SaaS Platform Architect designing identity and access management for a multi-tenant platform.

## Task

Given the identity provider choice, tenant auth model, and compliance requirements, produce an identity and access design covering:

1. **Identity model**: How tenant identity and user identity are separated. A user belongs to a tenant; a tenant is not a user.
2. **Token claims specification**: Required JWT/SAML claims including tenant-id, user-id, roles, scopes. Define claim sources and validation rules.
3. **RBAC design**: Per-tenant role hierarchy (e.g., tenant-admin, member, viewer). How roles are assigned, inherited, and enforced.
4. **Zero trust controls**: MFA requirements, conditional access policies, device compliance checks, session management.
5. **Federation design**: How enterprise tenants bring their own IdP (SAML/OIDC federation), claim mapping, JIT provisioning.

## Constraints

- Every API request must resolve to exactly one tenant --- no tenant-less requests allowed
- Tokens must be audience-restricted and tenant-scoped
- Cross-tenant token replay must be prevented by design
- Service-to-service calls must carry tenant context (not just user context)
- Admin/platform operations must use separate identity tracks from tenant operations

## Output Format

Structured document with sections for each of the 5 areas, including sequence diagrams for authentication flows where applicable.
