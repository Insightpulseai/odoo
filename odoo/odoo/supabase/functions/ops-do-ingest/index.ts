// =============================================================================
// ops-do-ingest — DigitalOcean Inventory Ingestion Edge Function
// =============================================================================
// Contract:  docs/contracts/C-DO-01-digitalocean-api.md (C-18)
// SSOT:      ssot/providers/digitalocean/provider.yaml
// Migration: supabase/migrations/20260301000050_ops_digitalocean.sql
//
// Auth:      Reads `digitalocean_api_token` from Supabase Vault at runtime.
// Schedule:  Invoked every hour via pg_cron / Vercel cron.
// =============================================================================

// ---------------------------------------------------------------------------
// Supabase PostgREST client (no SDK dependency — raw fetch against REST API)
// ---------------------------------------------------------------------------

const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

async function postgrest(
  method: string,
  path: string,
  body?: unknown,
  extraHeaders: Record<string, string> = {},
): Promise<unknown> {
  const headers: Record<string, string> = {
    apikey: serviceKey,
    Authorization: `Bearer ${serviceKey}`,
    "Content-Type": "application/json",
    ...extraHeaders,
  };
  if (method === "POST") {
    headers["Prefer"] = "resolution=merge-duplicates,return=representation";
  }
  const res = await fetch(`${supabaseUrl}/rest/v1/${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`PostgREST ${method} ${path}: ${res.status} ${text}`);
  }
  const text = await res.text();
  return text ? JSON.parse(text) : null;
}

// Read a single column from a PostgREST SELECT (returns first row value or null)
async function postgrestSelectOne<T>(
  path: string,
  column: string,
): Promise<T | null> {
  const rows = (await postgrest("GET", path)) as Record<string, T>[] | null;
  if (!rows || rows.length === 0) return null;
  return rows[0][column] ?? null;
}

// ---------------------------------------------------------------------------
// Vault: read DO API token
// ---------------------------------------------------------------------------

async function readDoToken(): Promise<string> {
  // vault.decrypted_secrets is a view — must use the Supabase REST API against
  // the `vault` schema via the special header.
  const res = await fetch(
    `${supabaseUrl}/rest/v1/vault.decrypted_secrets?name=eq.digitalocean_api_token&select=decrypted_secret`,
    {
      headers: {
        apikey: serviceKey,
        Authorization: `Bearer ${serviceKey}`,
        Accept: "application/json",
      },
    },
  );
  if (!res.ok) {
    throw new Error(
      `Vault read failed: ${res.status} ${await res.text()}`,
    );
  }
  const rows = (await res.json()) as { decrypted_secret: string }[];
  if (!rows || rows.length === 0) {
    throw new Error(
      "Vault secret `digitalocean_api_token` not found — add it via Supabase Vault before running ops-do-ingest",
    );
  }
  return rows[0].decrypted_secret;
}

// ---------------------------------------------------------------------------
// DigitalOcean REST client
// ---------------------------------------------------------------------------

const DO_BASE_URL = "https://api.digitalocean.com/v2";
const DO_MAX_ATTEMPTS = 5;

interface DOErrorBody {
  id: string;
  message: string;
}

class DOClientError extends Error {
  constructor(
    public readonly status: number,
    public readonly id: string,
    message: string,
  ) {
    super(message);
    this.name = "DOClientError";
  }
}

// Retry policy: exponential backoff 2^s seconds, handles 429 + 5xx.
async function withRetry(
  fn: () => Promise<Response>,
): Promise<Response> {
  let lastError: Error = new Error("withRetry: no attempts made");
  for (let attempt = 1; attempt <= DO_MAX_ATTEMPTS; attempt++) {
    const res = await fn();
    if (res.ok) return res;

    // 429 Too Many Requests — respect Retry-After
    if (res.status === 429) {
      const retryAfter = res.headers.get("Retry-After");
      const waitMs = retryAfter ? parseInt(retryAfter, 10) * 1000 : 60_000;
      console.warn(
        `DO API rate limited (429). Waiting ${waitMs}ms before retry ${attempt}/${DO_MAX_ATTEMPTS}`,
      );
      await sleep(waitMs);
      lastError = new Error(`DO API 429 rate limit on attempt ${attempt}`);
      continue;
    }

    // 5xx transient errors — exponential backoff
    if (res.status >= 500 && res.status < 600) {
      const waitMs = Math.pow(2, attempt) * 1000;
      console.warn(
        `DO API ${res.status}. Backoff ${waitMs}ms before retry ${attempt}/${DO_MAX_ATTEMPTS}`,
      );
      await sleep(waitMs);
      lastError = new Error(`DO API ${res.status} on attempt ${attempt}`);
      continue;
    }

    // 4xx (except 429) — do not retry; parse error body and throw
    let errBody: DOErrorBody = { id: "unknown", message: res.statusText };
    try {
      errBody = await res.json() as DOErrorBody;
    } catch { /* ignore parse error */ }
    throw new DOClientError(res.status, errBody.id, errBody.message);
  }
  throw lastError;
}

// Async generator: paginate through a DO API endpoint using page + per_page=200.
// Yields individual items from the resource array.
async function* paginate<T>(
  path: string,
  token: string,
  resourceKey: string,
): AsyncGenerator<T> {
  let page = 1;
  while (true) {
    const url = `${DO_BASE_URL}${path}?page=${page}&per_page=200`;
    const res = await withRetry(() =>
      fetch(url, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      })
    );
    const body = await res.json() as Record<string, unknown>;
    const items = (body[resourceKey] as T[]) ?? [];
    for (const item of items) {
      yield item;
    }
    // Check for next page
    const links = body["links"] as {
      pages?: { next?: string };
    } | undefined;
    if (!links?.pages?.next) break;
    page++;
  }
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// Extract the public IPv4 from DO networks array
function extractIpv4(
  networks: { v4?: { ip_address: string; type: string }[] } | undefined,
  type: "public" | "private",
): string | null {
  if (!networks?.v4) return null;
  const found = networks.v4.find((n) => n.type === type);
  return found?.ip_address ?? null;
}

// ---------------------------------------------------------------------------
// DO resource types
// ---------------------------------------------------------------------------

interface DODroplet {
  id: number;
  name: string;
  region: { slug: string };
  size: { slug: string };
  networks: { v4?: { ip_address: string; type: string }[] };
  status: string;
  tags: string[];
  image: { slug: string };
  vcpus: number;
  memory: number;
  disk: number;
  created_at: string;
}

interface DODatabase {
  id: string;
  name: string;
  engine: string;
  version: string;
  region: string;
  status: string;
  size: string;
  num_nodes: number;
  connection: {
    host?: string;
    port?: number;
    ssl?: boolean;
  };
  tags: string[];
  created_at: string;
}

interface DOFirewall {
  id: string;
  name: string;
  status: string;
  inbound_rules: unknown[];
  outbound_rules: unknown[];
  droplet_ids: number[];
  tags: string[];
  created_at: string;
}

// ---------------------------------------------------------------------------
// Ingest run helpers (PostgREST)
// ---------------------------------------------------------------------------

async function createIngestRun(
  triggeredBy: "cron" | "manual" | "webhook",
): Promise<string> {
  const rows = (await postgrest(
    "POST",
    "ops.do_ingest_runs",
    { status: "running", triggered_by: triggeredBy, counts: {} },
  )) as { run_id: string }[];
  if (!rows || rows.length === 0) {
    throw new Error("Failed to create ops.do_ingest_runs row");
  }
  return rows[0].run_id;
}

async function finalizeIngestRun(
  runId: string,
  status: "success" | "partial" | "error",
  counts: Record<string, number>,
  lastError?: string,
): Promise<void> {
  await postgrest(
    "PATCH",
    `ops.do_ingest_runs?run_id=eq.${encodeURIComponent(runId)}`,
    {
      status,
      counts,
      finished_at: new Date().toISOString(),
      ...(lastError ? { last_error: lastError } : {}),
    },
  );
}

async function logAction(
  resourceType: string,
  resourceId: string,
  count: number,
  errorMsg?: string,
): Promise<void> {
  await postgrest("POST", "ops.do_actions", {
    resource_type: resourceType,
    resource_id: resourceId,
    kind: "ingest_read",
    status: errorMsg ? "errored" : "completed",
    completed_at: new Date().toISOString(),
    metadata: { count, ...(errorMsg ? { error: errorMsg } : {}) },
  });
}

// ---------------------------------------------------------------------------
// Resource ingest functions
// ---------------------------------------------------------------------------

async function ingestDroplets(
  token: string,
): Promise<{ count: number; error?: string }> {
  const rows: unknown[] = [];
  let error: string | undefined;

  try {
    for await (const d of paginate<DODroplet>("/v2/droplets", token, "droplets")) {
      rows.push({
        do_id: d.id,
        name: d.name,
        region: d.region?.slug ?? "unknown",
        size_slug: d.size?.slug ?? null,
        ipv4_public: extractIpv4(d.networks, "public"),
        ipv4_private: extractIpv4(d.networks, "private"),
        status: d.status,
        tags: d.tags ?? [],
        image_slug: d.image?.slug ?? null,
        vcpus: d.vcpus ?? null,
        memory_mb: d.memory ?? null,
        disk_gb: d.disk ?? null,
        created_at_do: d.created_at ?? null,
        raw: d,
      });
    }

    if (rows.length > 0) {
      // Upsert in batches of 100 to stay within PostgREST limits
      for (let i = 0; i < rows.length; i += 100) {
        const batch = rows.slice(i, i + 100);
        await postgrest(
          "POST",
          "ops.do_droplets",
          batch,
          { Prefer: "resolution=merge-duplicates" },
        );
      }
    }
  } catch (e) {
    error = (e as Error).message;
    console.error("ingestDroplets error:", error);
  }

  await logAction("droplet", "all", rows.length, error);
  return { count: rows.length, error };
}

async function ingestDatabases(
  token: string,
): Promise<{ count: number; error?: string }> {
  const rows: unknown[] = [];
  let error: string | undefined;

  try {
    for await (const c of paginate<DODatabase>("/v2/databases", token, "databases")) {
      rows.push({
        do_id: c.id,
        name: c.name,
        engine: c.engine,
        version: c.version ?? null,
        region: c.region,
        status: c.status,
        size_slug: c.size ?? null,
        num_nodes: c.num_nodes ?? 1,
        endpoint_host: c.connection?.host ?? null,
        endpoint_port: c.connection?.port ?? null,
        ssl_required: c.connection?.ssl ?? true,
        tags: c.tags ?? [],
        created_at_do: c.created_at ?? null,
        raw: c,
      });
    }

    if (rows.length > 0) {
      for (let i = 0; i < rows.length; i += 100) {
        const batch = rows.slice(i, i + 100);
        await postgrest(
          "POST",
          "ops.do_databases",
          batch,
          { Prefer: "resolution=merge-duplicates" },
        );
      }
    }
  } catch (e) {
    error = (e as Error).message;
    console.error("ingestDatabases error:", error);
  }

  await logAction("database", "all", rows.length, error);
  return { count: rows.length, error };
}

async function ingestFirewalls(
  token: string,
): Promise<{ count: number; error?: string }> {
  const rows: unknown[] = [];
  let error: string | undefined;

  try {
    for await (const f of paginate<DOFirewall>("/v2/firewalls", token, "firewalls")) {
      rows.push({
        do_id: f.id,
        name: f.name,
        status: f.status,
        inbound_rules: f.inbound_rules ?? [],
        outbound_rules: f.outbound_rules ?? [],
        droplet_ids: f.droplet_ids ?? [],
        tags: f.tags ?? [],
        created_at_do: f.created_at ?? null,
        raw: f,
      });
    }

    if (rows.length > 0) {
      for (let i = 0; i < rows.length; i += 100) {
        const batch = rows.slice(i, i + 100);
        await postgrest(
          "POST",
          "ops.do_firewalls",
          batch,
          { Prefer: "resolution=merge-duplicates" },
        );
      }
    }
  } catch (e) {
    error = (e as Error).message;
    console.error("ingestFirewalls error:", error);
  }

  await logAction("firewall", "all", rows.length, error);
  return { count: rows.length, error };
}

// ---------------------------------------------------------------------------
// Main handler
// ---------------------------------------------------------------------------

Deno.serve(async (req: Request): Promise<Response> => {
  // CORS preflight
  if (req.method === "OPTIONS") {
    return new Response(null, {
      status: 204,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers":
          "authorization, x-client-info, apikey, content-type",
      },
    });
  }

  // Accept GET (cron) or POST (manual trigger)
  if (req.method !== "GET" && req.method !== "POST") {
    return Response.json({ ok: false, error: "Method not allowed" }, { status: 405 });
  }

  // Determine trigger source
  let triggeredBy: "cron" | "manual" | "webhook" = "cron";
  if (req.method === "POST") {
    try {
      const body = await req.json() as { triggered_by?: string };
      if (body.triggered_by === "webhook") triggeredBy = "webhook";
      else triggeredBy = "manual";
    } catch { /* POST with no body → manual */ triggeredBy = "manual"; }
  }

  let runId: string | undefined;

  try {
    // 1. Validate environment
    if (!supabaseUrl || !serviceKey) {
      throw new Error(
        "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables are required",
      );
    }

    // 2. Read DO token from Vault
    const doToken = await readDoToken();

    // 3. Open ingest run record
    runId = await createIngestRun(triggeredBy);
    console.log(`ops-do-ingest: run_id=${runId} triggered_by=${triggeredBy}`);

    // 4. Ingest resources (in order per contract)
    const [dropletResult, databaseResult, firewallResult] = await Promise.all([
      ingestDroplets(doToken),
      ingestDatabases(doToken),
      ingestFirewalls(doToken),
    ]);

    // 5. Compute final status
    const errors = [
      dropletResult.error,
      databaseResult.error,
      firewallResult.error,
    ].filter(Boolean) as string[];

    const counts = {
      droplets: dropletResult.count,
      databases: databaseResult.count,
      firewalls: firewallResult.count,
      errors: errors.length,
    };

    let finalStatus: "success" | "partial" | "error";
    if (errors.length === 0) {
      finalStatus = "success";
    } else if (errors.length < 3) {
      finalStatus = "partial";
    } else {
      finalStatus = "error";
    }

    // 6. Finalize run record
    await finalizeIngestRun(
      runId,
      finalStatus,
      counts,
      errors.length > 0 ? errors[0] : undefined,
    );

    console.log(
      `ops-do-ingest: ${finalStatus} run_id=${runId} counts=${JSON.stringify(counts)}`,
    );

    return Response.json({
      ok: finalStatus !== "error",
      run_id: runId,
      counts,
      ...(errors.length > 0 ? { errors } : {}),
    });
  } catch (err) {
    const message = (err as Error).message ?? "Internal error";
    console.error("ops-do-ingest fatal:", message);

    // Attempt to mark run as error if we managed to create it
    if (runId) {
      try {
        await finalizeIngestRun(runId, "error", {}, message);
      } catch { /* best-effort */ }
    }

    return Response.json({ ok: false, error: message }, { status: 500 });
  }
});
