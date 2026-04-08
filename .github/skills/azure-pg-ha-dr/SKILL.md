# azure-pg-ha-dr

**Impact tier**: P0 -- Data Loss

## Purpose

Close the PostgreSQL high-availability and disaster-recovery gap identified in
the Odoo-on-Azure enterprise benchmark audit. The current deployment uses a
single Azure Database for PostgreSQL Flexible Server (`pg-ipai-odoo`) with
default backup settings. Production ERP data has no verified HA failover, no
confirmed geo-redundant backup, no documented RPO/RTO, and no restore drill
evidence.

## When to Use

- Standing up or hardening an Azure PostgreSQL Flexible Server that hosts Odoo.
- Preparing for go-live readiness review.
- Responding to an audit finding about backup retention or disaster recovery.

## Required Evidence (inspect these repo paths first)

| Path | What to look for |
|------|-----------------|
| `infra/azure/modules/postgres-flexible.bicep` | SKU, HA mode, backup retention, geo-backup flag |
| `infra/ssot/azure/resources.yaml` | `pg-ipai-odoo` entry -- lifecycle, region, notes |
| `infra/ssot/azure/service-matrix.yaml` | Odoo service entry -- database reference |
| `docs/runbooks/DR_BACKUP_RESTORE.md` | Restore drill procedure and evidence |
| `docs/runbooks/ODOO19_GO_LIVE_CHECKLIST.md` | DB backup/HA line items |
| `docs/audits/ODOO_AZURE_ENTERPRISE_BENCHMARK.md` | PG HA/DR gap row |

## Microsoft Learn MCP Usage

Run at least these three queries before proposing changes:

1. `microsoft_docs_search("Azure Database PostgreSQL Flexible Server high availability zone redundant")`
   -- confirms HA architecture options (same-zone vs zone-redundant).
2. `microsoft_docs_search("Azure PostgreSQL Flexible Server backup geo-redundant restore")`
   -- retrieves backup retention limits, geo-backup enablement, PITR mechanics.
3. `microsoft_docs_search("Azure PostgreSQL Flexible Server disaster recovery RPO RTO")`
   -- retrieves Microsoft's documented RPO/RTO guarantees per HA tier.

Optional deeper fetches:

4. `microsoft_docs_fetch("https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/concepts-high-availability")`
5. `microsoft_code_sample_search("bicep PostgreSQL Flexible Server high availability", language="bicep")`

## Workflow

1. **Inspect repo** -- Read the Bicep module and SSOT YAML. Record current SKU,
   `highAvailability.mode`, `backup.retentionDays`, `backup.geoRedundantBackup`.
2. **Query MCP** -- Run the three searches above. Capture the recommended HA mode,
   maximum retention days (35), geo-backup requirements, and RPO/RTO numbers.
3. **Compare** -- Identify delta between current IaC and Microsoft recommendations.
   Flag any parameter that is missing or set below the recommended floor.
4. **Patch** -- Update `infra/azure/modules/postgres-flexible.bicep` to set:
   - `highAvailability.mode: 'ZoneRedundant'` (or `SameZone` with justification)
   - `backup.retentionDays: 35`
   - `backup.geoRedundantBackup: 'Enabled'`
   Update `docs/runbooks/DR_BACKUP_RESTORE.md` with restore drill procedure.
   Update `docs/runbooks/ODOO19_GO_LIVE_CHECKLIST.md` with RPO/RTO targets.
5. **Verify** -- Confirm Bicep lints clean (`az bicep build`). Confirm SSOT YAML
   reflects the new HA posture. Confirm runbook contains a step-by-step restore
   drill with expected completion time.

## Outputs

| File | Change |
|------|--------|
| `infra/azure/modules/postgres-flexible.bicep` | HA mode, backup retention, geo-backup |
| `infra/ssot/azure/resources.yaml` | Update `pg-ipai-odoo` entry with HA metadata |
| `docs/runbooks/DR_BACKUP_RESTORE.md` | Restore drill procedure, RPO/RTO targets |
| `docs/runbooks/ODOO19_GO_LIVE_CHECKLIST.md` | DB HA/DR line items checked |
| `docs/evidence/<stamp>/azure-pg-ha-dr/` | Bicep diff, MCP query results, drill log |

## Completion Criteria

- [ ] Bicep module sets `highAvailability.mode` to a non-`Disabled` value.
- [ ] `backup.retentionDays` is 35 (maximum).
- [ ] `backup.geoRedundantBackup` is `Enabled`.
- [ ] `docs/runbooks/DR_BACKUP_RESTORE.md` contains a numbered restore drill
      procedure with expected duration and success criteria.
- [ ] RPO and RTO targets are documented with explicit numbers (e.g., RPO < 5 min,
      RTO < 1 hour).
- [ ] Evidence directory contains the Bicep diff and MCP query excerpts.
