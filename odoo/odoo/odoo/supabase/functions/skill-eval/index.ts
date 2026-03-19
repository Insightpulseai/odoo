// =============================================================================
// SKILL-EVAL - Skill Certification Evaluation Endpoint
// =============================================================================
// Records skill evaluations from CI/BuildOps runs with criteria results
// Supports agents, humans, and hybrid teams as skill holders
// =============================================================================

import { serve } from "https://deno.land/std@0.177.0/http/server.ts";
import { createClient, SupabaseClient } from "https://esm.sh/@supabase/supabase-js@2";

// -----------------------------------------------------------------------------
// Types
// -----------------------------------------------------------------------------

interface CriterionResult {
  code: string;
  status: "passed" | "failed" | "skipped";
  score: number;
  details?: Record<string, unknown>;
}

interface EvalPayload {
  skillSlug: string;
  holderType: "agent" | "human" | "hybrid";
  holderSlug: string;
  displayName: string;
  runId: string;
  evidenceRepoUrl?: string;
  criteriaResults: CriterionResult[];
  telemetryRunId?: string;
  metadata?: Record<string, unknown>;
}

interface EvalResponse {
  evaluationId: string;
  status: "passed" | "failed";
  score: number;
  passedCriteria: number;
  totalCriteria: number;
  requiredFailures: string[];
}

interface SkillDefinition {
  id: string;
  slug: string;
  title: string;
}

interface SkillCriterion {
  id: string;
  code: string;
  required: boolean;
}

interface SkillHolder {
  id: string;
  holder_type: string;
  holder_slug: string;
  display_name: string;
}

// -----------------------------------------------------------------------------
// Helpers
// -----------------------------------------------------------------------------

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

function jsonResponse(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    headers: { ...corsHeaders, "Content-Type": "application/json" },
    status,
  });
}

function errorResponse(message: string, status = 400): Response {
  return jsonResponse({ error: message, ok: false }, status);
}

// -----------------------------------------------------------------------------
// Core Functions
// -----------------------------------------------------------------------------

async function getSkillDefinition(
  supabase: SupabaseClient,
  slug: string
): Promise<SkillDefinition | null> {
  const { data, error } = await supabase
    .from("skill_definitions")
    .select("id, slug, title")
    .eq("slug", slug)
    .single();

  if (error || !data) {
    console.error("Skill lookup error:", error);
    return null;
  }

  return data as SkillDefinition;
}

async function getSkillCriteria(
  supabase: SupabaseClient,
  skillId: string
): Promise<SkillCriterion[]> {
  const { data, error } = await supabase
    .from("skill_criteria")
    .select("id, code, required")
    .eq("skill_id", skillId);

  if (error) {
    console.error("Criteria lookup error:", error);
    return [];
  }

  return (data || []) as SkillCriterion[];
}

async function upsertHolder(
  supabase: SupabaseClient,
  holderType: string,
  holderSlug: string,
  displayName: string,
  meta?: Record<string, unknown>
): Promise<SkillHolder | null> {
  const { data, error } = await supabase
    .from("skill_holders")
    .upsert(
      {
        holder_type: holderType,
        holder_slug: holderSlug,
        display_name: displayName,
        meta: meta || {},
      },
      { onConflict: "holder_type,holder_slug" }
    )
    .select("id, holder_type, holder_slug, display_name")
    .single();

  if (error) {
    console.error("Holder upsert error:", error);
    return null;
  }

  return data as SkillHolder;
}

async function createEvaluation(
  supabase: SupabaseClient,
  params: {
    skillId: string;
    holderId: string;
    status: "passed" | "failed";
    score: number;
    evidenceRepoUrl?: string;
    runId: string;
    telemetryRunId?: string;
  }
): Promise<string | null> {
  const { data, error } = await supabase
    .from("skill_evaluations")
    .insert({
      skill_id: params.skillId,
      holder_id: params.holderId,
      status: params.status,
      score: params.score,
      evidence_repo_url: params.evidenceRepoUrl,
      run_id: params.runId,
      telemetry_run_id: params.telemetryRunId,
    })
    .select("id")
    .single();

  if (error) {
    console.error("Evaluation insert error:", error);
    return null;
  }

  return data.id;
}

