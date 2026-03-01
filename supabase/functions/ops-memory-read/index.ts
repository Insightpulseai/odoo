// ops-memory-read
// Reads memory entries from ops.memory_entries.
// Requires authenticated JWT (no anon access).
// Supports exact key lookup and prefix scan.
//
// Query params:
//   scope       - 'run' | 'project' | 'org'
//   key         - exact key lookup (optional if prefix provided)
//   prefix      - key prefix scan (optional if key provided)
//   run_id      - required when scope='run'
//   project     - required when scope='project'
//   limit       - max rows for prefix scan (default 20, max 100)
//
// Failure mode: AUTH.INVALID_JWT
// Runbook:      docs/runbooks/failures/AUTH.INVALID_JWT.md

import { createClient } from "jsr:@supabase/supabase-js@2";

const ALLOWED_SCOPES = new Set(["run", "project", "org"]);
const DEFAULT_LIMIT  = 20;
const MAX_LIMIT      = 100;

Deno.serve(async (req: Request) => {
  if (req.method !== "GET") {
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

  const authClient = createClient(supabaseUrl, serviceKey);
  const { data: { user }, error: userErr } = await authClient.auth.getUser(userToken);
  if (userErr || !user) {
    return new Response(
      JSON.stringify({ error: "AUTH.INVALID_JWT", message: "JWT verification failed" }),
      { status: 401, headers: { "Content-Type": "application/json" } }
    );
  }

  // ── Query params ──────────────────────────────────────────────────────────
  const url     = new URL(req.url);
  const scope   = url.searchParams.get("scope")   ?? "";
  const key     = url.searchParams.get("key")     ?? "";
  const prefix  = url.searchParams.get("prefix")  ?? "";
  const runId   = url.searchParams.get("run_id")  ?? "";
  const project = url.searchParams.get("project") ?? "";
  const limitRaw = parseInt(url.searchParams.get("limit") ?? String(DEFAULT_LIMIT), 10);
  const limit   = Math.min(Math.max(1, limitRaw), MAX_LIMIT);

  if (!scope || !ALLOWED_SCOPES.has(scope)) {
    return new Response(
      JSON.stringify({ error: "invalid_params",
        message: `scope must be one of: ${[...ALLOWED_SCOPES].join(", ")}` }),
      { status: 400, headers: { "Content-Type": "application/json" } }
    );
  }
  if (!key && !prefix) {
    return new Response(
      JSON.stringify({ error: "invalid_params", message: "key or prefix required" }),
      { status: 400, headers: { "Content-Type": "application/json" } }
    );
  }
  if (scope === "run" && !runId) {
    return new Response(
      JSON.stringify({ error: "invalid_params", message: "run_id required for scope=run" }),
      { status: 400, headers: { "Content-Type": "application/json" } }
    );
  }
  if (scope === "project" && !project) {
    return new Response(
      JSON.stringify({ error: "invalid_params", message: "project required for scope=project" }),
      { status: 400, headers: { "Content-Type": "application/json" } }
    );
  }

  // ── Query ─────────────────────────────────────────────────────────────────
  const supabase = createClient(supabaseUrl, serviceKey);

  let q = supabase
    .schema("ops")
    .from("memory_entries")
    .select("scope,key,value,run_id,project,created_at,updated_at,expires_at")
    .eq("scope", scope)
    .or(`expires_at.is.null,expires_at.gt.${new Date().toISOString()}`)  // exclude expired
    .limit(limit);

  if (scope === "run" && runId)   q = q.eq("run_id", runId);
  if (scope === "project" && project) q = q.eq("project", project);

  if (key) {
    q = q.eq("key", key);
  } else {
    // prefix scan: key LIKE 'prefix%'
    q = q.like("key", `${prefix}%`);
  }

  const { data, error: qErr } = await q;

  if (qErr) {
    return new Response(
      JSON.stringify({ error: "query_failed", message: qErr.message }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }

  return new Response(
    JSON.stringify({ entries: data ?? [], count: (data ?? []).length }),
    { status: 200, headers: { "Content-Type": "application/json" } }
  );
});
