/**
 * MCP Tool Definitions for n8n Public API Bridge
 *
 * Maps n8n Public API operations to MCP tools with validation,
 * error handling, and mutation controls.
 */

import { z } from 'zod';
import type { N8nClient } from './n8n-client.js';

/**
 * Environment configuration for mutation control
 */
const ALLOW_MUTATIONS = process.env.ALLOW_MUTATIONS === 'true';

/**
 * Zod schemas for tool parameters validation
 */
const ListWorkflowsSchema = z.object({
  limit: z.number().int().positive().max(100).optional().describe('Maximum number of workflows to return (1-100)'),
  cursor: z.string().optional().describe('Pagination cursor from previous response'),
});

const GetWorkflowSchema = z.object({
  id: z.string().min(1).describe('Workflow ID'),
});

const ListExecutionsSchema = z.object({
  limit: z.number().int().positive().max(100).optional().describe('Maximum number of executions to return (1-100)'),
  workflowId: z.string().optional().describe('Filter executions by workflow ID'),
});

const GetExecutionSchema = z.object({
  id: z.string().min(1).describe('Execution ID'),
});

const RetryExecutionSchema = z.object({
  id: z.string().min(1).describe('Execution ID to retry'),
});

const AuditEventSchema = z.object({
  event: z.object({
    category: z.string().min(1).describe('Event category (e.g., workflow, execution, user)'),
    action: z.string().min(1).describe('Action performed (e.g., created, updated, deleted)'),
    metadata: z.record(z.unknown()).optional().describe('Additional event metadata'),
  }).describe('Audit event details'),
});

/**
 * Tool handler type definition
 */
type ToolHandler<T> = (params: T) => Promise<unknown>;

/**
 * MCP Tool definition structure
 */
interface MCPTool<T = unknown> {
  name: string;
  description: string;
  inputSchema: z.ZodSchema<T>;
  handler: ToolHandler<T>;
}

/**
 * Create MCP tools for n8n API bridge
 */
export function createN8nTools(client: N8nClient): MCPTool[] {
  const tools: MCPTool[] = [
    {
      name: 'n8n.list_workflows',
      description: 'List all n8n workflows with optional filters. Returns workflow metadata including ID, name, active status, and creation date.',
      inputSchema: ListWorkflowsSchema,
      handler: async (params) => {
        try {
          const workflows = await client.listWorkflows(params);
          return {
            success: true,
            data: workflows,
            count: workflows.data.length,
            cursor: workflows.nextCursor,
          };
        } catch (error) {
          return {
            success: false,
            error: error instanceof Error ? error.message : 'Unknown error occurred',
            details: error instanceof Error ? error.stack : undefined,
          };
        }
      },
    },

    {
      name: 'n8n.get_workflow',
      description: 'Get detailed workflow information by ID. Returns complete workflow definition including nodes, connections, settings, and metadata.',
      inputSchema: GetWorkflowSchema,
      handler: async (params) => {
        try {
          const workflow = await client.getWorkflow(params.id);
          return {
            success: true,
            data: workflow,
          };
        } catch (error) {
          return {
            success: false,
            error: error instanceof Error ? error.message : 'Unknown error occurred',
            details: error instanceof Error ? error.stack : undefined,
          };
        }
      },
    },

    {
      name: 'n8n.list_executions',
      description: 'List workflow execution history with optional filtering. Returns execution metadata including status, start/end times, and workflow information.',
      inputSchema: ListExecutionsSchema,
      handler: async (params) => {
        try {
          const executions = await client.listExecutions(params);
          return {
            success: true,
            data: executions,
            count: executions.data.length,
          };
        } catch (error) {
          return {
            success: false,
            error: error instanceof Error ? error.message : 'Unknown error occurred',
            details: error instanceof Error ? error.stack : undefined,
          };
        }
      },
    },

    {
      name: 'n8n.get_execution',
      description: 'Get detailed execution information and logs by ID. Returns complete execution data including status, timing, error messages, and node execution details.',
      inputSchema: GetExecutionSchema,
      handler: async (params) => {
        try {
          const execution = await client.getExecution(params.id);
          return {
            success: true,
            data: execution,
          };
        } catch (error) {
          return {
            success: false,
            error: error instanceof Error ? error.message : 'Unknown error occurred',
            details: error instanceof Error ? error.stack : undefined,
          };
        }
      },
    },

    {
      name: 'n8n.audit',
      description: 'Log audit event to n8n for compliance and tracking. Records workflow/execution/user events with metadata for audit trails.',
      inputSchema: AuditEventSchema,
      handler: async (params) => {
        try {
          const result = await client.audit(params.event);
          return {
            success: true,
            data: result,
            message: 'Audit event logged successfully',
          };
        } catch (error) {
          return {
            success: false,
            error: error instanceof Error ? error.message : 'Unknown error occurred',
            details: error instanceof Error ? error.stack : undefined,
          };
        }
      },
    },
  ];

  // Add mutation tool only if mutations are enabled
  if (ALLOW_MUTATIONS) {
    tools.push({
      name: 'n8n.retry_execution',
      description: 'Retry a failed workflow execution. Requires ALLOW_MUTATIONS=true. Re-runs the workflow with the same input data and parameters.',
      inputSchema: RetryExecutionSchema,
      handler: async (params) => {
        try {
          const result = await client.retryExecution(params.id);
          return {
            success: true,
            data: result,
            message: `Execution ${params.id} queued for retry`,
          };
        } catch (error) {
          return {
            success: false,
            error: error instanceof Error ? error.message : 'Unknown error occurred',
            details: error instanceof Error ? error.stack : undefined,
          };
        }
      },
    });
  }

  return tools;
}

/**
 * Get available tool names based on configuration
 */
export function getAvailableTools(): string[] {
  const baseTools = [
    'n8n.list_workflows',
    'n8n.get_workflow',
    'n8n.list_executions',
    'n8n.get_execution',
    'n8n.audit',
  ];

  if (ALLOW_MUTATIONS) {
    baseTools.push('n8n.retry_execution');
  }

  return baseTools;
}

/**
 * Check if mutations are enabled
 */
export function areMutationsEnabled(): boolean {
  return ALLOW_MUTATIONS;
}
