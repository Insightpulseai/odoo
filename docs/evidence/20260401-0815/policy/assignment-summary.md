# Azure Policy Tag Governance — Live Deployment Evidence

**Date**: 2026-04-01T08:44:41Z
**Deployment**: `ipai-tag-governance-20260401-0844`
**Scope**: `rg-ipai-dev-odoo-runtime` (Southeast Asia)
**Status**: live
**Enforcement**: `DoNotEnforce` (audit-only)
**Related**: #647

## Assignments Created

| Assignment Name | Display Name | Enforcement | Tag |
|---|---|---|---|
| `ipai-req-env-tag-dev` | IPAI: Require Environment tag (dev) | DoNotEnforce | `Environment` |
| `ipai-req-proj-tag-dev` | IPAI: Require Project tag (dev) | DoNotEnforce | `Project` |
| `ipai-req-mgby-tag-dev` | IPAI: Require ManagedBy tag (dev) | DoNotEnforce | `ManagedBy` |

## Policy Definition

- Built-in: "Require a tag on resources"
- ID: `871b6d14-10aa-478d-b590-94f262ecfa99`

## Compliance

Initial compliance scan triggered at deployment time. Full evaluation may take up to 30 minutes.
Snapshot saved to `compliance-snapshot.json`.

## Bicep Fix Applied

The original Bicep template had an incorrect policy definition ID (`...b466-208cb8a14081`).
Corrected to `...b590-94f262ecfa99` (verified via `az policy definition list`).
The linter had already corrected the `tenantResourceId()` call; the comment was also updated.

## Rollback

```bash
az policy assignment delete --name ipai-req-env-tag-dev --resource-group rg-ipai-dev-odoo-runtime
az policy assignment delete --name ipai-req-proj-tag-dev --resource-group rg-ipai-dev-odoo-runtime
az policy assignment delete --name ipai-req-mgby-tag-dev --resource-group rg-ipai-dev-odoo-runtime
```
