/**
 * _template-bridge/index.ts
 * Canonical Edge Function template — copy this when creating a new integration bridge.
 *
 * Replace all occurrences of:
 *   _template-bridge → your-function-name
 *   TEMPLATE_SECRET  → YOUR_SECRET_ENV_VAR
 *
 * Contract: docs/contracts/SUPABASE_EDGE_FUNCTIONS_CONTRACT.md
 */

import { serve } from "https://deno.land/std@0.177.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

// ---------------------------------------------------------------------------
// Strict action allowlist — unknown actions return 404, not 400.
// Prevents probing for undocumented action names.
// ---------------------------------------------------------------------------
const ALLOWED_ACTIONS = new Set(["health", "example_action"]);

// ---------------------------------------------------------------------------
// Structured error types
// ---------------------------------------------------------------------------
type ErrorCode =
  | "UNAUTHORIZED"
  | "BAD_REQUEST"
  | "METHOD_NOT_ALLOWED"
  | "NOT_FOUND"
  | "SERVICE_ERROR"
  | "NOT_CONFIGURED";

function jsonErr(code: ErrorCode, message: string, status: number): Response {
  return new Response(
    JSON.stringify({ ok: false, code, message }),
    { status, headers: { "Content-Type": "application/json" } },
  );
}

function jsonOk(data: unknown, status = 200): Response {
  return new Response(
    JSON.stringify(data),
    { status, headers: { "Content-Type": "application/json" } },
  );
}

// ---------------------------------------------------------------------------
// Bridge auth guard (for internal functions — not user-facing)
// Uses x-bridge-secret header. NOT the Supabase anon key.
// For user-facing functions, set verify_jwt = true in config.toml instead.
// ---------------------------------------------------------------------------
function requireBridgeAuth(req: Request): Response | null {
  const expected = Deno.env.get("TEMPLATE_SECRET"); // Replace with your env var name
  if (!expected) {
    return jsonErr("NOT_CONFIGURED", "TEMPLATE_SECRET not set", 503);
  }
  const got = req.headers.get("x-bridge-secret") ?? "";
  if (!got || got !== expected) {
    return jsonErr("UNAUTHORIZED", "missing or invalid x-bridge-secret", 401);
  }
  return null;
}

// ---------------------------------------------------------------------------
// Audit helper — records all side-effecting operations.
// Logs: event_type, target, status. Never logs secret values.
// ---------------------------------------------------------------------------
async function audit(
  supabase: ReturnType<typeof createClient>,
  eventType: string,
  target: string,
  status: "ok" | "error",
  payload?: unknown,
  errorDetail?: string,
): Promise<void> {
  await supabase.from("ops.platform_events").insert({
    event_type: eventType,
    actor: "_template-bridge", // Replace with your function name
    target,
    payload: payload ?? null,
    status,
    error_detail: errorDetail ?? null,
  }).then(({ error }) => {
    if (error) {
      // Non-fatal — log the audit failure but don't break the response
      console.error(JSON.stringify({ event: "audit_failed", error: error.message }));
    }
  });
}

// ---------------------------------------------------------------------------
// Main handler
// ---------------------------------------------------------------------------
serve(async (req: Request) => {
  // Request ID for idempotency and tracing
  const requestId = req.headers.get("x-request-id") ?? crypto.randomUUID();
  const startMs = Date.now();

  // CORS preflight — include x-bridge-secret in allowed headers
  if (req.method === "OPTIONS") {
    return new Response(null, {
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, x-bridge-secret, x-request-id",
      },
    });
  }

  // Supabase service role client for audit writes (internal only)
  const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
  const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
  const supabase = createClient(supabaseUrl, supabaseKey);

  const url = new URL(req.url);
  const action = url.searchParams.get("action") ?? "";

  // Strict allowlist — unknown actions = 404
  if (!ALLOWED_ACTIONS.has(action)) {
    return jsonErr(
      "NOT_FOUND",
      `Unknown action '${action}'. Allowed: ${[...ALLOWED_ACTIONS].join(", ")}`,
      404,
    );
  }

  try {
    switch (action) {
      // ── Health check — no auth, no side effects ────────────────────────
      case "health": {
        return jsonOk({ ok: true, service: "_template-bridge", request_id: requestId });
      }

      // ── Example action — requires x-bridge-secret, POST only ──────────
      case "example_action": {
        const authErr = requireBridgeAuth(req);
        if (authErr) return authErr;

        if (req.method !== "POST") {
          return jsonErr("METHOD_NOT_ALLOWED", "POST required", 405);
        }

        const payload = await req.json() as { target?: string };
        if (!payload.target) {
          return jsonErr("BAD_REQUEST", "Missing required field: target", 400);
        }

        // --- Your outbound API call here ---
        // Use AbortSignal.timeout(20_000) to respect the 150s wall clock limit
        // const res = await fetch("https://api.example.com/...", {
        //   method: "POST",
        //   signal: AbortSignal.timeout(20_000),
        //   headers: { "Authorization": `Bearer ${Deno.env.get("SOME_TOKEN")}` },
        //   body: JSON.stringify({ ... }),
        // });

        // Structured log — no secret values
        console.log(JSON.stringify({
          request_id: requestId,
          action,
          target: payload.target,
          ms: Date.now() - startMs,
        }));

        await audit(supabase, "example_action", payload.target, "ok", {
          target: payload.target,
        });

        return jsonOk({ ok: true, request_id: requestId });
      }
    }
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    console.error(JSON.stringify({ request_id: requestId, action, error: message }));
    return jsonErr("SERVICE_ERROR", message, 500);
  }

  // Exhaustiveness check
  return jsonErr("SERVICE_ERROR", "Unhandled state", 500);
});
