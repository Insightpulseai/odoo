# CP-2: ACA Persistent Storage Evidence

## Date
2026-03-20

## Scope
Azure Files persistent mount for Odoo filestore (`/var/lib/odoo`) across all 3 ACA container apps.

## Final Status
**Status: DONE**

All 3 Odoo container apps mount Azure Files at `/var/lib/odoo`. Data persists across restart and new revision deployment.

## Infrastructure

| Resource | Value |
|----------|-------|
| Storage Account | `stipaiodoodev` (Standard_LRS, Southeast Asia) |
| File Share | `odoo-filestore` (10 GB, TransactionOptimized) |
| Key Vault | `ipai-odoo-dev-kv` |
| Key Vault Secret | `sa-odoo-filestore-key` |
| ACA Environment | `ipai-odoo-dev-env` |
| Environment Storage | `odoofilestore` (AzureFile, ReadWrite) |

## Container App Volume Mounts

| App | Container | Volume | Mount Path | Verified |
|-----|-----------|--------|------------|----------|
| `ipai-odoo-dev-web` | `odoo` | `odoo-filestore` → `odoofilestore` | `/var/lib/odoo` | YES |
| `ipai-odoo-dev-worker` | `odoo-worker` | `odoo-filestore` → `odoofilestore` | `/var/lib/odoo` | YES |
| `ipai-odoo-dev-cron` | `odoo-cron` | `odoo-filestore` → `odoofilestore` | `/var/lib/odoo` | YES |

## Persistence Tests

| Test | Result |
|------|--------|
| Odoo writes to mount | PASS — `addons/19.0/` directory created at mount time |
| Marker file survives `revision restart` | PASS — `CP2-PERSISTENCE-TEST-1773894921-PRE-RESTART` persisted |
| Marker file survives new revision (env var update) | PASS — content intact after revision 0000029 |
| Azure Files share accessible via storage API | PASS — file list, upload, download all work |

## Evidence Chain
- Storage account verified: `az storage account show --name stipaiodoodev`
- File share exists: `az storage share-rm list --storage-account stipaiodoodev` → `odoo-filestore`
- Key stored: `az keyvault secret set --vault-name ipai-odoo-dev-kv --name sa-odoo-filestore-key` → created 2026-03-19T03:48:01
- Environment storage registered: `az containerapp env storage list` → `odoofilestore`
- Apps updated via YAML patch: `az containerapp update --yaml` for all 3 apps
- Volume mounts confirmed: `az containerapp show --query properties.template` for all 3 apps
- Persistence verified: marker file survived restart (revision restart) and redeploy (new revision 0000029)
