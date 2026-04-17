/**
 * Application Insights tracing for the Odoo MCP Connector.
 *
 * Initializes telemetry collection for:
 * - MCP tool invocations (custom events)
 * - Odoo JSON-2 API calls (dependencies)
 * - Search queries (dependencies)
 * - Errors and exceptions
 *
 * Requires APPLICATIONINSIGHTS_CONNECTION_STRING env var.
 */

let client: any = null;

export function initTracing() {
  const connString = process.env.APPLICATIONINSIGHTS_CONNECTION_STRING;
  if (!connString) {
    console.log("[tracing] No APPLICATIONINSIGHTS_CONNECTION_STRING — tracing disabled");
    return;
  }

  try {
    const appInsights = require("applicationinsights");
    appInsights
      .setup(connString)
      .setAutoCollectRequests(true)
      .setAutoCollectPerformance(true)
      .setAutoCollectExceptions(true)
      .setAutoCollectDependencies(true)
      .start();

    client = appInsights.defaultClient;
    console.log("[tracing] Application Insights initialized");
  } catch (err) {
    console.log("[tracing] Failed to initialize:", err);
  }
}

export function trackToolCall(toolName: string, args: Record<string, unknown>, durationMs: number, success: boolean) {
  if (!client) return;

  client.trackEvent({
    name: "MCP_ToolCall",
    properties: {
      toolName,
      args: JSON.stringify(args).slice(0, 500),
      success: String(success),
    },
    measurements: {
      durationMs,
    },
  });
}

export function trackOdooCall(model: string, method: string, durationMs: number, statusCode: number) {
  if (!client) return;

  client.trackDependency({
    target: "odoo-json2",
    name: `${model}.${method}`,
    data: `${model}/${method}`,
    duration: durationMs,
    resultCode: statusCode,
    success: statusCode >= 200 && statusCode < 400,
    dependencyTypeName: "HTTP",
  });
}

export function trackSearchQuery(query: string, resultCount: number, durationMs: number) {
  if (!client) return;

  client.trackDependency({
    target: "azure-ai-search",
    name: "odoo-knowledge",
    data: query.slice(0, 200),
    duration: durationMs,
    resultCode: 200,
    success: true,
    dependencyTypeName: "HTTP",
  });

  client.trackMetric({
    name: "SearchResultCount",
    value: resultCount,
  });
}

export function trackError(error: Error, properties?: Record<string, string>) {
  if (!client) return;

  client.trackException({
    exception: error,
    properties,
  });
}
