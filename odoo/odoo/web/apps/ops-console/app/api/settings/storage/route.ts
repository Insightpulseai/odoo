import { NextRequest, NextResponse } from "next/server"

const SUPABASE_URL = process.env.SUPABASE_URL ?? process.env.NEXT_PUBLIC_SUPABASE_URL ?? ""
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY ?? ""

function supabaseHeaders() {
  return {
    apikey: SUPABASE_SERVICE_ROLE_KEY,
    Authorization: `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
    "Content-Type": "application/json",
  }
}

/**
 * GET /api/settings/storage
 *
 * Returns storage telemetry from the latest settings_snapshot and
 * artifact counts from ops.artifacts (one artifact per kind).
 */
export async function GET(_req: NextRequest) {
  if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
    return NextResponse.json({ error: "Supabase not configured" }, { status: 503 })
  }

  try {
    const [snapshotRes, artifactsRes] = await Promise.all([
      fetch(
        `${SUPABASE_URL}/rest/v1/ops.artifacts?kind=eq.settings_snapshot&order=created_at.desc&limit=1&select=metadata`,
        { headers: supabaseHeaders(), next: { revalidate: 120 } }
      ),
      // Count artifacts by kind (proxy for storage health)
      fetch(
        `${SUPABASE_URL}/rest/v1/ops.artifacts?select=kind,created_at&order=created_at.desc&limit=100`,
        { headers: supabaseHeaders(), next: { revalidate: 120 } }
      ),
    ])

    const snapshotRows = snapshotRes.ok ? await snapshotRes.json() : []
    const artifacts = artifactsRes.ok ? await artifactsRes.json() : []

    // Aggregate artifact counts by kind
    const kindCounts: Record<string, number> = {}
    for (const a of artifacts) {
      kindCounts[a.kind] = (kindCounts[a.kind] ?? 0) + 1
    }

    const storage = snapshotRows[0]?.metadata?.storage ?? null
    const capacity = snapshotRows[0]?.metadata?.capacity ?? null

    return NextResponse.json({ storage, capacity, artifact_kind_counts: kindCounts })
  } catch (err) {
    return NextResponse.json({ error: String(err) }, { status: 500 })
  }
}
