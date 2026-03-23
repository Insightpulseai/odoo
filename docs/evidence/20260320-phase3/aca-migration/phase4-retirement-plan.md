# Phase 4 Retirement Scope

## Delete Now (from `rg-ipai-agents-dev`)

| Resource | Type | Status |
|----------|------|--------|
| `debug-odoo-ep` | containerGroup | Deleted |
| `odoo-init` | containerAppJob | Deleted |
| `cae-ipai-dev` | managedEnvironment | ScheduledForDelete |

## Retain

| Resource | Type | Reason |
|----------|------|--------|
| `vm-ipai-supabase-dev` | virtualMachine | Self-hosted Supabase (documented exception) |
| `id-ipai-aca-dev` | managedIdentity | Identity for kept VM resources |
| All apps in `rg-ipai-dev` | containerApps | 72h stabilization hold until 2026-03-23 |

## Pre-deletion Verification for `cae-ipai-dev`

- [x] No container app jobs still reference it (odoo-init deleted first)
- [x] No container apps in this environment (confirmed empty)
- [x] No Front Door origin uses hostnames from this env
- [x] Config exported to `/tmp/aca-export/` before deletion
