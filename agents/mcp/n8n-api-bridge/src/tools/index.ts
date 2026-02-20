/**
 * MCP Tool Registry
 *
 * Registers all n8n API tools with the MCP server.
 */

import { N8nClient } from '../n8nClient.js';
import {
  ListWorkflowsParamsSchema,
  GetWorkflowParamsSchema,
  ActivateWorkflowParamsSchema,
  DeactivateWorkflowParamsSchema,
  TriggerWorkflowParamsSchema,
  ListExecutionsParamsSchema,
  GetExecutionParamsSchema,
  DeleteExecutionParamsSchema,
  RetryExecutionParamsSchema,
  AuditEventParamsSchema,
  ListCredentialsParamsSchema,
  ListTagsParamsSchema,
  McpToolDefinition,
} from '../types.js';
import { aiTools } from './aiTools.js';

/**
 * MCP Tool definition
 */
export interface McpTool {
  name: string;
  description: string;
  inputSchema: {
    type: 'object';
    properties: Record<string, unknown>;
    required?: string[];
  };
  handler: (args: Record<string, unknown>) => Promise<unknown>;
}

/**
 * Logger interface
 */
interface Logger {
  debug(message: string, ...args: unknown[]): void;
  info(message: string, ...args: unknown[]): void;
  warn(message: string, ...args: unknown[]): void;
  error(message: string, ...args: unknown[]): void;
}

/**
 * Convert McpToolDefinition to McpTool format
 */
function convertToolDefinition(toolDef: McpToolDefinition): McpTool {
  return {
    name: toolDef.name,
    description: toolDef.description,
    inputSchema: {
      type: 'object' as const,
      properties: toolDef.inputSchema.shape as Record<string, unknown>,
      required: toolDef.inputSchema._def.unknownKeys === 'strict'
        ? Object.keys(toolDef.inputSchema.shape).filter(key =>
            !toolDef.inputSchema.shape[key]._def.typeName?.includes('Optional')
          )
        : [],
    },
    handler: async (args) => {
      const result = await toolDef.handler(args);
      // Convert McpToolResponse to simple return value
      if (result.content && result.content[0]?.type === 'text') {
        return JSON.parse(result.content[0].text || '{}');
      }
      return result;
    },
  };
}

/**
 * Register all tools
 */
