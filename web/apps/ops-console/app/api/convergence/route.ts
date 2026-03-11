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
 * GET /api/convergence
 *
 * Returns recent unresolved convergence findings from ops.convergence_findings.
 * Query params:
 *   limit — max results (default 5)
 */
export async function GET(req: NextRequest) {
  if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
    return NextResponse.json({ error: "Supabase not configured" }, { status: 503 })
  }

  const { searchParams } = req.nextUrl
  const limit = searchParams.get("limit") ?? "5"

  try {
    const params = new URLSearchParams()
    params.set("status", "neq.resolved")
    params.set("order", "last_seen.desc")
    params.set("limit", limit)

    const res = await fetch(
      `${SUPABASE_URL}/rest/v1/ops.convergence_findings?${params.toString()}`,
      { headers: supabaseHeaders(), next: { revalidate: 60 } }
    )

    if (!res.ok) {
      return NextResponse.json({ error: await res.text() }, { status: res.status })
    }

    const findings = await res.json()
    return NextResponse.json({ findings })
  } catch (err) {
    return NextResponse.json({ error: String(err) }, { status: 500 })
  }
}
