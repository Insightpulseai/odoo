# many-models-governance — Checklist

## Model Inventory
- [ ] All production models cataloged with domain, owner, and metadata
- [ ] Last retrained date recorded for every model
- [ ] Serving mode documented (batch, real-time, or both)
- [ ] Monthly compute cost attributed to each model
- [ ] Model registry (MLflow or Unity Catalog) contains all production models

## Splitting Strategy
- [ ] Splitting decision is justified with measurable criteria (accuracy gain, isolation requirement)
- [ ] Default-to-fewer-models principle is documented
- [ ] Feature space analysis supports domain/segment separation
- [ ] Hybrid strategy is considered where appropriate
- [ ] Cost-benefit analysis performed for each split

## Routing Architecture
- [ ] Routing logic documented (feature-based, tenant ID, domain classifier)
- [ ] Fallback behavior defined when specialized model is unavailable
- [ ] Traffic splitting configured for gradual rollout
- [ ] Routing logic is testable and monitored
- [ ] Request attribution logs which model served each request

## Cost Governance
- [ ] Compute cost tagged per model, per domain, per tenant
- [ ] Budget thresholds and alerts configured
- [ ] Cost-per-prediction metric tracked
- [ ] Quarterly cost review scheduled
- [ ] Underperforming models flagged for consolidation or retirement

## Retirement Criteria
- [ ] Staleness threshold defined (max days since last retraining)
- [ ] Performance threshold defined (min accuracy, max drift)
- [ ] Cost threshold defined (max cost-per-prediction or monthly budget)
- [ ] Redundancy check (is this model superseded by a newer version?)
- [ ] Retirement process documented (notification, migration, decommission)
