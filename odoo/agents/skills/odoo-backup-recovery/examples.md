# Examples — odoo-backup-recovery

## Example 1: Healthy backup posture

**Input**: Pre-deployment backup verification for production release

**Output**:
- Server: `ipai-odoo-dev-pg`, Southeast Asia, `rg-ipai-dev`
- Backup enabled: PASS
- Retention: 14 days configured
- Geo-redundancy: enabled — PASS
- Latest backup: 2026-03-17T04:00:00Z (12 hours ago) — PASS
- Restore window: 2026-03-03T04:00:00Z to 2026-03-17T10:00:00Z
- Encryption: SSE with Microsoft-managed keys — PASS
- Alerting: Azure Monitor alert on backup failure — PASS
- Blockers: none
- Evidence: `az postgres flexible-server show --name ipai-odoo-dev-pg --resource-group rg-ipai-dev --query "backup"`

## Example 2: Geo-redundancy not configured

**Input**: Periodic backup posture audit

**Output**:
- Geo-redundancy: NOT CONFIGURED — FAIL (BLOCKER)
- Blockers: [geo-redundant backup must be enabled per platform policy]
- Recommendation: `az postgres flexible-server update --name ipai-odoo-dev-pg --resource-group rg-ipai-dev --geo-redundant-backup Enabled`
