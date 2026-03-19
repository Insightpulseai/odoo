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
 * Workflow tool node
 */
export interface WorkflowTool {
  nodeId: string;
  nodeName: string;
  nodeType: string;
  workflowId: string;
  workflowName: string;
  toolDescription?: string;
  operation?: string;
  parameters?: Record<string, unknown>;
}

/**
 * Tool execution context
 */
export interface ToolExecutionContext {
  workflowId: string;
  inputData?: Record<string, unknown>;
  aiContext?: {
    message?: string;
    variables?: Record<string, unknown>;
  };
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
   * Activate workflow
   */
  async activateWorkflow(id: string): Promise<WorkflowDetail> {
    if (!id) {
      throw new Error('Workflow ID is required');
    }
    this.checkMutationsAllowed('activateWorkflow');
    return this.request<WorkflowDetail>('PATCH', `/api/v1/workflows/${id}`, { active: true });
  }

  /**
   * Deactivate workflow
   */
  async deactivateWorkflow(id: string): Promise<WorkflowDetail> {
    if (!id) {
      throw new Error('Workflow ID is required');
    }
    this.checkMutationsAllowed('deactivateWorkflow');
    return this.request<WorkflowDetail>('PATCH', `/api/v1/workflows/${id}`, { active: false });
  }

  /**
   * Trigger workflow execution
   */
  async triggerWorkflow(id: string, data?: Record<string, unknown>): Promise<Execution> {
    if (!id) {
      throw new Error('Workflow ID is required');
    }
    this.checkMutationsAllowed('triggerWorkflow');
    return this.request<Execution>('POST', `/api/v1/workflows/${id}/execute`, data);
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
  async getExecution(id: string, includeData = true): Promise<ExecutionDetail> {
    if (!id) {
      throw new Error('Execution ID is required');
    }
    const query = includeData ? '?includeData=true' : '';
    return this.request<ExecutionDetail>('GET', `/api/v1/executions/${id}${query}`);
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
   * Delete execution
   */
  async deleteExecution(id: string): Promise<void> {
    if (!id) {
      throw new Error('Execution ID is required');
    }
    this.checkMutationsAllowed('deleteExecution');
    await this.request<void>('DELETE', `/api/v1/executions/${id}`);
  }

  /**
   * List credentials (metadata only)
   */
  async listCredentials(options?: ListWorkflowsOptions): Promise<PaginatedResponse<{ id: string; name: string; type: string }>> {
    const params = new URLSearchParams();
    if (options?.limit) {
      params.set('limit', options.limit.toString());
    }
    if (options?.cursor) {
      params.set('cursor', options.cursor);
    }

    const queryString = params.toString();
    const path = `/api/v1/credentials${queryString ? `?${queryString}` : ''}`;

    return this.request<PaginatedResponse<{ id: string; name: string; type: string }>>('GET', path);
  }

  /**
   * List tags
   */
  async listTags(options?: ListWorkflowsOptions): Promise<PaginatedResponse<{ id: string; name: string }>> {
    const params = new URLSearchParams();
    if (options?.limit) {
      params.set('limit', options.limit.toString());
    }
    if (options?.cursor) {
      params.set('cursor', options.cursor);
    }

    const queryString = params.toString();
    const path = `/api/v1/tags${queryString ? `?${queryString}` : ''}`;

    return this.request<PaginatedResponse<{ id: string; name: string }>>('GET', path);
  }

  /**
   * List workflow tools
   *
   * Finds tool-compatible nodes in workflows (jiraTool, notionTool, etc.)
   * that can be used by AI agents
   */
  async listWorkflowTools(workflowId?: string): Promise<WorkflowTool[]> {
    const tools: WorkflowTool[] = [];

    // Get workflows to search
    let workflows: WorkflowDetail[];
    if (workflowId) {
      workflows = [await this.getWorkflow(workflowId)];
    } else {
      const response = await this.listWorkflows({ limit: 100 });
      workflows = await Promise.all(
        response.data.map(w => this.getWorkflow(w.id))
      );
    }

    // Extract tool nodes
    for (const workflow of workflows) {
      for (const node of workflow.nodes) {
        // Check if node is a tool (ends with "Tool" or has toolDescription)
        const isTool = node.type.endsWith('Tool') ||
                       (node.parameters?.toolDescription as string | undefined);

        if (isTool) {
          tools.push({
            nodeId: node.id,
            nodeName: node.name,
            nodeType: node.type,
            workflowId: workflow.id,
            workflowName: workflow.name,
            toolDescription: node.parameters?.toolDescription as string | undefined,
            operation: node.parameters?.operation as string | undefined,
            parameters: node.parameters,
          });
        }
      }
    }

    return tools;
  }

  /**
   * Execute workflow with AI context
   *
   * Triggers workflow execution with AI-provided context and variables
   */
  async executeWorkflowWithContext(
    context: ToolExecutionContext
  ): Promise<ExecutionDetail> {
    if (!context.workflowId) {
      throw new Error('workflowId is required in ToolExecutionContext');
    }

    this.checkMutationsAllowed('executeWorkflowWithContext');

    // Prepare execution payload with AI context
    const payload: Record<string, unknown> = {
      ...context.inputData,
    };

    // Add AI context as metadata
    if (context.aiContext) {
      payload._aiContext = context.aiContext;
    }

    // Trigger workflow
    const execution = await this.triggerWorkflow(context.workflowId, payload);

    // Wait briefly for execution to complete, then fetch details
    await new Promise(resolve => setTimeout(resolve, 1000));

    return this.getExecution(execution.id, true);
  }

  /**
   * Get tool definition from workflow
   *
   * Extracts tool schema and parameters for a specific tool node
   */
  async getToolDefinition(
    workflowId: string,
    nodeId: string
  ): Promise<WorkflowTool | null> {
    const workflow = await this.getWorkflow(workflowId);
    const node = workflow.nodes.find(n => n.id === nodeId);

    if (!node) {
      return null;
    }

    return {
      nodeId: node.id,
      nodeName: node.name,
      nodeType: node.type,
      workflowId: workflow.id,
      workflowName: workflow.name,
      toolDescription: node.parameters?.toolDescription as string | undefined,
      operation: node.parameters?.operation as string | undefined,
      parameters: node.parameters,
    };
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
