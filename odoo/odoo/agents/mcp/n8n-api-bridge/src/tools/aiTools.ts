/**
 * AI Agent Tool Support for n8n MCP Bridge
 *
 * Enables Claude to discover and execute n8n workflow tools,
 * supporting advanced AI agent patterns like the JIRA automation workflow.
 */

import { z } from 'zod';
import { getN8nClient } from '../n8nClient.js';
import type { McpToolDefinition } from '../types.js';

/**
 * List workflow tools
 *
 * Discovers tool-compatible nodes in n8n workflows that can be used
 * by AI agents (e.g., jiraTool, notionTool, custom Odoo tools)
 */
export const listWorkflowTools: McpToolDefinition = {
  name: 'n8n_list_workflow_tools',
  description: 'List AI agent tools available in n8n workflows. Returns tool nodes that can be executed by AI agents for operations like searching JIRA, querying knowledge bases, or calling Odoo/Supabase APIs.',
  inputSchema: z.object({
    workflowId: z
      .string()
      .optional()
      .describe('Workflow ID to search for tools (omit to search all workflows)'),
    toolType: z
      .string()
      .optional()
      .describe('Filter by tool type (e.g., "jiraTool", "notionTool", "odooTool")'),
  }),
  handler: async (args) => {
    const client = getN8nClient();
    const allTools = await client.listWorkflowTools(args.workflowId);

    // Filter by tool type if specified
    let tools = allTools;
    if (args.toolType) {
      tools = allTools.filter(t => t.nodeType.includes(args.toolType!));
    }

    // Format for readability
    const formatted = tools.map(t => ({
      tool_id: `${t.workflowId}:${t.nodeId}`,
      name: t.nodeName,
      type: t.nodeType,
      workflow: t.workflowName,
      description: t.toolDescription || 'No description provided',
      operation: t.operation,
    }));

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            total_tools: formatted.length,
            tools: formatted,
          }, null, 2),
        },
      ],
    };
  },
};

/**
 * Execute workflow with AI context
 *
 * Triggers workflow execution with AI-provided context, enabling
 * workflows to use AI-generated parameters and variables
 */
export const executeWorkflowWithContext: McpToolDefinition = {
  name: 'n8n_execute_workflow_with_context',
  description: 'Execute n8n workflow with AI context. Use this to run workflows that contain AI agent tools, passing LLM-generated parameters and context. Returns execution details including tool outputs.',
  inputSchema: z.object({
    workflowId: z
      .string()
      .describe('Workflow ID to execute'),
    inputData: z
      .record(z.unknown())
      .optional()
      .describe('Input data for workflow execution'),
    aiContext: z
      .object({
        message: z.string().optional().describe('AI message/prompt for the workflow'),
        variables: z.record(z.unknown()).optional().describe('AI-generated variables'),
      })
      .optional()
      .describe('AI context to pass to workflow'),
  }),
  handler: async (args) => {
    const client = getN8nClient();

    const execution = await client.executeWorkflowWithContext({
      workflowId: args.workflowId,
      inputData: args.inputData,
      aiContext: args.aiContext,
    });

    // Extract execution results
    const result = {
      execution_id: execution.id,
      workflow_id: execution.workflowId,
      status: execution.status,
      started_at: execution.startedAt,
      stopped_at: execution.stoppedAt,
      error: execution.data?.resultData?.error,
      outputs: execution.data?.resultData?.runData,
    };

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(result, null, 2),
        },
      ],
    };
  },
};

/**
 * Get tool definition
 *
 * Retrieves detailed information about a specific tool node,
 * including its schema, parameters, and usage instructions
 */
export const getToolDefinition: McpToolDefinition = {
  name: 'n8n_get_tool_definition',
  description: 'Get detailed definition of an n8n workflow tool. Returns tool schema, parameters, and usage instructions for integrating with AI agents.',
  inputSchema: z.object({
    workflowId: z
      .string()
      .describe('Workflow ID containing the tool'),
    nodeId: z
      .string()
      .describe('Node ID of the tool'),
  }),
  handler: async (args) => {
    const client = getN8nClient();

    const toolDef = await client.getToolDefinition(args.workflowId, args.nodeId);

    if (!toolDef) {
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              error: 'Tool not found',
              workflow_id: args.workflowId,
              node_id: args.nodeId,
            }, null, 2),
          },
        ],
      };
    }

    // Extract parameter schema if available
    const schema = toolDef.parameters?.inputSchema ||
                   toolDef.parameters?.schema ||
                   'No schema defined';

    const definition = {
      tool_id: `${toolDef.workflowId}:${toolDef.nodeId}`,
      name: toolDef.nodeName,
      type: toolDef.nodeType,
      workflow: toolDef.workflowName,
      description: toolDef.toolDescription || 'No description provided',
      operation: toolDef.operation,
      schema: schema,
      parameters: toolDef.parameters,
    };

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(definition, null, 2),
        },
      ],
    };
  },
};

/**
 * All AI agent tools
 */
export const aiTools: McpToolDefinition[] = [
  listWorkflowTools,
  executeWorkflowWithContext,
  getToolDefinition,
];
