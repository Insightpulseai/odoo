#!/usr/bin/env node

/**
 * Ops Control Room MCP Server
 * 
 * This server exposes runbook planning and execution as ChatGPT tools.
 * When deployed, ChatGPT can invoke these tools to display inline runbook cards
 * and fullscreen execution logs.
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { 
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool
} from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";
import { planFromPrompt, executeRunbook } from "@ops-control-room/core";
import type { RunbookPlan, RunEvent } from "@ops-control-room/core";

const server = new Server(
  {
    name: "ops-control-room",
    version: "0.1.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

/**
 * Tool 1: plan_runbook
 * 
 * Parses a natural language prompt and returns a structured RunbookPlan.
 * The ChatGPT UI will render this as an inline card with Run/Edit actions.
 */
const planRunbookTool: Tool = {
  name: "plan_runbook",
  description: "Parse a natural language command (e.g., 'deploy prod', 'check status') and return a structured runbook plan with inputs, risks, and integrations.",
  inputSchema: {
    type: "object",
    properties: {
      prompt: {
        type: "string",
        description: "Natural language command describing the desired operation"
      }
    },
    required: ["prompt"]
  }
};

/**
 * Tool 2: execute_runbook
 * 
 * Executes a runbook plan and streams execution events.
 * In a ChatGPT App, this would trigger the fullscreen log viewer.
 */
const executeRunbookTool: Tool = {
  name: "execute_runbook",
  description: "Execute a runbook plan and stream execution events. Returns logs, status, and artifacts.",
  inputSchema: {
    type: "object",
    properties: {
      runbook_id: {
        type: "string",
        description: "The ID of the runbook plan to execute"
      },
      // In production, you'd accept input overrides here
    },
    required: ["runbook_id"]
  }
};

// Register tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [planRunbookTool, executeRunbookTool]
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name === "plan_runbook") {
    const { prompt } = args as { prompt: string };
    const plan = planFromPrompt(prompt);

    return {
      content: [
        {
          type: "text",
          text: `Created runbook plan: ${plan.title}`
        },
        {
          type: "text",
          text: JSON.stringify(plan, null, 2)
        }
      ]
    };
  }

  if (name === "execute_runbook") {
    const { runbook_id } = args as { runbook_id: string };

    // In production, you'd load the plan from storage
    // For demo, we'll re-parse from a default prompt
    const plan = planFromPrompt("check prod status");
    
    const events: RunEvent[] = [];
    
    // Collect all events (in production, you'd stream these)
    for await (const event of executeRunbook(plan)) {
      events.push(event);
    }

    const summary = {
      total: events.length,
      success: events.filter(e => e.level === "success").length,
      warnings: events.filter(e => e.level === "warn").length,
      errors: events.filter(e => e.level === "error").length
    };

    return {
      content: [
        {
          type: "text",
          text: `Executed runbook: ${plan.title}`
        },
        {
          type: "text",
          text: `Summary: ${summary.total} events, ${summary.success} success, ${summary.warnings} warnings, ${summary.errors} errors`
        },
        {
          type: "text",
          text: "Event log:\n" + events.map(e => 
            `[${new Date(e.ts).toLocaleTimeString()}] [${e.level.toUpperCase()}] ${e.source}: ${e.message}`
          ).join("\n")
        }
      ]
    };
  }

  throw new Error(`Unknown tool: ${name}`);
});

/**
 * Start the MCP server
 * 
 * For ChatGPT Apps:
 * 1. Deploy this server to a public HTTPS endpoint (e.g., Railway, Fly.io)
 * 2. Register the endpoint in ChatGPT's MCP connector
 * 3. ChatGPT will call these tools and render the UI based on responses
 * 
 * For local testing:
 * - Use the MCP Inspector: npx @modelcontextprotocol/inspector node dist/index.js
 */
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Ops Control Room MCP Server running on stdio");
}

main().catch((error) => {
  console.error("Server error:", error);
  process.exit(1);
});
