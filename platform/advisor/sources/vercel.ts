/**
 * Vercel source for Ops Advisor
 *
 * Fetches Vercel project state, deployments, env var presence, and analytics
 * to provide data for Vercel-sourced rules in the advisor ruleset.
 *
 * Requires: VERCEL_API_TOKEN env var
 */

const VERCEL_API = "https://api.vercel.com";

export interface VercelProject {
  id: string;
  name: string;
  framework: string | null;
  passwordProtection: unknown | null;
  ssoProtection: unknown | null;
  env?: Array<{ key: string; target: string[] }>;
}

export interface VercelDeployment {
  uid: string;
  state: string;
  createdAt: number;
}

export async function getProject(
  token: string,
  projectId: string,
  teamId?: string
): Promise<VercelProject | null> {
  const url = new URL(`${VERCEL_API}/v9/projects/${encodeURIComponent(projectId)}`);
  if (teamId) url.searchParams.set("teamId", teamId);

  const res = await fetch(url.toString(), {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`Vercel getProject failed: ${res.status}`);
  return res.json();
}

export async function getRecentDeployments(
  token: string,
  projectId: string,
  teamId?: string,
  limit = 5
): Promise<VercelDeployment[]> {
  const url = new URL(`${VERCEL_API}/v6/deployments`);
  url.searchParams.set("projectId", projectId);
  url.searchParams.set("limit", String(limit));
  if (teamId) url.searchParams.set("teamId", teamId);

  const res = await fetch(url.toString(), {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`Vercel getDeployments failed: ${res.status}`);
  const data = await res.json();
  return data.deployments ?? [];
}

export async function getEnvVars(
  token: string,
  projectId: string,
  teamId?: string
): Promise<Array<{ key: string; target: string[] }>> {
  const url = new URL(`${VERCEL_API}/v9/projects/${encodeURIComponent(projectId)}/env`);
  if (teamId) url.searchParams.set("teamId", teamId);

  const res = await fetch(url.toString(), {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`Vercel getEnv failed: ${res.status}`);
  const data = await res.json();
  return data.envs ?? [];
}
