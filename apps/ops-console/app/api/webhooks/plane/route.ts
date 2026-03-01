/**
 * POST /api/webhooks/plane
 *
 * Plane webhook receiver — event-driven work items ingest
 * Contract: docs/contracts/C-PLANE-02-workitems-webhooks.md (C-21)
 * SSOT: ssot/sources/plane/work_items.yaml
 *
 * Flow:
 *   1. Verify X-Plane-Signature (HMAC-SHA256 of raw body)
 *   2. Persist delivery to ops.plane_webhook_deliveries (PK = delivery_id)
 *   3. Enqueue to ops.work_queue
 *   4. Return 200 JSON immediately
 */

import { createHmac, timingSafeEqual } from "node:crypto";
import { NextRequest, NextResponse } from "next/server";

const supabaseUrl  = process.env.SUPABASE_URL!;
const serviceKey   = process.env.SUPABASE_SERVICE_ROLE_KEY!;
const webhookSecret = process.env.PLANE_WEBHOOK_SECRET ?? "";

function json(body: unknown, status = 200) {
  return NextResponse.json(body, { status });
}

async function postgrest(
  table: string,
  body: Record<string, unknown>,
  prefer = "resolution=merge-duplicates"
) {
  const res = await fetch(`${supabaseUrl}/rest/v1/${table}`, {
    method: "POST",
    headers: {
      apikey: serviceKey,
      Authorization: `Bearer ${serviceKey}`,
      "Content-Type": "application/json",
      "Accept-Profile": "ops",
      "Content-Profile": "ops",
      Prefer: prefer,
    },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`PostgREST ${table}: ${res.status} ${text}`);
  }
}

function verifySignature(rawBody: string, signature: string): boolean {
  if (!webhookSecret) return false;
  const expected = createHmac("sha256", webhookSecret)
    .update(rawBody)
    .digest("hex");
  try {
    return timingSafeEqual(Buffer.from(expected), Buffer.from(signature));
  } catch {
    return false;
  }
}

export async function POST(req: NextRequest) {
  const rawBody = await req.text();
  const deliveryId = req.headers.get("x-plane-delivery") ?? "";
  const signature  = req.headers.get("x-plane-signature") ?? "";
  const eventType  = req.headers.get("x-plane-event") ?? "unknown";

  // 1. Signature verification
  if (!verifySignature(rawBody, signature)) {
    return json({ ok: false, error: "invalid signature" }, 403);
  }

  let payload: unknown;
  try {
    payload = JSON.parse(rawBody);
  } catch {
    return json({ ok: false, error: "invalid JSON" }, 400);
  }

  if (!deliveryId) {
    return json({ ok: false, error: "missing X-Plane-Delivery header" }, 400);
  }

  // 2. Persist delivery ledger (PK dedupe — duplicate returns 200 idempotent)
  try {
    await postgrest(
      "plane_webhook_deliveries",
      { delivery_id: deliveryId, event_type: eventType, payload },
      "resolution=ignore-duplicates"
    );
  } catch (err) {
    console.error("webhooks/plane: ledger persist failed", err);
    return json({ ok: false, error: String(err) }, 500);
  }

  // 3. Enqueue async processing job
  try {
    await postgrest(
      "work_queue",
      { source: "plane", delivery_id: deliveryId },
      "return=minimal"
    );
  } catch (err) {
    // Non-fatal: ledger row exists; worker can recover via scanning received rows
    console.error("webhooks/plane: enqueue failed", err);
  }

  return json({ ok: true, delivery_id: deliveryId });
}
