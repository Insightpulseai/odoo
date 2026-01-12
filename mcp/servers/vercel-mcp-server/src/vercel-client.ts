/**
 * Vercel API Client
 */

const API_BASE = "https://api.vercel.com";

export class VercelClient {
  private token: string;
  private teamId?: string;

  constructor(token: string, teamId?: string) {
    this.token = token;
    this.teamId = teamId;
  }

  private async request<T>(
    endpoint: string,
    method: string = "GET",
    body?: unknown
  ): Promise<T> {
    const url = new URL(`${API_BASE}${endpoint}`);
    if (this.teamId) {
      url.searchParams.set("teamId", this.teamId);
    }

    const response = await fetch(url.toString(), {
      method,
      headers: {
        Authorization: `Bearer ${this.token}`,
        "Content-Type": "application/json",
      },
      body: body ? JSON.stringify(body) : undefined,
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Vercel API error: ${response.status} - ${error}`);
    }

    return response.json() as Promise<T>;
  }

  // Projects
  async listProjects(limit: number = 20): Promise<unknown> {
    return this.request(`/v9/projects?limit=${limit}`);
  }

  async getProject(id: string): Promise<unknown> {
    return this.request(`/v9/projects/${id}`);
  }

  async getProjectEnv(id: string): Promise<unknown> {
    return this.request(`/v10/projects/${id}/env`);
  }

  // Deployments
  async listDeployments(projectId: string, limit: number = 10): Promise<unknown> {
    return this.request(`/v6/deployments?projectId=${projectId}&limit=${limit}`);
  }

  async getDeployment(id: string): Promise<unknown> {
    return this.request(`/v13/deployments/${id}`);
  }

  async triggerDeployment(hookUrl: string): Promise<unknown> {
    const response = await fetch(hookUrl, { method: "POST" });
    if (!response.ok) {
      throw new Error(`Deploy hook failed: ${response.status}`);
    }
    return response.json();
  }

  async promoteDeployment(projectId: string, deploymentId: string): Promise<unknown> {
    return this.request(`/v10/projects/${projectId}/promote/${deploymentId}`, "POST");
  }

  async rollbackDeployment(projectId: string, deploymentId: string): Promise<unknown> {
    // Rollback is essentially promoting a previous deployment
    return this.promoteDeployment(projectId, deploymentId);
  }

  // Logs
  async getDeploymentLogs(id: string): Promise<unknown> {
    return this.request(`/v2/deployments/${id}/events`);
  }

  async getRuntimeLogs(
    projectId: string,
    deploymentId?: string,
    since?: number
  ): Promise<unknown> {
    let endpoint = `/v2/projects/${projectId}/logs`;
    const params = new URLSearchParams();
    if (deploymentId) params.set("deploymentId", deploymentId);
    if (since) params.set("since", since.toString());
    const query = params.toString();
    return this.request(`${endpoint}${query ? `?${query}` : ""}`);
  }

  // Domains
  async listDomains(projectId: string): Promise<unknown> {
    return this.request(`/v9/projects/${projectId}/domains`);
  }
}
