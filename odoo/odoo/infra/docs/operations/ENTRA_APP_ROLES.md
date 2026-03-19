# Entra App Roles — Operations Guide

> Version: 1.0.0
> Last updated: 2026-03-15
> Artifacts: `infra/entra/app-roles-manifest.json`, `scripts/entra/register-app-roles.sh`, `scripts/entra/assign-app-role.sh`
> Reference: `infra/docs/architecture/CONTEXT_AND_RBAC_MODEL.md`

---

## Overview

InsightPulseAI uses Azure Entra (Azure AD) app roles for in-application authorization. App roles appear in the `roles` claim of the access token. The backend reads this claim to compute `permitted_tools` and `retrieval_scope` in the context envelope before sending requests to Foundry.

There are 15 app roles across 7 domains: Product, Finance, Marketing, Media/Retail, Analytics, Copilot, and Operations.

---

## 1. Register App Roles

### Prerequisites

- Azure CLI installed and authenticated (`az login`)
- Permission: `Application.ReadWrite.All` or Application Administrator role in the tenant
- The app registration object ID (not the application/client ID)

### Find the app object ID

```bash
# By display name
az ad app list --display-name "InsightPulseAI" --query "[].{objectId:id, appId:appId, name:displayName}" -o table

# By app (client) ID
az ad app show --id <app-client-id> --query "id" -o tsv
```

### Apply roles from manifest

```bash
# With explicit app object ID
./scripts/entra/register-app-roles.sh --app-id <app-object-id>

# With environment variable
export AZURE_APP_OBJECT_ID=<app-object-id>
./scripts/entra/register-app-roles.sh
```

The script reads `infra/entra/app-roles-manifest.json`, extracts the `appRoles` array, and applies it via `az ad app update`. It then validates by fetching the app registration back and comparing role counts.

### Verify registration

```bash
az ad app show --id <app-object-id> --query "appRoles[].{value:value, displayName:displayName, id:id}" -o table
```

Expected output: 15 roles, all with `isEnabled: true`.

---

## 2. Assign Roles to Users

### Single user assignment

```bash
./scripts/entra/assign-app-role.sh \
  --app-id <app-object-id> \
  --principal-id <user-object-id> \
  --role-value finance.close.operator
```

### Find the user object ID

```bash
az ad user show --id user@insightpulseai.com --query id -o tsv
```

### Assign to a service principal

```bash
# Get the service principal object ID
az ad sp list --filter "displayName eq 'my-service'" --query "[0].id" -o tsv

# Assign
./scripts/entra/assign-app-role.sh \
  --app-id <app-object-id> \
  --principal-id <sp-object-id> \
  --role-value copilot.action
```

### Assign via group (bulk)

Groups cannot be assigned app roles directly via the manifest scripts. Use the Entra portal:

1. Navigate to Entra > Enterprise applications > InsightPulseAI > Users and groups
2. Add assignment > Select group > Select role
3. Users in the group inherit the role

Or use the Graph API:

```bash
az rest --method POST \
  --uri "https://graph.microsoft.com/v1.0/servicePrincipals/<sp-id>/appRoleAssignedTo" \
  --body '{
    "principalId": "<group-object-id>",
    "resourceId": "<sp-id>",
    "appRoleId": "<role-uuid>"
  }'
```

### List current assignments

```bash
SP_ID=$(az ad sp list --filter "appId eq '<app-client-id>'" --query "[0].id" -o tsv)
az rest --method GET \
  --uri "https://graph.microsoft.com/v1.0/servicePrincipals/${SP_ID}/appRoleAssignedTo" \
  --query "value[].{principal:principalDisplayName, role:appRoleId}" -o table
```

---

## 3. Verify Role Claims in Tokens

### Decode a token

After authentication, the access token contains the `roles` claim:

```json
{
  "aud": "<app-client-id>",
  "iss": "https://login.microsoftonline.com/<tenant-id>/v2.0",
  "roles": [
    "finance.close.operator",
    "copilot.action"
  ],
  ...
}
```

### Test with az CLI

```bash
# Acquire a token for the app
az account get-access-token --resource api://<app-client-id> --query accessToken -o tsv
```

Decode the JWT at https://jwt.ms (for development only; never paste production tokens into third-party sites).

### Programmatic validation (Python)

