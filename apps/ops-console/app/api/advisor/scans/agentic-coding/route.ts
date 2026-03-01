import { NextRequest, NextResponse } from "next/server"
import { getOrCreateRequestId, correlationHeaders } from "@/lib/http/correlation"

const SUPABASE_URL = process.env.SUPABASE_URL ?? process.env.NEXT_PUBLIC_SUPABASE_URL ?? ""
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY ?? ""

function supabaseHeaders() {
  return {
    apikey: SUPABASE_SERVICE_ROLE_KEY,
    Authorization: `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
    "Content-Type": "application/json",
  }
}

const RUBRIC_ID = "agentic_coding"

type RunEvent = {
  event_id: string
  run_id: string
  level?: string
  message?: string
  payload?: unknown
  created_at?: string
}

type DimensionScore = {
  dimension: string
  score: number
  breakdown: Record<string, unknown>
}

/**
 * POST /api/advisor/scans/agentic-coding
 *
 * Scores the last 20 ops.run_events against the agentic_coding rubric (5 dimensions).
 * Inserts scores into ops.advisor_scores (try/catch — table may not exist yet).
 * Inserts findings into ops.advisor_findings when total score < 10.
 *
 * Returns { scan_id, total_score, dimension_scores, findings }
 */
export async function POST(req: NextRequest) {
  const rid = getOrCreateRequestId(req.headers.get("x-request-id"))
  const hdrs = correlationHeaders(rid)

  if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
    return NextResponse.json({ error: "Supabase not configured" }, { status: 503, headers: hdrs })
  }

  try {
    // 1. Create advisor_scans row with provider: agentic_coding
    const scanRes = await fetch(`${SUPABASE_URL}/rest/v1/ops.advisor_scans`, {
      method: "POST",
      headers: { ...supabaseHeaders(), Prefer: "return=representation" },
      body: JSON.stringify({
        provider: "agentic_coding",
        status: "running",
      }),
    })
    if (!scanRes.ok) {
      const text = await scanRes.text()
      return NextResponse.json({ error: text }, { status: scanRes.status, headers: hdrs })
    }
    const [scan] = await scanRes.json()
    const scanId: string = scan.id

    // 2. Read last 20 ops.run_events ordered by created_at DESC
    const eventsRes = await fetch(
      `${SUPABASE_URL}/rest/v1/ops.run_events?order=created_at.desc&limit=20`,
      { headers: supabaseHeaders() }
    )

    let runEvents: RunEvent[] = []
    if (eventsRes.ok) {
      runEvents = await eventsRes.json()
    }

    // 3. Compute rubric scores across 5 dimensions
    const messageTexts = runEvents
      .map((e) => (e.message ?? "").toLowerCase())
      .join(" ")

    // planning_quality (0-3): presence of PLAN phase messages
    const planningMatches = runEvents.filter(
      (e) =>
        (e.level ?? "").toLowerCase().includes("plan") ||
        (e.message ?? "").toLowerCase().includes("plan") ||
        (e.message ?? "").toLowerCase().includes("planning")
    )
    let planningScore = 0
    if (planningMatches.length >= 3) planningScore = 3
    else if (planningMatches.length === 2) planningScore = 2
    else if (planningMatches.length === 1) planningScore = 1

    // patch_minimality (0-3): placeholder — no automated signal yet
    const patchMinimalityScore = 1

    // test_coverage (0-3): VERIFY phase messages mentioning tests
    const testMatches = runEvents.filter(
      (e) =>
        (e.level ?? "").toLowerCase().includes("verify") ||
        (e.message ?? "").toLowerCase().includes("test") ||
        (e.message ?? "").toLowerCase().includes("verify") ||
        (e.message ?? "").toLowerCase().includes("coverage")
    )
    let testCoverageScore = 0
    if (testMatches.length >= 3) testCoverageScore = 3
    else if (testMatches.length === 2) testCoverageScore = 2
    else if (testMatches.length === 1) testCoverageScore = 1

    // pr_evidence (0-3): PR phase messages
    const prMatches = runEvents.filter(
      (e) =>
        (e.level ?? "").toLowerCase().includes("pr") ||
        (e.message ?? "").toLowerCase().includes(" pr ") ||
        (e.message ?? "").toLowerCase().includes("pull request") ||
        (e.message ?? "").toLowerCase().includes("gh pr")
    )
    let prEvidenceScore = 0
    if (prMatches.length >= 3) prEvidenceScore = 3
    else if (prMatches.length === 2) prEvidenceScore = 2
    else if (prMatches.length === 1) prEvidenceScore = 1

    // audit_trail (0-3): count of runs logged
    const uniqueRunIds = new Set(runEvents.map((e) => e.run_id).filter(Boolean))
    const runCount = uniqueRunIds.size
    let auditTrailScore = 0
    if (runCount === 0) auditTrailScore = 0
    else if (runCount < 5) auditTrailScore = 1
    else if (runCount < 20) auditTrailScore = 2
    else auditTrailScore = 3

    const dimensionScores: DimensionScore[] = [
      {
        dimension: "planning_quality",
        score: planningScore,
        breakdown: {
          matching_events: planningMatches.length,
          sample_messages: planningMatches.slice(0, 3).map((e) => e.message),
        },
      },
      {
        dimension: "patch_minimality",
        score: patchMinimalityScore,
        breakdown: { note: "Placeholder score — no automated signal available yet." },
      },
      {
        dimension: "test_coverage",
        score: testCoverageScore,
        breakdown: {
          matching_events: testMatches.length,
          sample_messages: testMatches.slice(0, 3).map((e) => e.message),
        },
      },
      {
        dimension: "pr_evidence",
        score: prEvidenceScore,
        breakdown: {
          matching_events: prMatches.length,
          sample_messages: prMatches.slice(0, 3).map((e) => e.message),
        },
      },
      {
        dimension: "audit_trail",
        score: auditTrailScore,
        breakdown: {
          unique_run_ids: runCount,
          total_events: runEvents.length,
        },
      },
    ]

    const totalScore = dimensionScores.reduce((sum, d) => sum + d.score, 0)

    // 4. Insert ops.advisor_scores rows — wrapped in try/catch (table may not exist yet)
    try {
      const scoreRows = dimensionScores.map((d) => ({
        scan_id: scanId,
        rubric_id: RUBRIC_ID,
        dimension: d.dimension,
        score: d.score,
        breakdown_json: d.breakdown,
      }))
      await fetch(`${SUPABASE_URL}/rest/v1/ops.advisor_scores`, {
        method: "POST",
        headers: { ...supabaseHeaders(), Prefer: "return=minimal" },
        body: JSON.stringify(scoreRows),
      })
    } catch {
      // ops.advisor_scores table not yet created — will be added in migration PR C
    }

    // 5. Insert findings based on total score
    const findings: Array<{
      scan_id: string
      pillar: string
      severity: string
      title: string
      description?: string
      evidence_json?: object
      recommendation?: string
      citation_url?: string
    }> = []

    if (totalScore < 6) {
      findings.push({
        scan_id: scanId,
        pillar: "ops_excellence",
        severity: "high",
        title: "Agentic coding rubric below Developing band (score < 6)",
        description: `Total agentic coding rubric score is ${totalScore}/15, which is below the Developing band threshold of 6. Improvements needed across planning, test coverage, PR evidence, and audit trail.`,
        evidence_json: {
          total_score: totalScore,
          dimension_scores: dimensionScores,
          rubric_id: RUBRIC_ID,
          ssot_ref: "ssot/advisor/rubrics/agentic_coding.yaml",
        },
        recommendation:
          "Increase score by ensuring PLAN phase is logged in run_events, adding test verification steps, emitting PR-linked events, and maintaining consistent run logging.",
        citation_url: undefined,
      })
    } else if (totalScore < 10) {
      findings.push({
        scan_id: scanId,
        pillar: "ops_excellence",
        severity: "medium",
        title: `Agentic coding rubric in Developing band (score ${totalScore} < 10)`,
        description: `Total agentic coding rubric score is ${totalScore}/15, which is in the Developing band. Score is above threshold but below Proficient (10+).`,
        evidence_json: {
          total_score: totalScore,
          dimension_scores: dimensionScores,
          rubric_id: RUBRIC_ID,
          ssot_ref: "ssot/advisor/rubrics/agentic_coding.yaml",
        },
        recommendation:
          "Focus on dimensions scoring below 2 to reach the Proficient band.",
        citation_url: undefined,
      })
    }

    // 6. Insert findings into ops.advisor_findings
    if (findings.length > 0) {
      const findingsRes = await fetch(`${SUPABASE_URL}/rest/v1/ops.advisor_findings`, {
        method: "POST",
        headers: { ...supabaseHeaders(), Prefer: "return=representation" },
        body: JSON.stringify(findings),
      })
      if (!findingsRes.ok) {
        const text = await findingsRes.text()
        return NextResponse.json({ error: text }, { status: findingsRes.status, headers: hdrs })
      }
    }

    // 7. Update scan to completed
    const updateRes = await fetch(
      `${SUPABASE_URL}/rest/v1/ops.advisor_scans?id=eq.${scanId}`,
      {
        method: "PATCH",
        headers: { ...supabaseHeaders(), Prefer: "return=minimal" },
        body: JSON.stringify({
          status: "completed",
          finished_at: new Date().toISOString(),
          summary_json: {
            total_score: totalScore,
            max_score: 15,
            dimension_scores: dimensionScores,
            findings_count: findings.length,
            run_events_analyzed: runEvents.length,
          },
        }),
      }
    )
    if (!updateRes.ok) {
      const text = await updateRes.text()
      return NextResponse.json({ error: text }, { status: updateRes.status, headers: hdrs })
    }

    return NextResponse.json(
      {
        scan_id: scanId,
        total_score: totalScore,
        dimension_scores: dimensionScores,
        findings,
      },
      { status: 200, headers: hdrs }
    )
  } catch (err) {
    return NextResponse.json({ error: String(err) }, { status: 500, headers: hdrs })
  }
}
