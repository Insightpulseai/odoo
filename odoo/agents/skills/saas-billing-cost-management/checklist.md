# Checklist: SaaS Billing & Cost Management

## Pricing Model

- [ ] Pricing model type selected (per-seat, per-usage, tiered, hybrid)
- [ ] Tier definitions documented with feature matrix
- [ ] Free tier resource limits defined and enforced
- [ ] Upgrade/downgrade paths documented
- [ ] Enterprise custom pricing process defined

## Cost Management

- [ ] Azure Cost Management configured with per-tenant cost views
- [ ] Cost exports scheduled for billing reconciliation
- [ ] Cost allocation rules defined for shared infrastructure
- [ ] Reserved instance and savings plan strategy documented
- [ ] Cost anomaly detection enabled

## Budget Alerts

- [ ] Platform-wide budget threshold set with alert routing
- [ ] Per-tenant budget thresholds configurable
- [ ] Alert escalation paths defined (email, Slack, PagerDuty)
- [ ] Action groups configured for automated responses
- [ ] Monthly cost review process defined

## Billing Pipeline

- [ ] Metering event collection points identified
- [ ] Event aggregation and storage pipeline designed
- [ ] Rating engine maps usage to pricing
- [ ] Invoice generation process automated
- [ ] Payment integration defined (Stripe, Azure Marketplace, custom)
- [ ] Billing audit trail maintained

## Antipattern Prevention

- [ ] Under-metering risk assessed (shared resources not tracked)
- [ ] Over-provisioning risk assessed (reserved but unused capacity)
- [ ] Hidden shared costs identified and allocated
- [ ] Free tier abuse prevention mechanisms in place
- [ ] Billing accuracy validation process defined
