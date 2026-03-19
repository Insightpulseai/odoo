/**
 * Supabase Edge Function: bugbot-control-plane
 *
 * Provides runtime secret access for BugBot, Vercel Bot, and other control plane consumers.
 * All secrets are stored encrypted in Supabase Vault and retrieved via the control_plane schema.
 *
 * Usage:
 *   POST /functions/v1/bugbot-control-plane
 *   Body: { "secretName": "DIGITALOCEAN_API_TOKEN", "mode": "raw" | "proxy" | "exchange" }
 *
 * Modes:
 *   - raw: Returns the decrypted secret value directly
 *   - proxy: Proxies an API call using the secret as Bearer token
 *   - exchange: Returns the secret (future: exchange for short-lived token)
 */

import { createClient } from "npm:@supabase/supabase-js@2.48.0";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

// Allowed proxy target hosts
const ALLOWED_PROXY_HOSTS = [
  "api.digitalocean.com",
  "api.vercel.com",
  "api.openai.com",
  "api.anthropic.com",
  "api.github.com",
];

type SecretName =
  | "DIGITALOCEAN_API_TOKEN"
  | "VERCEL_API_TOKEN"
  | "OPENAI_API_KEY"
  | "GITHUB_TOKEN"
  | "SUPABASE_SERVICE_ROLE_KEY"
  | "ANTHROPIC_API_KEY"
  | "N8N_API_KEY"
  | "SENTRY_DSN"
  | "DO_SPACES_ACCESS_KEY"
  | "DO_SPACES_SECRET_KEY";

type Mode = "raw" | "proxy" | "exchange";

interface RequestPayload {
  secretName: SecretName;
  mode?: Mode;
  accessor?: string;
  // Proxy mode options
  proxyTarget?: string;
  proxyMethod?: "GET" | "POST" | "PUT" | "DELETE" | "PATCH";
  proxyBody?: Record<string, unknown>;
  proxyHeaders?: Record<string, string>;
}

interface SuccessResponse {
  ok: true;
  secretName: string;
  value?: string;
  proxiedResponse?: unknown;
  proxiedStatus?: number;
}

interface ErrorResponse {
  ok: false;
  error: string;
}

type Response = SuccessResponse | ErrorResponse;

Deno.serve(async (req: Request): Promise<globalThis.Response> => {
  // Handle CORS preflight
  if (req.method === "OPTIONS") {
    return new globalThis.Response(null, {
      status: 204,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization, x-bugbot-auth, x-bot-id",
      },
    });
  }

  if (req.method !== "POST") {
    return jsonResponse({ ok: false, error: "Method not allowed" }, 405);
  }

  try {
    const payload: RequestPayload = await req.json();

    // Validate required fields
    if (!payload.secretName) {
      return jsonResponse({ ok: false, error: "secretName is required" }, 400);
    }

    // Get accessor from header or payload
    const accessor = req.headers.get("x-bot-id") || payload.accessor || "anonymous";

    // TODO: Add authentication check here
    // const authHeader = req.headers.get("x-bugbot-auth");
    // if (!validateAuth(authHeader)) {
    //   return jsonResponse({ ok: false, error: "Unauthorized" }, 401);
    // }

    // Create Supabase client with service role
    const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);

    // Call the control_plane.get_secret_logged function
    const { data: secretValue, error: secretError } = await supabase.rpc(
      "control_plane_get_secret_logged",
      {
        p_name: payload.secretName,
        p_accessor: accessor,
        p_access_type: payload.mode || "read",
      }
    );

    if (secretError) {
      console.error("Secret fetch error:", secretError);
      return jsonResponse({ ok: false, error: "Failed to retrieve secret" }, 500);
    }

    if (!secretValue) {
      return jsonResponse({ ok: false, error: `Secret ${payload.secretName} not found` }, 404);
    }

    const decryptedSecret = secretValue as string;
    const mode = payload.mode || "raw";

    // Handle different modes
    switch (mode) {
      case "raw":
        // Return the raw secret value
        return jsonResponse({
          ok: true,
          secretName: payload.secretName,
          value: decryptedSecret,
        });

      case "proxy": {
        // Proxy an API call using the secret
        if (!payload.proxyTarget) {
          return jsonResponse({ ok: false, error: "proxyTarget is required for proxy mode" }, 400);
        }

        // Validate the proxy target host
        let targetUrl: URL;
        try {
          targetUrl = new URL(payload.proxyTarget);
        } catch {
          return jsonResponse({ ok: false, error: "Invalid proxyTarget URL" }, 400);
        }

        if (!ALLOWED_PROXY_HOSTS.some((host) => targetUrl.host.includes(host))) {
          return jsonResponse(
            { ok: false, error: `Proxy target host not allowed: ${targetUrl.host}` },
            400
          );
        }

        // Build headers
        const headers: Record<string, string> = {
          Authorization: `Bearer ${decryptedSecret}`,
          "Content-Type": "application/json",
          ...payload.proxyHeaders,
        };

        // Make the proxied request
        const proxyResp = await fetch(payload.proxyTarget, {
          method: payload.proxyMethod || "GET",
          headers,
          body: payload.proxyBody ? JSON.stringify(payload.proxyBody) : undefined,
        });

        let proxiedData: unknown;
        const contentType = proxyResp.headers.get("content-type") || "";

        if (contentType.includes("application/json")) {
          proxiedData = await proxyResp.json();
        } else {
          proxiedData = await proxyResp.text();
        }

        return jsonResponse({
          ok: proxyResp.ok,
          secretName: payload.secretName,
          proxiedResponse: proxiedData,
          proxiedStatus: proxyResp.status,
        });
      }

      case "exchange":
        // For now, just return the secret
        // Future: implement token exchange logic for short-lived tokens
        return jsonResponse({
          ok: true,
          secretName: payload.secretName,
          value: decryptedSecret,
        });

      default:
        return jsonResponse({ ok: false, error: `Unknown mode: ${mode}` }, 400);
    }
  } catch (err) {
    console.error("bugbot-control-plane error:", err);
    const errorMessage = err instanceof Error ? err.message : "Unknown error";
    return jsonResponse({ ok: false, error: errorMessage }, 500);
  }
});

function jsonResponse(data: Response, status = 200): globalThis.Response {
  return new globalThis.Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
    },
  });
}
