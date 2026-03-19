# Prompt — odoo-monitoring-posture

You are validating the monitoring and observability posture for the Odoo platform on Azure.

Your job is to:
1. Verify Azure Monitor workspace is configured and collecting container logs
2. Confirm Application Insights is connected to Container Apps
3. Check health probe endpoints return 200 on all Container Apps
4. Validate alert rules exist for: error rate > threshold, p95 latency > threshold, availability < 99.5%
5. Verify alert notification channels (email, Slack webhook)
6. Check log retention meets policy (minimum 30 days)
7. Confirm KPI dashboard exists with key metrics
8. Produce monitoring posture report

Platform context:
- Container Apps: `ipai-odoo-dev-web`, `ipai-odoo-dev-worker`, `ipai-odoo-dev-cron`
- Azure Monitor: Log Analytics workspace in `rg-ipai-dev`
- Application Insights: connected via managed identity
- Health probes: `/web/health` or `/` depending on app
- Alert targets: error rate, latency, availability, container restarts, OOM

Key metrics to monitor:
- HTTP error rate (5xx responses / total requests)
- p95 response latency
- Container restart count
- Database connection pool utilization
- Memory and CPU usage per container
- Odoo cron job execution duration

Output format:
- Monitor workspace: configured (pass/fail), collecting data (pass/fail)
- Application Insights: connected (pass/fail)
- Health probes: per-app status (pass/fail)
- Alert rules: list with metric, threshold, status
- Notifications: channels configured (pass/fail)
- Log retention: days configured vs policy minimum
- Dashboard: exists with key KPIs (pass/fail)
- Evidence: az CLI output and metric queries

Rules:
- Never disable monitoring or alerting
- Never reduce log retention
- Never expose connection strings
- Read-only queries only
- Bind to Azure Monitor, not Odoo.sh monitoring
