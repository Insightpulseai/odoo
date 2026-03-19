#!/usr/bin/env node
/**
 * Memory MCP Server
 *
 * Repository-scoped verified memory system for AI agents.
 * Based on GitHub Copilot's verified memory approach (Jan 2026).
 *
 * Tools:
 * - store_memory: Store a durable convention with citations
 * - get_recent_memories: Retrieve recent memories for session start
 * - search_memories: Search by subject pattern
 * - verify_memory: Mark memory as verified after citation check
 * - invalidate_memory: Mark memory invalid when citations contradict
 * - supersede_memory: Replace incorrect memory with correction
 * - get_memory_stats: Get telemetry statistics
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";
import { MemoryClient, Citation } from "./memory-client.js";

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_KEY || process.env.SUPABASE_KEY;

if (!SUPABASE_URL || !SUPABASE_KEY) {
  console.error(
    "Error: SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables are required"
  );
  process.exit(1);
}

const client = new MemoryClient(SUPABASE_URL, SUPABASE_KEY);

const tools: Tool[] = [
  // Core memory operations
  {
    name: "store_memory",
    description: `Store a durable convention or invariant with code citations.
Use when discovering patterns that have future impact (API contracts, sync rules, naming conventions, required multi-file edits).
Memory is treated as a hypothesis - agents must verify citations before applying.`,
    inputSchema: {
      type: "object",
      properties: {
        repo: {
          type: "string",
          description: "Repository identifier (owner/name format)",
        },
        subject: {
          type: "string",
          description: "Short topic/category for the memory (e.g., 'API versioning', 'Test conventions')",
        },
        fact: {
          type: "string",
          description: "The durable convention or invariant being stored",
        },
        citations: {
          type: "array",
          items: {
            type: "object",
            properties: {
              path: { type: "string", description: "File path relative to repo root" },
              line_start: { type: "number", description: "Starting line number" },
              line_end: { type: "number", description: "Ending line number" },
              sha: { type: "string", description: "Optional commit SHA for version pinning" },
              snippet_hash: { type: "string", description: "Optional hash for fuzzy matching" },
            },
            required: ["path", "line_start", "line_end"],
          },
          description: "Code locations that support this memory",
        },
        reason: {
          type: "string",
          description: "Why this memory was created (helps future verification)",
        },
        created_by: {
          type: "string",
          description: "Agent or user ID creating this memory",
        },
      },
      required: ["repo", "subject", "fact", "citations"],
    },
  },
  {
    name: "get_recent_memories",
    description: `Retrieve most recent memories for a repository.
Call at session start to load context from previous sessions.
Memories are ordered by recency (most recently refreshed/verified first).
IMPORTANT: You must verify citations before applying any memory.`,
    inputSchema: {
      type: "object",
      properties: {
        repo: {
          type: "string",
          description: "Repository identifier (owner/name format)",
        },
        limit: {
          type: "number",
          description: "Maximum number of memories to return (default 20)",
        },
      },
      required: ["repo"],
    },
  },
  {
    name: "search_memories",
    description: "Search memories by subject pattern within a repository.",
    inputSchema: {
      type: "object",
      properties: {
        repo: {
          type: "string",
          description: "Repository identifier (owner/name format)",
        },
        subject_pattern: {
          type: "string",
          description: "Pattern to search for in subject (case-insensitive)",
        },
        limit: {
          type: "number",
          description: "Maximum number of memories to return (default 20)",
        },
      },
      required: ["repo"],
    },
  },
  {
    name: "verify_memory",
    description: `Mark a memory as verified after successful citation check.
Call this AFTER reading and confirming all cited code locations match the memory.
Updates verification count and refreshes timestamp for recency ranking.`,
    inputSchema: {
      type: "object",
      properties: {
        memory_id: {
          type: "string",
          description: "UUID of the memory to verify",
        },
        agent_id: {
          type: "string",
          description: "Agent ID performing the verification",
        },
      },
      required: ["memory_id"],
    },
  },
  {
    name: "invalidate_memory",
    description: `Mark a memory as invalid when citations contradict the fact.
Use when verification reveals the memory is no longer accurate.
The memory remains in history but won't appear in get_recent_memories.`,
    inputSchema: {
      type: "object",
      properties: {
        memory_id: {
          type: "string",
          description: "UUID of the memory to invalidate",
        },
        agent_id: {
          type: "string",
          description: "Agent ID performing the invalidation",
        },
        reason: {
          type: "string",
          description: "Why the memory is being invalidated",
        },
      },
      required: ["memory_id"],
    },
  },
  {
    name: "supersede_memory",
    description: `Replace an incorrect memory with a corrected version.
Creates a chain linking the new memory to the old one.
Use when a memory is partially correct but needs updating.`,
    inputSchema: {
      type: "object",
      properties: {
        old_memory_id: {
          type: "string",
          description: "UUID of the memory being replaced",
        },
        repo: {
          type: "string",
          description: "Repository identifier",
        },
        subject: {
          type: "string",
          description: "Subject for the corrected memory",
        },
        fact: {
          type: "string",
          description: "Corrected fact",
        },
        citations: {
          type: "array",
          items: {
            type: "object",
            properties: {
              path: { type: "string" },
              line_start: { type: "number" },
              line_end: { type: "number" },
              sha: { type: "string" },
            },
            required: ["path", "line_start", "line_end"],
          },
          description: "Updated citations for the corrected memory",
        },
        reason: {
          type: "string",
          description: "Why this correction was needed",
        },
        created_by: {
          type: "string",
          description: "Agent ID creating the correction",
        },
      },
      required: ["old_memory_id", "repo", "subject", "fact", "citations"],
    },
  },
  // Telemetry and debugging
  {
    name: "get_memory",
    description: "Get a single memory by its ID.",
    inputSchema: {
      type: "object",
      properties: {
        memory_id: {
          type: "string",
          description: "UUID of the memory to retrieve",
        },
      },
      required: ["memory_id"],
    },
  },
  {
    name: "get_memory_stats",
    description: "Get aggregated statistics for agent memory.",
    inputSchema: {
      type: "object",
      properties: {
        repo: {
          type: "string",
          description: "Filter by repository (optional, omit for all repos)",
        },
      },
    },
  },
  {
    name: "get_memory_logs",
    description: "Get memory operation logs for debugging.",
    inputSchema: {
      type: "object",
      properties: {
        repo: {
          type: "string",
          description: "Repository to get logs for",
        },
        limit: {
          type: "number",
          description: "Maximum number of logs to return (default 50)",
        },
        event_type: {
          type: "string",
          enum: ["created", "retrieved", "verified", "rejected", "corrected", "refreshed", "invalidated"],
          description: "Filter by event type",
        },
      },
      required: ["repo"],
    },
  },
];

const server = new Server(
  {
    name: "memory-mcp-server",
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
      case "store_memory":
        result = await client.storeMemory({
          repo: args.repo as string,
          subject: args.subject as string,
          fact: args.fact as string,
          citations: args.citations as Citation[],
          reason: args.reason as string | undefined,
          created_by: args.created_by as string | undefined,
        });
        break;

      case "get_recent_memories":
        result = await client.getRecentMemories(
          args.repo as string,
          args.limit as number | undefined
        );
        break;

      case "search_memories":
        result = await client.searchMemories(
          args.repo as string,
          args.subject_pattern as string | undefined,
          args.limit as number | undefined
        );
        break;

      case "verify_memory":
        result = await client.verifyMemory(
          args.memory_id as string,
          args.agent_id as string | undefined
        );
        break;

      case "invalidate_memory":
        result = await client.invalidateMemory(
          args.memory_id as string,
          args.agent_id as string | undefined,
          args.reason as string | undefined
        );
        break;

      case "supersede_memory":
        result = await client.supersedeMemory(args.old_memory_id as string, {
          repo: args.repo as string,
          subject: args.subject as string,
          fact: args.fact as string,
          citations: args.citations as Citation[],
          reason: args.reason as string | undefined,
          created_by: args.created_by as string | undefined,
        });
        break;

      case "get_memory":
        result = await client.getMemory(args.memory_id as string);
        break;

      case "get_memory_stats":
        result = await client.getStats(args.repo as string | undefined);
        break;

      case "get_memory_logs":
        result = await client.getLogs(
          args.repo as string,
          args.limit as number | undefined,
          args.event_type as string | undefined
        );
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
  console.error("Memory MCP Server running on stdio");
}

main().catch(console.error);
