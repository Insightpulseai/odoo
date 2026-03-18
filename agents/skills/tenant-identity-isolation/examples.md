# Examples: Tenant Identity Isolation

## Example 1: Single Multi-Tenant App Registration (Shared Pool)

**Scenario**: 50 tenants sharing a single Odoo CE deployment on Azure Container Apps.

**App registration**: One multi-tenant app registration in the platform's Entra ID tenant.

**Token claims**:
```json
{
  "iss": "https://login.microsoftonline.com/{platform-tenant-id}/v2.0",
  "sub": "user-object-id",
  "aud": "api://ipai-odoo-multitenant",
  "tenant_id": "acme-corp",
  "tenant_tier": "standard",
  "roles": ["odoo.user", "odoo.sale_manager"],
  "exp": 1711900800
}
```

**RBAC model**:
| Role | Permissions | Scope |
|------|------------|-------|
| odoo.admin | Full module access, user management | Single tenant |
| odoo.user | Read/write on assigned modules | Single tenant |
| odoo.viewer | Read-only on assigned modules | Single tenant |

**Validation middleware** (Python/FastAPI):
```python
async def validate_tenant(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    claims = verify_jwt(token, audience="api://ipai-odoo-multitenant")
    tenant_id = claims.get("tenant_id")
    if not tenant_id:
        raise HTTPException(403, "Missing tenant_id claim")
    request.state.tenant_id = tenant_id
    request.state.roles = claims.get("roles", [])
```

---

## Example 2: Per-Tenant App Registration (Enterprise Isolation)

**Scenario**: Enterprise tenant requiring dedicated identity boundary.

**App registration**: Dedicated app registration per enterprise tenant.

**Configuration**:
- App: `ipai-odoo-{tenant-id}` (e.g., `ipai-odoo-acme-enterprise`)
- Audience: `api://ipai-odoo-acme-enterprise`
- Reply URL: `https://acme.erp.insightpulseai.com/auth/callback`
- Managed identity: `mi-ipai-prod-acme-odoo` scoped to `rg-ipai-prod-tenant-acme`

**Cross-tenant prevention**:
- API gateway (APIM) routes `acme.erp.insightpulseai.com` to dedicated backend
- Token audience must match the tenant-specific app registration
- Managed identity cannot access resources outside `rg-ipai-prod-tenant-acme`

---

## Example 3: Keycloak-to-Entra Migration Path

**Scenario**: Existing platform uses Keycloak for SSO, migrating to Entra ID.

**Migration steps**:
1. Deploy Entra ID app registration alongside Keycloak
2. Configure dual-IdP support in Odoo (accept tokens from both)
3. Migrate tenant users to Entra ID with matching UPN
4. Map Keycloak roles to Entra ID app roles
5. Switch DNS from Keycloak to Entra ID login endpoint
6. Decommission Keycloak after 30-day parallel operation

**Tenant claim mapping**:
- Keycloak: `realm_access.roles` contains tenant roles
- Entra ID: `roles` claim contains app roles
- Middleware accepts both formats during migration window
