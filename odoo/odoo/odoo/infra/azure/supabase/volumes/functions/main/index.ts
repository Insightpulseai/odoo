// =============================================================================
// Supabase Edge Functions — Main Service Router
// =============================================================================
// This is the entrypoint for the Edge Runtime. It routes requests to individual
// functions deployed in sibling directories under /home/deno/functions/.
//
// Copy project edge functions from supabase/functions/ to volumes/functions/
// during deployment.
// =============================================================================

import { serve } from "https://deno.land/std@0.177.0/http/server.ts";

serve(async (req: Request) => {
  const url = new URL(req.url);

  if (url.pathname === "/functions/v1/_internal/health") {
    return new Response(JSON.stringify({ status: "ok" }), {
      headers: { "Content-Type": "application/json" },
      status: 200,
    });
  }

  return new Response(
    JSON.stringify({ error: "Function not found", path: url.pathname }),
    { headers: { "Content-Type": "application/json" }, status: 404 }
  );
});