export function registerTools(client: N8nClient, logger: Logger): McpTool[] {
  // Standard workflow/execution tools
  const standardTools: McpTool[] = [
    // ====================================================================
    // Workflow Tools
    // ====================================================================
    {
      name: 'n8n_list_workflows',
      description: 'List all workflows with optional filters for active status and tags',
      inputSchema: {
        type: 'object' as const,
        properties: ListWorkflowsParamsSchema.shape as Record<string, unknown>,
        required: [],
      },
      handler: async (args) => {
        const params = ListWorkflowsParamsSchema.parse(args);
        logger.debug('Listing workflows with params:', params);
        return await client.listWorkflows(params);
      },
    },

    {
      name: 'n8n_get_workflow',
      description: 'Get detailed information about a specific workflow including nodes and connections',
      inputSchema: {
        type: 'object' as const,
        properties: GetWorkflowParamsSchema.shape as Record<string, unknown>,
        required: ['workflowId'],
      },
      handler: async (args) => {
        const params = GetWorkflowParamsSchema.parse(args);
        logger.debug(`Getting workflow: ${params.workflowId}`);
        return await client.getWorkflow(params.workflowId);
      },
    },

    {
      name: 'n8n_activate_workflow',
      description: 'Activate a workflow to enable automatic execution (requires ALLOW_MUTATIONS=true)',
      inputSchema: {
        type: 'object' as const,
        properties: ActivateWorkflowParamsSchema.shape as Record<string, unknown>,
        required: ['workflowId'],
      },
      handler: async (args) => {
        const params = ActivateWorkflowParamsSchema.parse(args);
        logger.info(`Activating workflow: ${params.workflowId}`);
        return await client.activateWorkflow(params.workflowId);
      },
    },

    {
      name: 'n8n_deactivate_workflow',
      description: 'Deactivate a workflow to disable automatic execution (requires ALLOW_MUTATIONS=true)',
      inputSchema: {
        type: 'object' as const,
        properties: DeactivateWorkflowParamsSchema.shape as Record<string, unknown>,
        required: ['workflowId'],
      },
      handler: async (args) => {
        const params = DeactivateWorkflowParamsSchema.parse(args);
        logger.info(`Deactivating workflow: ${params.workflowId}`);
        return await client.deactivateWorkflow(params.workflowId);
      },
    },

    {
      name: 'n8n_trigger_workflow',
      description: 'Manually trigger a workflow execution with optional input data (requires ALLOW_MUTATIONS=true)',
      inputSchema: {
        type: 'object' as const,
        properties: TriggerWorkflowParamsSchema.shape as Record<string, unknown>,
        required: ['workflowId'],
      },
      handler: async (args) => {
        const params = TriggerWorkflowParamsSchema.parse(args);
        logger.info(`Triggering workflow: ${params.workflowId}`);
        return await client.triggerWorkflow(params.workflowId, params.data);
      },
    },

    // ====================================================================
    // Execution Tools
    // ====================================================================
    {
      name: 'n8n_list_executions',
      description: 'List workflow executions with optional filters for workflow ID and status',
      inputSchema: {
        type: 'object' as const,
        properties: ListExecutionsParamsSchema.shape as Record<string, unknown>,
        required: [],
      },
      handler: async (args) => {
        const params = ListExecutionsParamsSchema.parse(args);
        logger.debug('Listing executions with params:', params);
        return await client.listExecutions(params);
      },
    },

    {
      name: 'n8n_get_execution',
      description: 'Get detailed information about a specific execution including result data',
      inputSchema: {
        type: 'object' as const,
        properties: GetExecutionParamsSchema.shape as Record<string, unknown>,
        required: ['executionId'],
      },
      handler: async (args) => {
        const params = GetExecutionParamsSchema.parse(args);
        logger.debug(`Getting execution: ${params.executionId}`);
        return await client.getExecution(params.executionId, params.includeData);
      },
    },

    {
      name: 'n8n_delete_execution',
      description: 'Delete a workflow execution (requires ALLOW_MUTATIONS=true)',
      inputSchema: {
        type: 'object' as const,
        properties: DeleteExecutionParamsSchema.shape as Record<string, unknown>,
        required: ['executionId'],
      },
      handler: async (args) => {
        const params = DeleteExecutionParamsSchema.parse(args);
        logger.info(`Deleting execution: ${params.executionId}`);
        await client.deleteExecution(params.executionId);
        return { success: true, deletedExecutionId: params.executionId };
      },
    },

    {
      name: 'n8n_retry_execution',
      description: 'Retry a failed workflow execution (requires ALLOW_MUTATIONS=true)',
      inputSchema: {
        type: 'object' as const,
        properties: RetryExecutionParamsSchema.shape as Record<string, unknown>,
        required: ['executionId'],
      },
      handler: async (args) => {
        const params = RetryExecutionParamsSchema.parse(args);
        logger.info(`Retrying execution: ${params.executionId}`);
        const result = await client.retryExecution(params.executionId);
        return { success: true, execution: result };
      },
    },

    // ====================================================================
    // Audit Tools
    // ====================================================================

    {
      name: 'n8n_audit',
      description: 'Log audit event to n8n for compliance and tracking',
      inputSchema: {
        type: 'object' as const,
        properties: AuditEventParamsSchema.shape as Record<string, unknown>,
        required: ['eventName'],
      },
      handler: async (args) => {
        const params = AuditEventParamsSchema.parse(args);
        logger.info(`Logging audit event: ${params.eventName}`);
        await client.audit(params);
        return { success: true };
      },
    },

    // ====================================================================
    // Credential Tools (metadata only)
    // ====================================================================
    {
      name: 'n8n_list_credentials',
      description: 'List credential metadata (does not expose sensitive credential data)',
      inputSchema: {
        type: 'object' as const,
        properties: ListCredentialsParamsSchema.shape as Record<string, unknown>,
        required: [],
      },
      handler: async (args) => {
        const params = ListCredentialsParamsSchema.parse(args);
        logger.debug('Listing credentials');
        return await client.listCredentials(params);
      },
    },

    // ====================================================================
    // Tag Tools
    // ====================================================================
    {
      name: 'n8n_list_tags',
      description: 'List all workflow tags',
      inputSchema: {
        type: 'object' as const,
        properties: ListTagsParamsSchema.shape as Record<string, unknown>,
        required: [],
      },
      handler: async (args) => {
        const params = ListTagsParamsSchema.parse(args);
        logger.debug('Listing tags');
        return await client.listTags(params);
      },
    },
  ];

  // AI Agent Tools
  const aiAgentTools: McpTool[] = aiTools.map(toolDef => {
    const converted = convertToolDefinition(toolDef);
    // Wrap handler with logging
    const originalHandler = converted.handler;
    converted.handler = async (args) => {
      logger.info(`AI Tool: ${toolDef.name}`, args);
      return await originalHandler(args);
    };
    return converted;
  });

  // Combine all tools
  return [
    ...standardTools,
    ...aiAgentTools,
  ];
}
