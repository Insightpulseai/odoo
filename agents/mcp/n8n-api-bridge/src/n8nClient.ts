/**
 * n8n Public API Client
 *
 * Implements the n8n Public API with authentication, error handling,
 * and mutation guards.
 *
 * @see https://docs.n8n.io/api/
 */

import fetch, { Response } from 'node-fetch';

/**
 * n8n API Error
 */
export class N8nApiError extends Error {
  constructor(
    public statusCode: number,
    message: string,
    public details?: unknown
  ) {
    super(message);
    this.name = 'N8nApiError';
  }
}

/**
 * Workflow list options
 */
export interface ListWorkflowsOptions {
  limit?: number;
  cursor?: string;
}

/**
 * Workflow metadata
 */
export interface Workflow {
  id: string;
  name: string;
  active: boolean;
  createdAt: string;
  updatedAt: string;
  tags?: Array<{ id: string; name: string }>;
}

/**
 * Workflow detail (includes nodes)
 */
export interface WorkflowDetail extends Workflow {
  nodes: Array<{
    id: string;
    name: string;
    type: string;
    position: [number, number];
    parameters?: Record<string, unknown>;
  }>;
  connections?: Record<string, unknown>;
  settings?: Record<string, unknown>;
}

/**
 * Execution list options
 */
export interface ListExecutionsOptions {
  limit?: number;
  cursor?: string;
  workflowId?: string;
}

/**
 * Execution metadata
 */
export interface Execution {
  id: string;
  workflowId: string;
  mode: 'manual' | 'trigger' | 'webhook' | 'retry';
  startedAt: string;
  stoppedAt?: string;
  status: 'success' | 'error' | 'waiting' | 'canceled' | 'running';
}

/**
 * Execution detail (includes data)
 */
export interface ExecutionDetail extends Execution {
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

/**
 * Audit event payload
 */
export interface AuditEvent {
  eventName: string;
  userId?: string;
  metadata?: Record<string, unknown>;
}

/**
 * Paginated response
 */
interface PaginatedResponse<T> {
  data: T[];
  nextCursor?: string;
}

/**
 * n8n API Client
 */
export class N8nClient {
  private readonly baseUrl: string;
  private readonly apiKey: string;
  private readonly allowMutations: boolean;

  constructor() {
    const baseUrl = process.env.N8N_BASE_URL;
    const apiKey = process.env.N8N_API_KEY;

    if (!baseUrl) {
      throw new Error('N8N_BASE_URL environment variable is required');
    }
    if (!apiKey) {
      throw new Error('N8N_API_KEY environment variable is required');
    }

    this.baseUrl = baseUrl.replace(/\/$/, ''); // Remove trailing slash
    this.apiKey = apiKey;
    this.allowMutations = process.env.ALLOW_MUTATIONS === 'true';
  }

