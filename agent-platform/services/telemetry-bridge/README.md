# Telemetry Bridge

Bridges agent runtime telemetry to Azure Monitor / Application Insights.

## Responsibilities

- Collect traces, metrics, and logs from orchestrator, executor, and gateways
- Forward to Azure Application Insights via OpenTelemetry SDK
- Enrich spans with agent-specific attributes (agentId, sessionId, toolName)
- Support structured logging for eval results

## Status

TODO: Implement when runtime services are deployed to Azure Container Apps.
