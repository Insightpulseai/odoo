// supabase/functions/ops-metrics-ingest/index.ts
import { serve } from "https://deno.land/std@0.224.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.49.1";

type Sample = { metric: string; value: number; dims?: Record<string, unknown> };
type IngestReq = {
  project_id: string;
  branch_id?: string;
  ts: string;
  samples: Sample[];
};

function json(status: number, body: unknown) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });
}

serve(async (req) => {
  if (req.method !== "POST") return json(405, { error: "Method not allowed" });

  const token = req.headers.get("x-ops-ingest-token") || "";
  const expected = Deno.env.get("OPS_INGEST_TOKEN") || "";
  if (!expected || token !== expected) return json(401, { error: "Unauthorized" });

  const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
  const SERVICE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
  const supa = createClient(SUPABASE_URL, SERVICE_KEY, { auth: { persistSession: false } });

  let payload: IngestReq;
  try {
    payload = await req.json();
  } catch {
    return json(400, { error: "Invalid JSON" });
  }

  if (!payload.project_id || !payload.ts || !Array.isArray(payload.samples)) {
    return json(400, { error: "project_id, ts, samples required" });
  }

  const ts = new Date(payload.ts);
  if (Number.isNaN(ts.getTime())) return json(400, { error: "Invalid ts" });

  const rows = payload.samples.map((s) => ({
    project_id: payload.project_id,
    branch_id: payload.branch_id ?? null,
    ts: ts.toISOString(),
    metric: s.metric,
    value: s.value,
    dims: s.dims ?? {},
  }));

  const { error } = await supa.from("ops.metrics").insert(rows);
  if (error) return json(500, { error: error.message });

  return json(200, { inserted: rows.length });
});
