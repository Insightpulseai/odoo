# Azure Files Filestore — Deployment Evidence

**Date**: 2026-04-01T09:33–09:42 UTC
**Gap**: Odoo.sh parity #1.12 (Persistent filestore)
**Verdict**: GAP → **PARITY**

## Before

- ACA env storage `odoofilestore` existed but referenced nonexistent account `stipaiodoodev`
- Volume `odoo-filestore` defined on containers but `volumeMounts: null`
- No file share existed for Odoo filestore

## Actions

1. Created Azure Files share `odoo-filestore` on `stipaidev` (50 GiB quota)
2. Removed broken env storage `odoofilestore` (required removing volume refs from all 3 containers, temporarily removing RG lock)
3. Recreated env storage `odoofilestore` → `stipaidev/odoo-filestore` (ReadWrite)
4. Mounted volume on all 3 Odoo containers at `/var/lib/odoo/filestore`:
   - `ipai-odoo-dev-web`
   - `ipai-odoo-dev-worker`
   - `ipai-odoo-dev-cron`
5. Restored RG delete lock

## After

```json
{
  "mounts": [{"mountPath": "/var/lib/odoo/filestore", "volumeName": "odoo-filestore"}],
  "volumes": [{"name": "odoo-filestore", "storageName": "odoofilestore", "storageType": "AzureFile"}]
}
```

All 3 containers confirmed with identical mount config.

## Storage details

| Property | Value |
|----------|-------|
| Storage account | `stipaidev` |
| Resource group | `rg-ipai-dev-odoo-runtime` |
| File share | `odoo-filestore` |
| Quota | 50 GiB |
| ACA env storage name | `odoofilestore` |
| Access mode | ReadWrite |
| Mount path | `/var/lib/odoo/filestore` |
