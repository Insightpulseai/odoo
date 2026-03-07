/**
 * Ops Assistant — ChatGPT MCP Server (SSE transport)
 *
 * Unified MCP server exposing plane.* tools for ChatGPT Apps SDK.
 * Deny-by-default tool policy. All calls audited to ops.run_events.
 *
 * Endpoints:
 *   GET  /health           → { status: "ok", version }
 *   GET  /sse              → SSE stream (MCP protocol)
 *   POST /message?sessionId=X → MCP JSON-RPC messages
 *
 * SSOT:
 *   - ssot/apps/chatgpt_apps/odoo_plane_slack.yaml
 *   - ssot/integrations/chatgpt_app_tool_allowlist.yaml
 *
 * Environment:
 *   - PLANE_API_KEY, PLANE_WORKSPACE_SLUG, PLANE_BASE_URL
 *   - SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
 */

import { serve } from "https://deno.land/std@0.177.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";
import { PlaneClient } from "./lib/plane-api.ts";

// ---------------------------------------------------------------------------
// Config (from env — never hardcoded)
// ---------------------------------------------------------------------------

const VERSION = "1.0.0";

const PLANE_API_KEY = Deno.env.get("PLANE_API_KEY") ?? "";
const PLANE_WORKSPACE_SLUG = Deno.env.get("PLANE_WORKSPACE_SLUG") ?? "";
const PLANE_BASE_URL = Deno.env.get("PLANE_BASE_URL") ?? "https://api.plane.so/api/v1";
const SUPABASE_URL = Deno.env.get("SUPABASE_URL") ?? "";
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "";

// ---------------------------------------------------------------------------
// Plane client singleton
// ---------------------------------------------------------------------------

let planeClient: PlaneClient | null = null;

function getPlaneClient(): PlaneClient {
  if (!planeClient) {
    if (!PLANE_API_KEY || !PLANE_WORKSPACE_SLUG) {
      throw new Error("PLANE_API_KEY and PLANE_WORKSPACE_SLUG are required");
    }
    planeClient = new PlaneClient({
      baseUrl: PLANE_BASE_URL,
      apiKey: PLANE_API_KEY,
      workspaceSlug: PLANE_WORKSPACE_SLUG,
    });
  }
  return planeClient;
}

// ---------------------------------------------------------------------------
// Audit sink (ops.run_events)
// ---------------------------------------------------------------------------

interface AuditEntry {
  tool_name: string;
  input_hash: string;
  response_status: "success" | "error";
  latency_ms: number;
  timestamp: string;
  telemetry_source: string;
  metadata?: Record<string, unknown>;
}

async function emitAudit(entry: AuditEntry): Promise<void> {
  if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
    console.error("[ops-assistant audit]", JSON.stringify(entry));
    return;
  }
  try {
    const sb = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);
    await sb.from("ops_run_events").insert({
      ...entry,
      integration: "chatgpt_ops_assistant",
    });
  } catch (err) {
    console.error("[ops-assistant audit-error]", err);
  }
}

async function hashInput(input: unknown): Promise<string> {
  const data = new TextEncoder().encode(JSON.stringify(input));
  const hash = await crypto.subtle.digest("SHA-256", data);
  return Array.from(new Uint8Array(hash))
    .slice(0, 8)
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

// ---------------------------------------------------------------------------
// Tool allowlist (deny-by-default)
// Mirrors: ssot/integrations/chatgpt_app_tool_allowlist.yaml §plane.*
// ---------------------------------------------------------------------------

const TOOL_ALLOWLIST = new Set([
  "plane.list_work_items",
  "plane.create_work_item",
  "plane.update_work_item",
  "plane.create_page",
  "plane.add_comment",
]);

// ---------------------------------------------------------------------------
// Tool definitions (MCP format)
// ---------------------------------------------------------------------------

const TOOLS = [
  {
    name: "plane.list_work_items",
    description:
      "List or search work items (issues) in a Plane project. Returns up to 100 items.",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "string", description: "Plane project UUID" },
        state: { type: "string", description: "Filter by state name" },
        priority: {
          type: "string",
          enum: ["urgent", "high", "medium", "low", "none"],
        },
        page: { type: "number", description: "Page number (default 1)" },
      },
      required: ["project_id"],
    },
  },
  {
    name: "plane.create_work_item",
    description:
      "Create a new work item (issue) in a Plane project. Returns the created item.",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "string", description: "Plane project UUID" },
        name: { type: "string", description: "Work item title" },
        description_html: {
          type: "string",
          description: "Description (HTML supported)",
        },
        priority: {
          type: "string",
          enum: ["urgent", "high", "medium", "low", "none"],
        },
        state_id: { type: "string", description: "State UUID" },
        assignee_ids: {
          type: "array",
          items: { type: "string" },
          description: "Assignee user UUIDs",
        },
        label_ids: {
          type: "array",
          items: { type: "string" },
          description: "Label UUIDs",
        },
        idempotency_key: {
          type: "string",
          description: "Unique key to prevent duplicate creation",
        },
      },
      required: ["project_id", "name", "idempotency_key"],
    },
  },
  {
    name: "plane.update_work_item",
    description: "Update an existing Plane work item (issue).",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "string", description: "Plane project UUID" },
        issue_id: { type: "string", description: "Work item UUID" },
        name: { type: "string", description: "Updated title" },
        description_html: { type: "string" },
        priority: {
          type: "string",
          enum: ["urgent", "high", "medium", "low", "none"],
        },
        state_id: { type: "string" },
        assignee_ids: { type: "array", items: { type: "string" } },
        label_ids: { type: "array", items: { type: "string" } },
        idempotency_key: { type: "string" },
      },
      required: ["project_id", "issue_id", "idempotency_key"],
    },
  },
  {
    name: "plane.create_page",
    description: "Create a new Plane page (wiki/doc) in a project.",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "string", description: "Plane project UUID" },
        title: { type: "string", description: "Page title" },
        description_html: {
          type: "string",
          description: "Page content (HTML)",
        },
        access: {
          type: "number",
          enum: [0, 1],
          description: "0 = workspace-public, 1 = private",
        },
        idempotency_key: { type: "string" },
      },
      required: ["project_id", "title", "idempotency_key"],
    },
  },
  {
    name: "plane.add_comment",
    description: "Add a comment to an existing Plane work item.",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "string", description: "Plane project UUID" },
        issue_id: { type: "string", description: "Work item UUID" },
        comment_html: {
          type: "string",
          description: "Comment body (HTML supported)",
        },
        idempotency_key: { type: "string" },
      },
      required: ["project_id", "issue_id", "comment_html", "idempotency_key"],
    },
  },
];

