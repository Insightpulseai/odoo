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
 * GET /api/settings/parity
 *
 * Returns EE parity gate summary from the latest settings_snapshot.
 * Source: ssot/parity/odoo_enterprise.yaml (compiled into snapshot by CI).
 *
 * Query params:
 *   status — filter features by status (met|partial|missing|waived)
 */
export async function GET(req: NextRequest) {
  if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
    return NextResponse.json({ error: "Supabase not configured" }, { status: 503 })
  }

  const { searchParams } = req.nextUrl
  const statusFilter = searchParams.get("status") // optional

  try {
    const res = await fetch(
      `${SUPABASE_URL}/rest/v1/ops.artifacts?kind=eq.settings_snapshot&order=created_at.desc&limit=1&select=metadata`,
      { headers: supabaseHeaders(), next: { revalidate: 120 } }
    )

    if (!res.ok) {
      return NextResponse.json({ error: await res.text() }, { status: res.status })
    }

    const rows = await res.json()
    if (!rows.length) {
      return NextResponse.json({ parity: null })
    }

    const parity = rows[0]?.metadata?.parity ?? null
    if (!parity) {
      return NextResponse.json({ parity: null })
    }

    // Optionally filter feature list
    if (statusFilter && parity.features) {
      parity.features = parity.features.filter((f: { status: string }) => f.status === statusFilter)
    }

    return NextResponse.json({ parity })
  } catch (err) {
    return NextResponse.json({ error: String(err) }, { status: 500 })
  }
}
