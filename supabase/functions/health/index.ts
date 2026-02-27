import { createClient } from "https://esm.sh/@supabase/supabase-js@2.39.0";
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SERVICE_ROLE = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const sb = createClient(SUPABASE_URL, SERVICE_ROLE);

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type",
};

serve(async (req) => {
  if (req.method === "OPTIONS")
    return new Response("ok", { headers: corsHeaders });

  // Read metrics views directly using service_role
  const { data: integrations } = await sb
    .from("ops.integration_metrics")
    .select("*")
    .order("name");
  const { data: queue } = await sb
    .from("ops.queue_metrics")
    .select("*")
    .order("status");

  // Determine state health
  const dead =
    (queue || []).find((q: any) => q.status === "dead")?.job_count ?? 0;
  const ok = dead === 0;

  return new Response(
    JSON.stringify({ ok, dead_jobs: dead, integrations, queue }),
    {
      status: ok ? 200 : 500,
      headers: { ...corsHeaders, "content-type": "application/json" },
    },
  );
});
