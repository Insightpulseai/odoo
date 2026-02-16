#!/usr/bin/env node
/**
 * SpecKit MCP Server
 *
 * Tools for spec bundle enforcement and validation:
 * - Bundles: list, validate, ensure required files
 * - Specs: get content, diff against implementation
 * - Tasks: list, update status, sync with code
 * - Constitution: validate compliance
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";
import { SpecKitClient } from "./speckit-client.js";

const REPO_ROOT = process.env.REPO_ROOT || process.cwd();
const SPEC_DIR = process.env.SPEC_DIR || "spec";

const client = new SpecKitClient(REPO_ROOT, SPEC_DIR);

const tools: Tool[] = [
  // Bundle tools
  {
    name: "list_spec_bundles",
    description: "List all spec bundles in the repository",
    inputSchema: {
      type: "object",
      properties: {
        include_status: {
          type: "boolean",
          description: "Include validation status for each bundle",
        },
      },
    },
  },
  {
    name: "get_spec_bundle",
    description: "Get contents of a spec bundle",
    inputSchema: {
      type: "object",
      properties: {
        slug: { type: "string", description: "Spec bundle slug (directory name)" },
      },
      required: ["slug"],
    },
  },
  {
    name: "validate_spec_bundle",
    description: "Validate a spec bundle has all required files",
    inputSchema: {
      type: "object",
      properties: {
        slug: { type: "string", description: "Spec bundle slug" },
      },
      required: ["slug"],
    },
  },
  {
    name: "ensure_spec_bundle",
    description: "Create missing files in a spec bundle with templates",
    inputSchema: {
      type: "object",
      properties: {
        slug: { type: "string", description: "Spec bundle slug" },
        title: { type: "string", description: "Human-readable title for templates" },
      },
      required: ["slug"],
    },
  },
  {
    name: "list_missing_specs",
    description: "Find features/modules without spec bundles",
    inputSchema: {
      type: "object",
      properties: {
        scan_paths: {
          type: "array",
          items: { type: "string" },
          description: "Paths to scan for features (default: addons/ipai/)",
        },
      },
    },
  },
  // Spec content tools
  {
    name: "get_prd",
    description: "Get the PRD (Product Requirements Document) for a feature",
    inputSchema: {
      type: "object",
      properties: {
        slug: { type: "string", description: "Spec bundle slug" },
      },
      required: ["slug"],
    },
  },
  {
    name: "get_constitution",
    description: "Get the constitution (non-negotiable rules) for a feature",
    inputSchema: {
      type: "object",
      properties: {
        slug: { type: "string", description: "Spec bundle slug" },
      },
      required: ["slug"],
    },
  },
  {
    name: "get_plan",
    description: "Get the implementation plan for a feature",
    inputSchema: {
      type: "object",
      properties: {
        slug: { type: "string", description: "Spec bundle slug" },
      },
      required: ["slug"],
    },
  },
  // Task tools
  {
    name: "get_tasks",
    description: "Get task checklist for a spec bundle",
    inputSchema: {
      type: "object",
      properties: {
        slug: { type: "string", description: "Spec bundle slug" },
        status: {
          type: "string",
          enum: ["all", "pending", "in_progress", "completed"],
          description: "Filter by status",
        },
      },
      required: ["slug"],
    },
  },
  {
    name: "update_task_status",
    description: "Update a task's status in tasks.md",
    inputSchema: {
      type: "object",
      properties: {
        slug: { type: "string", description: "Spec bundle slug" },
        task_id: { type: "string", description: "Task identifier" },
        status: {
          type: "string",
          enum: ["pending", "in_progress", "completed"],
          description: "New status",
        },
      },
      required: ["slug", "task_id", "status"],
    },
  },
  // Validation tools
  {
    name: "validate_all_bundles",
    description: "Validate all spec bundles in the repository",
    inputSchema: {
      type: "object",
      properties: {},
    },
  },
  {
    name: "spec_coverage_report",
    description: "Generate a spec coverage report",
    inputSchema: {
      type: "object",
      properties: {
        format: {
          type: "string",
          enum: ["json", "markdown"],
          description: "Output format",
        },
      },
    },
  },
];

const server = new Server(
  {
    name: "speckit-mcp-server",
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
      case "list_spec_bundles":
        result = await client.listBundles(args?.include_status as boolean);
        break;
      case "get_spec_bundle":
        result = await client.getBundle(args.slug as string);
        break;
      case "validate_spec_bundle":
        result = await client.validateBundle(args.slug as string);
        break;
      case "ensure_spec_bundle":
        result = await client.ensureBundle(
          args.slug as string,
          args?.title as string
        );
        break;
      case "list_missing_specs":
        result = await client.listMissingSpecs(args?.scan_paths as string[]);
        break;
      case "get_prd":
        result = await client.getFile(args.slug as string, "prd.md");
        break;
      case "get_constitution":
        result = await client.getFile(args.slug as string, "constitution.md");
        break;
      case "get_plan":
        result = await client.getFile(args.slug as string, "plan.md");
        break;
      case "get_tasks":
        result = await client.getTasks(args.slug as string, args?.status as string);
        break;
      case "update_task_status":
        result = await client.updateTaskStatus(
          args.slug as string,
          args.task_id as string,
          args.status as string
        );
        break;
      case "validate_all_bundles":
        result = await client.validateAllBundles();
        break;
      case "spec_coverage_report":
        result = await client.generateCoverageReport(args?.format as string);
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
  console.error("SpecKit MCP Server running on stdio");
}

main().catch(console.error);
