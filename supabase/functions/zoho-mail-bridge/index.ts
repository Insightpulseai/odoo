/**
 * zoho-mail-bridge/index.ts
 * Supabase Edge Function — Zoho Mail OAuth2 token minting + send API
 *
 * Routes (via ?action= query param):
 *   mint_token  — Refresh OAuth2 access token using refresh_token grant
 *   send_email  — Send email via Zoho Mail API (uses minted token)
 *
 * Required Env Vars (from Supabase Vault / Edge Function secrets):
 *   ZOHO_CLIENT_ID
 *   ZOHO_CLIENT_SECRET
 *   ZOHO_REFRESH_TOKEN
 *   ZOHO_ACCOUNT_ID       (Zoho Mail account ID — obtained from /api/accounts)
 *
 * All operations are audited to ops.platform_events via the service role client.
 */

import { serve } from "https://deno.land/std@0.177.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface SendEmailPayload {
  from: string;
  to: string | string[];
  subject: string;
  htmlBody?: string;
  textBody?: string;
  replyTo?: string;
}

interface TokenCache {
  access_token: string;
  expires_at: number; // epoch ms
}

// ---------------------------------------------------------------------------
// In-memory token cache (valid for Edge Function instance lifetime)
// ---------------------------------------------------------------------------

let tokenCache: TokenCache | null = null;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function jsonError(message: string, status = 400): Response {
  return new Response(
    JSON.stringify({ error: message }),
    { status, headers: { "Content-Type": "application/json" } },
  );
}

function jsonOk(data: unknown, status = 200): Response {
  return new Response(
    JSON.stringify(data),
    { status, headers: { "Content-Type": "application/json" } },
  );
}

async function audit(
  supabase: ReturnType<typeof createClient>,
  eventType: string,
  target: string,
  status: "ok" | "error",
  payload?: unknown,
  errorDetail?: string,
) {
  await supabase.from("ops.platform_events").insert({
    event_type: eventType,
    actor: "zoho-mail-bridge",
    target,
    payload: payload ?? null,
    status,
    error_detail: errorDetail ?? null,
  });
}

// ---------------------------------------------------------------------------
// Token minting
// ---------------------------------------------------------------------------

async function mintToken(supabase: ReturnType<typeof createClient>): Promise<string> {
  // Return cached token if still valid (60s buffer)
  if (tokenCache && tokenCache.expires_at > Date.now() + 60_000) {
    return tokenCache.access_token;
  }

  const clientId = Deno.env.get("ZOHO_CLIENT_ID");
  const clientSecret = Deno.env.get("ZOHO_CLIENT_SECRET");
  const refreshToken = Deno.env.get("ZOHO_REFRESH_TOKEN");

  if (!clientId || !clientSecret || !refreshToken) {
    throw new Error("Missing Zoho OAuth2 credentials in environment");
  }

  const params = new URLSearchParams({
    grant_type: "refresh_token",
    client_id: clientId,
    client_secret: clientSecret,
    refresh_token: refreshToken,
  });

  const res = await fetch("https://accounts.zoho.com/oauth/v2/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: params.toString(),
  });

  if (!res.ok) {
    const err = await res.text();
    await audit(supabase, "token_mint", "zoho_oauth", "error", null, err);
    throw new Error(`Token mint failed: ${res.status} ${err}`);
  }

  const data = await res.json() as { access_token: string; expires_in: number; error?: string };
  if (data.error) {
    await audit(supabase, "token_mint", "zoho_oauth", "error", null, data.error);
    throw new Error(`Token mint error: ${data.error}`);
  }

  tokenCache = {
    access_token: data.access_token,
    expires_at: Date.now() + data.expires_in * 1000,
  };

  await audit(supabase, "token_mint", "zoho_oauth", "ok", { expires_in: data.expires_in });
  return tokenCache.access_token;
}

// ---------------------------------------------------------------------------
// Send email
// ---------------------------------------------------------------------------

async function sendEmail(
  supabase: ReturnType<typeof createClient>,
  payload: SendEmailPayload,
): Promise<void> {
  const accountId = Deno.env.get("ZOHO_ACCOUNT_ID");
  if (!accountId) throw new Error("ZOHO_ACCOUNT_ID env var required");

  const accessToken = await mintToken(supabase);
  const toList = Array.isArray(payload.to) ? payload.to : [payload.to];

  const body = {
    fromAddress: payload.from,
    toAddress: toList.join(","),
    subject: payload.subject,
    content: payload.htmlBody ?? payload.textBody ?? "",
    mailFormat: payload.htmlBody ? "html" : "plaintext",
    ...(payload.replyTo ? { replyTo: payload.replyTo } : {}),
  };

  const res = await fetch(
    `https://mail.zoho.com/api/accounts/${accountId}/messages`,
    {
      method: "POST",
      headers: {
        "Authorization": `Zoho-oauthtoken ${accessToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    },
  );

  const responseText = await res.text();

  if (!res.ok) {
    await audit(
      supabase,
      "email_send",
      toList.join(","),
      "error",
      { subject: payload.subject },
      `${res.status}: ${responseText}`,
    );
    throw new Error(`Send failed: ${res.status} ${responseText}`);
  }

  await audit(supabase, "email_send", toList.join(","), "ok", {
    subject: payload.subject,
    from: payload.from,
    recipients: toList.length,
  });
}

// ---------------------------------------------------------------------------
// Main handler
// ---------------------------------------------------------------------------

serve(async (req: Request) => {
  // CORS preflight
  if (req.method === "OPTIONS") {
    return new Response(null, {
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Authorization, Content-Type",
      },
    });
  }

  // Supabase service role client for audit writes
  const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
  const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
  const supabase = createClient(supabaseUrl, supabaseKey);

  const url = new URL(req.url);
  const action = url.searchParams.get("action");

  try {
    switch (action) {
      case "mint_token": {
        const token = await mintToken(supabase);
        return jsonOk({ ok: true, expires_at: tokenCache?.expires_at });
      }

      case "send_email": {
        if (req.method !== "POST") return jsonError("POST required", 405);
        const payload = await req.json() as SendEmailPayload;
        if (!payload.to || !payload.subject) {
          return jsonError("Missing required fields: to, subject");
        }
        await sendEmail(supabase, payload);
        return jsonOk({ ok: true });
      }

      default:
        return jsonError("Unknown action. Use ?action=mint_token or ?action=send_email");
    }
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return jsonError(message, 500);
  }
});