async function insertCriterionResults(
  supabase: SupabaseClient,
  evalId: string,
  criteria: SkillCriterion[],
  results: CriterionResult[]
): Promise<void> {
  const criteriaMap = new Map(criteria.map((c) => [c.code, c.id]));

  const rows = results
    .filter((r) => criteriaMap.has(r.code))
    .map((r) => ({
      eval_id: evalId,
      criterion_id: criteriaMap.get(r.code),
      status: r.status,
      score: r.score,
      details: r.details || {},
    }));

  if (rows.length > 0) {
    const { error } = await supabase
      .from("skill_eval_results")
      .insert(rows);

    if (error) {
      console.error("Results insert error:", error);
    }
  }
}

// -----------------------------------------------------------------------------
// API Handlers
// -----------------------------------------------------------------------------

async function handleEvaluate(
  supabase: SupabaseClient,
  body: EvalPayload
): Promise<Response> {
  const {
    skillSlug,
    holderType,
    holderSlug,
    displayName,
    runId,
    evidenceRepoUrl,
    criteriaResults,
    telemetryRunId,
    metadata,
  } = body;

  // Validate required fields
  if (!skillSlug || !holderType || !holderSlug || !displayName || !runId) {
    return errorResponse("Missing required fields: skillSlug, holderType, holderSlug, displayName, runId");
  }

  if (!criteriaResults || !Array.isArray(criteriaResults)) {
    return errorResponse("criteriaResults must be an array");
  }

  // Get skill definition
  const skill = await getSkillDefinition(supabase, skillSlug);
  if (!skill) {
    return errorResponse(`Skill not found: ${skillSlug}`, 404);
  }

  // Get skill criteria
  const criteria = await getSkillCriteria(supabase, skill.id);

  // Upsert holder
  const holder = await upsertHolder(supabase, holderType, holderSlug, displayName, metadata);
  if (!holder) {
    return errorResponse("Failed to create/update holder", 500);
  }

  // Calculate pass/fail status
  const criteriaMap = new Map(criteria.map((c) => [c.code, c]));
  const passedResults = criteriaResults.filter((r) => r.status === "passed");
  const failedRequiredCriteria: string[] = [];

  for (const result of criteriaResults) {
    if (result.status === "failed") {
      const criterion = criteriaMap.get(result.code);
      if (criterion?.required) {
        failedRequiredCriteria.push(result.code);
      }
    }
  }

  const totalScore = criteriaResults.reduce((acc, r) => acc + (r.score || 0), 0);
  const evalStatus = failedRequiredCriteria.length === 0 ? "passed" : "failed";

  // Create evaluation
  const evalId = await createEvaluation(supabase, {
    skillId: skill.id,
    holderId: holder.id,
    status: evalStatus,
    score: totalScore,
    evidenceRepoUrl,
    runId,
    telemetryRunId,
  });

  if (!evalId) {
    return errorResponse("Failed to create evaluation", 500);
  }

  // Insert criterion results
  await insertCriterionResults(supabase, evalId, criteria, criteriaResults);

  const response: EvalResponse = {
    evaluationId: evalId,
    status: evalStatus,
    score: totalScore,
    passedCriteria: passedResults.length,
    totalCriteria: criteriaResults.length,
    requiredFailures: failedRequiredCriteria,
  };

  console.log(`Skill evaluation recorded: ${skillSlug} for ${holderSlug} = ${evalStatus}`);

  return jsonResponse(response, 201);
}

async function handleGetSkill(
  supabase: SupabaseClient,
  slug: string
): Promise<Response> {
  const skill = await getSkillDefinition(supabase, slug);
  if (!skill) {
    return errorResponse(`Skill not found: ${slug}`, 404);
  }

  const criteria = await getSkillCriteria(supabase, skill.id);

  // Get full skill details
  const { data: fullSkill } = await supabase
    .from("skill_definitions")
    .select("*")
    .eq("slug", slug)
    .single();

  // Get full criteria details
  const { data: fullCriteria } = await supabase
    .from("skill_criteria")
    .select("*")
    .eq("skill_id", skill.id)
    .order("required", { ascending: false })
    .order("weight", { ascending: false });

  return jsonResponse({
    skill: fullSkill,
    criteria: fullCriteria || [],
  });
}

