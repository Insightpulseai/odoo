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
 * GET /api/advisor/findings
 *
 * Returns findings from the latest advisor run.
 * Query params:
 *   pillar    — filter by pillar (cost|security|reliability|operational_excellence|performance)
 *   severity  — filter by severity (critical|high|medium|low|info)
 *   limit     — max results (default 100)
 */
export async function GET(req: NextRequest) {
  if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
    return NextResponse.json({ error: "Supabase not configured" }, { status: 503 })
  }

  const { searchParams } = req.nextUrl
  const pillar = searchParams.get("pillar")
  const severity = searchParams.get("severity")
  const limit = searchParams.get("limit") ?? "100"

  try {
    // Get latest complete run
    const runRes = await fetch(
      `${SUPABASE_URL}/rest/v1/ops.advisor_runs?status=eq.complete&order=started_at.desc&limit=1`,
      { headers: supabaseHeaders() }
    )
    if (!runRes.ok) {
      return NextResponse.json({ error: await runRes.text() }, { status: runRes.status })
    }
    const runs = await runRes.json()
    if (runs.length === 0) {
      return NextResponse.json({ findings: [], run: null })
    }
    const latestRun = runs[0]

    // Build findings query
    const params = new URLSearchParams()
    params.set("run_id", `eq.${latestRun.id}`)
    if (pillar) params.set("pillar", `eq.${pillar}`)
    if (severity) params.set("severity", `eq.${severity}`)
    params.set("order", "severity.asc")
    params.set("limit", limit)

    const findingsRes = await fetch(
      `${SUPABASE_URL}/rest/v1/ops.advisor_findings?${params.toString()}`,
      { headers: supabaseHeaders() }
    )
    if (!findingsRes.ok) {
      return NextResponse.json({ error: await findingsRes.text() }, { status: findingsRes.status })
    }
    const findings = await findingsRes.json()

    return NextResponse.json({ findings, run: latestRun })
  } catch (err) {
    return NextResponse.json({ error: String(err) }, { status: 500 })
  }
}
