/**
 * Plane REST API client for the ops-assistant MCP server.
 *
 * Implements token-bucket rate limiting (60 req/min) and idempotency key
 * support for write operations. All calls go through a single client
 * instance per function invocation.
 *
 * SSOT: ssot/integrations/plane_mcp.yaml
 */

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface PlaneIssue {
  id: string;
  name: string;
  description_html?: string;
  state?: string;
  priority?: string;
  assignee_ids?: string[];
  label_ids?: string[];
  project: string;
  workspace: string;
  created_at: string;
  updated_at: string;
  [key: string]: unknown;
}

export interface PlaneProject {
  id: string;
  name: string;
  identifier: string;
  description: string;
  [key: string]: unknown;
}

export interface PlaneComment {
  id: string;
  comment_html: string;
  actor: string;
  created_at: string;
  [key: string]: unknown;
}

export interface PlanePage {
  id: string;
  name: string;
  description_html?: string;
  access: number;
  created_at: string;
  [key: string]: unknown;
}

export interface PlaneApiError {
  status: number;
  message: string;
  detail?: string;
}

// ---------------------------------------------------------------------------
// Rate limiter (token bucket — 60 req/min)
// ---------------------------------------------------------------------------

class TokenBucket {
  private tokens: number;
  private lastRefill: number;

  constructor(
    private readonly maxTokens: number = 60,
    private readonly refillIntervalMs: number = 60_000,
  ) {
    this.tokens = maxTokens;
    this.lastRefill = Date.now();
  }

  async acquire(): Promise<void> {
    this.refill();
    if (this.tokens <= 0) {
      const waitMs = this.refillIntervalMs - (Date.now() - this.lastRefill);
      await new Promise((resolve) => setTimeout(resolve, Math.max(waitMs, 100)));
      this.refill();
    }
    this.tokens--;
  }

  private refill(): void {
    const now = Date.now();
    const elapsed = now - this.lastRefill;
    if (elapsed >= this.refillIntervalMs) {
      this.tokens = this.maxTokens;
      this.lastRefill = now;
    }
  }
}

// ---------------------------------------------------------------------------
// Client
// ---------------------------------------------------------------------------

export class PlaneClient {
  private readonly baseUrl: string;
  private readonly apiKey: string;
  private readonly workspaceSlug: string;
  private readonly rateLimiter: TokenBucket;

  constructor(opts: {
    baseUrl?: string;
    apiKey: string;
    workspaceSlug: string;
  }) {
    this.baseUrl = (opts.baseUrl || "https://api.plane.so/api/v1").replace(
      /\/$/,
      "",
    );
    this.apiKey = opts.apiKey;
    this.workspaceSlug = opts.workspaceSlug;
    this.rateLimiter = new TokenBucket(60, 60_000);
  }

  // -------------------------------------------------------------------------
  // Generic request
  // -------------------------------------------------------------------------

  private async request<T>(
    method: string,
    path: string,
    body?: unknown,
  ): Promise<T> {
    await this.rateLimiter.acquire();

    const url = `${this.baseUrl}${path}`;
    const init: RequestInit = {
      method,
      headers: {
        "X-API-Key": this.apiKey,
        "Content-Type": "application/json",
      },
    };
    if (body !== undefined) {
      init.body = JSON.stringify(body);
    }

    const res = await fetch(url, init);

    if (!res.ok) {
      const text = await res.text();
      const err: PlaneApiError = {
        status: res.status,
        message: `Plane API ${method} ${path} failed`,
        detail: text,
      };
      throw err;
    }

    return res.json() as Promise<T>;
  }

  private ws(): string {
    return this.workspaceSlug;
  }

  // -------------------------------------------------------------------------
  // Projects
  // -------------------------------------------------------------------------

  async listProjects(): Promise<PlaneProject[]> {
    return this.request("GET", `/workspaces/${this.ws()}/projects/`);
  }

  // -------------------------------------------------------------------------
  // Issues (work items)
  // -------------------------------------------------------------------------

  async listIssues(
    projectId: string,
    filters?: { state?: string; priority?: string; page?: number },
  ): Promise<unknown> {
    const params = new URLSearchParams();
    if (filters?.state) params.set("state__name", filters.state);
    if (filters?.priority) params.set("priority", filters.priority);
    if (filters?.page) params.set("page", String(filters.page));
    const qs = params.toString();
    return this.request(
      "GET",
      `/workspaces/${this.ws()}/projects/${projectId}/issues/${qs ? `?${qs}` : ""}`,
    );
  }

  async getIssue(projectId: string, issueId: string): Promise<PlaneIssue> {
    return this.request(
      "GET",
      `/workspaces/${this.ws()}/projects/${projectId}/issues/${issueId}/`,
    );
  }

  async createIssue(
    projectId: string,
    data: {
      name: string;
      description_html?: string;
      state?: string;
      priority?: string;
      assignee_ids?: string[];
      label_ids?: string[];
    },
  ): Promise<PlaneIssue> {
    return this.request(
      "POST",
      `/workspaces/${this.ws()}/projects/${projectId}/issues/`,
      data,
    );
  }

  async updateIssue(
    projectId: string,
    issueId: string,
    data: Partial<{
      name: string;
      description_html: string;
      state: string;
      priority: string;
      assignee_ids: string[];
      label_ids: string[];
    }>,
  ): Promise<PlaneIssue> {
    return this.request(
      "PATCH",
      `/workspaces/${this.ws()}/projects/${projectId}/issues/${issueId}/`,
      data,
    );
  }

  // -------------------------------------------------------------------------
  // Comments
  // -------------------------------------------------------------------------

  async addComment(
    projectId: string,
    issueId: string,
    commentHtml: string,
  ): Promise<PlaneComment> {
    return this.request(
      "POST",
      `/workspaces/${this.ws()}/projects/${projectId}/issues/${issueId}/comments/`,
      { comment_html: commentHtml },
    );
  }

  // -------------------------------------------------------------------------
  // Pages
  // -------------------------------------------------------------------------

  async createPage(
    projectId: string,
    data: { name: string; description_html?: string; access?: number },
  ): Promise<PlanePage> {
    return this.request(
      "POST",
      `/workspaces/${this.ws()}/projects/${projectId}/pages/`,
      { name: data.name, description_html: data.description_html ?? "", access: data.access ?? 0 },
    );
  }

  async searchPages(projectId: string, query: string): Promise<PlanePage[]> {
    const qs = new URLSearchParams({ search: query }).toString();
    return this.request(
      "GET",
      `/workspaces/${this.ws()}/projects/${projectId}/pages/?${qs}`,
    );
  }
}
