/**
 * n8n Public API client
 */

import fetch from 'node-fetch';
import {
  N8nConfig,
  N8nApiError,
  N8nWorkflow,
  N8nExecution,
  N8nCredential,
  N8nTag,
  N8nPaginatedResponse,
  MutationNotAllowedError,
} from './types.js';

export class N8nClient {
  private readonly baseUrl: string;
  private readonly headers: Record<string, string>;
  private readonly timeout: number;
  private readonly allowMutations: boolean;

  constructor(config: N8nConfig) {
    this.baseUrl = `${config.baseUrl}/api/v1`;
    this.headers = {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      'X-N8N-API-KEY': config.apiKey,
    };
    this.timeout = config.requestTimeout;
    this.allowMutations = config.allowMutations;
  }

  // ========================================================================
  // Low-level HTTP methods
  // ========================================================================

  private async request<T>(
    method: string,
    path: string,
    body?: unknown,
  ): Promise<T> {
    const url = `${this.baseUrl}${path}`;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        method,
        headers: this.headers,
        body: body ? JSON.stringify(body) : undefined,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const text = await response.text();
        let errorMessage = `n8n API error: ${response.status} ${response.statusText}`;

        try {
          const json = JSON.parse(text);
          errorMessage = json.message ?? errorMessage;
        } catch {
          // Use default message if response is not JSON
        }

        throw new N8nApiError(errorMessage, response.status, text);
      }

      // Handle 204 No Content
      if (response.status === 204) {
        return {} as T;
      }

      const data = await response.json();
      return data as T;
    } catch (error) {
      clearTimeout(timeoutId);

      if (error instanceof N8nApiError) {
        throw error;
      }

      if ((error as Error).name === 'AbortError') {
        throw new N8nApiError(`Request timeout after ${this.timeout}ms`);
      }

      throw new N8nApiError(
        `Network error: ${(error as Error).message}`,
        undefined,
        error,
      );
    }
  }

  private async get<T>(path: string): Promise<T> {
    return this.request<T>('GET', path);
  }

  private async post<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>('POST', path, body);
  }

  private async patch<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>('PATCH', path, body);
  }

  private async delete<T>(path: string): Promise<T> {
    return this.request<T>('DELETE', path);
  }

  private ensureMutationsAllowed(operation: string): void {
    if (!this.allowMutations) {
      throw new MutationNotAllowedError(operation);
    }
  }

  // ========================================================================
  // Workflow API
  // ========================================================================

  async listWorkflows(params?: {
    active?: boolean;
    tags?: string[];
    limit?: number;
    cursor?: string;
  }): Promise<N8nPaginatedResponse<N8nWorkflow>> {
    const query = new URLSearchParams();

    if (params?.active !== undefined) {
      query.set('active', String(params.active));
    }
    if (params?.tags?.length) {
      query.set('tags', params.tags.join(','));
    }
    if (params?.limit) {
      query.set('limit', String(params.limit));
    }
    if (params?.cursor) {
      query.set('cursor', params.cursor);
    }

    const path = `/workflows${query.toString() ? `?${query.toString()}` : ''}`;
    return this.get<N8nPaginatedResponse<N8nWorkflow>>(path);
  }

  async getWorkflow(workflowId: string): Promise<N8nWorkflow> {
    return this.get<N8nWorkflow>(`/workflows/${workflowId}`);
  }

  async activateWorkflow(workflowId: string): Promise<N8nWorkflow> {
    this.ensureMutationsAllowed('activate_workflow');
    return this.patch<N8nWorkflow>(`/workflows/${workflowId}`, { active: true });
  }

  async deactivateWorkflow(workflowId: string): Promise<N8nWorkflow> {
    this.ensureMutationsAllowed('deactivate_workflow');
    return this.patch<N8nWorkflow>(`/workflows/${workflowId}`, { active: false });
  }

  async triggerWorkflow(
    workflowId: string,
    data?: Record<string, unknown>,
  ): Promise<N8nExecution> {
    this.ensureMutationsAllowed('trigger_workflow');
    return this.post<N8nExecution>(`/workflows/${workflowId}/execute`, data);
  }

  // ========================================================================
  // Execution API
  // ========================================================================

  async listExecutions(params?: {
    workflowId?: string;
    status?: N8nExecution['status'];
    limit?: number;
    cursor?: string;
  }): Promise<N8nPaginatedResponse<N8nExecution>> {
    const query = new URLSearchParams();

    if (params?.workflowId) {
      query.set('workflowId', params.workflowId);
    }
    if (params?.status) {
      query.set('status', params.status);
    }
    if (params?.limit) {
      query.set('limit', String(params.limit));
    }
    if (params?.cursor) {
      query.set('cursor', params.cursor);
    }

    const path = `/executions${query.toString() ? `?${query.toString()}` : ''}`;
    return this.get<N8nPaginatedResponse<N8nExecution>>(path);
  }

  async getExecution(executionId: string, includeData = true): Promise<N8nExecution> {
    const query = includeData ? '?includeData=true' : '';
    return this.get<N8nExecution>(`/executions/${executionId}${query}`);
  }

  async deleteExecution(executionId: string): Promise<void> {
    this.ensureMutationsAllowed('delete_execution');
    await this.delete<void>(`/executions/${executionId}`);
  }

  async retryExecution(executionId: string): Promise<N8nExecution> {
    this.ensureMutationsAllowed('retry_execution');
    return this.post<N8nExecution>(`/executions/${executionId}/retry`);
  }

  // ========================================================================
  // Audit API
  // ========================================================================

  async audit(event: {
    category: string;
    action: string;
    metadata?: Record<string, unknown>;
  }): Promise<{ success: boolean }> {
    return this.post<{ success: boolean }>('/audit', event);
  }

  // ========================================================================
  // Credential API (metadata only)
  // ========================================================================

  async listCredentials(params?: {
    limit?: number;
    cursor?: string;
  }): Promise<N8nPaginatedResponse<N8nCredential>> {
    const query = new URLSearchParams();

    if (params?.limit) {
      query.set('limit', String(params.limit));
    }
    if (params?.cursor) {
      query.set('cursor', params.cursor);
    }

    const path = `/credentials${query.toString() ? `?${query.toString()}` : ''}`;
    return this.get<N8nPaginatedResponse<N8nCredential>>(path);
  }

  // ========================================================================
  // Tag API
  // ========================================================================

  async listTags(params?: {
    limit?: number;
    cursor?: string;
  }): Promise<N8nPaginatedResponse<N8nTag>> {
    const query = new URLSearchParams();

    if (params?.limit) {
      query.set('limit', String(params.limit));
    }
    if (params?.cursor) {
      query.set('cursor', params.cursor);
    }

    const path = `/tags${query.toString() ? `?${query.toString()}` : ''}`;
    return this.get<N8nPaginatedResponse<N8nTag>>(path);
  }
}
