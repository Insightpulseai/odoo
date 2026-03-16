#!/usr/bin/env node
/**
 * Agent Coordination MCP Server
 *
 * Implements Agent-to-Agent (A2A) communication on MCP following
 * Microsoft's pattern for multi-agent orchestration.
 *
 * Tools:
 * - Registry: register, unregister, discover, list agents
 * - Invocation: invoke_agent, submit_job, get_job_status
 * - Coordination: handoff, delegate, broadcast
 * - State: get_agent_state, update_agent_state, heartbeat
 *
 * @see https://developer.microsoft.com/blog/can-you-build-agent2agent-communication-on-mcp-yes
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";
import { registry } from "./agent-registry.js";
import { coordinator } from "./coordinator.js";
import {
  AgentMetadata,
  AgentCapability,
  AgentStatus,
  AgentState,
  MessagePayload,
  MessagePriority,
  HandoffRequest,
  DelegationRequest,
} from "./types.js";

const tools: Tool[] = [
  // ============ Registry Tools ============
  {
    name: "register_agent",
    description:
      "Register a new agent or update existing registration in the A2A registry",
    inputSchema: {
      type: "object",
      properties: {
        id: { type: "string", description: "Unique agent identifier" },
        name: { type: "string", description: "Human-readable agent name" },
        version: { type: "string", description: "Agent version" },
        description: {
          type: "string",
          description: "What this agent does",
        },
        capabilities: {
          type: "array",
          items: { type: "string" },
          description:
            "Agent capabilities (odoo_erp, finance, hr, analytics, etc.)",
        },
        transport: {
          type: "string",
          enum: ["stdio", "http", "grpc", "websocket"],
          description: "Communication transport type",
        },
        endpoint: {
          type: "string",
          description: "HTTP endpoint for http transport",
        },
        mcp_server: {
          type: "string",
          description: "MCP server name for stdio transport",
        },
        tools: {
          type: "array",
          items: { type: "string" },
          description: "List of tools this agent exposes",
        },
        timeout_ms: {
          type: "number",
          description: "Default timeout for invocations (ms)",
        },
        max_concurrent: {
          type: "number",
          description: "Maximum concurrent requests",
        },
        tags: {
          type: "array",
          items: { type: "string" },
          description: "Tags for discovery filtering",
        },
      },
      required: ["id", "name", "version", "description", "capabilities", "transport"],
    },
  },
  {
    name: "unregister_agent",
    description: "Remove an agent from the A2A registry",
    inputSchema: {
      type: "object",
      properties: {
        agent_id: { type: "string", description: "Agent ID to unregister" },
      },
      required: ["agent_id"],
    },
  },
  {
    name: "discover_agents",
    description:
      "Find agents matching criteria (capabilities, status, tags, tools)",
    inputSchema: {
      type: "object",
      properties: {
        capabilities: {
          type: "array",
          items: { type: "string" },
          description: "Filter by capabilities",
        },
        status: {
          type: "array",
          items: {
            type: "string",
            enum: ["active", "idle", "busy", "offline", "maintenance"],
          },
          description: "Filter by status",
        },
        tags: {
          type: "array",
          items: { type: "string" },
          description: "Filter by tags",
        },
        tools: {
          type: "array",
          items: { type: "string" },
          description: "Filter by tools the agent exposes",
        },
        max_results: {
          type: "number",
          description: "Maximum number of results",
        },
      },
    },
  },
  {
    name: "list_agents",
    description: "List all registered agents in the A2A registry",
    inputSchema: {
      type: "object",
      properties: {},
    },
  },
  {
    name: "get_agent",
    description: "Get detailed information about a specific agent",
    inputSchema: {
      type: "object",
      properties: {
        agent_id: { type: "string", description: "Agent ID" },
      },
      required: ["agent_id"],
    },
  },

  // ============ Invocation Tools ============
  {
    name: "invoke_agent",
    description:
      "Invoke an agent synchronously and wait for response (A2A call)",
    inputSchema: {
      type: "object",
      properties: {
        target_agent_id: {
          type: "string",
          description: "ID of the agent to invoke",
        },
        tool_name: {
          type: "string",
          description: "Name of the tool to call on the target agent",
        },
        arguments: {
          type: "object",
          description: "Arguments to pass to the tool",
        },
        caller_agent_id: {
          type: "string",
          description: "ID of the calling agent (for context propagation)",
        },
        priority: {
          type: "string",
          enum: ["critical", "high", "normal", "low"],
          description: "Message priority",
        },
        timeout_ms: {
          type: "number",
          description: "Timeout for this invocation (ms)",
        },
      },
      required: ["target_agent_id", "tool_name"],
    },
  },
  {
    name: "submit_job",
    description:
      "Submit an async job to an agent (returns immediately with job ID)",
    inputSchema: {
      type: "object",
      properties: {
        source_agent_id: {
          type: "string",
          description: "ID of the agent submitting the job",
        },
        target_agent_id: {
          type: "string",
          description: "ID of the agent to execute the job",
        },
        tool_name: {
          type: "string",
          description: "Tool to invoke",
        },
        arguments: {
          type: "object",
          description: "Tool arguments",
        },
        priority: {
          type: "string",
          enum: ["critical", "high", "normal", "low"],
        },
        max_retries: {
          type: "number",
          description: "Maximum retry attempts",
        },
      },
      required: ["source_agent_id", "target_agent_id", "tool_name"],
    },
  },
  {
    name: "get_job_status",
    description: "Get the status of an async agent job",
    inputSchema: {
      type: "object",
      properties: {
        job_id: { type: "string", description: "Job ID" },
      },
      required: ["job_id"],
    },
  },
  {
    name: "cancel_job",
    description: "Cancel a queued job (cannot cancel running jobs)",
    inputSchema: {
      type: "object",
      properties: {
        job_id: { type: "string", description: "Job ID to cancel" },
      },
      required: ["job_id"],
    },
  },
  {
    name: "list_pending_jobs",
    description: "List pending jobs for an agent",
    inputSchema: {
      type: "object",
      properties: {
        agent_id: { type: "string", description: "Agent ID" },
        limit: { type: "number", description: "Max results (default 20)" },
      },
      required: ["agent_id"],
    },
  },

  // ============ Coordination Tools ============
  {
    name: "handoff",
    description:
      "Transfer conversation/task from one agent to another with context",
    inputSchema: {
      type: "object",
      properties: {
        from_agent_id: { type: "string", description: "Source agent ID" },
        to_agent_id: { type: "string", description: "Target agent ID" },
        reason: {
          type: "string",
          description: "Why the handoff is happening",
        },
        conversation_context: {
          type: "object",
          description: "Context to transfer to the new agent",
        },
        memory_refs: {
          type: "array",
          items: { type: "string" },
          description: "Memory references to include",
        },
        user_intent: {
          type: "string",
          description: "What the user is trying to accomplish",
        },
      },
      required: ["from_agent_id", "to_agent_id", "reason", "conversation_context"],
    },
  },
  {
    name: "delegate",
    description: "Delegate a subtask to another agent with constraints",
    inputSchema: {
      type: "object",
      properties: {
        delegator_id: {
          type: "string",
          description: "Agent delegating the task",
        },
        delegate_id: {
          type: "string",
          description: "Agent receiving the task",
        },
        tool_name: { type: "string", description: "Tool to invoke" },
        arguments: { type: "object", description: "Tool arguments" },
        timeout_ms: {
          type: "number",
          description: "Timeout constraint",
        },
        max_tokens: {
          type: "number",
          description: "Token limit constraint",
        },
        allowed_tools: {
          type: "array",
          items: { type: "string" },
          description: "Tools the delegate is allowed to use",
        },
      },
      required: ["delegator_id", "delegate_id", "tool_name"],
    },
  },
  {
    name: "broadcast",
    description: "Send a message to multiple agents simultaneously",
    inputSchema: {
      type: "object",
      properties: {
        from_agent_id: { type: "string", description: "Sender agent ID" },
        target_agent_ids: {
          type: "array",
          items: { type: "string" },
          description: "List of recipient agent IDs",
        },
        tool_name: { type: "string", description: "Tool to invoke on all" },
        arguments: { type: "object", description: "Tool arguments" },
      },
      required: ["from_agent_id", "target_agent_ids", "tool_name"],
    },
  },
  {
    name: "invoke_by_capability",
    description:
      "Find and invoke the best available agent with a specific capability",
    inputSchema: {
      type: "object",
      properties: {
        capability: {
          type: "string",
          description: "Required capability (odoo_erp, finance, hr, etc.)",
        },
        tool_name: { type: "string", description: "Tool to invoke" },
        arguments: { type: "object", description: "Tool arguments" },
        caller_agent_id: { type: "string", description: "Calling agent ID" },
      },
      required: ["capability", "tool_name"],
    },
  },

  // ============ State Tools ============
  {
    name: "get_agent_state",
    description: "Get runtime state of an agent (status, queue depth, metrics)",
    inputSchema: {
      type: "object",
      properties: {
        agent_id: { type: "string", description: "Agent ID" },
      },
      required: ["agent_id"],
    },
  },
  {
    name: "update_agent_state",
    description: "Update runtime state of an agent",
    inputSchema: {
      type: "object",
      properties: {
        agent_id: { type: "string", description: "Agent ID" },
        status: {
          type: "string",
          enum: ["active", "idle", "busy", "offline", "maintenance"],
        },
        current_task_id: { type: "string", description: "Current task ID" },
        queue_depth: { type: "number", description: "Items in queue" },
      },
      required: ["agent_id"],
    },
  },
  {
    name: "heartbeat",
    description: "Send heartbeat to keep agent registration active",
    inputSchema: {
      type: "object",
      properties: {
        agent_id: { type: "string", description: "Agent ID" },
      },
      required: ["agent_id"],
    },
  },
  {
    name: "update_agent_status",
    description: "Update agent status in the registry",
    inputSchema: {
      type: "object",
      properties: {
        agent_id: { type: "string", description: "Agent ID" },
        status: {
          type: "string",
          enum: ["active", "idle", "busy", "offline", "maintenance"],
          description: "New status",
        },
      },
      required: ["agent_id", "status"],
    },
  },

  // ============ History/Stats Tools ============
  {
    name: "get_message_history",
    description: "Get message history between two agents",
    inputSchema: {
      type: "object",
      properties: {
        agent_id_1: { type: "string", description: "First agent ID" },
        agent_id_2: { type: "string", description: "Second agent ID" },
        limit: { type: "number", description: "Max messages to return" },
      },
      required: ["agent_id_1", "agent_id_2"],
    },
  },
  {
    name: "get_registry_stats",
    description: "Get statistics about the agent registry",
    inputSchema: {
      type: "object",
      properties: {},
    },
  },
  {
    name: "cleanup_stale_agents",
    description: "Mark agents without recent heartbeat as offline",
    inputSchema: {
      type: "object",
      properties: {
        threshold_ms: {
          type: "number",
          description: "Threshold in ms (default 5 minutes)",
        },
      },
    },
  },
];

const server = new Server(
  {
    name: "agent-coordination-server",
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
      // Registry tools
      case "register_agent": {
        const agent: AgentMetadata = {
          id: args.id as string,
          name: args.name as string,
          version: args.version as string,
          description: args.description as string,
          capabilities: args.capabilities as AgentCapability[],
          transport: args.transport as AgentMetadata["transport"],
          endpoint: args.endpoint as string | undefined,
          mcp_server: args.mcp_server as string | undefined,
          tools: args.tools as string[] | undefined,
          timeout_ms: (args.timeout_ms as number) || 30000,
          max_concurrent: (args.max_concurrent as number) || 5,
          tags: args.tags as string[] | undefined,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        };
        result = await registry.register(agent);
        break;
      }
      case "unregister_agent":
        await registry.unregister(args.agent_id as string);
        result = { success: true, agent_id: args.agent_id };
        break;
      case "discover_agents":
        result = await registry.discover({
          capabilities: args.capabilities as AgentCapability[],
          status: args.status as AgentStatus[],
          tags: args.tags as string[],
          tools: args.tools as string[],
          max_results: args.max_results as number,
        });
        break;
      case "list_agents":
        result = await registry.listAll();
        break;
      case "get_agent":
        result = await registry.get(args.agent_id as string);
        break;

      // Invocation tools
      case "invoke_agent": {
        const payload: MessagePayload = {
          tool_name: args.tool_name as string,
          arguments: args.arguments as Record<string, unknown>,
        };
        result = await coordinator.invokeAgent(
          args.target_agent_id as string,
          payload,
          { caller_agent_id: args.caller_agent_id as string },
          {
            priority: args.priority as MessagePriority,
            timeout_ms: args.timeout_ms as number,
          }
        );
        break;
      }
      case "submit_job": {
        const jobPayload: MessagePayload = {
          tool_name: args.tool_name as string,
          arguments: args.arguments as Record<string, unknown>,
        };
        result = await coordinator.submitJob(
          args.source_agent_id as string,
          args.target_agent_id as string,
          jobPayload,
          undefined,
          {
            priority: args.priority as MessagePriority,
            max_retries: args.max_retries as number,
          }
        );
        break;
      }
      case "get_job_status":
        result = await coordinator.getJobStatus(args.job_id as string);
        break;
      case "cancel_job":
        result = await coordinator.cancelJob(args.job_id as string);
        break;
      case "list_pending_jobs":
        result = await coordinator.listPendingJobs(
          args.agent_id as string,
          args.limit as number
        );
        break;

      // Coordination tools
      case "handoff": {
        const handoffReq: HandoffRequest = {
          from_agent_id: args.from_agent_id as string,
          to_agent_id: args.to_agent_id as string,
          reason: args.reason as string,
          conversation_context: args.conversation_context as unknown,
          memory_refs: args.memory_refs as string[],
          user_intent: args.user_intent as string,
        };
        result = await coordinator.handoff(handoffReq);
        break;
      }
      case "delegate": {
        const delegateReq: DelegationRequest = {
          delegator_id: args.delegator_id as string,
          delegate_id: args.delegate_id as string,
          task: {
            tool_name: args.tool_name as string,
            arguments: args.arguments as Record<string, unknown>,
          },
          constraints: {
            timeout_ms: args.timeout_ms as number,
            max_tokens: args.max_tokens as number,
            allowed_tools: args.allowed_tools as string[],
          },
        };
        result = await coordinator.delegate(delegateReq);
        break;
      }
      case "broadcast": {
        const broadcastPayload: MessagePayload = {
          tool_name: args.tool_name as string,
          arguments: args.arguments as Record<string, unknown>,
        };
        const broadcastResults = await coordinator.broadcast(
          args.from_agent_id as string,
          args.target_agent_ids as string[],
          broadcastPayload
        );
        result = Object.fromEntries(broadcastResults);
        break;
      }
      case "invoke_by_capability": {
        const capPayload: MessagePayload = {
          tool_name: args.tool_name as string,
          arguments: args.arguments as Record<string, unknown>,
        };
        result = await coordinator.invokeByCapability(
          args.capability as string,
          capPayload,
          { caller_agent_id: args.caller_agent_id as string }
        );
        break;
      }

      // State tools
      case "get_agent_state":
        result = await registry.getState(args.agent_id as string);
        break;
      case "update_agent_state": {
        const state: AgentState = {
          agent_id: args.agent_id as string,
          status: (args.status as AgentStatus) || "active",
          current_task_id: args.current_task_id as string,
          queue_depth: (args.queue_depth as number) || 0,
          last_heartbeat: new Date().toISOString(),
        };
        await registry.updateState(state);
        result = { success: true, state };
        break;
      }
      case "heartbeat":
        await registry.heartbeat(args.agent_id as string);
        result = { success: true, agent_id: args.agent_id };
        break;
      case "update_agent_status":
        await registry.updateStatus(
          args.agent_id as string,
          args.status as AgentStatus
        );
        result = { success: true, agent_id: args.agent_id, status: args.status };
        break;

      // History/Stats tools
      case "get_message_history":
        result = await coordinator.getMessageHistory(
          args.agent_id_1 as string,
          args.agent_id_2 as string,
          args.limit as number
        );
        break;
      case "get_registry_stats":
        result = await registry.getStats();
        break;
      case "cleanup_stale_agents": {
        const count = await registry.markStaleOffline(
          args.threshold_ms as number
        );
        result = { success: true, marked_offline: count };
        break;
      }

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
  console.error("Agent Coordination MCP Server running on stdio");
  console.error("A2A communication enabled following Microsoft's pattern");
}

main().catch(console.error);
