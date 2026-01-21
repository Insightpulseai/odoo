/**
 * seed-odoo-finance Edge Function
 *
 * Reads from odoo_seed.projects and odoo_seed.tasks and upserts into Odoo
 * via JSON-RPC. Supabase is source-of-truth, Odoo is execution surface.
 *
 * Usage:
 *   curl -X POST \
 *     -H "Authorization: Bearer $SEED_RUN_TOKEN" \
 *     "${SUPABASE_URL}/functions/v1/seed-odoo-finance"
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

interface SeedProject {
  id: string;
  program_slug: string;
  external_ref: string;
  name: string;
  description: string | null;
  company_name: string;
  manager_email: string | null;
  visibility: string;
  allow_dependencies: boolean;
  date_start: string | null;
  date_end: string | null;
  is_active: boolean;
  sync_enabled: boolean;
}

interface SeedTask {
  id: string;
  project_external_ref: string;
  external_ref: string;
  name: string;
  description: string | null;
  stage_name: string;
  tag_names: string[];
  assignee_email: string | null;
  planned_hours: number;
  deadline: string | null;
  sequence: number;
  is_milestone: boolean;
  depends_on_refs: string[];
  parent_external_ref: string | null;
}

interface SyncResult {
  external_ref: string;
  odoo_id: number;
  action: "created" | "updated";
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
// Odoo Helper Functions
// -----------------------------------------------------------------------------

const companyCache = new Map<string, number>();

async function findCompanyId(companyName: string): Promise<number> {
  if (companyCache.has(companyName)) {
    return companyCache.get(companyName)!;
  }

  const ids = await odooRpc<number[]>("res.company", "search", [[["name", "=", companyName]]], { limit: 1 });
  if (!ids.length) {
    throw new Error(`Company not found: ${companyName}`);
  }

  companyCache.set(companyName, ids[0]);
  return ids[0];
}

const userCache = new Map<string, number | null>();

async function findUserIdByEmail(email: string | null): Promise<number | null> {
  if (!email) return null;

  if (userCache.has(email)) {
    return userCache.get(email)!;
  }

  const ids = await odooRpc<number[]>("res.users", "search", [[["login", "=", email]]], { limit: 1 });
  const userId = ids[0] ?? null;

  userCache.set(email, userId);
  return userId;
}

async function findOrCreateTags(tagNames: string[]): Promise<number[]> {
  if (!tagNames?.length) return [];

  const ids: number[] = [];
  for (const name of tagNames) {
    const found = await odooRpc<number[]>("project.tags", "search", [[["name", "=", name]]], { limit: 1 });
    if (found.length) {
      ids.push(found[0]);
    } else {
      const newId = await odooRpc<number>("project.tags", "create", [{ name }]);
      ids.push(newId);
    }
  }
  return ids;
}

async function findStageId(stageName: string, projectId?: number): Promise<number | null> {
  // Try project-specific stages first
  if (projectId) {
    const projectStages = await odooRpc<number[]>(
      "project.task.type",
      "search",
      [[["name", "=", stageName], ["project_ids", "in", [projectId]]]],
      { limit: 1 }
    );
    if (projectStages.length) return projectStages[0];
  }

  // Fallback to global stages
  const globalStages = await odooRpc<number[]>(
    "project.task.type",
    "search",
    [[["name", "=", stageName]]],
    { limit: 1 }
  );
  return globalStages[0] ?? null;
}

// -----------------------------------------------------------------------------
// Upsert Functions
// -----------------------------------------------------------------------------

async function upsertProject(
  supabase: SupabaseClient,
  p: SeedProject
): Promise<SyncResult> {
  const companyId = await findCompanyId(p.company_name);
  const userId = await findUserIdByEmail(p.manager_email);

  // Find existing project by x_external_ref
  const existingIds = await odooRpc<number[]>(
    "project.project",
    "search",
    [[["x_external_ref", "=", p.external_ref]]],
    { limit: 1 }
  );

  // CE-compatible fields only
  const vals: Record<string, unknown> = {
    name: p.name,
    description: p.description,
    company_id: companyId,
    user_id: userId,
    privacy_visibility: p.visibility,
    allow_task_dependencies: p.allow_dependencies,
    x_external_ref: p.external_ref,
    active: p.is_active,
  };

  if (p.date_start) vals.date_start = p.date_start;
  if (p.date_end) vals.date = p.date_end;

  let projectId: number;
  let action: "created" | "updated";

  if (existingIds.length) {
    projectId = existingIds[0];
    await odooRpc("project.project", "write", [[projectId], vals]);
    action = "updated";
  } else {
    projectId = await odooRpc<number>("project.project", "create", [vals]);
    action = "created";
  }

  // Update seed table with Odoo ID
  await supabase
    .from("projects")
    .update({
      odoo_project_id: projectId,
      last_sync_at: new Date().toISOString(),
      sync_error: null,
    })
    .eq("external_ref", p.external_ref)
    .schema("odoo_seed");

  return { external_ref: p.external_ref, odoo_id: projectId, action };
}

async function upsertTasksForProject(
  supabase: SupabaseClient,
  projectExternalRef: string,
  projectId: number
): Promise<SyncResult[]> {
  // Load tasks for this project
  const { data: tasks, error } = await supabase
    .from("tasks")
    .select("*")
    .eq("project_external_ref", projectExternalRef)
    .eq("is_active", true)
    .order("sequence", { ascending: true })
    .schema("odoo_seed");

  if (error) throw error;
  if (!tasks?.length) return [];

  const results: SyncResult[] = [];
  const refToOdooId: Record<string, number> = {};

  // First pass: create/update tasks without dependencies
  for (const t of tasks as SeedTask[]) {
    const assigneeId = await findUserIdByEmail(t.assignee_email);
    const tagIds = await findOrCreateTags(t.tag_names ?? []);
    const stageId = await findStageId(t.stage_name || "To Do", projectId);

    const existingIds = await odooRpc<number[]>(
      "project.task",
      "search",
      [[["x_external_ref", "=", t.external_ref]]],
      { limit: 1 }
    );

    const vals: Record<string, unknown> = {
      name: t.name,
      description: t.description,
      project_id: projectId,
      user_ids: assigneeId ? [[6, 0, [assigneeId]]] : [[5]], // Odoo 18 uses user_ids (m2m)
      tag_ids: [[6, 0, tagIds]],
      planned_hours: t.planned_hours,
      x_external_ref: t.external_ref,
      sequence: t.sequence,
    };

    if (stageId) vals.stage_id = stageId;
    if (t.deadline) vals.date_deadline = t.deadline;

    // Milestone support (requires ipai_ppm or custom field)
    // vals.is_milestone = t.is_milestone;

    let taskId: number;
    let action: "created" | "updated";

    if (existingIds.length) {
      taskId = existingIds[0];
      await odooRpc("project.task", "write", [[taskId], vals]);
      action = "updated";
    } else {
      taskId = await odooRpc<number>("project.task", "create", [vals]);
      action = "created";
    }

    refToOdooId[t.external_ref] = taskId;

    // Update seed table
    await supabase
      .from("tasks")
      .update({
        odoo_task_id: taskId,
        last_sync_at: new Date().toISOString(),
        sync_error: null,
      })
      .eq("external_ref", t.external_ref)
      .schema("odoo_seed");

    results.push({ external_ref: t.external_ref, odoo_id: taskId, action });
  }

  // Second pass: set dependencies (requires allow_task_dependencies on project)
  for (const t of tasks as SeedTask[]) {
    if (!t.depends_on_refs?.length) continue;

    const taskId = refToOdooId[t.external_ref];
    const depIds = t.depends_on_refs
      .map((ref) => refToOdooId[ref])
      .filter((id): id is number => !!id);

    if (!depIds.length) continue;

    // Odoo 18 uses depend_on_ids for task dependencies
    await odooRpc("project.task", "write", [[taskId], {
      depend_on_ids: [[6, 0, depIds]],
    }]);
  }

  // Third pass: set parent tasks (subtasks)
  for (const t of tasks as SeedTask[]) {
    if (!t.parent_external_ref) continue;

    const taskId = refToOdooId[t.external_ref];
    const parentId = refToOdooId[t.parent_external_ref];

    if (!parentId) continue;

    await odooRpc("project.task", "write", [[taskId], {
      parent_id: parentId,
    }]);
  }

  return results;
}

// -----------------------------------------------------------------------------
// Sync Run Management
// -----------------------------------------------------------------------------

async function createSyncRun(
  supabase: SupabaseClient,
  runType: string,
  triggeredBy: string
): Promise<string> {
  const { data, error } = await supabase
    .from("sync_runs")
    .insert({
      run_type: runType,
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
  errors: unknown[],
  results: unknown
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
      results,
    })
    .eq("id", runId)
    .schema("odoo_seed");
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
    runId = await createSyncRun(supabase, "seed", "edge_function");

    // Load active, sync-enabled projects
    const { data: projects, error: projectsError } = await supabase
      .from("projects")
      .select("*")
      .eq("is_active", true)
      .eq("sync_enabled", true)
      .schema("odoo_seed");

    if (projectsError) throw projectsError;

    if (!projects?.length) {
      await completeSyncRun(supabase, runId, "success", 0, 0, [], { message: "No projects to sync" });
      return new Response(
        JSON.stringify({ ok: true, message: "No seed projects found" }),
        { headers: { "Content-Type": "application/json" } }
      );
    }

    const projectResults: SyncResult[] = [];
    const taskResults: SyncResult[] = [];
    const errors: Array<{ ref: string; error: string }> = [];

    for (const p of projects as SeedProject[]) {
      try {
        // Upsert project
        const projectResult = await upsertProject(supabase, p);
        projectResults.push(projectResult);

        // Upsert tasks
        const taskResultsForProject = await upsertTasksForProject(
          supabase,
          p.external_ref,
          projectResult.odoo_id
        );
        taskResults.push(...taskResultsForProject);

      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : String(err);
        errors.push({ ref: p.external_ref, error: errorMsg });

        // Update project with error
        await supabase
          .from("projects")
          .update({ sync_error: errorMsg })
          .eq("external_ref", p.external_ref)
          .schema("odoo_seed");
      }
    }

    const status = errors.length === 0 ? "success" : errors.length < projects.length ? "partial" : "failed";

    await completeSyncRun(
      supabase,
      runId,
      status,
      projectResults.length,
      taskResults.length,
      errors,
      { projects: projectResults, tasks: taskResults }
    );

    return new Response(
      JSON.stringify({
        ok: errors.length < projects.length,
        run_id: runId,
        status,
        projects_synced: projectResults.length,
        tasks_synced: taskResults.length,
        errors: errors.length,
        results: {
          projects: projectResults,
          tasks: taskResults.slice(0, 10), // Limit for response size
        },
      }),
      { headers: { "Content-Type": "application/json" } }
    );

  } catch (err) {
    console.error("seed-odoo-finance error:", err);

    if (runId) {
      await completeSyncRun(supabase, runId, "failed", 0, 0, [{ error: String(err) }], {});
    }

    return new Response(
      JSON.stringify({ ok: false, run_id: runId, error: String(err) }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
});