async function handleGetHolder(
  supabase: SupabaseClient,
  holderSlug: string
): Promise<Response> {
  // Get holder
  const { data: holder, error: holderError } = await supabase
    .from("skill_holders")
    .select("*")
    .eq("holder_slug", holderSlug)
    .single();

  if (holderError || !holder) {
    return errorResponse(`Holder not found: ${holderSlug}`, 404);
  }

  // Get evaluations with skill info
  const { data: evaluations } = await supabase
    .from("skill_evaluations")
    .select(`
      id,
      status,
      score,
      run_id,
      evidence_repo_url,
      created_at,
      skill:skill_definitions(slug, title, level, category)
    `)
    .eq("holder_id", holder.id)
    .order("created_at", { ascending: false });

  // Group by skill, keeping only latest evaluation
  const skillMap = new Map<string, unknown>();
  for (const evaluation of evaluations || []) {
    const skillSlug = (evaluation.skill as Record<string, unknown>)?.slug;
    if (skillSlug && !skillMap.has(skillSlug as string)) {
      skillMap.set(skillSlug as string, evaluation);
    }
  }

  return jsonResponse({
    holder,
    skills: Array.from(skillMap.values()),
    totalEvaluations: evaluations?.length || 0,
  });
}

async function handleListSkills(supabase: SupabaseClient): Promise<Response> {
  const { data: skills, error } = await supabase
    .from("skill_definitions")
    .select("*")
    .order("category")
    .order("level")
    .order("title");

  if (error) {
    return errorResponse(error.message, 500);
  }

  return jsonResponse({ skills: skills || [] });
}

// -----------------------------------------------------------------------------
// Main Handler
// -----------------------------------------------------------------------------

serve(async (req: Request) => {
  // Handle CORS preflight
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    // Initialize Supabase client with service role for full access
    const supabaseUrl = Deno.env.get("SUPABASE_URL") ?? "";
    const serviceRoleKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "";

    if (!supabaseUrl || !serviceRoleKey) {
      return errorResponse("Missing Supabase configuration", 500);
    }

    // Create client with skills schema
    const supabase = createClient(supabaseUrl, serviceRoleKey, {
      auth: { persistSession: false },
      db: { schema: "skills" },
    });

    const url = new URL(req.url);
    const path = url.pathname.replace(/^\/skill-eval\/?/, "").replace(/^\//, "");

    // Route: POST / or POST /evaluate - Create evaluation
    if (req.method === "POST" && (path === "" || path === "evaluate")) {
      let body: EvalPayload;
      try {
        body = await req.json();
      } catch {
        return errorResponse("Invalid JSON body");
      }
      return handleEvaluate(supabase, body);
    }

    // Route: GET /skills - List all skills
    if (req.method === "GET" && path === "skills") {
      return handleListSkills(supabase);
    }

    // Route: GET /skills/:slug - Get skill details
    if (req.method === "GET" && path.startsWith("skills/")) {
      const slug = path.replace("skills/", "");
      if (!slug) {
        return errorResponse("Missing skill slug");
      }
      return handleGetSkill(supabase, slug);
    }

    // Route: GET /holders/:slug - Get holder details
    if (req.method === "GET" && path.startsWith("holders/")) {
      const slug = path.replace("holders/", "");
      if (!slug) {
        return errorResponse("Missing holder slug");
      }
      return handleGetHolder(supabase, slug);
    }

    // Health check
    if (req.method === "GET" && (path === "" || path === "health")) {
      return jsonResponse({
        ok: true,
        service: "skill-eval",
        version: "1.0.0",
        timestamp: new Date().toISOString(),
      });
    }

    return errorResponse(`Unknown route: ${req.method} /${path}`, 404);
  } catch (error) {
    console.error("skill-eval error:", error);
    return errorResponse(`Internal error: ${error}`, 500);
  }
});
