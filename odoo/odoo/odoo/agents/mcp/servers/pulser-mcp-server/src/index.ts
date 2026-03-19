#!/usr/bin/env node
/**
 * Pulser MCP Server
 *
 * Tools for Pulser agent orchestration:
 * - Agents: list, run, cancel
 * - Runs: get status, get output, list history
 * - Skills: list available, invoke skill
 * - Workflows: trigger n8n workflows
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";
import { PulserClient } from "./pulser-client.js";

const PULSER_API_URL = process.env.PULSER_API_URL || "http://localhost:3000";
const PULSER_API_KEY = process.env.PULSER_API_KEY;

const client = new PulserClient(PULSER_API_URL, PULSER_API_KEY);

const tools: Tool[] = [
  // Agent tools
  {
    name: "list_agents",
    description: "List available agents and their capabilities",
    inputSchema: {
      type: "object",
      properties: {
        category: { type: "string", description: "Filter by category" },
      },
    },
  },
  {
    name: "run_agent",
    description: "Execute an agent with given input",
    inputSchema: {
      type: "object",
      properties: {
        agent_id: { type: "string", description: "Agent identifier" },
        input: { type: "object", description: "Input data for the agent" },
        context: { type: "object", description: "Optional execution context" },
        async: { type: "boolean", description: "Run asynchronously (default true)" },
      },
      required: ["agent_id", "input"],
    },
  },
  {
    name: "cancel_run",
    description: "Cancel a running agent execution",
    inputSchema: {
      type: "object",
      properties: {
        run_id: { type: "string", description: "Run ID to cancel" },
      },
      required: ["run_id"],
    },
  },
  // Run status tools
  {
    name: "get_run_status",
    description: "Get status of an agent run",
    inputSchema: {
      type: "object",
      properties: {
        run_id: { type: "string", description: "Run ID" },
      },
      required: ["run_id"],
    },
  },
  {
    name: "get_run_output",
    description: "Get output/result of a completed run",
    inputSchema: {
      type: "object",
      properties: {
        run_id: { type: "string", description: "Run ID" },
      },
      required: ["run_id"],
    },
  },
  {
    name: "list_runs",
    description: "List recent agent runs",
    inputSchema: {
      type: "object",
      properties: {
        agent_id: { type: "string", description: "Filter by agent" },
        status: {
          type: "string",
          enum: ["pending", "running", "completed", "failed", "cancelled"],
          description: "Filter by status",
        },
        limit: { type: "number", description: "Max results (default 20)" },
      },
    },
  },
  // Skill tools
  {
    name: "list_skills",
    description: "List available skills that can be invoked",
    inputSchema: {
      type: "object",
      properties: {},
    },
  },
  {
    name: "invoke_skill",
    description: "Invoke a skill directly",
    inputSchema: {
      type: "object",
      properties: {
        skill_id: { type: "string", description: "Skill identifier" },
        params: { type: "object", description: "Skill parameters" },
      },
      required: ["skill_id"],
    },
  },
  // Workflow tools
  {
    name: "trigger_workflow",
    description: "Trigger an n8n workflow via webhook",
    inputSchema: {
      type: "object",
      properties: {
        workflow_id: { type: "string", description: "Workflow ID" },
        data: { type: "object", description: "Webhook payload data" },
      },
      required: ["workflow_id"],
    },
  },
  {
    name: "list_workflows",
    description: "List available n8n workflows",
    inputSchema: {
      type: "object",
      properties: {
        active: { type: "boolean", description: "Filter by active status" },
      },
    },
  },
];

const server = new Server(
  {
    name: "pulser-mcp-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools,
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    let result: unknown;

    switch (name) {
      case "list_agents":
        result = await client.listAgents(args?.category as string);
        break;
      case "run_agent":
        result = await client.runAgent(
          args.agent_id as string,
          args.input as Record<string, unknown>,
          args?.context as Record<string, unknown>,
          args?.async as boolean
        );
        break;
      case "cancel_run":
        result = await client.cancelRun(args.run_id as string);
        break;
      case "get_run_status":
        result = await client.getRunStatus(args.run_id as string);
        break;
      case "get_run_output":
        result = await client.getRunOutput(args.run_id as string);
        break;
      case "list_runs":
        result = await client.listRuns(
          args?.agent_id as string,
          args?.status as string,
          args?.limit as number
        );
        break;
      case "list_skills":
        result = await client.listSkills();
        break;
      case "invoke_skill":
        result = await client.invokeSkill(
          args.skill_id as string,
          args?.params as Record<string, unknown>
        );
        break;
      case "trigger_workflow":
        result = await client.triggerWorkflow(
          args.workflow_id as string,
          args?.data as Record<string, unknown>
        );
        break;
      case "list_workflows":
        result = await client.listWorkflows(args?.active as boolean);
        break;
      default:
        throw new Error(`Unknown tool: ${name}`);
    }

    return {
      content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return {
      content: [{ type: "text", text: `Error: ${message}` }],
      isError: true,
    };
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Pulser MCP Server running on stdio");
}

main().catch(console.error);
