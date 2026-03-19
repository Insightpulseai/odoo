// supabase/functions/m365-copilot-broker/index.ts
// Deno Edge Function — M365 Copilot Declarative Agent Broker
//
// Routes:
//   GET  /m365-copilot-broker/manifest    → allowlisted action IDs JSON
//   GET  /m365-copilot-broker/handshake   → actions + capabilities JSON
//   POST /m365-copilot-broker/query       → knowledge retrieval (JWT required)
//   POST /m365-copilot-broker/action      → enqueue advisor action intent (JWT required)
//
// ssot_ref: ssot/integrations/m365_copilot.yaml
// ssot_ref: ssot/m365/agents/insightpulseai_ops_advisor/actions.yaml
// ssot_ref: ssot/m365/agents/insightpulseai_ops_advisor/capabilities.yaml

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

// ---------------------------------------------------------------------------
// Env
// ---------------------------------------------------------------------------
const SUPABASE_URL = Deno.env.get("SUPABASE_URL");
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
const M365_COPILOT_TENANT_ID = Deno.env.get("M365_COPILOT_TENANT_ID");
const M365_COPILOT_CLIENT_ID = Deno.env.get("M365_COPILOT_CLIENT_ID");

const REQUIRED_KEYS = [
  "SUPABASE_URL",
  "SUPABASE_SERVICE_ROLE_KEY",
  "M365_COPILOT_TENANT_ID",
  "M365_COPILOT_CLIENT_ID",
];

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------
const ALLOWED_ACTION_IDS = [
  "query_advisor_findings",
  "query_ops_runs",
  "trigger_advisor_scan",
  "acknowledge_finding",
] as const;

type AllowedActionId = (typeof ALLOWED_ACTION_IDS)[number];

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
};

// ---------------------------------------------------------------------------
// SSOT payloads — inline from ssot/m365/agents/insightpulseai_ops_advisor/
// ---------------------------------------------------------------------------
const ACTIONS_ALLOWLIST = [
  {
    id: "query_advisor_findings",
    description: "Query open advisor findings",
  },
  {
    id: "query_ops_runs",
    description: "Query ops run history",
  },
  {
    id: "trigger_advisor_scan",
    description: "Trigger a new advisor scan",
  },
  {
    id: "acknowledge_finding",
    description: "Acknowledge an advisor finding",
  },
];

const CAPABILITIES = [
  {
    id: "advisor_findings_query",
    connector_type: "federated",
    data_residency: "sg1",
  },
  {
    id: "agent_run_audit",
    connector_type: "federated",
    data_residency: "sg1",
  },
  {
    id: "advisor_scan_trigger",
    confirmation_required: true,
    data_residency: "sg1",
  },
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function sbHeaders(serviceKey: string): Record<string, string> {
  return {
    apikey: serviceKey,
    Authorization: `Bearer ${serviceKey}`,
    "Content-Type": "application/json",
    Prefer: "return=representation",
  };
}

function jsonResponse(
  body: unknown,
  status = 200,
  extra: Record<string, string> = {}
): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      ...CORS_HEADERS,
      "Content-Type": "application/json",
      ...extra,
    },
  });
}

function missingEnvResponse(missingKeys: string[]): Response {
  return jsonResponse(
    {
      error: "KEY_MISSING",
      keys: missingKeys,
      ssot_ref: "ssot/integrations/m365_copilot.yaml",
    },
    503
  );
}

// ---------------------------------------------------------------------------
// JWT validation
//
// Validates iss, aud, and exp from the JWT payload.
// NOTE: Cryptographic signature verification (JWKS) is deferred to a future
// iteration — this validates structural claims only. Track as tech-debt.
// ---------------------------------------------------------------------------
interface JwtPayload {
  iss?: string;
  aud?: string | string[];
  exp?: number;
  [key: string]: unknown;
}

function base64urlDecode(input: string): string {
  // Normalise base64url → base64
  const base64 = input
    .replace(/-/g, "+")
    .replace(/_/g, "/")
    .padEnd(input.length + ((4 - (input.length % 4)) % 4), "=");
  return atob(base64);
}

