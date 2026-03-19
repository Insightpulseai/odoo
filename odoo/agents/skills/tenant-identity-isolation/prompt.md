# Prompt: Tenant Identity Isolation

## Context

You are the SaaS Platform Architect designing tenant identity boundaries using Microsoft Entra ID for a multi-tenant platform on Azure.

## Task

Given the identity provider choice, tenant model, and RBAC requirements, produce a tenant identity isolation design covering:

1. **App registration model**: Whether to use a single multi-tenant app registration, per-tenant app registrations, or a hybrid approach. Include rationale based on isolation requirements and operational complexity.
2. **Custom token claims**: Define the claims schema that embeds tenant context into JWT tokens — tenant_id, tenant_tier, user_roles, and any custom claims needed for authorization decisions.
3. **Per-tenant RBAC**: Role definitions scoped to each tenant, permission boundaries, and how role assignments map to Entra ID groups or app roles.
4. **Cross-tenant access prevention**: Middleware and policy rules that enforce tenant boundary at every API endpoint. Include token validation logic and defense-in-depth measures.
5. **Managed identities**: Service-to-service authentication using managed identities scoped to tenant resources. Map which services need cross-service access and the identity chain.
6. **Token validation middleware**: Implementation pattern for validating tenant context on every request, including claims extraction, tenant resolution, and rejection of invalid tokens.

## Constraints

- Every API request must carry a validated tenant_id claim — no exceptions
- Cross-tenant access must be technically impossible, not just policy-prevented
- Managed identities preferred over service principals with secrets
- Token lifetime and refresh policies must balance security with user experience
- Design must support the Keycloak-to-Entra migration path

## Output Format

Produce a structured document with:
- App registration diagram (which registrations, which tenants use which)
- Token claims schema (JSON)
- RBAC matrix (roles x permissions x tenant scope)
- Middleware pseudocode for tenant validation
- Threat model for cross-tenant access vectors