  /**
   * Make HTTP request to n8n API
   */
  private async request<T>(
    method: string,
    path: string,
    body?: unknown
  ): Promise<T> {
    const url = `${this.baseUrl}${path}`;

    const headers: Record<string, string> = {
      'Accept': 'application/json',
      'X-N8N-API-KEY': this.apiKey,
    };

    if (body !== undefined) {
      headers['Content-Type'] = 'application/json';
    }

    const options = {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    };

    let response: Response;
    try {
      response = await fetch(url, options);
    } catch (error) {
      throw new N8nApiError(
        0,
        `Network error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        { url, method }
      );
    }

    // Handle non-2xx responses
    if (!response.ok) {
      let errorDetails: unknown;
      try {
        errorDetails = await response.json();
      } catch {
        errorDetails = await response.text();
      }

      // Normalize error messages by status code
      let message: string;
      switch (response.status) {
        case 401:
          message = 'Authentication failed: Invalid API key';
          break;
        case 404:
          message = 'Resource not found';
          break;
        case 429:
          message = 'Rate limit exceeded';
          break;
        default:
          message = `API error: ${response.statusText}`;
      }

      throw new N8nApiError(response.status, message, errorDetails);
    }

    // Parse successful response
    try {
      return await response.json() as T;
    } catch (error) {
      throw new N8nApiError(
        response.status,
        `Failed to parse response: ${error instanceof Error ? error.message : 'Unknown error'}`,
        { url, method }
      );
    }
  }

  /**
   * Check if mutations are allowed, throw if not
   */
  private checkMutationsAllowed(operation: string): void {
    if (!this.allowMutations) {
      throw new Error(
        `Mutation operation '${operation}' is disabled. Set ALLOW_MUTATIONS=true to enable.`
      );
    }
  }

  /**
   * List workflows
   *
   * @see https://docs.n8n.io/api/v1/workflows/
   */
  async listWorkflows(
    options?: ListWorkflowsOptions
  ): Promise<PaginatedResponse<Workflow>> {
    const params = new URLSearchParams();
    if (options?.limit) {
      params.set('limit', options.limit.toString());
    }
    if (options?.cursor) {
      params.set('cursor', options.cursor);
    }

    const queryString = params.toString();
    const path = `/api/v1/workflows${queryString ? `?${queryString}` : ''}`;

    return this.request<PaginatedResponse<Workflow>>('GET', path);
  }

  /**
   * Get workflow by ID
   *
   * @see https://docs.n8n.io/api/v1/workflows/
   */
  async getWorkflow(id: string): Promise<WorkflowDetail> {
    if (!id) {
      throw new Error('Workflow ID is required');
    }
    return this.request<WorkflowDetail>('GET', `/api/v1/workflows/${id}`);
  }

  /**
   * List executions
   *
   * @see https://docs.n8n.io/api/v1/executions/
   */
  async listExecutions(
    options?: ListExecutionsOptions
  ): Promise<PaginatedResponse<Execution>> {
    const params = new URLSearchParams();
    if (options?.limit) {
      params.set('limit', options.limit.toString());
    }
    if (options?.cursor) {
      params.set('cursor', options.cursor);
    }
    if (options?.workflowId) {
      params.set('workflowId', options.workflowId);
    }

    const queryString = params.toString();
    const path = `/api/v1/executions${queryString ? `?${queryString}` : ''}`;

    return this.request<PaginatedResponse<Execution>>('GET', path);
  }

  /**
   * Get execution by ID
   *
   * @see https://docs.n8n.io/api/v1/executions/
   */
  async getExecution(id: string): Promise<ExecutionDetail> {
    if (!id) {
      throw new Error('Execution ID is required');
    }
    return this.request<ExecutionDetail>('GET', `/api/v1/executions/${id}`);
  }

  /**
   * Retry failed execution
   *
   * @see https://docs.n8n.io/api/v1/executions/
   */
  async retryExecution(id: string): Promise<ExecutionDetail> {
    if (!id) {
      throw new Error('Execution ID is required');
    }
    this.checkMutationsAllowed('retryExecution');

    return this.request<ExecutionDetail>('POST', `/api/v1/executions/${id}/retry`);
  }

  /**
   * Submit audit event
   *
   * Note: Exempt from mutation guard (audit is read-only logging)
   *
   * @see https://docs.n8n.io/api/v1/audit/
   */
  async audit(event: AuditEvent): Promise<void> {
    if (!event.eventName) {
      throw new Error('eventName is required in AuditEvent');
    }

    // Audit is exempt from mutation guard
    await this.request<void>('POST', '/api/v1/audit', event);
  }
}

/**
 * Create singleton client instance
 */
let clientInstance: N8nClient | null = null;

export function getN8nClient(): N8nClient {
  if (!clientInstance) {
    clientInstance = new N8nClient();
  }
  return clientInstance;
}

/**
 * Reset client instance (for testing)
 */
export function resetN8nClient(): void {
  clientInstance = null;
}