// ---------------------------------------------------------------------------
// Tool executor
// ---------------------------------------------------------------------------

type ToolArgs = Record<string, unknown>;

async function executeTool(
  name: string,
  args: ToolArgs,
): Promise<{ result: unknown; isError: boolean }> {
  if (!TOOL_ALLOWLIST.has(name)) {
    return {
      result: `Error: tool '${name}' is not in the allowlist. See ssot/integrations/chatgpt_app_tool_allowlist.yaml.`,
      isError: true,
    };
  }

  const client = getPlaneClient();

  switch (name) {
    case "plane.list_work_items": {
      const { project_id, state, priority, page } = args as {
        project_id: string;
        state?: string;
        priority?: string;
        page?: number;
      };
      const data = await client.listIssues(project_id, { state, priority, page });
      return { result: data, isError: false };
    }

    case "plane.create_work_item": {
      const { project_id, name: itemName, description_html, priority, state_id, assignee_ids, label_ids } =
        args as {
          project_id: string;
          name: string;
          description_html?: string;
          priority?: string;
          state_id?: string;
          assignee_ids?: string[];
          label_ids?: string[];
        };
      const data = await client.createIssue(project_id, {
        name: itemName,
        description_html,
        priority,
        state: state_id,
        assignee_ids,
        label_ids,
      });
      return { result: data, isError: false };
    }

    case "plane.update_work_item": {
      const { project_id, issue_id, name: itemName, description_html, priority, state_id, assignee_ids, label_ids } =
        args as {
          project_id: string;
          issue_id: string;
          name?: string;
          description_html?: string;
          priority?: string;
          state_id?: string;
          assignee_ids?: string[];
          label_ids?: string[];
        };
      const patch: Record<string, unknown> = {};
      if (itemName) patch.name = itemName;
      if (description_html !== undefined) patch.description_html = description_html;
      if (priority) patch.priority = priority;
      if (state_id) patch.state = state_id;
      if (assignee_ids) patch.assignee_ids = assignee_ids;
      if (label_ids) patch.label_ids = label_ids;
      const data = await client.updateIssue(project_id, issue_id, patch);
      return { result: data, isError: false };
    }

    case "plane.create_page": {
      const { project_id, title, description_html, access } = args as {
        project_id: string;
        title: string;
        description_html?: string;
        access?: number;
      };
      const data = await client.createPage(project_id, {
        name: title,
        description_html,
        access,
      });
      return { result: data, isError: false };
    }

    case "plane.add_comment": {
      const { project_id, issue_id, comment_html } = args as {
        project_id: string;
        issue_id: string;
        comment_html: string;
      };
      const data = await client.addComment(project_id, issue_id, comment_html);
      return { result: data, isError: false };
    }

    default:
      return { result: `Unknown tool: ${name}`, isError: true };
  }
}

// ---------------------------------------------------------------------------
// MCP JSON-RPC handler
// ---------------------------------------------------------------------------

interface JsonRpcRequest {
  jsonrpc: "2.0";
  id?: string | number;
  method: string;
  params?: Record<string, unknown>;
}

interface JsonRpcResponse {
  jsonrpc: "2.0";
  id?: string | number;
  result?: unknown;
  error?: { code: number; message: string; data?: unknown };
}