function decodeJwtPayload(token: string): JwtPayload | null {
  const parts = token.split(".");
  if (parts.length !== 3) return null;
  try {
    const raw = base64urlDecode(parts[1]);
    return JSON.parse(raw) as JwtPayload;
  } catch {
    return null;
  }
}

interface JwtValidationResult {
  valid: boolean;
  detail?: string;
}

function validateJwt(
  authHeader: string | null,
  tenantId: string,
  clientId: string
): JwtValidationResult {
  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    return { valid: false, detail: "missing_bearer_token" };
  }

  const token = authHeader.slice(7).trim();
  const payload = decodeJwtPayload(token);

  if (!payload) {
    return { valid: false, detail: "malformed_jwt" };
  }

  // Check expiry
  const now = Math.floor(Date.now() / 1000);
  if (payload.exp !== undefined && payload.exp < now) {
    return { valid: false, detail: "token_expired" };
  }

  // Validate issuer
  const expectedIss = `https://login.microsoftonline.com/${tenantId}/v2.0`;
  if (payload.iss !== expectedIss) {
    return { valid: false, detail: "invalid_issuer" };
  }

  // Validate audience (aud can be string or string[])
  const audList = Array.isArray(payload.aud) ? payload.aud : [payload.aud];
  if (!audList.includes(clientId)) {
    return { valid: false, detail: "invalid_audience" };
  }

  return { valid: true };
}

// ---------------------------------------------------------------------------
// Supabase REST helpers
// ---------------------------------------------------------------------------
async function sbGet(
  path: string,
  serviceKey: string,
  supabaseUrl: string
): Promise<{ data: unknown; error: string | null; status: number }> {
  const url = `${supabaseUrl}/rest/v1/${path}`;
  const res = await fetch(url, {
    method: "GET",
    headers: sbHeaders(serviceKey),
  });
  const body = await res.json();
  if (!res.ok) {
    return {
      data: null,
      error:
        typeof body === "object" && body !== null && "message" in body
          ? String((body as Record<string, unknown>).message)
          : `HTTP ${res.status}`,
      status: res.status,
    };
  }
  return { data: body, error: null, status: res.status };
}

async function sbPost(
  path: string,
  payload: unknown,
  serviceKey: string,
  supabaseUrl: string
): Promise<{ data: unknown; error: string | null; status: number }> {
  const url = `${supabaseUrl}/rest/v1/${path}`;
  const res = await fetch(url, {
    method: "POST",
    headers: sbHeaders(serviceKey),
    body: JSON.stringify(payload),
  });
  const body = await res.json();
  if (!res.ok) {
    return {
      data: null,
      error:
        typeof body === "object" && body !== null && "message" in body
          ? String((body as Record<string, unknown>).message)
          : `HTTP ${res.status}`,
      status: res.status,
    };
  }
  return { data: body, error: null, status: res.status };
}

async function sbPatch(
  path: string,
  payload: unknown,
  serviceKey: string,
  supabaseUrl: string
): Promise<{ data: unknown; error: string | null; status: number }> {
  const url = `${supabaseUrl}/rest/v1/${path}`;
  const res = await fetch(url, {
    method: "PATCH",
    headers: sbHeaders(serviceKey),
    body: JSON.stringify(payload),
  });
  const body = await res.json();
  if (!res.ok) {
    return {
      data: null,
      error:
        typeof body === "object" && body !== null && "message" in body
          ? String((body as Record<string, unknown>).message)
          : `HTTP ${res.status}`,
      status: res.status,
    };
  }
  return { data: body, error: null, status: res.status };
}

async function logRunEvent(
  actionId: string,
  serviceKey: string,
  supabaseUrl: string
): Promise<void> {
  // Best-effort log — do not fail the request on log errors
  try {
    await sbPost(
      "ops.run_events",
      {
        level: "info",
        message: `M365 query: ${actionId}`,
        payload: { action_id: actionId, surface: "m365_copilot" },
      },
      serviceKey,
      supabaseUrl
    );
  } catch {
    console.warn("logRunEvent: failed to write run_event (non-fatal)");
  }
}

