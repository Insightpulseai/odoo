/**
 * Chart management tools
 */

import { SupersetClient } from "../superset-client.js";

export async function listCharts(
  client: SupersetClient,
  dashboardId?: number
): Promise<unknown> {
  return client.listCharts(dashboardId);
}

export async function getChart(
  client: SupersetClient,
  id: number
): Promise<unknown> {
  return client.getChart(id);
}

export async function updateChartSql(
  client: SupersetClient,
  id: number,
  sql: string
): Promise<unknown> {
  return client.updateChart(id, {
    query_context: {
      datasource: { type: "table" },
      queries: [{ sql }],
    },
  });
}
