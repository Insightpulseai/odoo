# Service Level Objectives

## Scope
Pulser for Odoo and dependent runtime surfaces on Azure Container Apps.

## SLOs

### Availability
- Objective: 99.5% monthly
- Measurement: successful `/web/health` probe responses / total probes
- Source: ACA health probe + AFD health probe

### Latency
- Objective: P95 < 2s for primary interactive request paths
- Measurement: AFD backend latency metric
- Excludes: Foundry inference calls (cross-region, expected ~150ms overhead)

### Error budget
- Monthly allowable downtime: ~3.6 hours (at 99.5%)
- Burn alert thresholds:
  - 25% budget consumed → informational
  - 50% budget consumed → warning to admin@insightpulseai.com
  - 75% budget consumed → freeze non-critical deployments
  - 100% budget consumed → incident declared

## Measurement sources
- Azure Monitor / Application Insights (when instrumented)
- Front Door health probes and backend latency
- ACA revision health checks (liveness + readiness)
- Synthetic health checks: `curl https://erp.insightpulseai.com/web/health`

## Deployment safety
- Canary rollout required for production-impacting changes
- ACA revision labels used for staged traffic exposure (5% → 25% → 100%)
- Rollback trigger: health probe failure rate > 5% after traffic shift
- Minimum bake time: 15 minutes at each traffic percentage before advancing

## Review cadence
- Weekly: operational review (health, latency, error rate)
- Monthly: SLO review (budget burn, availability trend, deployment safety record)
