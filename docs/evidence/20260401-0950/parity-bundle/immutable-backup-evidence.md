# Immutable Cold Storage — Deployment Evidence

**Date**: 2026-04-01T09:50 UTC
**Gap**: Odoo.sh parity #5.4 (Immutable cold storage) and #12.5 (Immutable backup / ransomware protection)
**Verdict**: GAP → **PARITY**

## Before

- No immutable storage policy configured for backups
- No dedicated backup blob container

## Actions

1. Created blob container `odoo-backups` on `stipaidev`
2. Enabled blob versioning on `stipaidev` (required for immutability)
3. Applied time-based immutable storage policy:
   - Retention: 30 days
   - State: Unlocked (can be extended, not shortened)
   - Protected append writes: enabled (allows adding new backups)

## After

| Property | Value |
|----------|-------|
| Storage account | `stipaidev` |
| Container | `odoo-backups` |
| Immutability period | 30 days |
| Policy state | Unlocked |
| Allow append writes | true |
| Versioning | Enabled |

## Policy behavior

- Blobs written to `odoo-backups` cannot be deleted or overwritten for 30 days
- Append writes are permitted (backup jobs can write new blobs)
- Policy is unlocked — retention can be extended but not shortened
- Locking the policy (making it permanent) is deferred to production hardening

## Ransomware protection posture

Matches Odoo.sh's 4th backup copy (immutable) concept:
- Backup data survives accidental deletion
- Backup data survives ransomware overwrite attempts
- 30-day minimum retention window
