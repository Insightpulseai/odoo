// supabase/functions/ops-trigger-build/index.ts
import { serve } from "https://deno.land/std@0.224.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.49.1";

type TriggerReq = {
  project_id: string;
  branch_id: string;
  trigger?: "manual" | "commit" | "schedule";
  commit_sha?: string;
  params?: {
    target?: "build" | "deploy" | "promote";
    env?: "dev" | "stage" | "prod";
    force?: boolean;
  };
};

function json(status: number, body: unknown) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });
}

serve(async (req) => {
  if (req.method !== "POST") return json(405, { error: "Method not allowed" });

  const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
  const SERVICE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
  if (!SUPABASE_URL || !SERVICE_KEY) return json(500, { error: "Missing server env" });

  const authHeader = req.headers.get("authorization") || "";
  if (!authHeader.startsWith("Bearer ")) return json(401, { error: "Missing bearer token" });
  const jwt = authHeader.slice("Bearer ".length);

  // Client that enforces RLS via user JWT for permission checks
  const supaUser = createClient(SUPABASE_URL, Deno.env.get("SUPABASE_ANON_KEY") ?? "", {
    global: { headers: { authorization: `Bearer ${jwt}` } },
    auth: { persistSession: false },
  });

  // Service client for inserts (bypasses RLS)
  const supaSvc = createClient(SUPABASE_URL, SERVICE_KEY, {
    auth: { persistSession: false },
  });

  let payload: TriggerReq;
  try {
    payload = await req.json();
  } catch {
    return json(400, { error: "Invalid JSON" });
  }

  const { project_id, branch_id } = payload;
  if (!project_id || !branch_id) return json(400, { error: "project_id and branch_id required" });

  // Permission: Check user has access to project
  const { data: project, error: projErr } = await supaUser
    .from("ops.projects")
    .select("id, org_id")
    .eq("id", project_id)
    .single();

  if (projErr || !project) return json(403, { error: "Forbidden (project not visible)" });

  // Create build
  const trigger = payload.trigger ?? "manual";
  const commit_sha = payload.commit_sha ?? null;

  const { data: buildRow, error: buildErr } = await supaSvc
    .from("ops.builds")
    .insert({
      project_id,
      branch_id,
      status: "queued",
      trigger,
      commit_sha,
    })
    .select("id, status, created_at")
    .single();

  if (buildErr) return json(500, { error: buildErr.message });

  // enqueue
  const { data: queueId, error: qErr } = await supaSvc.rpc("ops.enqueue_build", { p_build_id: buildRow.id });
  if (qErr) return json(500, { error: qErr.message });

  // append event
  await supaSvc.rpc("ops.append_build_event", {
    p_build_id: buildRow.id,
    p_phase: "system",
    p_level: "info",
    p_message: "Build queued by ops-trigger-build",
    p_meta: { params: payload.params ?? {}, trigger },
  });

  return json(200, {
    build_id: buildRow.id,
    status: buildRow.status,
    queue_key: `ops.builds:${buildRow.id}`,
    queue_id: queueId,
    created_at: buildRow.created_at,
  });
});