async function handleJsonRpc(req: JsonRpcRequest): Promise<JsonRpcResponse> {
  const { id, method, params } = req;

  switch (method) {
    case "initialize":
      return {
        jsonrpc: "2.0",
        id,
        result: {
          protocolVersion: "2024-11-05",
          capabilities: { tools: {} },
          serverInfo: { name: "ops-assistant", version: VERSION },
        },
      };

    case "tools/list":
      return {
        jsonrpc: "2.0",
        id,
        result: { tools: TOOLS },
      };

    case "tools/call": {
      const toolName = (params?.name as string) ?? "";
      const toolArgs = (params?.arguments as ToolArgs) ?? {};
      const startMs = Date.now();

      let result: unknown;
      let isError = false;

      try {
        const out = await executeTool(toolName, toolArgs);
        result = out.result;
        isError = out.isError;
      } catch (err: unknown) {
        isError = true;
        result =
          err && typeof err === "object" && "message" in err
            ? (err as { message: string }).message
            : String(err);
      }

      // Audit (non-blocking)
      emitAudit({
        tool_name: toolName,
        input_hash: await hashInput(toolArgs),
        response_status: isError ? "error" : "success",
        latency_ms: Date.now() - startMs,
        timestamp: new Date().toISOString(),
        telemetry_source: "chatgpt_ops_assistant",
        metadata: isError ? { error: String(result) } : undefined,
      }).catch(() => {});

      return {
        jsonrpc: "2.0",
        id,
        result: {
          content: [
            {
              type: "text",
              text: isError
                ? `Error: ${result}`
                : JSON.stringify(result, null, 2),
            },
          ],
          isError,
        },
      };
    }

    case "notifications/initialized":
      // Client notification — no response needed
      return { jsonrpc: "2.0", id, result: {} };

    default:
      return {
        jsonrpc: "2.0",
        id,
        error: { code: -32601, message: `Method not found: ${method}` },
      };
  }
}

// ---------------------------------------------------------------------------
// SSE session management
// ---------------------------------------------------------------------------

const sessions = new Map<
  string,
  { controller: ReadableStreamDefaultController; lastActivity: number }
>();

function generateSessionId(): string {
  return crypto.randomUUID();
}

// ---------------------------------------------------------------------------
// HTTP handler
// ---------------------------------------------------------------------------

serve(async (req: Request) => {
  const url = new URL(req.url);
  const path = url.pathname.replace(/\/ops-assistant\/?/, "/").replace(/\/+$/, "") || "/";

  // CORS
  const corsHeaders = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
  };

  if (req.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: corsHeaders });
  }

  // Health check
  if (path === "/health" && req.method === "GET") {
    return new Response(
      JSON.stringify({ status: "ok", version: VERSION, tools: TOOLS.length }),
      { status: 200, headers: { ...corsHeaders, "Content-Type": "application/json" } },
    );
  }

  // SSE endpoint — client connects here for MCP streaming
  if (path === "/sse" && req.method === "GET") {
    const sessionId = generateSessionId();
    const messageEndpoint = `${url.origin}${url.pathname.replace(/\/sse$/, "")}/message?sessionId=${sessionId}`;

    const stream = new ReadableStream({
      start(controller) {
        sessions.set(sessionId, { controller, lastActivity: Date.now() });

        // Send the endpoint event so the MCP client knows where to POST
        const endpointEvent = `event: endpoint\ndata: ${messageEndpoint}\n\n`;
        controller.enqueue(new TextEncoder().encode(endpointEvent));
      },
      cancel() {
        sessions.delete(sessionId);
      },
    });

    return new Response(stream, {
      status: 200,
      headers: {
        ...corsHeaders,
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        Connection: "keep-alive",
      },
    });
  }

  // Message endpoint — client POSTs JSON-RPC here
  if (path === "/message" && req.method === "POST") {
    const sessionId = url.searchParams.get("sessionId");
    if (!sessionId || !sessions.has(sessionId)) {
      return new Response(
        JSON.stringify({ error: "Invalid or expired session" }),
        { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } },
      );
    }

    const session = sessions.get(sessionId)!;
    session.lastActivity = Date.now();

    const body: JsonRpcRequest = await req.json();
    const response = await handleJsonRpc(body);

    // Send response via SSE
    const sseData = `event: message\ndata: ${JSON.stringify(response)}\n\n`;
    try {
      session.controller.enqueue(new TextEncoder().encode(sseData));
    } catch {
      sessions.delete(sessionId);
    }

    return new Response(JSON.stringify({ ok: true }), {
      status: 202,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }

  // Tool discovery (convenience — non-MCP clients)
  if (path === "/tools" && req.method === "GET") {
    return new Response(JSON.stringify({ tools: TOOLS }), {
      status: 200,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }

  return new Response(JSON.stringify({ error: "Not found" }), {
    status: 404,
    headers: { ...corsHeaders, "Content-Type": "application/json" },
  });
});
