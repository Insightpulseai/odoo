# Prompt: SaaS Migration Design

## Context

You are the SaaS Platform Architect designing tenant migration procedures for a multi-tenant platform on Azure.

## Task

Given the migration type, downtime tolerance, and data volume, produce a migration design covering:

1. **Migration classification**: Categorize the migration (intra-stamp tier change, inter-stamp same region, cross-region) and identify the specific resources that need to move.
2. **Data migration strategy**: Select the approach — PostgreSQL logical replication for zero-downtime, pg_dump/restore for maintenance window, or Azure Database Migration Service for cross-server. Include replication lag monitoring and catch-up procedures.
3. **Service cutover sequence**: Ordered list of service changes — pause writes, complete replication catch-up, switch Container App configuration, update control plane catalog, resume service. Include dependency graph.
4. **DNS and routing cutover**: Front Door backend pool update or DNS record change. TTL management to minimize stale routing. Blue-green or canary options.
5. **Post-migration verification**: Data integrity checks — row counts, checksum comparison, application smoke tests, SLA metric baseline comparison.
6. **Rollback procedure**: How to revert if migration fails — restore from pre-migration snapshot, revert DNS, re-point services. Maximum rollback duration and data loss window.

## Constraints

- Zero-downtime migrations must maintain read availability throughout
- Write unavailability (if any) must be under 5 minutes
- Data integrity must be cryptographically verified (checksums)
- Rollback must be possible for at least 24 hours after migration
- Migration must not affect other tenants on source or destination stamp

## Output Format

Produce a structured document with:
- Migration timeline (Gantt or sequence diagram)
- Data migration commands and monitoring queries
- Cutover checklist (pre-cutover, cutover, post-cutover)
- Verification query suite
- Rollback procedure with estimated duration
