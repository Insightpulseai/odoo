# Examples: SaaS Identity & Access Design

## Example 1: Platform-Managed Identity (Entra ID B2C)

**Scenario**: SaaS platform manages all user identities via Azure AD B2C.

**Identity model**:
- Tenant record in platform database with unique tenant-id (UUID)
- Users sign up via B2C, linked to tenant via invitation or domain matching
- B2C custom policy injects tenant-id into token claims

**Token claims**:
```json
{
  "iss": "https://ipai.b2clogin.com/...",
  "aud": "api://ipai-platform",
  "sub": "user-uuid",
  "tid": "tenant-uuid",
  "roles": ["tenant-admin"],
  "scp": "Platform.ReadWrite"
}
```

**RBAC**: Platform DB stores tenant-role assignments. Middleware validates `tid` + `roles` on every request.

---

## Example 2: Federated Enterprise Identity (Entra ID + SAML)

**Scenario**: Enterprise tenants bring their own Entra ID via SAML federation.

**Identity model**:
- Tenant record includes federation metadata URL
- Enterprise users authenticate via their corporate IdP
- Platform maps SAML assertions to platform claims via claim transformation rules

**Claim mapping**:
```
SAML NameID           -> sub (user identifier)
SAML groups           -> roles (mapped via tenant config)
Platform tenant-id    -> tid (injected by platform, not from SAML)
```

**Key design decision**: tenant-id is NEVER sourced from the external IdP. The platform resolves tenant-id from the federation configuration, then injects it.

---

## Example 3: Service-to-Service with Tenant Context

**Scenario**: Backend service A calls backend service B on behalf of a tenant.

**Token flow**:
1. Service A receives user request with tenant-scoped token
2. Service A extracts tenant-id from incoming token
3. Service A requests a service token from token service, including tenant-id
4. Service B validates service token and enforces tenant-id in data access

**Anti-pattern**: Service A calls Service B with a platform-wide service account that has no tenant context. This breaks tenant isolation.
