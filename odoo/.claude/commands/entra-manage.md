# /entra-manage — Entra ID Tenant Management

Manage the InsightPulse AI Microsoft Entra ID tenant.

## Skill Reference
`~/.claude/superclaude/skills/identity/azure-entra-management/SKILL.md`

## Actions

| Action | Description |
|--------|-------------|
| `list-users` | List all tenant users with UPN, type, and role |
| `create-user <displayName> <mailNickname>` | Create native user, store password in Key Vault |
| `update-upn <objectId> <newUpn>` | Update user principal name |
| `reset-password <objectId>` | Reset password, store in Key Vault |
| `list-groups` | List all security groups |
| `create-group <name> <description>` | Create security group |
| `add-member <groupId> <userId>` | Add user to group |
| `list-domains` | List verified domains |
| `add-domain <domain>` | Add and verify custom domain |
| `list-skus` | List subscribed license SKUs |
| `assign-license <userId> <skuId>` | Assign license to user |
| `assign-role <userId> <roleTemplateId>` | Assign directory role |
| `audit` | Full tenant audit (users, roles, domains, licenses, Security Defaults) |

## Security Rules

- Passwords are NEVER displayed in output — stored directly in Key Vault
- All operations via `az rest` against Microsoft Graph API v1.0
- Verification query runs after every mutation
- Emergency access accounts (`admin@`, `emergency-admin@`) must never be deleted

## Usage

```
/entra-manage audit
/entra-manage create-user "DevOps Engineer" devops
/entra-manage assign-role <objectId> 62e90394-69f5-4237-9190-012177145e10
```
