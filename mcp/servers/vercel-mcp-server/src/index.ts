#!/usr/bin/env node
/**
 * Vercel MCP Server
 *
 * Tools for managing Vercel platform:
 * - Projects: list, get details, env vars
 * - Deployments: list, trigger, promote, rollback
 * - Logs: get deployment/runtime logs
 * - Domains: list, add, remove
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";
import { VercelClient } from "./vercel-client.js";

const VERCEL_TOKEN = process.env.VERCEL_TOKEN;
const VERCEL_TEAM_ID = process.env.VERCEL_TEAM_ID;

if (!VERCEL_TOKEN) {
  console.error("Error: VERCEL_TOKEN environment variable required");
  process.exit(1);
}

const client = new VercelClient(VERCEL_TOKEN, VERCEL_TEAM_ID);

const tools: Tool[] = [
  // Project tools
  {
    name: "list_projects",
    description: "List all Vercel projects",
    inputSchema: {
      type: "object",
      properties: {
        limit: { type: "number", description: "Max results (default 20)" },
      },
    },
  },
  {
    name: "get_project",
    description: "Get project details",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "string", description: "Project ID or name" },
      },
      required: ["project_id"],
    },
  },
  {
    name: "get_project_env",
    description: "Get project environment variables",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "string", description: "Project ID or name" },
      },
      required: ["project_id"],
    },
  },
  // Deployment tools
  {
    name: "list_deployments",
    description: "List recent deployments",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "string", description: "Project ID or name" },
        limit: { type: "number", description: "Max results (default 10)" },
      },
      required: ["project_id"],
    },
  },
  {
    name: "get_deployment",
    description: "Get deployment details",
    inputSchema: {
      type: "object",
      properties: {
        deployment_id: { type: "string", description: "Deployment ID or URL" },
      },
      required: ["deployment_id"],
    },
  },
  {
    name: "trigger_deployment",
    description: "Trigger a new deployment via deploy hook",
    inputSchema: {
      type: "object",
      properties: {
        hook_url: { type: "string", description: "Deploy hook URL" },
      },
      required: ["hook_url"],
    },
  },
  {
    name: "promote_deployment",
    description: "Promote a deployment to production",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "string", description: "Project ID" },
        deployment_id: { type: "string", description: "Deployment ID" },
      },
      required: ["project_id", "deployment_id"],
    },
  },
  {
    name: "rollback_deployment",
    description: "Rollback to a previous deployment",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "string", description: "Project ID" },
        deployment_id: { type: "string", description: "Target deployment ID" },
      },
      required: ["project_id", "deployment_id"],
    },
  },
  // Log tools
  {
    name: "get_deployment_logs",
    description: "Get build logs for a deployment",
    inputSchema: {
      type: "object",
      properties: {
        deployment_id: { type: "string", description: "Deployment ID" },
      },
      required: ["deployment_id"],
    },
  },
  {
    name: "get_runtime_logs",
    description: "Get runtime/function logs",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "string", description: "Project ID" },
        deployment_id: { type: "string", description: "Deployment ID (optional)" },
        since: { type: "number", description: "Unix timestamp to start from" },
      },
      required: ["project_id"],
    },
  },
  // Domain tools
  {
    name: "list_domains",
    description: "List project domains",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "string", description: "Project ID" },
      },
      required: ["project_id"],
    },
  },
];

const server = new Server(
  {
    name: "vercel-mcp-server",
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
      case "list_projects":
        result = await client.listProjects(args?.limit as number);
        break;
      case "get_project":
        result = await client.getProject(args.project_id as string);
        break;
      case "get_project_env":
        result = await client.getProjectEnv(args.project_id as string);
        break;
      case "list_deployments":
        result = await client.listDeployments(
          args.project_id as string,
          args?.limit as number
        );
        break;
      case "get_deployment":
        result = await client.getDeployment(args.deployment_id as string);
        break;
      case "trigger_deployment":
        result = await client.triggerDeployment(args.hook_url as string);
        break;
      case "promote_deployment":
        result = await client.promoteDeployment(
          args.project_id as string,
          args.deployment_id as string
        );
        break;
      case "rollback_deployment":
        result = await client.rollbackDeployment(
          args.project_id as string,
          args.deployment_id as string
        );
        break;
      case "get_deployment_logs":
        result = await client.getDeploymentLogs(args.deployment_id as string);
        break;
      case "get_runtime_logs":
        result = await client.getRuntimeLogs(
          args.project_id as string,
          args?.deployment_id as string,
          args?.since as number
        );
        break;
      case "list_domains":
        result = await client.listDomains(args.project_id as string);
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
  console.error("Vercel MCP Server running on stdio");
}

main().catch(console.error);
