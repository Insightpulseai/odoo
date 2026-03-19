# CP-2: ACA Persistent Storage Validation Evidence

## Date: 2026-03-19
## Target: ipai-odoo-dev-web (rg-ipai-dev)

## Volume Mount Status

**Status: NOT CONFIGURED**

- `properties.template.volumes`: null (no volumes defined)
- `properties.template.containers[0].volumeMounts`: null (no mounts)
- No storage accounts found in `rg-ipai-dev`

## What this means

The Odoo filestore (`/var/lib/odoo`) is currently using ephemeral container storage. Uploads, attachments, and generated reports will be lost on container restart/redeploy.

## Required fix

1. Create Azure Files share (or use existing Azure Files in another RG)
2. Add volume to ACA environment
3. Mount at `/var/lib/odoo` on all 3 Odoo containers (web, worker, cron)
4. Verify persistence across restart

## Bicep reference

`infra/azure/modules/azure-files.bicep` exists in the repo but has not been applied to the ACA configuration.

## Assessment

**Status: BLOCKED**

This is a go-live blocker. Filestore persistence must be proven before production use.
