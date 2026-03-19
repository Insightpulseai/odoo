# Checklist: SaaS Identity & Access Design

## Identity Model

- [ ] Tenant identity and user identity are distinct concepts in the design
- [ ] Tenant-id is a first-class entity, not derived from user attributes
- [ ] User-to-tenant mapping is explicit (not assumed from email domain alone)
- [ ] Multi-tenant user support defined (user belonging to multiple tenants)
- [ ] Service accounts / machine identities carry tenant context

## Token Claims

- [ ] tenant-id is a required claim in all access tokens
- [ ] Audience (aud) claim is restricted to the target service
- [ ] Issuer (iss) claim is validated against known issuers
- [ ] Role claims are tenant-scoped (not global)
- [ ] Token lifetime and refresh strategy defined
- [ ] Token validation middleware enforces tenant-id presence

## RBAC Design

- [ ] Per-tenant role hierarchy defined (admin, member, viewer minimum)
- [ ] Platform-level roles separated from tenant-level roles
- [ ] Role assignment mechanism documented (API, admin UI, federation mapping)
- [ ] Permission model defined (role-to-permission mapping)
- [ ] Default role for new users within a tenant specified

## Zero Trust Controls

- [ ] MFA required for all tenant admins
- [ ] Conditional access policies defined per tier
- [ ] Session timeout and re-authentication rules defined
- [ ] Device compliance requirements documented (if applicable)
- [ ] Network-based access restrictions defined (if applicable)

## Federation

- [ ] SAML and/or OIDC federation supported for enterprise tenants
- [ ] Claim mapping from external IdP to platform claims documented
- [ ] JIT (just-in-time) user provisioning defined
- [ ] Federation metadata exchange process documented
- [ ] Fallback authentication path defined when federation is unavailable
