# Checklist — azure-resiliency-ops

- [ ] PostgreSQL Flexible Server zone redundancy verified (HA mode: ZoneRedundant)
- [ ] Point-in-time restore (PITR) enabled on PostgreSQL
- [ ] Backup retention meets policy minimum (7 days dev, 30 days prod)
- [ ] Last successful backup timestamp confirmed (within last 24 hours)
- [ ] Front Door health probes configured for all origin groups
- [ ] Health probe endpoints responding with HTTP 200
- [ ] Front Door origin priority routing configured for failover
- [ ] Container App replicas distributed across availability zones (production)
- [ ] Single-zone deployments flagged as blockers for production
- [ ] Failover DNS records exist for critical services
- [ ] DR runbook exists and references current resource names
- [ ] Evidence saved to `docs/evidence/{stamp}/azure-ops/resiliency/`
