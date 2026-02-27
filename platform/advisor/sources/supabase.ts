/**
 * Supabase source for Ops Advisor
 *
 * Fetches project health, branch status, and connection pool metrics
 * via Supabase Management API.
 * Requires: SUPABASE_MANAGEMENT_API_TOKEN env var
 */

const MGMT_API = "https://api.supabase.com/v1";

export interface ProjectHealth {
  ref: string;
  status: string; // 'ACTIVE_HEALTHY' | 'INACTIVE' | ...
  region: string;
}

export async function getProjectHealth(
  managementToken: string,
  projectRef: string
): Promise<ProjectHealth | null> {
  const res = await fetch(`${MGMT_API}/projects/${projectRef}`, {
    headers: { Authorization: `Bearer ${managementToken}` },
  });
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`Supabase mgmt getProject failed: ${res.status}`);
  return res.json();
}

export async function getBranches(
  managementToken: string,
  projectRef: string
): Promise<Array<{ id: string; name: string; status: string }>> {
  const res = await fetch(`${MGMT_API}/projects/${projectRef}/branches`, {
    headers: { Authorization: `Bearer ${managementToken}` },
  });
  if (!res.ok) {
    // Branches API may not be available on all plans
    return [];
  }
  return res.json();
}

export async function getConnectionStats(
  supabaseUrl: string,
  serviceRoleKey: string,
  projectRef: string
): Promise<{ active: number; max: number } | null> {
  // Query pg_stat_activity via Supabase REST → RPC
  const res = await fetch(`${supabaseUrl}/rest/v1/rpc/get_connection_stats`, {
    method: "POST",
    headers: {
      apikey: serviceRoleKey,
      Authorization: `Bearer ${serviceRoleKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ project_ref: projectRef }),
  });
  if (!res.ok) return null; // RPC function may not exist yet
  return res.json();
}