```python
import jwt  # PyJWT

decoded = jwt.decode(
    token,
    options={"verify_signature": False}  # dev only; in production, verify against JWKS
)
roles = decoded.get("roles", [])
```

### Expected claim behavior

| Scenario | `roles` claim |
|----------|--------------|
| User with 2 roles assigned | `["finance.close.operator", "copilot.action"]` |
| User with no roles assigned | `roles` claim absent or empty array |
| Service principal with role | `["ops.admin"]` |
| Group-based assignment | Individual user tokens contain the role |

---

## 4. Role-to-Tool Runtime Mapping

The file `infra/entra/role-tool-mapping.yaml` defines which tools and retrieval scopes each role grants. The backend context envelope builder:

1. Reads `roles` from the token
2. Looks up each role in the mapping
3. Computes `permitted_tools` as the union of all role tool sets
4. Computes `retrieval_scope` as the union of all role scope sets
5. Intersects with entity scope (company, operating entities)
6. Injects the result into the context envelope

If the mapping file is missing or a role is not found, the default is most-restrictive: no tools, no retrieval scope, advisory mode only.

---

## 5. Troubleshooting

### Role not appearing in token

| Symptom | Cause | Fix |
|---------|-------|-----|
| `roles` claim missing entirely | User not assigned any app role | Assign at least one role |
| `roles` claim missing specific role | Role not assigned to this user/group | Check assignments via portal or Graph |
| Token has old roles after change | Token cache | Sign out and re-authenticate; tokens are cached for their lifetime (typically 1 hour) |
| Service principal has no roles | Roles assigned to app, not to SP | Assign roles to the service principal object, not the app registration |

### Role assignment fails

| Symptom | Cause | Fix |
|---------|-------|-----|
| "Insufficient privileges" | Caller lacks `AppRoleAssignment.ReadWrite.All` | Grant the permission or use Application Administrator role |
| "Resource not found" | Wrong object ID (used app ID instead of object ID) | Use `az ad app show --id <app-id> --query id` to get the object ID |
| "appRole not found" | Role value typo or manifest not applied | Run `register-app-roles.sh` first, then retry |
| Duplicate assignment error | Role already assigned to this principal | Safe to ignore; assignment is idempotent |

### Role registered but not assignable

| Symptom | Cause | Fix |
|---------|-------|-----|
| Role visible in manifest but not in portal | No service principal for the app | Create one: `az ad sp create --id <app-client-id>` |
| Role shows as disabled | `isEnabled: false` in manifest | Set to `true` in `app-roles-manifest.json` and re-register |

### Diagnostic commands

```bash
# Show all registered roles
az ad app show --id <app-object-id> --query "appRoles[].{value:value, enabled:isEnabled}" -o table

# Show all assignments for the enterprise app
SP_ID=$(az ad sp list --filter "appId eq '<app-client-id>'" --query "[0].id" -o tsv)
az rest --method GET \
  --uri "https://graph.microsoft.com/v1.0/servicePrincipals/${SP_ID}/appRoleAssignedTo" -o json

# Check if a specific user has the role
az rest --method GET \
  --uri "https://graph.microsoft.com/v1.0/servicePrincipals/${SP_ID}/appRoleAssignedTo" \
  --query "value[?principalId=='<user-object-id>'].{role:appRoleId}" -o table
```

---

## Canonical Role Reference

| Value | Display Name | Domain |
|-------|-------------|--------|
| `product.viewer` | Product Viewer | Product |
| `product.operator` | Product Operator | Product |
| `finance.close.operator` | Finance Close Operator | Finance |
| `finance.close.approver` | Finance Close Approver | Finance |
| `finance.viewer` | Finance Viewer | Finance |
| `marketing.manager` | Marketing Manager | Marketing |
| `marketing.viewer` | Marketing Viewer | Marketing |
| `media.ops` | Media Operations | Media |
| `retail.operator` | Retail Operator | Retail |
| `analytics.viewer` | Analytics Viewer | Analytics |
| `analytics.admin` | Analytics Admin | Analytics |
| `copilot.advisory` | Copilot Advisory | Copilot |
| `copilot.action` | Copilot Action | Copilot |
| `ops.admin` | Operations Admin | Operations |
| `ops.viewer` | Operations Viewer | Operations |

UUID generation method: UUID v5 with namespace `DNS:insightpulseai.com` and role value as name. This is deterministic and reproducible.
