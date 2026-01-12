/**
 * DigitalOcean API Client wrapper
 */

const API_BASE = "https://api.digitalocean.com/v2";

export class DigitalOceanClient {
  private token: string;

  constructor(token: string) {
    this.token = token;
  }

  private async request<T>(
    endpoint: string,
    method: string = "GET",
    body?: unknown
  ): Promise<T> {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method,
      headers: {
        Authorization: `Bearer ${this.token}`,
        "Content-Type": "application/json",
      },
      body: body ? JSON.stringify(body) : undefined,
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`DO API error: ${response.status} - ${error}`);
    }

    return response.json() as Promise<T>;
  }

  // Droplets
  async listDroplets(tag?: string): Promise<unknown> {
    const query = tag ? `?tag_name=${encodeURIComponent(tag)}` : "";
    return this.request(`/droplets${query}`);
  }

  async getDroplet(id: number): Promise<unknown> {
    return this.request(`/droplets/${id}`);
  }

  async dropletAction(id: number, action: string): Promise<unknown> {
    return this.request(`/droplets/${id}/actions`, "POST", { type: action });
  }

  // Apps
  async listApps(): Promise<unknown> {
    return this.request("/apps");
  }

  async getApp(id: string): Promise<unknown> {
    return this.request(`/apps/${id}`);
  }

  async getAppLogs(
    appId: string,
    deploymentId?: string,
    component?: string,
    lines: number = 100
  ): Promise<unknown> {
    const deplId = deploymentId || "active";
    let endpoint = `/apps/${appId}/deployments/${deplId}/logs`;
    const params = new URLSearchParams();
    if (component) params.set("component_name", component);
    params.set("type", "RUN");
    params.set("follow", "false");
    return this.request(`${endpoint}?${params}`);
  }

  async deployApp(id: string, forceBuild: boolean = false): Promise<unknown> {
    return this.request(`/apps/${id}/deployments`, "POST", {
      force_build: forceBuild,
    });
  }

  async createApp(spec: unknown): Promise<unknown> {
    return this.request("/apps", "POST", { spec });
  }

  // Databases
  async listDatabases(): Promise<unknown> {
    return this.request("/databases");
  }

  async getDatabaseConnection(id: string): Promise<unknown> {
    return this.request(`/databases/${id}`);
  }
}
