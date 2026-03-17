# Checklist: Tenancy Model Selection

## Requirements Gathering

- [ ] Tenant count estimated (current and 12-month projection)
- [ ] Isolation requirements documented per regulation and contract
- [ ] Performance SLOs defined per tenant tier
- [ ] Cost budget defined per tenant and platform-wide
- [ ] Compliance requirements mapped to isolation levels

## Decision Matrix

- [ ] All three models (shared, dedicated, hybrid) evaluated
- [ ] Criteria weighted by business priority
- [ ] Scores documented with evidence/rationale
- [ ] Decision reviewed by stakeholders
- [ ] Decision documented in architecture decision record (ADR)

## Tier Mapping (Hybrid Model)

- [ ] Free tier model defined (typically shared)
- [ ] Standard tier model defined (typically shared with limits)
- [ ] Enterprise tier model defined (typically dedicated)
- [ ] Compliance-driven exceptions documented
- [ ] Tier boundaries clearly defined with measurable criteria

## Migration Path

- [ ] Upgrade path documented (shared to dedicated)
- [ ] Downgrade path documented (dedicated to shared)
- [ ] Data migration procedure defined
- [ ] DNS/routing cutover procedure defined
- [ ] Rollback plan for failed migrations

## Risk Assessment

- [ ] Noisy neighbor risk assessed (shared model)
- [ ] Cost overrun risk assessed (dedicated model)
- [ ] Operational complexity risk assessed (hybrid model)
- [ ] Compliance gap risk assessed
- [ ] Mitigation plan documented for each identified risk
