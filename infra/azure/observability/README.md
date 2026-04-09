# Azure Observability

Azure Monitor configuration: alerts, dashboards, Log Analytics workspaces, and Application Insights.

## Architecture

- Log Analytics workspace for centralized logging
- Application Insights for ACA app telemetry
- Azure Monitor alerts for SLA-critical services
- Dashboards in Azure Portal and Power BI

## Convention

- All ACA apps emit structured logs to Log Analytics
- Alert severity levels: 0 (critical) through 4 (informational)
- Dashboard definitions stored as ARM/Bicep templates
- Retention: 90 days in Log Analytics, 30 days in App Insights

<!-- TODO: Add Bicep templates for observability resources -->
