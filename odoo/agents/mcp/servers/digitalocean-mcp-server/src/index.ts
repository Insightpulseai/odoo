#!/usr/bin/env node
/**
 * DigitalOcean MCP Server
 *
 * Tools for managing DigitalOcean infrastructure:
 * - Droplets: list, create, reboot, power actions
 * - Apps: list, deploy, logs, specs
 * - Databases: list, connection strings
 * - Domains: list, DNS records
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";
import { DigitalOceanClient } from "./do-client.js";
import * as dropletTools from "./tools/droplets.js";
import * as appTools from "./tools/apps.js";

const DO_TOKEN = process.env.DIGITALOCEAN_TOKEN;

if (!DO_TOKEN) {
  console.error("Error: DIGITALOCEAN_TOKEN environment variable required");
  process.exit(1);
}

const client = new DigitalOceanClient(DO_TOKEN);

const tools: Tool[] = [
  // Droplet tools
  {
    name: "list_droplets",
    description: "List all droplets in the account",
    inputSchema: {
      type: "object",
      properties: {
        tag: { type: "string", description: "Filter by tag" },
      },
    },
  },
  {
    name: "get_droplet",
    description: "Get details of a specific droplet",
    inputSchema: {
      type: "object",
      properties: {
        droplet_id: { type: "number", description: "Droplet ID" },
      },
      required: ["droplet_id"],
    },
  },
  {
    name: "reboot_droplet",
    description: "Reboot a droplet",
    inputSchema: {
      type: "object",
      properties: {
        droplet_id: { type: "number", description: "Droplet ID" },
      },
      required: ["droplet_id"],
    },
  },
  {
    name: "power_cycle_droplet",
    description: "Power cycle (hard restart) a droplet",
    inputSchema: {
      type: "object",
      properties: {
        droplet_id: { type: "number", description: "Droplet ID" },
      },
      required: ["droplet_id"],
    },
  },
  // App Platform tools
  {
    name: "list_apps",
    description: "List all App Platform apps",
    inputSchema: {
      type: "object",
      properties: {},
    },
  },
  {
    name: "get_app",
    description: "Get details of a specific app",
    inputSchema: {
      type: "object",
      properties: {
        app_id: { type: "string", description: "App ID" },
      },
      required: ["app_id"],
    },
  },
  {
    name: "get_app_logs",
    description: "Get recent logs for an app deployment",
    inputSchema: {
      type: "object",
      properties: {
        app_id: { type: "string", description: "App ID" },
        deployment_id: {
          type: "string",
          description: "Deployment ID (optional, defaults to active)",
        },
        component: { type: "string", description: "Component name (optional)" },
        lines: {
          type: "number",
          description: "Number of log lines (default 100)",
        },
      },
      required: ["app_id"],
    },
  },
  {
    name: "deploy_app",
    description: "Trigger a new deployment for an app",
    inputSchema: {
      type: "object",
      properties: {
        app_id: { type: "string", description: "App ID" },
        force_build: {
          type: "boolean",
          description: "Force rebuild even if no changes",
        },
      },
      required: ["app_id"],
    },
  },
  {
    name: "create_app_from_spec",
    description: "Create a new app from an app spec YAML",
    inputSchema: {
      type: "object",
      properties: {
        spec: { type: "object", description: "App spec object" },
      },
      required: ["spec"],
    },
  },
  // Database tools
  {
    name: "list_databases",
    description: "List managed databases",
    inputSchema: {
      type: "object",
      properties: {},
    },
  },
  {
    name: "get_database_connection",
    description: "Get connection details for a database",
    inputSchema: {
      type: "object",
      properties: {
        database_id: { type: "string", description: "Database cluster ID" },
      },
      required: ["database_id"],
    },
  },
];

const server = new Server(
  {
    name: "digitalocean-mcp-server",
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
      case "list_droplets":
        result = await dropletTools.listDroplets(client, args?.tag as string);
        break;
      case "get_droplet":
        result = await dropletTools.getDroplet(client, args.droplet_id as number);
        break;
      case "reboot_droplet":
        result = await dropletTools.rebootDroplet(client, args.droplet_id as number);
        break;
      case "power_cycle_droplet":
        result = await dropletTools.powerCycleDroplet(client, args.droplet_id as number);
        break;
      case "list_apps":
        result = await appTools.listApps(client);
        break;
      case "get_app":
        result = await appTools.getApp(client, args.app_id as string);
        break;
      case "get_app_logs":
        result = await appTools.getAppLogs(
          client,
          args.app_id as string,
          args.deployment_id as string,
          args.component as string,
          args.lines as number
        );
        break;
      case "deploy_app":
        result = await appTools.deployApp(
          client,
          args.app_id as string,
          args.force_build as boolean
        );
        break;
      case "create_app_from_spec":
        result = await appTools.createAppFromSpec(client, args.spec);
        break;
      case "list_databases":
        result = await client.listDatabases();
        break;
      case "get_database_connection":
        result = await client.getDatabaseConnection(args.database_id as string);
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
  console.error("DigitalOcean MCP Server running on stdio");
}

main().catch(console.error);
