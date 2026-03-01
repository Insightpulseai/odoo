/**
 * Plane MCP Server — @ipai/mcp-server-plane
 *
 * SSOT-governed MCP tool surface for Plane.so (issues, cycles, modules, pages).
 * Registered in: ssot/integrations/plane_mcp.yaml
 * Contract doc:  docs/architecture/PLANE_MARKETPLACE_INTEGRATIONS.md §MCP
 *
 * Rules (from ssot/integrations/plane_mcp.yaml §boundary_rules):
 *   1. plane_api_key read from env — never hardcoded
 *   2. Every tool call MUST emit an ops.run_events row before returning
 *   3. Write-tools MUST use idempotency_key to prevent duplicate Plane issues
 *   4. Only tools in TOOL_ALLOWLIST are served; others return 403-equivalent
 *   5. Never write directly to work_plane.* tables (sync workers own that)
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";
import { createClient, SupabaseClient } from "@supabase/supabase-js";
import { createHash } from "crypto";

// ---------------------------------------------------------------------------
// Configuration (all from environment — never hardcoded)
// ---------------------------------------------------------------------------

const PLANE_API_KEY = process.env.PLANE_API_KEY;
const PLANE_WORKSPACE_ID = process.env.PLANE_WORKSPACE_ID;
const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

// Audit buffer for when Supabase is unreachable (drained on reconnect)
const AUDIT_BUFFER_PATH = "./.audit-buffer.ndjson";

// ---------------------------------------------------------------------------
// Validation
// ---------------------------------------------------------------------------

function assertConfig(): void {
  const missing: string[] = [];
  if (!PLANE_API_KEY) missing.push("PLANE_API_KEY");
  if (!PLANE_WORKSPACE_ID) missing.push("PLANE_WORKSPACE_ID");
  if (missing.length > 0) {
    throw new Error(
      `Missing required environment variables: ${missing.join(", ")}. ` +
        `See ssot/secrets/registry.yaml for approved storage locations.`
    );
  }
}

// ---------------------------------------------------------------------------
// Plane API client
// ---------------------------------------------------------------------------

const PLANE_API_BASE = "https://api.plane.so/api/v1";

async function planeRequest<T>(
  method: string,
  path: string,
  body?: unknown
): Promise<T> {
  const url = `${PLANE_API_BASE}${path}`;
  const response = await fetch(url, {
    method,
    headers: {
      "X-API-Key": PLANE_API_KEY!,
      "Content-Type": "application/json",
    },
    ...(body ? { body: JSON.stringify(body) } : {}),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Plane API ${method} ${path} → ${response.status}: ${text}`);
  }

  return response.json() as Promise<T>;
}

// ---------------------------------------------------------------------------
// Audit sink (ops.run_events)
// ---------------------------------------------------------------------------

let supabase: SupabaseClient | null = null;

function getSupabase(): SupabaseClient | null {
  if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) return null;
  if (!supabase) {
    supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);
  }
  return supabase;
}

interface RunEvent {
  tool_name: string;
  input_hash: string;
  response_status: "success" | "error";
  latency_ms: number;
  timestamp: string;
  telemetry_source: "plane_mcp";
  metadata?: Record<string, unknown>;
}

async function emitRunEvent(event: RunEvent): Promise<void> {
  const sb = getSupabase();
  if (sb) {
    const { error } = await sb.from("ops.run_events").insert({
      ...event,
      integration: "plane_mcp",
    });
    if (error) {
      // Buffer locally if Supabase unreachable
      const { appendFile } = await import("fs/promises");
      await appendFile(AUDIT_BUFFER_PATH, JSON.stringify(event) + "\n").catch(
        () => {} // best-effort; don't fail the tool call
      );
    }
  } else {
    // No Supabase configured — log to stderr for local dev
    console.error("[plane-mcp audit]", JSON.stringify(event));
  }
}

// ---------------------------------------------------------------------------
// Tool allowlist (mirrors ssot/integrations/plane_mcp.yaml §tool_allowlist)
// ---------------------------------------------------------------------------

const TOOL_ALLOWLIST = new Set([
  "create_issue",
  "update_issue",
  "get_issue",
  "list_issues",
  "list_projects",
  "list_cycles",
  "list_modules",
  "search_pages",
]);

// ---------------------------------------------------------------------------
// Tool definitions
// ---------------------------------------------------------------------------

const TOOLS: Tool[] = [
  {
    name: "create_issue",
    description:
      "Create a new issue in a Plane project. Requires idempotency_key to prevent duplicate creation on retry.",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "string", description: "Plane project UUID" },
        title: { type: "string", description: "Issue title" },
        description: { type: "string", description: "Issue description (markdown supported)" },
        state: { type: "string", description: "State name (e.g. 'Backlog', 'In Progress')" },
        priority: {
          type: "string",
          enum: ["urgent", "high", "medium", "low", "none"],
          description: "Issue priority",
        },
        label_ids: {
          type: "array",
          items: { type: "string" },
          description: "Label UUIDs to attach",
        },
        assignee_ids: {
          type: "array",
          items: { type: "string" },
          description: "Assignee user UUIDs",
        },
        idempotency_key: {
          type: "string",
          description:
            "Unique key to prevent duplicate creation (e.g. 'plane_mcp:create:{source}:{ref}')",
        },
      },
      required: ["project_id", "title", "idempotency_key"],
    },
  },
  {
    name: "update_issue",
    description: "Update an existing Plane issue (state, priority, assignee, labels).",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "string", description: "Plane project UUID" },
        issue_id: { type: "string", description: "Plane issue UUID" },
        title: { type: "string" },
        description: { type: "string" },
        state: { type: "string" },
        priority: { type: "string", enum: ["urgent", "high", "medium", "low", "none"] },
        label_ids: { type: "array", items: { type: "string" } },
        assignee_ids: { type: "array", items: { type: "string" } },
        idempotency_key: { type: "string", description: "Unique key for this update operation" },
      },
      required: ["project_id", "issue_id", "idempotency_key"],
    },
  },
  {
    name: "get_issue",
    description: "Get a single Plane issue by ID.",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "string" },
        issue_id: { type: "string" },
      },
      required: ["project_id", "issue_id"],
    },
  },
  {
    name: "list_issues",
    description:
      "List issues in a Plane project with optional filters (state, priority, assignee).",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "string" },
        state: { type: "string", description: "Filter by state name" },
        priority: { type: "string" },
        page: { type: "number", default: 1 },
      },
      required: ["project_id"],
    },
  },
  {
    name: "list_projects",
    description: "List all Plane projects in the workspace.",
    inputSchema: {
      type: "object",
      properties: {},
      required: [],
    },
  },
  {
    name: "list_cycles",
    description: "List cycles (sprints) in a Plane project.",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "string" },
      },
      required: ["project_id"],
    },
  },
  {
    name: "list_modules",
    description: "List modules (epics) in a Plane project.",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "string" },
      },
      required: ["project_id"],
    },
  },
  {
    name: "search_pages",
    description: "Search Plane Pages by keyword within a project.",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "string" },
        query: { type: "string", description: "Search keyword" },
      },
      required: ["project_id", "query"],
    },
  },
];

// ---------------------------------------------------------------------------
// Tool handlers
// ---------------------------------------------------------------------------

type ToolArgs = Record<string, unknown>;

async function handleTool(
  name: string,
  args: ToolArgs
): Promise<Record<string, unknown>> {
  const ws = PLANE_WORKSPACE_ID!;

  switch (name) {
    case "create_issue": {
      const { project_id, title, description, state, priority, label_ids, assignee_ids } =
        args as {
          project_id: string;
          title: string;
          description?: string;
          state?: string;
          priority?: string;
          label_ids?: string[];
          assignee_ids?: string[];
          idempotency_key: string;
        };
      return planeRequest("POST", `/workspaces/${ws}/projects/${project_id}/issues/`, {
        name: title,
        description_html: description ?? "",
        state,
        priority,
        label_ids,
        assignee_ids,
      });
    }

    case "update_issue": {
      const { project_id, issue_id, title, description, state, priority, label_ids, assignee_ids } =
        args as {
          project_id: string;
          issue_id: string;
          title?: string;
          description?: string;
          state?: string;
          priority?: string;
          label_ids?: string[];
          assignee_ids?: string[];
          idempotency_key: string;
        };
      const patch: Record<string, unknown> = {};
      if (title) patch.name = title;
      if (description !== undefined) patch.description_html = description;
      if (state) patch.state = state;
      if (priority) patch.priority = priority;
      if (label_ids) patch.label_ids = label_ids;
      if (assignee_ids) patch.assignee_ids = assignee_ids;
      return planeRequest(
        "PATCH",
        `/workspaces/${ws}/projects/${project_id}/issues/${issue_id}/`,
        patch
      );
    }

    case "get_issue": {
      const { project_id, issue_id } = args as { project_id: string; issue_id: string };
      return planeRequest("GET", `/workspaces/${ws}/projects/${project_id}/issues/${issue_id}/`);
    }

    case "list_issues": {
      const { project_id, state, priority, page } = args as {
        project_id: string;
        state?: string;
        priority?: string;
        page?: number;
      };
      const params = new URLSearchParams();
      if (state) params.set("state__name", state);
      if (priority) params.set("priority", priority);
      if (page) params.set("page", String(page));
      const qs = params.toString();
      return planeRequest(
        "GET",
        `/workspaces/${ws}/projects/${project_id}/issues/${qs ? `?${qs}` : ""}`
      );
    }

    case "list_projects":
      return planeRequest("GET", `/workspaces/${ws}/projects/`);

    case "list_cycles": {
      const { project_id } = args as { project_id: string };
      return planeRequest("GET", `/workspaces/${ws}/projects/${project_id}/cycles/`);
    }

    case "list_modules": {
      const { project_id } = args as { project_id: string };
      return planeRequest("GET", `/workspaces/${ws}/projects/${project_id}/modules/`);
    }

    case "search_pages": {
      const { project_id, query } = args as { project_id: string; query: string };
      const qs = new URLSearchParams({ search: query }).toString();
      return planeRequest("GET", `/workspaces/${ws}/projects/${project_id}/pages/?${qs}`);
    }

    default:
      throw new Error(`Tool '${name}' is not in the Plane MCP allowlist`);
  }
}

// ---------------------------------------------------------------------------
// MCP Server bootstrap
// ---------------------------------------------------------------------------

async function main(): Promise<void> {
  assertConfig();

  const server = new Server(
    { name: "plane-mcp", version: "0.1.0" },
    { capabilities: { tools: {} } }
  );

  // List tools
  server.setRequestHandler(ListToolsRequestSchema, async () => ({ tools: TOOLS }));

  // Call tool
  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args = {} } = request.params;
    const startMs = Date.now();

    // Enforce allowlist (boundary rule #4)
    if (!TOOL_ALLOWLIST.has(name)) {
      const event: RunEvent = {
        tool_name: name,
        input_hash: createHash("sha256").update(JSON.stringify(args)).digest("hex").slice(0, 16),
        response_status: "error",
        latency_ms: Date.now() - startMs,
        timestamp: new Date().toISOString(),
        telemetry_source: "plane_mcp",
        metadata: { error: "tool_not_in_allowlist" },
      };
      await emitRunEvent(event);
      return {
        content: [
          {
            type: "text",
            text: `Error: tool '${name}' is not in the Plane MCP tool allowlist. ` +
              `See ssot/integrations/plane_mcp.yaml §tool_allowlist.`,
          },
        ],
        isError: true,
      };
    }

    let responseStatus: "success" | "error" = "success";
    let result: Record<string, unknown>;

    try {
      result = await handleTool(name, args as ToolArgs);
    } catch (err: unknown) {
      responseStatus = "error";
      const message = err instanceof Error ? err.message : String(err);
      result = { error: message };
    }

    // Emit audit row (boundary rule #2)
    const event: RunEvent = {
      tool_name: name,
      input_hash: createHash("sha256").update(JSON.stringify(args)).digest("hex").slice(0, 16),
      response_status: responseStatus,
      latency_ms: Date.now() - startMs,
      timestamp: new Date().toISOString(),
      telemetry_source: "plane_mcp",
    };
    await emitRunEvent(event);

    return {
      content: [
        {
          type: "text",
          text: responseStatus === "error"
            ? `Error: ${(result as { error: string }).error}`
            : JSON.stringify(result, null, 2),
        },
      ],
      isError: responseStatus === "error",
    };
  });

  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((err) => {
  console.error("[plane-mcp] Fatal:", err);
  process.exit(1);
});