// ---------------------------------------------------------------------------
// Route handlers
// ---------------------------------------------------------------------------
function handleManifest(): Response {
  return jsonResponse({
    schema_version: "v1.5",
    name_for_human: "InsightPulse Ops Advisor",
    actions: ACTIONS_ALLOWLIST,
    ssot_ref: "ssot/m365/agents/insightpulseai_ops_advisor/actions.yaml",
  });
}

function handleHandshake(): Response {
  return jsonResponse({
    actions: ACTIONS_ALLOWLIST,
    capabilities: CAPABILITIES,
    data_residency: "sg1",
    ssot_ref: "ssot/m365/agents/insightpulseai_ops_advisor/capabilities.yaml",
  });
}

async function handleQuery(
  req: Request,
  serviceKey: string,
  supabaseUrl: string
): Promise<Response> {
  let body: { action_id?: string; parameters?: Record<string, unknown> };

  try {
    body = await req.json();
  } catch {
    return jsonResponse({ error: "invalid_json_body" }, 400);
  }

  const { action_id, parameters = {} } = body;

  if (
    action_id !== "query_advisor_findings" &&
    action_id !== "query_ops_runs"
  ) {
    return jsonResponse(
      {
        error: "action_not_supported_on_query_route",
        supported: ["query_advisor_findings", "query_ops_runs"],
      },
      400
    );
  }

  if (action_id === "query_advisor_findings") {
    let qPath =
      "ops.advisor_findings?status=eq.open&order=created_at.desc&limit=20";
    if (parameters.pillar) {
      qPath += `&pillar=eq.${encodeURIComponent(String(parameters.pillar))}`;
    }
    if (parameters.severity) {
      qPath += `&severity=eq.${encodeURIComponent(String(parameters.severity))}`;
    }

    const { data, error } = await sbGet(qPath, serviceKey, supabaseUrl);
    if (error) {
      return jsonResponse({ error: "upstream_error", detail: error }, 502);
    }

    await logRunEvent(action_id, serviceKey, supabaseUrl);

    const findings = Array.isArray(data) ? data : [];
    return jsonResponse({
      citations: findings,
      count: findings.length,
      ssot_ref:
        "ssot/m365/agents/insightpulseai_ops_advisor/actions.yaml",
    });
  }

  // query_ops_runs
  const { data, error } = await sbGet(
    "ops.advisor_scans?order=created_at.desc&limit=10",
    serviceKey,
    supabaseUrl
  );
  if (error) {
    return jsonResponse({ error: "upstream_error", detail: error }, 502);
  }

  await logRunEvent(action_id, serviceKey, supabaseUrl);

  const scans = Array.isArray(data) ? data : [];
  return jsonResponse({
    citations: scans,
    count: scans.length,
    ssot_ref:
      "ssot/m365/agents/insightpulseai_ops_advisor/actions.yaml",
  });
}

