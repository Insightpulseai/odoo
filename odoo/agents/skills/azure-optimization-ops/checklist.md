# Checklist — azure-optimization-ops

- [ ] Stale resources query (q92) executed and results reviewed
- [ ] Each idle resource classified (zero traffic, orphaned, or low utilization)
- [ ] SKU compliance checked against platform sizing policy
- [ ] Container Apps autoscaling rules verified (min/max replicas appropriate)
- [ ] Zero-traffic Container Apps identified with 30-day evidence
- [ ] Azure Advisor cost recommendations reviewed
- [ ] Orphaned disks, NICs, and public IPs identified
- [ ] Reserved capacity alignment validated against actual usage
- [ ] Estimated monthly savings calculated per recommendation
- [ ] Each recommendation includes rollback path
- [ ] Stakeholder approval flagged for any downgrade or deletion
- [ ] Evidence saved to `docs/evidence/{stamp}/azure-ops/optimization/`
