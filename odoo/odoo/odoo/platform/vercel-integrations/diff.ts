/**
 * Vercel Integrations Diff Engine
 *
 * Compares two snapshots of a Vercel team's integrations and returns
 * what was added, removed, or changed between them.
 *
 * Reads from ops.integrations_snapshots via Supabase REST API.
 */

export interface Integration {
  id: string;
  name: string;
  slug: string;
  status: string;
  scopes?: string[];
  [key: string]: unknown;
}

export interface IntegrationSnapshot {
  id: string;
  team_id: string;
  captured_at: string;
  integrations: Integration[];
}

export interface DiffResult {
  team_id: string;
  before_captured_at: string;
  after_captured_at: string;
  added: Integration[];
  removed: Integration[];
  changed: Array<{ before: Integration; after: Integration; fields: string[] }>;
  has_drift: boolean;
}

/**
 * Fetch the two most recent snapshots for a team from Supabase.
 */
export async function fetchLatestSnapshots(
  supabaseUrl: string,
  serviceRoleKey: string,
  teamId: string
): Promise<[IntegrationSnapshot, IntegrationSnapshot] | null> {
  const res = await fetch(
    `${supabaseUrl}/rest/v1/ops.integrations_snapshots?team_id=eq.${encodeURIComponent(teamId)}&order=captured_at.desc&limit=2`,
    {
      headers: {
        apikey: serviceRoleKey,
        Authorization: `Bearer ${serviceRoleKey}`,
        "Content-Type": "application/json",
      },
    }
  );

  if (!res.ok) {
    throw new Error(`Supabase fetch failed: ${res.status} ${await res.text()}`);
  }

  const rows: IntegrationSnapshot[] = await res.json();
  if (rows.length < 2) return null; // Not enough history yet

  // Most recent first, so rows[0]=after, rows[1]=before
  return [rows[1], rows[0]];
}

/**
 * Compute diff between two snapshots.
 */
export function diffSnapshots(
  before: IntegrationSnapshot,
  after: IntegrationSnapshot
): DiffResult {
  const beforeMap = new Map(before.integrations.map((i) => [i.id, i]));
  const afterMap = new Map(after.integrations.map((i) => [i.id, i]));

  const added: Integration[] = [];
  const removed: Integration[] = [];
  const changed: DiffResult["changed"] = [];

  // Find added and changed
  for (const [id, afterInt] of afterMap) {
    const beforeInt = beforeMap.get(id);
    if (!beforeInt) {
      added.push(afterInt);
    } else {
      const changedFields = detectChangedFields(beforeInt, afterInt);
      if (changedFields.length > 0) {
        changed.push({ before: beforeInt, after: afterInt, fields: changedFields });
      }
    }
  }

  // Find removed
  for (const [id, beforeInt] of beforeMap) {
    if (!afterMap.has(id)) {
      removed.push(beforeInt);
    }
  }

  return {
    team_id: after.team_id,
    before_captured_at: before.captured_at,
    after_captured_at: after.captured_at,
    added,
    removed,
    changed,
    has_drift: added.length > 0 || removed.length > 0 || changed.length > 0,
  };
}

function detectChangedFields(before: Integration, after: Integration): string[] {
  const TRACKED_FIELDS = ["name", "slug", "status", "scopes"];
  const changed: string[] = [];
  for (const field of TRACKED_FIELDS) {
    const b = JSON.stringify(before[field]);
    const a = JSON.stringify(after[field]);
    if (b !== a) changed.push(field);
  }
  return changed;
}
