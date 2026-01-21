/**
 * shadow-odoo-finance Edge Function
 *
 * Pulls project/task data FROM Odoo INTO odoo_seed.shadow_* tables.
 * Enables verification: seed definition vs actual Odoo state.
 *
 * Usage:
 *   curl -X POST \
 *     -H "Authorization: Bearer $SEED_RUN_TOKEN" \
 *     "${SUPABASE_URL}/functions/v1/shadow-odoo-finance"
 *
 * Environment:
 *   - SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY (auto-injected)
 *   - ODOO_URL, ODOO_DB, ODOO_USER, ODOO_PASSWORD
 *   - SEED_RUN_TOKEN (shared secret for auth)
 */

import { serve } from "https://deno.land/std@0.224.0/http/server.ts";
import { createClient, SupabaseClient } from "https://esm.sh/@supabase/supabase-js@2.48.0";

// -----------------------------------------------------------------------------
// Types
// -----------------------------------------------------------------------------

interface OdooConfig {
  url: string;
  db: string;
  user: string;
  password: string;
}

interface OdooProject {
  id: number;
  name: string;
  x_external_ref: string | false;
  company_id: [number, string] | false;
  user_id: [number, string] | false;
  active: boolean;
  privacy_visibility: string;
  allow_task_dependencies: boolean;
  date_start: string | false;
  date: string | false;
  task_count: number;
}

interface OdooTask {
  id: number;
  name: string;
  x_external_ref: string | false;
  project_id: [number, string] | false;
  stage_id: [number, string] | false;
  user_ids: [number, string][];
  planned_hours: number;
  date_deadline: string | false;
  sequence: number;
  parent_id: [number, string] | false;
}

// -----------------------------------------------------------------------------
// Configuration
// -----------------------------------------------------------------------------

const ODOO: OdooConfig = {
  url: Deno.env.get("ODOO_URL") ?? "https://erp.insightpulseai.net",
  db: Deno.env.get("ODOO_DB") ?? "production",
  user: Deno.env.get("ODOO_USER") ?? "",
  password: Deno.env.get("ODOO_PASSWORD") ?? "",
};

const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
const supabaseServiceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const SEED_RUN_TOKEN = Deno.env.get("SEED_RUN_TOKEN") ?? "";

// -----------------------------------------------------------------------------
// Odoo JSON-RPC Client
// -----------------------------------------------------------------------------

let cachedUid: number | null = null;

async function odooLogin(): Promise<number> {
  if (cachedUid) return cachedUid;

  const res = await fetch(`${ODOO.url}/jsonrpc`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      jsonrpc: "2.0",
      method: "call",
      params: {
        service: "common",
        method: "login",
        args: [ODOO.db, ODOO.user, ODOO.password],
      },
      id: 1,
    }),
  });

  const json = await res.json();
  if (json.error || !json.result) {
    throw new Error(`Odoo login failed: ${json.error?.data?.message ?? "Unknown error"}`);
  }

  cachedUid = json.result;
  return cachedUid!;
}

async function odooRpc<T = unknown>(
  model: string,
  method: string,
  args: unknown[],
  kwargs: Record<string, unknown> = {}
): Promise<T> {
  const uid = await odooLogin();

  const res = await fetch(`${ODOO.url}/jsonrpc`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      jsonrpc: "2.0",
      method: "call",
      params: {
        service: "object",
        method: "execute_kw",
        args: [ODOO.db, uid, ODOO.password, model, method, args, kwargs],
      },
      id: Date.now(),
    }),
  });

  const json = await res.json();
  if (json.error) {
    console.error("Odoo RPC error:", json.error);
    throw new Error(json.error.data?.message ?? "Odoo RPC error");
  }

  return json.result as T;
}

// -----------------------------------------------------------------------------
// Shadow Sync Functions
// -----------------------------------------------------------------------------

async function shadowProjects(supabase: SupabaseClient): Promise<number> {
  // Fetch all projects with x_external_ref (seeded projects)
  const projects = await odooRpc<OdooProject[]>(
    "project.project",
    "search_read",
    [[["x_external_ref", "!=", false]]],
    {
      fields: [
        "id", "name", "x_external_ref", "company_id", "user_id",
        "active", "privacy_visibility", "allow_task_dependencies",
        "date_start", "date", "task_count"
      ],
    }
  );

  if (!projects?.length) return 0;

  // Upsert into shadow_projects
  for (const p of projects) {
    const shadowRow = {
      odoo_id: p.id,
      external_ref: p.x_external_ref || null,
      name: p.name,
      company_name: Array.isArray(p.company_id) ? p.company_id[1] : null,
      manager_name: Array.isArray(p.user_id) ? p.user_id[1] : null,
      active: p.active,
      raw: p,
      synced_at: new Date().toISOString(),
    };

    // Upsert by odoo_id
    const { error } = await supabase
      .from("shadow_projects")
      .upsert(shadowRow, { onConflict: "odoo_id" })
      .schema("odoo_seed");

    if (error) {
      console.error(`Failed to shadow project ${p.id}:`, error);
    }
  }

  return projects.length;
}

