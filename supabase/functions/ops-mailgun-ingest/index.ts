/**
 * ops-mailgun-ingest — Mailgun webhook receiver
 *
 * Contract:  docs/contracts/C-MAIL-01-mail-catcher.md (C-20)
 * SSOT:      ssot/integrations/mailgun.yaml
 * Table:     ops.mail_events
 *
 * Verifies Mailgun HMAC signature, normalizes payload,
 * upserts into ops.mail_events, always returns JSON.
 */

import { createHmac } from "node:crypto";

const supabaseUrl  = Deno.env.get("SUPABASE_URL")!;
const serviceKey   = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

// Secret: Vault key 'mailgun_signing_key' injected at runtime
const signingKey   = Deno.env.get("MAILGUN_SIGNING_KEY") ?? "";

// ── JSON response helper ───────────────────────────────────────────────────────
function json(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

// ── PostgREST upsert helper ────────────────────────────────────────────────────
async function upsert(table: string, row: Record<string, unknown>): Promise<void> {
  const res = await fetch(`${supabaseUrl}/rest/v1/${table}`, {
    method: "POST",
    headers: {
      apikey:          serviceKey,
      Authorization:   `Bearer ${serviceKey}`,
      "Content-Type":  "application/json",
      Prefer:          "resolution=merge-duplicates",
    },
    body: JSON.stringify(row),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`PostgREST upsert ${table}: ${res.status} ${text}`);
  }
}

// ── Mailgun HMAC signature verification ───────────────────────────────────────
// https://documentation.mailgun.com/docs/mailgun/user-manual/tracking-messages/#securing-webhooks
function verifyMailgunSignature(params: {
  timestamp: string;
  token: string;
  signature: string;
}): boolean {
  if (!signingKey) return false;
  const value = params.timestamp + params.token;
  const expected = createHmac("sha256", signingKey)
    .update(value)
    .digest("hex");
  return expected === params.signature;
}

// ── Detect environment from recipient / X-Mailgun-Tag ─────────────────────────
function detectEnv(data: Record<string, string>): "prod" | "stage" | "dev" | "unknown" {
  const tags = (data["message-headers"] ?? "").toLowerCase();
  if (tags.includes("stage") || (data.recipient ?? "").includes("stage")) return "stage";
  if (tags.includes("dev")   || (data.recipient ?? "").includes("dev"))   return "dev";
  if (tags.includes("prod")  || (data.recipient ?? "").includes("prod"))  return "prod";
  return "unknown";
}

// ── Main handler ───────────────────────────────────────────────────────────────
Deno.serve(async (req: Request) => {
  if (req.method !== "POST") {
    return json({ ok: false, error: "method not allowed" }, 405);
  }

  let formData: FormData;
  try {
    formData = await req.formData();
  } catch {
    return json({ ok: false, error: "invalid form data" }, 400);
  }

  const data = Object.fromEntries(formData.entries()) as Record<string, string>;

  // Verify signature
  const { timestamp = "", token = "", signature = "" } = data;
  if (!verifyMailgunSignature({ timestamp, token, signature })) {
    console.error("ops-mailgun-ingest: invalid signature");
    return json({ ok: false, error: "invalid signature" }, 403);
  }

  // Normalize payload
  const messageId = data["Message-Id"] ?? data["message-id"] ?? `mg-${token}`;
  const subject   = data.subject ?? "(no subject)";
  const sender    = data.sender ?? data.from ?? "";
  const recipient = data.recipient ?? data.To ?? "";
  const transport = data["X-Mailgun-Relay"] ?? "smtp.mailgun.org";
  const stamp     = new Date(parseInt(timestamp, 10) * 1000).toISOString();
  const env       = detectEnv(data);

  try {
    await upsert("mail_events", {
      env,
      provider:    "mailgun",
      message_id:  messageId,
      subject,
      sender,
      recipient,
      transport,
      stamp,
      raw:         data,
      received_at: new Date().toISOString(),
    });
  } catch (err) {
    console.error("ops-mailgun-ingest: upsert failed", err);
    return json({ ok: false, error: String(err) }, 500);
  }

  console.log(`ops-mailgun-ingest: captured ${messageId} env=${env}`);
  return json({ ok: true, message_id: messageId, env });
});
