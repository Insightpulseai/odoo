# Storage Account Normalization — Evidence

> Date: 2026-04-01
> Scope: Azure Storage accounts for Odoo runtime

## Classification

| Account | RG | Role | TLS | Versioning | Status |
|---------|-----|------|-----|------------|--------|
| `stipaidev` | `rg-ipai-dev-odoo-runtime` | **Canonical** — filestore, backups, function artifacts | TLS 1.2 | Yes | **ACTIVE** |
| `stipaiodoodev` | `rg-ipai-dev-odoo-data` | Retire candidate — data migrated to `stipaidev` | TLS 1.2 (hardened) | No | **RETIRE** |

## What was done

1. **Discovered** ACA env storage `odoofilestore` pointed to `stipaidev` (empty share) while actual Odoo data lived on `stipaiodoodev`
2. **Migrated** 57 files from `stipaiodoodev/odoo-filestore` → `stipaidev/odoo-filestore` (addons/, filestore/odoo/, sessions/)
3. **Cleaned** legacy `filestore/odoo_prod/` directory (DB already dropped)
4. **Hardened** `stipaiodoodev` TLS from 1.0 → 1.2
5. **Verified** all 3 ACA containers (web, worker, cron) mount `odoofilestore` → `stipaidev`

## Authority map

| Content | Account | Share/Container | Mount path |
|---------|---------|-----------------|------------|
| Odoo filestore | `stipaidev` | `odoo-filestore` (file share) | `/var/lib/odoo/filestore` |
| Odoo backups | `stipaidev` | `odoo-backups` (blob, immutable 30d) | N/A (backup target) |
| Azure Functions artifacts | `stipaidev` | `azure-webjobs-*`, `function-releases`, `scm-releases` | N/A |
| Legacy Odoo data | `stipaiodoodev` | `odoo-filestore` | **No longer mounted** — retire |

## ACA env storage binding

```
Environment: ipai-odoo-dev-env
Storage name: odoofilestore
Account: stipaidev
Share: odoo-filestore
Access: ReadWrite
```

## Retirement plan for stipaiodoodev

- Data fully migrated (verified)
- TLS hardened to 1.2
- No ACA references remain
- Safe to delete after 7-day hold (target: 2026-04-08)
- Before deletion: confirm no other services reference it
