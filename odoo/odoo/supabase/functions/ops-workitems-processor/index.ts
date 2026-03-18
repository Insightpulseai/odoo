/**
 * ops-workitems-processor — async work items processor
 *
 * Claims queued items from ops.work_queue, normalises payloads
 * from delivery ledgers, upserts into ops.work_items, marks
 * ledger rows processed/failed.
 *
 * Idempotent: same delivery_id processed twice → same result, no duplicate side effects.
 */

const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
const serviceKey  = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

const BATCH_SIZE = 10;

interface WorkQueueItem {
  id: number;
  source: "plane" | "github";
  delivery_id: string;
  attempts: number;
}

interface WorkItem {
  work_item_ref: string;
  system: string;
  external_id: string;
  project_ref?: string;
  title: string;
  status: string;
  assignee?: string;
  url?: string;
  updated_at?: string;
}

function json(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

async function postgrest(
  path: string,
  method: string,
  body?: unknown,
  prefer?: string
): Promise<unknown> {
  const headers: Record<string, string> = {
    apikey: serviceKey,
    Authorization: `Bearer ${serviceKey}`,
    "Content-Type": "application/json",
    "Accept-Profile": "ops",
  };
  if (prefer) headers["Prefer"] = prefer;
  if (method !== "GET" && method !== "DELETE") headers["Content-Profile"] = "ops";

  const res = await fetch(`${supabaseUrl}/rest/v1/${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error(`PostgREST ${path}: ${res.status} ${await res.text()}`);
  const text = await res.text();
  return text ? JSON.parse(text) : null;
}

async function claimBatch(): Promise<WorkQueueItem[]> {
  // Claim queued items using status transition
  const items = await postgrest(
    `work_queue?status=eq.queued&available_at=lte.${new Date().toISOString()}&order=id.asc&limit=${BATCH_SIZE}`,
    "GET"
  ) as WorkQueueItem[];
  if (!items?.length) return [];

  // Mark claimed
  const ids = items.map((i) => i.id);
  await postgrest(
    `work_queue?id=in.(${ids.join(",")})`,
    "PATCH",
    { status: "claimed", claimed_at: new Date().toISOString() },
    "return=minimal"
  );
  return items;
}

function normalizePlane(payload: Record<string, unknown>): WorkItem | null {
  const issue = payload.issue as Record<string, unknown> | undefined;
  const project = payload.project as Record<string, unknown> | undefined;
  if (!issue?.id) return null;

  const assignees = (issue.assignees as Array<{ display_name?: string }>) ?? [];
  return {
    work_item_ref: `plane:${issue.id}`,
    system: "plane",
    external_id: String(issue.id),
    project_ref: project?.id ? String(project.id) : undefined,
    title: String(issue.name ?? ""),
    status: (issue.state as { name?: string })?.name ?? "unknown",
    assignee: assignees[0]?.display_name,
    url: issue.url ? String(issue.url) : undefined,
    updated_at: issue.updated_at ? String(issue.updated_at) : undefined,
  };
}

function normalizeGitHub(payload: Record<string, unknown>): WorkItem | null {
  const issue = payload.issue as Record<string, unknown> | undefined;
  const repo  = payload.repository as Record<string, unknown> | undefined;
  if (!issue?.number || !repo?.full_name) return null;

  return {
    work_item_ref: `github:${repo.full_name}#${issue.number}`,
    system: "github",
    external_id: `${repo.full_name}#${issue.number}`,
    project_ref: String(repo.full_name),
    title: String(issue.title ?? ""),
    status: String(issue.state ?? "open"),
    assignee: (issue.assignee as { login?: string } | null)?.login ?? undefined,
    url: issue.html_url ? String(issue.html_url) : undefined,
    updated_at: issue.updated_at ? String(issue.updated_at) : undefined,
  };
}

async function processItem(item: WorkQueueItem): Promise<void> {
  const ledgerTable = item.source === "plane"
    ? "plane_webhook_deliveries"
    : "github_webhook_deliveries";

  // Fetch delivery
  const rows = await postgrest(
    `${ledgerTable}?delivery_id=eq.${encodeURIComponent(item.delivery_id)}&select=payload`,
    "GET"
  ) as Array<{ payload: Record<string, unknown> }>;

  if (!rows?.length) throw new Error(`Delivery not found: ${item.delivery_id}`);
  const payload = rows[0].payload;

  // Normalize
  const workItem = item.source === "plane"
    ? normalizePlane(payload)
    : normalizeGitHub(payload);

  if (!workItem) throw new Error(`Cannot normalize payload for ${item.delivery_id}`);

  // Upsert ops.work_items
  await postgrest(
    "work_items",
    "POST",
    { ...workItem, ingested_at: new Date().toISOString() },
    "resolution=merge-duplicates,return=minimal"
  );

  // Mark delivery processed
  await postgrest(
    `${ledgerTable}?delivery_id=eq.${encodeURIComponent(item.delivery_id)}`,
    "PATCH",
    { status: "processed" },
    "return=minimal"
  );

  // Mark queue item done
  await postgrest(
    `work_queue?id=eq.${item.id}`,
    "PATCH",
    { status: "done" },
    "return=minimal"
  );
}

Deno.serve(async (_req: Request) => {
  const items = await claimBatch();
  if (!items.length) return json({ ok: true, processed: 0 });

  const results = { processed: 0, failed: 0 };
  for (const item of items) {
    try {
      await processItem(item);
      results.processed++;
    } catch (err) {
      results.failed++;
      console.error(`processor: failed item ${item.id}`, err);
      // Mark failed in queue
      try {
        await postgrest(
          `work_queue?id=eq.${item.id}`,
          "PATCH",
          {
            status: "failed",
            last_error: String(err),
            attempts: item.attempts + 1,
            available_at: new Date(Date.now() + 60_000).toISOString(), // retry in 60s
          },
          "return=minimal"
        );
        // Mark delivery failed
        const ledgerTable = item.source === "plane"
          ? "plane_webhook_deliveries"
          : "github_webhook_deliveries";
        await postgrest(
          `${ledgerTable}?delivery_id=eq.${encodeURIComponent(item.delivery_id)}`,
          "PATCH",
          { status: "failed", last_error: String(err) },
          "return=minimal"
        );
      } catch (auditErr) {
        console.error("processor: audit update failed", auditErr);
      }
    }
  }

  return json({ ok: true, ...results });
});
