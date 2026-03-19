# Checklist — odoo-monitoring-posture

- [ ] Azure Monitor workspace configured and collecting data
- [ ] Application Insights connected to all Container Apps
- [ ] Health probe endpoints configured on all Container Apps
- [ ] Health probes returning 200 on all Container Apps
- [ ] Alert rule: error rate threshold configured
- [ ] Alert rule: p95 latency threshold configured
- [ ] Alert rule: availability threshold configured
- [ ] Alert rule: container restart count configured
- [ ] Alert notification channels configured (email, Slack)
- [ ] Log retention meets policy minimum (30+ days)
- [ ] KPI dashboard exists with key metrics
- [ ] No connection strings exposed in output
- [ ] Evidence captured in `docs/evidence/{stamp}/odoo-delivery/odoo-monitoring-posture/`
