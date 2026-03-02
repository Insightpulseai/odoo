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
 * GET /api/settings/integrations
 *
 * Returns GitHub App integration status and last webhook deliveries.
 * Combines:
 *   - integrations section from latest settings_snapshot (ops.artifacts)
 *   - last 20 rows from ops.github_webhook_deliveries
 */
export async function GET(req: NextRequest) {
  if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
    return NextResponse.json({ error: "Supabase not configured" }, { status: 503 })
  }

  const { searchParams } = req.nextUrl
  const limit = searchParams.get("limit") ?? "20"

  try {
    // Deliveries ledger
    const deliveriesParams = new URLSearchParams({
      order: "received_at.desc",
      limit,
      select: "delivery_id,event_type,received_at,status,last_error",
    })

    const [snapshotRes, deliveriesRes] = await Promise.all([
      fetch(
        `${SUPABASE_URL}/rest/v1/ops.artifacts?kind=eq.settings_snapshot&order=created_at.desc&limit=1&select=metadata`,
        { headers: supabaseHeaders(), next: { revalidate: 120 } }
      ),
      fetch(
        `${SUPABASE_URL}/rest/v1/ops.github_webhook_deliveries?${deliveriesParams}`,
        { headers: supabaseHeaders(), next: { revalidate: 30 } }
      ),
    ])

    const snapshotRows = snapshotRes.ok ? await snapshotRes.json() : []
    const deliveries = deliveriesRes.ok ? await deliveriesRes.json() : []

    const integrations = snapshotRows[0]?.metadata?.integrations ?? null

    return NextResponse.json({ integrations, deliveries })
  } catch (err) {
    return NextResponse.json({ error: String(err) }, { status: 500 })
  }
}
