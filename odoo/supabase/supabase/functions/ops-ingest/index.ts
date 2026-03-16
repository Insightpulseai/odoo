/**
 * OPS-INGEST Edge Function
 * HMAC-secured endpoint for ingesting events from Odoo outbox worker.
 * Features: dedupe, DLQ, audit trail, structured logging.
 */
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

function toHex(bytes: ArrayBuffer): string {
  return Array.from(new Uint8Array(bytes))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

async function hmacSha256(secret: string, msg: string): Promise<string> {
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey(
    "raw",
    enc.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );
  const sig = await crypto.subtle.sign("HMAC", key, enc.encode(msg));
  return toHex(sig);
}

async function sha256Hex(msg: string): Promise<string> {
  const data = new TextEncoder().encode(msg);
  return toHex(await crypto.subtle.digest("SHA-256", data));
}

function nowIso(): string {
  return new Date().toISOString();
}

function bad(msg: string, status = 400): Response {
  return new Response(JSON.stringify({ error: msg }), {
    status,
    headers: { "content-type": "application/json" },
  });
}

Deno.serve(async (req) => {
  // CORS preflight
  if (req.method === "OPTIONS") {
    return new Response(null, {
      status: 204,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "content-type, x-ops-signature",
      },
    });
  }

  if (req.method !== "POST") {
    return bad("Method Not Allowed", 405);
  }

  const secret = Deno.env.get("OPS_INGEST_HMAC_SECRET");
  if (!secret) {
    return bad("Missing OPS_INGEST_HMAC_SECRET", 500);
  }

  const sig = req.headers.get("x-ops-signature") || "";
  const raw = await req.text();
  const expected = await hmacSha256(secret, raw);
  if (sig !== expected) {
    return bad("Unauthorized", 401);
  }

  let payload: Record<string, unknown>;
  try {
    payload = JSON.parse(raw);
  } catch {
    return bad("Invalid JSON", 400);
  }

  // Required fields
  const topic = payload.topic as string;
  const action = (payload.action as string) || "ingest";
  const actor = (payload.actor as string) || "worker";
  const eventId = String(payload.event_id || payload.id || "");

  if (!topic || typeof topic !== "string") {
    return bad("Missing topic", 400);
  }
  if (!eventId) {
    return bad("Missing event_id", 400);
  }

  const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
  const serviceRoleKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
  const sb = createClient(supabaseUrl, serviceRoleKey);

  const payloadHash = await sha256Hex(raw);

  // Dedupe: first insert wins; duplicates become no-op
  const { error: dedupeErr } = await sb.from("ops.ingest_dedupe").insert({
    event_id: eventId,
    topic,
    action,
    source: "odoo-worker",
    payload_hash: payloadHash,
  });

  // If insert fails due to duplicate, treat as OK (idempotent)
  if (dedupeErr) {
    const errMsg = String(dedupeErr.message || "").toLowerCase();
    if (!errMsg.includes("duplicate") && !errMsg.includes("unique")) {
      // Actual error - log + dlq
      await sb.from("ops.run_events").insert({
        event_id: eventId,
        level: "error",
        message: "dedupe_insert_failed",
        context: { err: dedupeErr, topic },
      });
      await sb.from("ops.ingest_dlq").insert({
        event_id: eventId,
        reason: "dedupe_insert_failed",
        payload,
      });
      return bad("Dedupe failure", 500);
    }
    // Duplicate - idempotent success
    await sb.from("ops.run_events").insert({
      event_id: eventId,
      level: "info",
      message: "duplicate_event_noop",
      context: { topic },
    });
    return new Response(JSON.stringify({ ok: true, deduped: true }), {
      headers: { "content-type": "application/json" },
    });
  }

  // Audit (append-only)
  const { error: auditErr } = await sb.from("audit.events").insert({
    topic,
    action,
    actor,
    payload,
  });
  if (auditErr) {
    await sb.from("ops.run_events").insert({
      event_id: eventId,
      level: "error",
      message: "audit_insert_failed",
      context: { err: auditErr, topic },
    });
    await sb.from("ops.ingest_dlq").insert({
      event_id: eventId,
      reason: "audit_insert_failed",
      payload,
    });
    return bad("Audit insert failed", 500);
  }

  // Topic routing with validation
  try {
    if (topic === "deployment") {
      const d = payload.deployment as Record<string, unknown>;
      if (!d?.system || !d?.environment || !d?.status) {
        throw new Error("invalid deployment payload");
      }
      const { error } = await sb.from("ops.deployments").insert({
        system: d.system,
        environment: d.environment,
        version: d.version ?? null,
        status: d.status,
        started_at: (d.started_at as string) ?? nowIso(),
        finished_at: d.finished_at ?? null,
        artifact_ref: d.artifact_ref ?? null,
        evidence_ref: d.evidence_ref ?? null,
        metadata: d.metadata ?? {},
      });
      if (error) {
        throw new Error(`deployment_insert_failed:${error.message}`);
      }
    } else if (topic === "incident") {
      const i = payload.incident as Record<string, unknown>;
      if (!i?.system || !i?.environment || !i?.severity || !i?.status || !i?.title) {
        throw new Error("invalid incident payload");
      }
      const { error } = await sb.from("ops.incidents").insert({
        system: i.system,
        environment: i.environment,
        severity: i.severity,
        status: i.status,
        title: i.title,
        started_at: (i.started_at as string) ?? nowIso(),
        mitigated_at: i.mitigated_at ?? null,
        closed_at: i.closed_at ?? null,
        timeline: i.timeline ?? [],
        artifact_ref: i.artifact_ref ?? null,
        metadata: i.metadata ?? {},
      });
      if (error) {
        throw new Error(`incident_insert_failed:${error.message}`);
      }
    } else if (topic === "mirror") {
      // Odoo object snapshot
      const m = payload.mirror as Record<string, unknown>;
      if (m?.odoo_model && m?.odoo_id) {
        await sb.from("mirror.odoo_object_snapshots").insert({
          odoo_model: m.odoo_model,
          odoo_id: m.odoo_id,
          external_key: m.external_key ?? null,
          snapshot: m.snapshot ?? {},
        });
      }
    } else {
      // Unknown topic: keep in audit only, but note it
      await sb.from("ops.run_events").insert({
        event_id: eventId,
        level: "warn",
        message: "unknown_topic_audited_only",
        context: { topic },
      });
    }

    await sb.from("ops.run_events").insert({
      event_id: eventId,
      level: "info",
      message: "ingest_ok",
      context: { topic },
    });

    return new Response(JSON.stringify({ ok: true }), {
      headers: { "content-type": "application/json" },
    });
  } catch (e) {
    await sb.from("ops.run_events").insert({
      event_id: eventId,
      level: "error",
      message: "ingest_failed",
      context: { topic, err: String(e) },
    });
    await sb.from("ops.ingest_dlq").insert({
      event_id: eventId,
      reason: "ingest_failed",
      payload,
    });
    return bad("Ingest failed", 500);
  }
});
