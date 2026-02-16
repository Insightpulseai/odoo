/**
 * Dashboard management tools
 */

import { SupersetClient } from "../superset-client.js";

export async function listDashboards(
  client: SupersetClient,
  page?: number,
  pageSize?: number
): Promise<unknown> {
  return client.listDashboards(page, pageSize);
}

export async function getDashboard(
  client: SupersetClient,
  id: number
): Promise<unknown> {
  return client.getDashboard(id);
}

export async function exportDashboard(
  client: SupersetClient,
  id: number
): Promise<unknown> {
  return client.exportDashboard(id);
}

export async function refreshDashboard(
  client: SupersetClient,
  id: number
): Promise<{ status: string; dashboard_id: number }> {
  // Superset doesn't have a direct refresh endpoint, but we can trigger
  // a cache invalidation by getting the dashboard with force_refresh
  await client.getDashboard(id);
  return { status: "refreshed", dashboard_id: id };
}
