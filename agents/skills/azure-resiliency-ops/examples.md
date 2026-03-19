# Examples — azure-resiliency-ops

## Example 1: PostgreSQL with full HA posture

**Input**: Validate resiliency for `ipai-odoo-dev-pg` in `rg-ipai-dev`

**Output**:
- Service: `ipai-odoo-dev-pg` (Microsoft.DBforPostgreSQL/flexibleServers)
- Zone redundancy: ZoneRedundant HA enabled — PASS
- Backup retention: 35 days (minimum 30 for prod) — PASS
- PITR: enabled, recovery window 35 days — PASS
- Last backup: 2026-03-17T02:00:00Z — PASS
- Health probes: N/A (database, not HTTP endpoint)
- Failover routing: automatic failover to standby zone — PASS
- DR runbook: `docs/runbooks/pg-disaster-recovery.md` — PASS
- Blockers: none
- Evidence: `az postgres flexible-server show --name ipai-odoo-dev-pg --resource-group rg-ipai-dev`

## Example 2: Container App in single zone

**Input**: Pre-release audit for `ipai-crm-dev` targeting production

**Output**:
- Service: `ipai-crm-dev` (Microsoft.App/containerApps)
- Zone redundancy: single zone — FAIL (BLOCKER for production)
- Backup retention: N/A (stateless service)
- Health probes: Front Door probe on `/health` — PASS
- Failover routing: Front Door priority routing configured — PASS
- DR runbook: not found — FAIL
- Blockers: [single-zone deployment, missing DR runbook]
- Recommendation: Enable zone redundancy via `zones: ["1","2","3"]` in Bicep; create DR runbook

## Example 3: Backup retention below policy

**Input**: Validate resiliency for `pg-ipai-dev` in `rg-ipai-data-dev`

**Output**:
- Service: `pg-ipai-dev` (Microsoft.DBforPostgreSQL/flexibleServers)
- Zone redundancy: disabled — FAIL (dev acceptable if documented)
- Backup retention: 5 days (minimum 7 for dev) — FAIL
- PITR: enabled — PASS
- Last backup: 2026-03-17T01:30:00Z — PASS
- Blockers: [backup retention 5 days is below 7-day dev minimum]
- Recommendation: Increase retention to 7 days: `az postgres flexible-server update --backup-retention 7`
