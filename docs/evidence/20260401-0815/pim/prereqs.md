# PIM Governance Prerequisites — #644

**Date**: 2026-04-01
**Status**: resolved

## Entra Security Groups

| Group | Object ID | Security Enabled |
|---|---|---|
| IPAI Platform Admins | `84b0949f-7134-4913-bf04-7b089791291c` | Yes |
| IPAI Odoo Operators | `940bcb9f-fb45-4c39-9046-e4ac36d4a61f` | Yes |

## Environment Variables

```bash
export ENTRA_PLATFORM_ADMIN_GROUP_ID="84b0949f-7134-4913-bf04-7b089791291c"
export ENTRA_ODOO_OPERATOR_GROUP_ID="940bcb9f-fb45-4c39-9046-e4ac36d4a61f"
```

## Target Scopes

| Role | Scope | Max Duration |
|---|---|---|
| Contributor | `rg-ipai-dev-odoo-runtime` | 8h |
| Contributor | `rg-ipai-dev-odoo-data` | 8h |
| Key Vault Secrets Officer | `kv-ipai-dev` | 4h |
| Owner | subscription | 4h (approval required) |

## Tenant

- ID: `402de71a-87ec-4302-a609-fb76098d1da7`
- Domain: `insightpulseai.com`
- Entra P2 required for PIM eligible assignments
