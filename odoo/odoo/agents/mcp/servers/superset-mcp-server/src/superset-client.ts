/**
 * Apache Superset API Client
 */

export class SupersetClient {
  private baseUrl: string;
  private username: string;
  private password: string;
  private accessToken: string | null = null;
  private csrfToken: string | null = null;

  constructor(baseUrl: string, username: string, password: string) {
    this.baseUrl = baseUrl.replace(/\/$/, "");
    this.username = username;
    this.password = password;
  }

  async ensureAuthenticated(): Promise<void> {
    if (this.accessToken) return;

    // Get CSRF token
    const csrfResponse = await fetch(`${this.baseUrl}/api/v1/security/csrf_token/`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    });

    if (!csrfResponse.ok) {
      throw new Error("Failed to get CSRF token");
    }

    const csrfData = (await csrfResponse.json()) as { result: string };
    this.csrfToken = csrfData.result;

    // Login
    const loginResponse = await fetch(`${this.baseUrl}/api/v1/security/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": this.csrfToken,
      },
      body: JSON.stringify({
        username: this.username,
        password: this.password,
        provider: "db",
      }),
    });

    if (!loginResponse.ok) {
      throw new Error("Authentication failed");
    }

    const loginData = (await loginResponse.json()) as { access_token: string };
    this.accessToken = loginData.access_token;
  }

  private async request<T>(
    endpoint: string,
    method: string = "GET",
    body?: unknown
  ): Promise<T> {
    await this.ensureAuthenticated();

    const response = await fetch(`${this.baseUrl}/api/v1${endpoint}`, {
      method,
      headers: {
        Authorization: `Bearer ${this.accessToken}`,
        "Content-Type": "application/json",
        ...(this.csrfToken && { "X-CSRFToken": this.csrfToken }),
      },
      body: body ? JSON.stringify(body) : undefined,
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Superset API error: ${response.status} - ${error}`);
    }

    return response.json() as Promise<T>;
  }

  // Dashboards
  async listDashboards(page: number = 0, pageSize: number = 20): Promise<unknown> {
    return this.request(`/dashboard/?q=(page:${page},page_size:${pageSize})`);
  }

  async getDashboard(id: number): Promise<unknown> {
    return this.request(`/dashboard/${id}`);
  }

  async exportDashboard(id: number): Promise<unknown> {
    return this.request(`/dashboard/export/?q=[${id}]`);
  }

  // Charts
  async listCharts(dashboardId?: number): Promise<unknown> {
    const filter = dashboardId
      ? `?q=(filters:!((col:dashboards,opr:rel_m_m,value:${dashboardId})))`
      : "";
    return this.request(`/chart/${filter}`);
  }

  async getChart(id: number): Promise<unknown> {
    return this.request(`/chart/${id}`);
  }

  async updateChart(id: number, data: unknown): Promise<unknown> {
    return this.request(`/chart/${id}`, "PUT", data);
  }

  // Datasets
  async listDatasets(databaseId?: number): Promise<unknown> {
    const filter = databaseId
      ? `?q=(filters:!((col:database,opr:rel_o_m,value:${databaseId})))`
      : "";
    return this.request(`/dataset/${filter}`);
  }

  async getDataset(id: number): Promise<unknown> {
    return this.request(`/dataset/${id}`);
  }

  async createDataset(data: unknown): Promise<unknown> {
    return this.request("/dataset/", "POST", data);
  }

  async refreshDatasetColumns(id: number): Promise<unknown> {
    return this.request(`/dataset/${id}/refresh`, "PUT");
  }

  // Databases
  async listDatabases(): Promise<unknown> {
    return this.request("/database/");
  }

  async testDatabaseConnection(id: number): Promise<unknown> {
    return this.request(`/database/${id}/test_connection`, "POST");
  }
}