async function handleAction(
  req: Request,
  serviceKey: string,
  supabaseUrl: string
): Promise<Response> {
  let body: { action_id?: string; parameters?: Record<string, unknown> };

  try {
    body = await req.json();
  } catch {
    return jsonResponse({ error: "invalid_json_body" }, 400);
  }

  const { action_id, parameters = {} } = body;

  // Validate action_id against allowlist
  if (!action_id || !(ALLOWED_ACTION_IDS as readonly string[]).includes(action_id)) {
    return jsonResponse(
      {
        error: "action_not_allowed",
        ssot_ref:
          "ssot/m365/agents/insightpulseai_ops_advisor/actions.yaml",
      },
      400
    );
  }

  const typedActionId = action_id as AllowedActionId;

  if (typedActionId === "trigger_advisor_scan") {
    const { data, error } = await sbPost(
      "ops.advisor_scans",
      {
        provider: "github",
        status: "running",
        summary_json: {
          triggered_by: "m365_copilot",
          surface: "declarative_agent",
        },
      },
      serviceKey,
      supabaseUrl
    );

    if (error) {
      return jsonResponse({ error: "upstream_error", detail: error }, 502);
    }

    const scanRow = Array.isArray(data) ? data[0] : data;
    const scanId =
      scanRow && typeof scanRow === "object" && "id" in scanRow
        ? (scanRow as Record<string, unknown>).id
        : null;

    await logRunEvent(typedActionId, serviceKey, supabaseUrl);

    return jsonResponse({
      queued: true,
      scan_id: scanId,
      message:
        "Scan queued. Results available via query_advisor_findings.",
    });
  }

  if (typedActionId === "acknowledge_finding") {
    const findingId = parameters.finding_id;
    if (!findingId || typeof findingId !== "string") {
      return jsonResponse(
        { error: "missing_parameter", parameter: "finding_id" },
        400
      );
    }

    const { error } = await sbPatch(
      `ops.advisor_findings?id=eq.${encodeURIComponent(findingId)}`,
      { status: "dismissed" },
      serviceKey,
      supabaseUrl
    );

    if (error) {
      return jsonResponse({ error: "upstream_error", detail: error }, 502);
    }

    await logRunEvent(typedActionId, serviceKey, supabaseUrl);

    return jsonResponse({
      acknowledged: true,
      finding_id: findingId,
    });
  }

  // query_* action_ids sent to /action route — redirect guidance
  return jsonResponse(
    {
      error: "use_query_route",
      detail: `action_id '${typedActionId}' must be sent to POST /m365-copilot-broker/query`,
    },
    400
  );
}

// ---------------------------------------------------------------------------
// Main handler
// ---------------------------------------------------------------------------
serve(async (req: Request): Promise<Response> => {
  // CORS preflight
  if (req.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: CORS_HEADERS });
  }

  // Check required env vars
  const missingKeys = REQUIRED_KEYS.filter((k) => !Deno.env.get(k));
  if (missingKeys.length > 0) {
    return missingEnvResponse(missingKeys);
  }

  // At this point all env vars are confirmed present
  const serviceKey = SUPABASE_SERVICE_ROLE_KEY!;
  const supabaseUrl = SUPABASE_URL!;
  const tenantId = M365_COPILOT_TENANT_ID!;
  const clientId = M365_COPILOT_CLIENT_ID!;

  // Parse route from URL path suffix
  const url = new URL(req.url);
  const pathname = url.pathname;

  // GET /m365-copilot-broker/manifest
  if (req.method === "GET" && pathname.endsWith("/manifest")) {
    return handleManifest();
  }

  // GET /m365-copilot-broker/handshake
  if (req.method === "GET" && pathname.endsWith("/handshake")) {
    return handleHandshake();
  }

  // POST /m365-copilot-broker/query — JWT required
  if (req.method === "POST" && pathname.endsWith("/query")) {
    const authHeader = req.headers.get("Authorization");
    const jwtResult = validateJwt(authHeader, tenantId, clientId);
    if (!jwtResult.valid) {
      return jsonResponse(
        { error: "Unauthorized", detail: "invalid_jwt", reason: jwtResult.detail },
        401
      );
    }
    return handleQuery(req, serviceKey, supabaseUrl);
  }

  // POST /m365-copilot-broker/action — JWT required
  if (req.method === "POST" && pathname.endsWith("/action")) {
    const authHeader = req.headers.get("Authorization");
    const jwtResult = validateJwt(authHeader, tenantId, clientId);
    if (!jwtResult.valid) {
      return jsonResponse(
        { error: "Unauthorized", detail: "invalid_jwt", reason: jwtResult.detail },
        401
      );
    }
    return handleAction(req, serviceKey, supabaseUrl);
  }

  // Unknown route
  return jsonResponse({ error: "route_not_found" }, 404);
});
