/**
 * POST /api/webhooks/github
 *
 * GitHub issues webhook receiver — event-driven work items ingest
 * Contract: docs/contracts/C-GH-02-workitems-webhooks.md (C-22)
 * SSOT: ssot/sources/github/work_items.yaml
 *
 * Flow:
 *   1. Verify X-Hub-Signature-256 (sha256= + HMAC-SHA256 of raw body)
 *   2. Persist delivery to ops.github_webhook_deliveries (PK = delivery_id)
 *   3. Enqueue to ops.work_queue
 *   4. Return 200 JSON immediately
 */

import { createHmac, timingSafeEqual } from "node:crypto";
import { NextRequest, NextResponse } from "next/server";

const supabaseUrl   = process.env.SUPABASE_URL!;
const serviceKey    = process.env.SUPABASE_SERVICE_ROLE_KEY!;
const webhookSecret = process.env.GITHUB_WEBHOOK_SECRET ?? "";

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

function verifySignature(rawBody: string, sigHeader: string): boolean {
  if (!webhookSecret) return false;
  const expected = "sha256=" + createHmac("sha256", webhookSecret)
    .update(rawBody)
    .digest("hex");
  try {
    return timingSafeEqual(Buffer.from(expected), Buffer.from(sigHeader));
  } catch {
    return false;
  }
}

export async function POST(req: NextRequest) {
  const rawBody    = await req.text();
  const deliveryId = req.headers.get("x-github-delivery") ?? "";
  const sigHeader  = req.headers.get("x-hub-signature-256") ?? "";
  const eventType  = req.headers.get("x-github-event") ?? "unknown";

  // 1. Signature verification
  if (!verifySignature(rawBody, sigHeader)) {
    return json({ ok: false, error: "invalid signature" }, 403);
  }

  let payload: unknown;
  try {
    payload = JSON.parse(rawBody);
  } catch {
    return json({ ok: false, error: "invalid JSON" }, 400);
  }

  if (!deliveryId) {
    return json({ ok: false, error: "missing X-GitHub-Delivery header" }, 400);
  }

  // 2. Persist delivery ledger (PK dedupe — duplicate returns 200 idempotent)
  try {
    await postgrest(
      "github_webhook_deliveries",
      { delivery_id: deliveryId, event_type: eventType, payload },
      "resolution=ignore-duplicates"
    );
  } catch (err) {
    console.error("webhooks/github: ledger persist failed", err);
    return json({ ok: false, error: String(err) }, 500);
  }

  // 3. Enqueue async processing job
  try {
    await postgrest(
      "work_queue",
      { source: "github", delivery_id: deliveryId },
      "return=minimal"
    );
  } catch (err) {
    console.error("webhooks/github: enqueue failed", err);
  }

  return json({ ok: true, delivery_id: deliveryId });
}
