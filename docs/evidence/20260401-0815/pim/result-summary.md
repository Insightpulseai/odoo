# PIM Governance — Live Evidence Summary

**Date**: 2026-04-01
**Status**: live
**Related**: #644

## PIM Eligible Assignments (Verified Live)

| Role | Scope | Status | Activation Required |
|---|---|---|---|
| Contributor (`b24988ac...`) | `rg-ipai-dev-odoo-runtime` | Provisioned | Yes — justification + MFA |
| Contributor (`b24988ac...`) | `rg-ipai-dev-odoo-data` | Provisioned | Yes — justification + MFA |
| Owner (`8e3af657...`) | subscription | Provisioned | Yes — justification + MFA + approval |

## Key Vault Assignment

- **Deferred**: `kv-ipai-dev` does not exist in the current subscription.
- Key Vault Secrets Officer assignment will be created when the vault is provisioned.
- This is not a regression — the vault was never deployed.

## Standing Access (Active, Always-On)

Per `pim-governance.bicep` (deployed via commit `302d8e98`):
- Platform Admin Group → Reader on RG
- Platform Admin Group → Monitoring Reader on RG
- Odoo Operator Group → Custom Odoo Operator role (view + restart ACA apps)

## Entra Groups

| Group | Object ID |
|---|---|
| IPAI Platform Admins | `84b0949f-7134-4913-bf04-7b089791291c` |
| IPAI Odoo Operators | `940bcb9f-fb45-4c39-9046-e4ac36d4a61f` |

## Script Fixes Applied

1. Tenant ID corrected from `402de71a-da66-494f-8049-cfa0dade7532` to `402de71a-87ec-4302-a609-fb76098d1da7`
2. API version corrected from `2022-04-01` to `2020-10-01` (PIM `roleEligibilityScheduleRequests` requires this version)

## Verification Method

```bash
az rest --method GET \
  --uri "/subscriptions/536d8cf6.../resourceGroups/rg-ipai-dev-odoo-runtime/providers/Microsoft.Authorization/roleEligibilityScheduleInstances?api-version=2020-10-01&$filter=principalId eq '84b0949f...'"
```

## Remaining

- Key Vault eligible assignment: blocked on `kv-ipai-dev` provisioning
- PIM activation policies (duration limits, MFA enforcement): require PIM settings API (`roleManagementPolicies`) — not yet configured
