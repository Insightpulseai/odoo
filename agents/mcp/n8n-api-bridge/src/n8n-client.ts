/**
 * n8n Public API Client
 *
 * HTTP client for n8n Public API with error handling,
 * request validation, and type safety.
 */

import fetch from 'node-fetch';

/**
 * n8n API response types
 */
export interface N8nWorkflow {
  id: string;
  name: string;
  active: boolean;
  createdAt: string;
  updatedAt: string;
  tags?: Array<{ id: string; name: string }>;
  versionId?: string;
}

export interface N8nWorkflowDetail extends N8nWorkflow {
  nodes: unknown[];
  connections: Record<string, unknown>;
  settings?: Record<string, unknown>;
  staticData?: unknown;
}

export interface N8nExecution {
  id: string;
  workflowId: string;
  workflowName?: string;
  mode: string;
  status: 'success' | 'error' | 'running' | 'waiting' | 'canceled';
  startedAt: string;
  stoppedAt?: string;
  finished: boolean;
}

export interface N8nExecutionDetail extends N8nExecution {
  data?: {
    resultData?: {
      runData?: Record<string, unknown[]>;
      error?: {
        message: string;
        stack?: string;
      };
    };
  };
}

export interface N8nWorkflowsResponse {
  data: N8nWorkflow[];
  nextCursor?: string;
}

export interface N8nExecutionsResponse {
  data: N8nExecution[];
}

export interface N8nAuditEvent {
  category: string;
  action: string;
  metadata?: Record<string, unknown>;
}

/**
 * n8n API Client configuration
 */
export interface N8nClientConfig {
  baseUrl: string;
  apiKey: string;
  timeout?: number;
}

/**
 * n8n API Client
 */
export class N8nClient {
  private readonly baseUrl: string;
  private readonly apiKey: string;
  private readonly timeout: number;

  constructor(config: N8nClientConfig) {
    this.baseUrl = config.baseUrl.replace(/\/$/, ''); // Remove trailing slash
    this.apiKey = config.apiKey;
    this.timeout = config.timeout ?? 30000;
  }

  /**
   * Make authenticated request to n8n API
   */
  private async request<T>(
    method: string,
    endpoint: string,
    body?: unknown
  ): Promise<T> {
    const url = `${this.baseUrl}/api/v1${endpoint}`;

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        method,
        headers: {
          'X-N8N-API-KEY': this.apiKey,
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: body ? JSON.stringify(body) : undefined,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorText = await response.text();
        let errorMessage: string;

        try {
          const errorJson = JSON.parse(errorText);
          errorMessage = errorJson.message || errorJson.error || errorText;
        } catch {
          errorMessage = errorText || response.statusText;
        }

        throw new Error(
          `n8n API error (${response.status}): ${errorMessage}`
        );
      }

      const data = await response.json();
      return data as T;
    } catch (error) {
      clearTimeout(timeoutId);

      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          throw new Error(`Request timeout after ${this.timeout}ms`);
        }
        throw error;
      }

      throw new Error('Unknown error occurred during API request');
    }
  }

  /**
   * List workflows with optional pagination
   */
  async listWorkflows(params?: {
    limit?: number;
    cursor?: string;
  }): Promise<N8nWorkflowsResponse> {
    const queryParams = new URLSearchParams();

    if (params?.limit) {
      queryParams.append('limit', params.limit.toString());
    }
    if (params?.cursor) {
      queryParams.append('cursor', params.cursor);
    }

    const query = queryParams.toString();
    const endpoint = query ? `/workflows?${query}` : '/workflows';

    return this.request<N8nWorkflowsResponse>('GET', endpoint);
  }

  /**
   * Get detailed workflow information by ID
   */
  async getWorkflow(id: string): Promise<N8nWorkflowDetail> {
    if (!id || typeof id !== 'string') {
      throw new Error('Workflow ID must be a non-empty string');
    }

    return this.request<N8nWorkflowDetail>('GET', `/workflows/${id}`);
  }

  /**
   * List workflow executions with optional filtering
   */
  async listExecutions(params?: {
    limit?: number;
    workflowId?: string;
  }): Promise<N8nExecutionsResponse> {
    const queryParams = new URLSearchParams();

    if (params?.limit) {
      queryParams.append('limit', params.limit.toString());
    }
    if (params?.workflowId) {
      queryParams.append('workflowId', params.workflowId);
    }

    const query = queryParams.toString();
    const endpoint = query ? `/executions?${query}` : '/executions';

    return this.request<N8nExecutionsResponse>('GET', endpoint);
  }

  /**
   * Get detailed execution information and logs
   */
  async getExecution(id: string): Promise<N8nExecutionDetail> {
    if (!id || typeof id !== 'string') {
      throw new Error('Execution ID must be a non-empty string');
    }

    return this.request<N8nExecutionDetail>('GET', `/executions/${id}`);
  }

  /**
   * Retry a failed workflow execution
   */
  async retryExecution(id: string): Promise<{ success: boolean; executionId: string }> {
    if (!id || typeof id !== 'string') {
      throw new Error('Execution ID must be a non-empty string');
    }

    return this.request<{ success: boolean; executionId: string }>(
      'POST',
      `/executions/${id}/retry`
    );
  }

  /**
   * Log audit event to n8n
   */
  async audit(event: N8nAuditEvent): Promise<{ success: boolean }> {
    if (!event.category || !event.action) {
      throw new Error('Audit event must have category and action');
    }

    return this.request<{ success: boolean }>('POST', '/audit', event);
  }

  /**
   * Health check for n8n API connectivity
   */
  async healthCheck(): Promise<{ healthy: boolean; version?: string }> {
    try {
      // Most n8n instances expose /healthz endpoint
      const response = await fetch(`${this.baseUrl}/healthz`, {
        method: 'GET',
        headers: { 'Accept': 'application/json' },
      });

      return {
        healthy: response.ok,
        version: response.headers.get('X-N8N-Version') || undefined,
      };
    } catch {
      return { healthy: false };
    }
  }
}

/**
 * Create n8n client from environment variables
 */
export function createN8nClientFromEnv(): N8nClient {
  const baseUrl = process.env.N8N_BASE_URL;
  const apiKey = process.env.N8N_API_KEY;

  if (!baseUrl) {
    throw new Error('N8N_BASE_URL environment variable is required');
  }

  if (!apiKey) {
    throw new Error('N8N_API_KEY environment variable is required');
  }

  return new N8nClient({
    baseUrl,
    apiKey,
    timeout: process.env.REQUEST_TIMEOUT
      ? parseInt(process.env.REQUEST_TIMEOUT, 10)
      : undefined,
  });
}
