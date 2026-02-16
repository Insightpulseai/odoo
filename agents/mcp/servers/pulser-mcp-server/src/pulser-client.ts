/**
 * Pulser API Client for agent orchestration
 */

export class PulserClient {
  private baseUrl: string;
  private apiKey?: string;

  constructor(baseUrl: string, apiKey?: string) {
    this.baseUrl = baseUrl.replace(/\/$/, "");
    this.apiKey = apiKey;
  }

  private async request<T>(
    endpoint: string,
    method: string = "GET",
    body?: unknown
  ): Promise<T> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    if (this.apiKey) {
      headers["Authorization"] = `Bearer ${this.apiKey}`;
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Pulser API error: ${response.status} - ${error}`);
    }

    return response.json() as Promise<T>;
  }

  // Agents
  async listAgents(category?: string): Promise<unknown> {
    const query = category ? `?category=${encodeURIComponent(category)}` : "";
    return this.request(`/api/agents${query}`);
  }

  async runAgent(
    agentId: string,
    input: Record<string, unknown>,
    context?: Record<string, unknown>,
    async: boolean = true
  ): Promise<unknown> {
    return this.request(`/api/agents/${agentId}/run`, "POST", {
      input,
      context,
      async,
    });
  }

  async cancelRun(runId: string): Promise<unknown> {
    return this.request(`/api/runs/${runId}/cancel`, "POST");
  }

  // Runs
  async getRunStatus(runId: string): Promise<unknown> {
    return this.request(`/api/runs/${runId}`);
  }

  async getRunOutput(runId: string): Promise<unknown> {
    return this.request(`/api/runs/${runId}/output`);
  }

  async listRuns(
    agentId?: string,
    status?: string,
    limit: number = 20
  ): Promise<unknown> {
    const params = new URLSearchParams();
    if (agentId) params.set("agent_id", agentId);
    if (status) params.set("status", status);
    params.set("limit", limit.toString());
    return this.request(`/api/runs?${params}`);
  }

  // Skills
  async listSkills(): Promise<unknown> {
    return this.request("/api/skills");
  }

  async invokeSkill(
    skillId: string,
    params?: Record<string, unknown>
  ): Promise<unknown> {
    return this.request(`/api/skills/${skillId}/invoke`, "POST", params || {});
  }

  // Workflows (n8n integration)
  async triggerWorkflow(
    workflowId: string,
    data?: Record<string, unknown>
  ): Promise<unknown> {
    return this.request(`/api/workflows/${workflowId}/trigger`, "POST", data || {});
  }

  async listWorkflows(active?: boolean): Promise<unknown> {
    const query = active !== undefined ? `?active=${active}` : "";
    return this.request(`/api/workflows${query}`);
  }
}
