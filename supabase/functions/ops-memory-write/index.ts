// ops-memory-write
// Writes a memory entry to ops.memory_entries.
// Requires authenticated JWT (no anon access).
// Rate limit: 100 writes/min per user (enforced by Supabase RLS + leaky bucket in DB).
//
// Request body:
//   { scope: 'run' | 'project' | 'org',
//     key: string,
//     value: Record<string, unknown>,
//     run_id?: string,       -- required when scope='run'
//     project?: string,      -- required when scope='project'
//     expires_at?: string    -- ISO 8601; null = never expires
//   }
//
// Failure mode: AGENT.MEMORY_WRITE_FAILED
// Runbook:      docs/runbooks/failures/AGENT.MEMORY_WRITE_FAILED.md

import { createClient } from "jsr:@supabase/supabase-js@2";

const ALLOWED_SCOPES = new Set(["run", "project", "org"]);
const MAX_KEY_LEN    = 200;
const MAX_VALUE_KEYS = 50;

Deno.serve(async (req: Request) => {
  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "Method Not Allowed" }), {
      status: 405,
      headers: { "Content-Type": "application/json" },
    });
  }

  // ── Auth ──────────────────────────────────────────────────────────────────
  const authHeader = req.headers.get("Authorization");
  if (!authHeader?.startsWith("Bearer ")) {
    return new Response(
      JSON.stringify({ error: "AUTH.INVALID_JWT", message: "Authorization header required" }),
      { status: 401, headers: { "Content-Type": "application/json" } }
    );
  }
  const userToken = authHeader.slice(7);

  const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
  const serviceKey  = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

  // Validate user JWT
  const authClient = createClient(supabaseUrl, serviceKey);
  const { data: { user }, error: userErr } = await authClient.auth.getUser(userToken);
  if (userErr || !user) {
    return new Response(
      JSON.stringify({ error: "AUTH.INVALID_JWT", message: "JWT verification failed" }),
      { status: 401, headers: { "Content-Type": "application/json" } }
    );
  }

  // ── Parse body ────────────────────────────────────────────────────────────
  let body: Record<string, unknown>;
  try {
    body = await req.json();
  } catch {
    return new Response(
      JSON.stringify({ error: "AGENT.MEMORY_WRITE_FAILED", message: "Invalid JSON body" }),
      { status: 400, headers: { "Content-Type": "application/json" } }
    );
  }

  const { scope, key, value, run_id, project, expires_at } = body as {
    scope?: string;
    key?: string;
    value?: unknown;
    run_id?: string;
    project?: string;
    expires_at?: string;
  };

  // Validate scope
  if (!scope || !ALLOWED_SCOPES.has(scope)) {
    return new Response(
      JSON.stringify({ error: "AGENT.MEMORY_WRITE_FAILED",
        message: `scope must be one of: ${[...ALLOWED_SCOPES].join(", ")}` }),
      { status: 400, headers: { "Content-Type": "application/json" } }
    );
  }

  // Validate key
  if (!key || typeof key !== "string" || key.length > MAX_KEY_LEN) {
    return new Response(
      JSON.stringify({ error: "AGENT.MEMORY_WRITE_FAILED",
        message: `key must be a non-empty string (max ${MAX_KEY_LEN} chars)` }),
      { status: 400, headers: { "Content-Type": "application/json" } }
    );
  }

  // Validate value
  if (value === null || value === undefined || typeof value !== "object" || Array.isArray(value)) {
    return new Response(
      JSON.stringify({ error: "AGENT.MEMORY_WRITE_FAILED", message: "value must be a JSON object" }),
      { status: 400, headers: { "Content-Type": "application/json" } }
    );
  }
  if (Object.keys(value as object).length > MAX_VALUE_KEYS) {
    return new Response(
      JSON.stringify({ error: "AGENT.MEMORY_WRITE_FAILED",
        message: `value must have ≤ ${MAX_VALUE_KEYS} top-level keys` }),
      { status: 400, headers: { "Content-Type": "application/json" } }
    );
  }

  // Scope-specific required fields
  if (scope === "run" && !run_id) {
    return new Response(
      JSON.stringify({ error: "AGENT.MEMORY_WRITE_FAILED", message: "run_id required for scope=run" }),
      { status: 400, headers: { "Content-Type": "application/json" } }
    );
  }
  if (scope === "project" && !project) {
    return new Response(
      JSON.stringify({ error: "AGENT.MEMORY_WRITE_FAILED", message: "project required for scope=project" }),
      { status: 400, headers: { "Content-Type": "application/json" } }
    );
  }

  // ── Upsert ────────────────────────────────────────────────────────────────
  const supabase = createClient(supabaseUrl, serviceKey);

  const record: Record<string, unknown> = {
    scope,
    key,
    value,
    ...(run_id  ? { run_id }  : {}),
    ...(project ? { project } : {}),
    ...(expires_at ? { expires_at } : {}),
  };

  // Determine conflict target based on scope
  const { error: upsertErr } = await supabase
    .schema("ops")
    .from("memory_entries")
    .upsert(record, {
      onConflict: scope === "run"
        ? "scope,run_id,key"
        : scope === "project"
        ? "scope,project,key"
        : "scope,key",
    });

  if (upsertErr) {
    console.error("ops-memory-write upsert error:", upsertErr.message);
    return new Response(
      JSON.stringify({ error: "AGENT.MEMORY_WRITE_FAILED", message: upsertErr.message }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }

  return new Response(
    JSON.stringify({ ok: true, scope, key }),
    { status: 200, headers: { "Content-Type": "application/json" } }
  );
});
