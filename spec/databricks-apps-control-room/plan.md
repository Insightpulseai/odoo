# Databricks Apps Control Room — Implementation Plan

## Phase 1: Foundation (Week 1-2)
- Set up `infra/databricks/src/apps/control_room/` structure
- Create Streamlit app skeleton with Databricks Apps config
- Implement sync status dashboard (read from connector state tables)
- Deploy via DABs to dev workspace

## Phase 2: Alerting & Failures (Week 3-4)
- Add failure alert feed
- Implement one-click replay trigger (calls connector replay job)
- Set up Databricks SQL alerts for SLA breaches
- Slack integration for critical failures

## Phase 3: Schema & SLA (Week 5-6)
- Schema drift detection UI
- SLA tracking dashboard
- Historical compliance reports
- Freshness heatmap

## Phase 4: Polish & Production (Week 7-8)
- Production deployment
- Performance optimization (caching, incremental refresh)
- Documentation and runbooks
- User onboarding
