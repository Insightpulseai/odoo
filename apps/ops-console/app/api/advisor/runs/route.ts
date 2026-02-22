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
 * GET /api/advisor/runs
 *
 * Returns the latest advisor run(s) with their scores.
 * Query params: limit (default 1)
 */
export async function GET(req: NextRequest) {
  if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
    return NextResponse.json({ error: "Supabase not configured" }, { status: 503 })
  }

  const limit = req.nextUrl.searchParams.get("limit") ?? "1"

  try {
    // Fetch latest run
    const runsRes = await fetch(
      `${SUPABASE_URL}/rest/v1/ops.advisor_runs?order=started_at.desc&limit=${encodeURIComponent(limit)}`,
      { headers: supabaseHeaders() }
    )
    if (!runsRes.ok) {
      const text = await runsRes.text()
      return NextResponse.json({ error: text }, { status: runsRes.status })
    }
    const runs = await runsRes.json()

    // Fetch scores for the latest run
    let scores: unknown[] = []
    if (runs.length > 0) {
      const scoresRes = await fetch(
        `${SUPABASE_URL}/rest/v1/ops.advisor_scores?run_id=eq.${runs[0].id}`,
        { headers: supabaseHeaders() }
      )
      if (scoresRes.ok) scores = await scoresRes.json()
    }

    return NextResponse.json({ runs, scores })
  } catch (err) {
    return NextResponse.json({ error: String(err) }, { status: 500 })
  }
}

/**
 * POST /api/advisor/runs
 *
 * Triggers a new advisor scan (async, returns the run record immediately).
 * The scorer runs as a background task; status is updated in ops.advisor_runs.
 */
export async function POST() {
  if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
    return NextResponse.json({ error: "Supabase not configured" }, { status: 503 })
  }

  try {
    // Create a pending run record
    const runRes = await fetch(`${SUPABASE_URL}/rest/v1/ops.advisor_runs`, {
      method: "POST",
      headers: { ...supabaseHeaders(), Prefer: "return=representation" },
      body: JSON.stringify({
        team_id: "default",
        triggered_by: "api",
        status: "pending",
      }),
    })
    if (!runRes.ok) {
      const text = await runRes.text()
      return NextResponse.json({ error: text }, { status: runRes.status })
    }
    const [run] = await runRes.json()

    // TODO: Trigger scorer asynchronously (e.g., via n8n webhook or Edge Function)
    // For now, the run is created with status "pending" and must be executed via:
    //   tsx platform/advisor/scorer.ts
    // or a scheduled CI workflow.

    return NextResponse.json({ run, message: "Scan queued. Run: tsx platform/advisor/scorer.ts to execute." }, { status: 202 })
  } catch (err) {
    return NextResponse.json({ error: String(err) }, { status: 500 })
  }
}
