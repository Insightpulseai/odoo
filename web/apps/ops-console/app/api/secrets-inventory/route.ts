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
 * GET /api/secrets-inventory
 *
 * Returns the current observed state of secrets from ops.secret_inventory.
 * Ordered by severity_if_missing DESC (critical first), then status.
 *
 * Query params:
 *   status  — filter by status (ok|missing|stale|unknown). Default: all.
 *   limit   — max results (default 100)
 */
export async function GET(req: NextRequest) {
  if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
    return NextResponse.json(
      { error: "Supabase not configured" },
      { status: 503 }
    )
  }

  const { searchParams } = req.nextUrl
  const statusFilter = searchParams.get("status")
  const limit = searchParams.get("limit") ?? "100"

  try {
    const params = new URLSearchParams()

    // Severity ordering: critical > high > medium > low
    params.set(
      "order",
      "severity_if_missing.asc,status.asc,key.asc"
    )
    params.set("limit", limit)

    if (statusFilter) {
      params.set("status", `eq.${statusFilter}`)
    }

    const res = await fetch(
      `${SUPABASE_URL}/rest/v1/ops.secret_inventory?${params.toString()}`,
      {
        headers: supabaseHeaders(),
        next: { revalidate: 60 },
      }
    )

    if (!res.ok) {
      const body = await res.text()
      return NextResponse.json({ error: body }, { status: res.status })
    }

    const secrets = (await res.json()) as Array<Record<string, unknown>>

    // Re-sort client-side so critical appears before low
    const severityOrder: Record<string, number> = {
      critical: 0,
      high: 1,
      medium: 2,
      low: 3,
    }
    secrets.sort((a, b) => {
      const aS = severityOrder[String(a.severity_if_missing ?? "")] ?? 99
      const bS = severityOrder[String(b.severity_if_missing ?? "")] ?? 99
      if (aS !== bS) return aS - bS
      return String(a.status ?? "").localeCompare(String(b.status ?? ""))
    })

    return NextResponse.json({ secrets })
  } catch (err) {
    return NextResponse.json({ error: String(err) }, { status: 500 })
  }
}