async function shadowTasks(supabase: SupabaseClient): Promise<number> {
  // Fetch all tasks with x_external_ref (seeded tasks)
  const tasks = await odooRpc<OdooTask[]>(
    "project.task",
    "search_read",
    [[["x_external_ref", "!=", false]]],
    {
      fields: [
        "id", "name", "x_external_ref", "project_id", "stage_id",
        "user_ids", "planned_hours", "date_deadline", "sequence", "parent_id"
      ],
    }
  );

  if (!tasks?.length) return 0;

  // Upsert into shadow_tasks
  for (const t of tasks) {
    const shadowRow = {
      odoo_id: t.id,
      external_ref: t.x_external_ref || null,
      name: t.name,
      project_odoo_id: Array.isArray(t.project_id) ? t.project_id[0] : null,
      stage_name: Array.isArray(t.stage_id) ? t.stage_id[1] : null,
      assignee_name: t.user_ids?.length ? t.user_ids[0][1] : null,
      raw: t,
      synced_at: new Date().toISOString(),
    };

    const { error } = await supabase
      .from("shadow_tasks")
      .upsert(shadowRow, { onConflict: "odoo_id" })
      .schema("odoo_seed");

    if (error) {
      console.error(`Failed to shadow task ${t.id}:`, error);
    }
  }

  return tasks.length;
}

// -----------------------------------------------------------------------------
// Sync Run Management
// -----------------------------------------------------------------------------

async function createSyncRun(
  supabase: SupabaseClient,
  triggeredBy: string
): Promise<string> {
  const { data, error } = await supabase
    .from("sync_runs")
    .insert({
      run_type: "shadow",
      triggered_by: triggeredBy,
      status: "running",
    })
    .select("id")
    .single()
    .schema("odoo_seed");

  if (error) throw error;
  return data.id;
}

async function completeSyncRun(
  supabase: SupabaseClient,
  runId: string,
  status: string,
  projectsProcessed: number,
  tasksProcessed: number,
  errors: unknown[]
): Promise<void> {
  await supabase
    .from("sync_runs")
    .update({
      status,
      completed_at: new Date().toISOString(),
      projects_processed: projectsProcessed,
      tasks_processed: tasksProcessed,
      errors_count: errors.length,
      error_log: errors,
    })
    .eq("id", runId)
    .schema("odoo_seed");
}

// -----------------------------------------------------------------------------
// Verification Queries
// -----------------------------------------------------------------------------

async function runVerification(supabase: SupabaseClient): Promise<{
  missing_in_odoo: number;
  orphan_in_odoo: number;
  name_drift: number;
}> {
  // Count missing projects (seed exists, shadow doesn't)
  const { count: missingCount } = await supabase
    .from("v_missing_in_odoo")
    .select("*", { count: "exact", head: true })
    .schema("odoo_seed");

  // Count orphan projects (shadow exists, seed doesn't)
  const { count: orphanCount } = await supabase
    .from("v_orphan_in_odoo")
    .select("*", { count: "exact", head: true })
    .schema("odoo_seed");

  // Count name drift
  const { count: driftCount } = await supabase
    .from("v_name_drift")
    .select("*", { count: "exact", head: true })
    .schema("odoo_seed");

  return {
    missing_in_odoo: missingCount ?? 0,
    orphan_in_odoo: orphanCount ?? 0,
    name_drift: driftCount ?? 0,
  };
}

// -----------------------------------------------------------------------------
// Main Handler
// -----------------------------------------------------------------------------

serve(async (req) => {
  // Auth check
  const authHeader = req.headers.get("authorization") ?? "";
  if (authHeader !== `Bearer ${SEED_RUN_TOKEN}`) {
    return new Response(JSON.stringify({ ok: false, error: "Unauthorized" }), {
      status: 401,
      headers: { "Content-Type": "application/json" },
    });
  }

  const supabase = createClient(supabaseUrl, supabaseServiceKey, {
    db: { schema: "odoo_seed" },
  });

  let runId: string | null = null;

  try {
    // Create sync run record
    runId = await createSyncRun(supabase, "edge_function");

    // Shadow projects
    const projectCount = await shadowProjects(supabase);

    // Shadow tasks
    const taskCount = await shadowTasks(supabase);

    // Run verification
    const verification = await runVerification(supabase);

    // Complete run
    await completeSyncRun(supabase, runId, "success", projectCount, taskCount, []);

    return new Response(
      JSON.stringify({
        ok: true,
        run_id: runId,
        status: "success",
        projects_shadowed: projectCount,
        tasks_shadowed: taskCount,
        verification,
      }),
      { headers: { "Content-Type": "application/json" } }
    );

  } catch (err) {
    console.error("shadow-odoo-finance error:", err);

    if (runId) {
      await completeSyncRun(supabase, runId, "failed", 0, 0, [{ error: String(err) }]);
    }

    return new Response(
      JSON.stringify({ ok: false, run_id: runId, error: String(err) }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
});
