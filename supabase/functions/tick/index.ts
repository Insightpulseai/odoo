import { createClient } from "https://esm.sh/@supabase/supabase-js@2.39.0";
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const EXPECTED = Deno.env.get("JOBS_TICK_TOKEN") ?? "";

serve(async (req) => {
  const auth = req.headers.get("authorization") || "";

  // Protect the scheduled ping via a shared token
  if (EXPECTED && auth !== `Bearer ${EXPECTED}`) {
    return new Response("unauthorized", { status: 401 });
  }

  // Wake up the jobs-worker
  const workerUrl = `${SUPABASE_URL.replace(".supabase.co", ".functions.supabase.co")}/functions/v1/jobs-worker`;

  // Fire-and-forget: jobs worker
  fetch(workerUrl, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: "{}",
  }).catch((e) => console.log(`Worker init fail: ${e}`));

  // Fire-and-forget: email notification dispatcher
  const dispatcherUrl = `${SUPABASE_URL.replace(".supabase.co", ".functions.supabase.co")}/functions/v1/email-dispatcher`;
  fetch(dispatcherUrl, {
    method: "POST",
    headers: { "content-type": "application/json" },
  }).catch((e) => console.log(`Email dispatcher fail: ${e}`));

  return new Response("ok", { status: 200 });
});
