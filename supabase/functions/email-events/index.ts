import { serve } from "https://deno.land/std@0.224.0/http/server.ts";

const MAILGUN_SIGNING_KEY = Deno.env.get("MAILGUN_SIGNING_KEY") ?? "";

interface MailgunEventPayload {
  "event-data": {
    id: string;
    event: string;
    timestamp: number;
    message: {
      headers: {
        "message-id"?: string;
        subject?: string;
        from?: string;
        to?: string;
      };
    };
    recipient?: string;
    ip?: string;
    "user-agent"?: string;
  };
}

function verifySignature(req: Request): boolean {
  // NOTE: Implement real Mailgun signature verification here if desired.
  // For now we just require the secret to be configured.
  // 
  // Full implementation would verify:
  // 1. Extract timestamp, token, signature from request
  // 2. Compute HMAC-SHA256(timestamp + token, signing_key)
  // 3. Compare computed signature with provided signature
  // 
  // Reference: https://documentation.mailgun.com/en/latest/api-webhooks.html#webhooks
  return MAILGUN_SIGNING_KEY.length > 0;
}

serve(async (req: Request): Promise<Response> => {
  const url = new URL(req.url);
  const endpoint = url.pathname;

  let payload: MailgunEventPayload | null = null;
  let bodyText = "";

  try {
    bodyText = await req.text();
    payload = JSON.parse(bodyText);
  } catch (_err) {
    // fallback: log raw body
  }

  const headersObj: Record<string, string> = {};
  req.headers.forEach((value, key) => {
    headersObj[key] = value;
  });

  const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
  const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
  const supabaseSchema = "email_parity";

  const client = (path: string, method: string, body: unknown) =>
    fetch(`${supabaseUrl}/rest/v1/${path}`, {
      method,
      headers: {
        "apikey": supabaseKey,
        "Authorization": `Bearer ${supabaseKey}`,
        "Content-Type": "application/json",
        "Prefer": "return=representation",
      },
      body: JSON.stringify(body),
    });

  // basic signature gate
  if (!verifySignature(req)) {
    // still log webhook attempt
    await client(`${supabaseSchema}.webhook_logs`, "POST", [{
      endpoint,
      status_code: 401,
      request_headers: headersObj,
      request_body: bodyText ? JSON.parse(bodyText) : {},
      error_message: "Invalid or missing Mailgun signature",
    }]);
    return new Response("unauthorized", { status: 401 });
  }

  if (!payload) {
    await client(`${supabaseSchema}.webhook_logs`, "POST", [{
      endpoint,
      status_code: 400,
      request_headers: headersObj,
      request_body: bodyText ? { raw: bodyText } : {},
      error_message: "Invalid JSON payload",
    }]);
    return new Response("bad request", { status: 400 });
  }

  const eventData = payload["event-data"];
  const eventType = eventData.event;
  const messageId = eventData.message.headers["message-id"] ?? eventData.id;
  const subject = eventData.message.headers.subject ?? null;
  const fromAddress = eventData.message.headers.from ?? "";
  const toRaw = eventData.message.headers.to ?? "";
  const toAddresses = toRaw.split(",").map(s => s.trim()).filter(Boolean);

  const occurredAt = new Date(eventData.timestamp * 1000).toISOString();

  try {
    // upsert message (only if not exists, using ON CONFLICT DO NOTHING pattern)
    await client(`${supabaseSchema}.messages?on_conflict=message_id`, "POST", [{
      message_id: messageId,
      from_address: fromAddress,
      to_addresses: toAddresses,
      subject,
    }]);

    // insert event
    await client(`${supabaseSchema}.events`, "POST", [{
      message_id: messageId,
      event_type: eventType,
      provider: "mailgun",
      provider_event_id: eventData.id,
      event_payload: payload,
      recipient: eventData.recipient ?? null,
      endpoint,
      ip: eventData.ip ?? null,
      user_agent: eventData["user-agent"] ?? null,
      occurred_at: occurredAt,
    }]);

    // log webhook success
    await client(`${supabaseSchema}.webhook_logs`, "POST", [{
      endpoint,
      status_code: 200,
      request_headers: headersObj,
      request_body: payload,
      error_message: null,
    }]);

    return new Response("ok", { status: 200 });
  } catch (err) {
    await client(`${supabaseSchema}.webhook_logs`, "POST", [{
      endpoint,
      status_code: 500,
      request_headers: headersObj,
      request_body: payload ?? (bodyText ? { raw: bodyText } : {}),
      error_message: String(err),
    }]);
    return new Response("internal error", { status: 500 });
  }
});
