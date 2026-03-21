# CP-2 Storage Validation — Azure Files + ACA Mounts

**Date**: 2026-03-20
**Method**: Azure CLI (az containerapp show, az storage share list)

## Storage Account
- Name: stipaiodoodev
- Kind: StorageV2
- SKU: Standard_LRS
- Location: southeastasia
- State: Succeeded

## Azure Files Share
- Share name: odoo-filestore
- ACA env storage name: odoofilestore
- Access mode: ReadWrite

## ACA Volume Mounts

| App | Volume | Mount Path | Type |
|-----|--------|------------|------|
| ipai-odoo-dev-web | odoo-filestore | /var/lib/odoo | AzureFile |
| ipai-odoo-dev-worker | odoo-filestore | /var/lib/odoo | AzureFile |
| ipai-odoo-dev-cron | odoo-filestore | /var/lib/odoo | AzureFile |

## Verdict
- CP-2: **DONE** — All 3 ACA apps share persistent Azure Files storage
