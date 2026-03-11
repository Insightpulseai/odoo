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

const GITHUB_ORG = "Insightpulseai"
const GITHUB_REPO = "odoo"
const SSOT_REF = "ssot/advisor/assessments/microsoft_devops_lifecycle.yaml"

type PhaseSummary = {
  status: "pass" | "fail" | "skip"
  checks: Record<string, boolean | string | number>
  findings_inserted: number
}

/**
 * POST /api/advisor/scans/devops-lifecycle
 *
 * Fans out to the 4 Microsoft DevOps lifecycle phases and checks:
 *   - Plan:    ops.runs count for last 30 days (active development proxy)
 *   - Develop: GitHub branch protection + CODEOWNERS (reuses github scan logic)
 *   - Deliver: VERCEL_TOKEN env var presence (Vercel CI gated proxy)
 *   - Operate: ops.advisor_findings open high-severity items older than 24h
 *
 * Returns { scan_id, phases: { plan, develop, deliver, operate }, findings_count }
 */
export async function POST(req: NextRequest) {
  const rid = getOrCreateRequestId(req.headers.get("x-request-id"))
  const hdrs = correlationHeaders(rid)

  if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
    return NextResponse.json({ error: "Supabase not configured" }, { status: 503, headers: hdrs })
  }

  const GITHUB_TOKEN = process.env.GITHUB_TOKEN ?? ""
  const VERCEL_TOKEN = process.env.VERCEL_TOKEN ?? ""

  try {
    // Create advisor_scans row with provider: devops_lifecycle
    const scanRes = await fetch(`${SUPABASE_URL}/rest/v1/ops.advisor_scans`, {
      method: "POST",
      headers: { ...supabaseHeaders(), Prefer: "return=representation" },
      body: JSON.stringify({
        provider: "devops_lifecycle",
        status: "running",
      }),
    })
    if (!scanRes.ok) {
      const text = await scanRes.text()
      return NextResponse.json({ error: text }, { status: scanRes.status, headers: hdrs })
    }
    const [scan] = await scanRes.json()
    const scanId: string = scan.id

    const allFindings: Array<{
      scan_id: string
      pillar: string
      severity: string
      title: string
      description?: string
      resource_ref?: string
      evidence_json?: object
      recommendation?: string
      citation_url?: string
    }> = []

    const phases: Record<string, PhaseSummary> = {
      plan: { status: "pass", checks: {}, findings_inserted: 0 },
      develop: { status: "pass", checks: {}, findings_inserted: 0 },
      deliver: { status: "pass", checks: {}, findings_inserted: 0 },
      operate: { status: "pass", checks: {}, findings_inserted: 0 },
    }

    // -------------------------------------------------------------------------
    // PLAN PHASE — check ops.runs count for last 30 days
    // -------------------------------------------------------------------------
    try {
      const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString()
      const runsRes = await fetch(
        `${SUPABASE_URL}/rest/v1/ops.runs?created_at=gte.${encodeURIComponent(thirtyDaysAgo)}&select=id`,
        { headers: { ...supabaseHeaders(), Prefer: "count=exact" } }
      )
      let recentRunCount = 0
      if (runsRes.ok) {
        const contentRange = runsRes.headers.get("content-range")
        // content-range header format: 0-N/TOTAL or */TOTAL
        if (contentRange) {
          const total = parseInt(contentRange.split("/")[1] ?? "0", 10)
          recentRunCount = isNaN(total) ? 0 : total
        } else {
          const data = await runsRes.json()
          recentRunCount = Array.isArray(data) ? data.length : 0
        }
      }
      phases.plan.checks.recent_run_count = recentRunCount

      if (recentRunCount < 5) {
        phases.plan.status = "fail"
        const finding = {
          scan_id: scanId,
          pillar: "ops_excellence",
          severity: recentRunCount === 0 ? "high" : "medium",
          title:
            recentRunCount === 0
              ? "No active development runs detected in last 30 days"
              : `Low development cadence: only ${recentRunCount} run(s) in last 30 days`,
          description:
            "The Plan phase check uses ops.runs count as a proxy for active development activity. Low run counts may indicate stalled delivery or missing observability.",
          evidence_json: {
            recent_run_count: recentRunCount,
            window_days: 30,
            ssot_ref: SSOT_REF,
          },
          recommendation:
            "Ensure development runs are being logged to ops.runs. Review delivery cadence.",
          citation_url:
            "https://learn.microsoft.com/en-us/devops/plan/what-is-planning",
        }
        allFindings.push(finding)
        phases.plan.findings_inserted += 1
      }
    } catch {
      phases.plan.status = "fail"
      phases.plan.checks.error = "Failed to query ops.runs"
    }

    // -------------------------------------------------------------------------
    // DEVELOP PHASE — GitHub branch protection + CODEOWNERS
    // Requires GITHUB_TOKEN; emit KEY_MISSING finding if absent
    // -------------------------------------------------------------------------
    if (!GITHUB_TOKEN) {
      phases.develop.status = "fail"
      phases.develop.checks.github_token = "missing"
      allFindings.push({
        scan_id: scanId,
        pillar: "ops_excellence",
        severity: "high",
        title: "Develop phase skipped: GITHUB_TOKEN not configured",
        description:
          "GITHUB_TOKEN is required to check branch protection and CODEOWNERS for the Develop phase.",
        evidence_json: {
          error: "KEY_MISSING",
          key: "GITHUB_TOKEN",
          ssot_ref: "ssot/integrations/github_features.yaml",
        },
        recommendation:
          "Set GITHUB_TOKEN in the runtime environment. See ssot/integrations/github_features.yaml.",
      })
      phases.develop.findings_inserted += 1
    } else {
      const githubHeaders = {
        Authorization: `Bearer ${GITHUB_TOKEN}`,
        Accept: "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
      }

      // Branch protection
      const branchProtRes = await fetch(
        `https://api.github.com/repos/${GITHUB_ORG}/${GITHUB_REPO}/branches/main/protection`,
        { headers: githubHeaders }
      )
      const branchProtected = branchProtRes.status === 200
      phases.develop.checks.branch_protection = branchProtected

      if (!branchProtected) {
        phases.develop.status = "fail"
        allFindings.push({
          scan_id: scanId,
          pillar: "ops_excellence",
          severity: "high",
          title: "main branch not protected (Develop phase)",
          description:
            "Branch protection is not configured on main, allowing unreviewed direct pushes.",
          resource_ref: `github.com/${GITHUB_ORG}/${GITHUB_REPO}/tree/main`,
          evidence_json: { http_status: branchProtRes.status, ssot_ref: SSOT_REF },
          recommendation: "Enable branch protection rules in Repository Settings → Branches.",
          citation_url:
            "https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches",
        })
        phases.develop.findings_inserted += 1
      }

      // CODEOWNERS
      const codeownersRes = await fetch(
        `https://api.github.com/repos/${GITHUB_ORG}/${GITHUB_REPO}/contents/.github/CODEOWNERS`,
        { headers: githubHeaders }
      )
      const codeownersExists = codeownersRes.status === 200
      phases.develop.checks.codeowners_exists = codeownersExists

      if (!codeownersExists) {
        phases.develop.status = "fail"
        allFindings.push({
          scan_id: scanId,
          pillar: "ops_excellence",
          severity: "medium",
          title: "CODEOWNERS file missing (Develop phase)",
          description:
            "No CODEOWNERS file found at .github/CODEOWNERS. Code ownership is undefined.",
          resource_ref: `github.com/${GITHUB_ORG}/${GITHUB_REPO}/blob/main/.github/CODEOWNERS`,
          evidence_json: { http_status: codeownersRes.status, ssot_ref: SSOT_REF },
          recommendation: "Create a .github/CODEOWNERS file mapping paths to responsible teams.",
          citation_url:
            "https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners",
        })
        phases.develop.findings_inserted += 1
      }
    }

    // -------------------------------------------------------------------------
    // DELIVER PHASE — VERCEL_TOKEN presence (proxy for Vercel CI gated)
    // -------------------------------------------------------------------------
    const vercelConfigured = !!VERCEL_TOKEN
    phases.deliver.checks.vercel_token_present = vercelConfigured

    if (!vercelConfigured) {
      phases.deliver.status = "fail"
      allFindings.push({
        scan_id: scanId,
        pillar: "ops_excellence",
        severity: "high",
        title: "Deliver phase: VERCEL_TOKEN not configured",
        description:
          "VERCEL_TOKEN is not present in the environment. This is used as a proxy for Vercel CI delivery gating.",
        evidence_json: {
          error: "KEY_MISSING",
          key: "VERCEL_TOKEN",
          ssot_ref: SSOT_REF,
        },
        recommendation:
          "Set VERCEL_TOKEN in the runtime environment to enable Vercel CI delivery checks.",
        citation_url: "https://vercel.com/docs/rest-api",
      })
      phases.deliver.findings_inserted += 1
    }

    // -------------------------------------------------------------------------
    // OPERATE PHASE — open high-severity findings older than 24h
    // -------------------------------------------------------------------------
    try {
      const twentyFourHoursAgo = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString()
      const openFindingsRes = await fetch(
        `${SUPABASE_URL}/rest/v1/ops.advisor_findings?status=eq.open&severity=in.(critical,high)&created_at=lt.${encodeURIComponent(twentyFourHoursAgo)}&select=id,title,severity,pillar,created_at&limit=10`,
        { headers: supabaseHeaders() }
      )

      let staleHighFindings: Array<{ id: string; title: string; severity: string; pillar: string; created_at: string }> = []
      if (openFindingsRes.ok) {
        staleHighFindings = await openFindingsRes.json()
      }
      phases.operate.checks.stale_high_severity_findings = staleHighFindings.length

      if (staleHighFindings.length > 0) {
        phases.operate.status = "fail"
        allFindings.push({
          scan_id: scanId,
          pillar: "reliability",
          severity: staleHighFindings.some((f) => f.severity === "critical") ? "critical" : "high",
          title: `${staleHighFindings.length} unresolved high/critical finding(s) older than 24h`,
          description:
            "Open high or critical severity advisor findings have not been resolved or dismissed within 24 hours.",
          evidence_json: {
            stale_findings: staleHighFindings,
            threshold_hours: 24,
            ssot_ref: SSOT_REF,
          },
          recommendation:
            "Review and resolve or dismiss open high/critical findings in the advisor dashboard.",
          citation_url:
            "https://learn.microsoft.com/en-us/devops/operate/what-is-monitoring",
        })
        phases.operate.findings_inserted += 1
      }
    } catch {
      phases.operate.status = "fail"
      phases.operate.checks.error = "Failed to query ops.advisor_findings"
    }

    // Insert all findings
    if (allFindings.length > 0) {
      const findingsRes = await fetch(`${SUPABASE_URL}/rest/v1/ops.advisor_findings`, {
        method: "POST",
        headers: { ...supabaseHeaders(), Prefer: "return=minimal" },
        body: JSON.stringify(allFindings),
      })
      if (!findingsRes.ok) {
        const text = await findingsRes.text()
        return NextResponse.json({ error: text }, { status: findingsRes.status, headers: hdrs })
      }
    }

    // Update scan to completed
    const updateRes = await fetch(
      `${SUPABASE_URL}/rest/v1/ops.advisor_scans?id=eq.${scanId}`,
      {
        method: "PATCH",
        headers: { ...supabaseHeaders(), Prefer: "return=minimal" },
        body: JSON.stringify({
          status: "completed",
          finished_at: new Date().toISOString(),
          summary_json: {
            phases: {
              plan: { status: phases.plan.status, checks: phases.plan.checks },
              develop: { status: phases.develop.status, checks: phases.develop.checks },
              deliver: { status: phases.deliver.status, checks: phases.deliver.checks },
              operate: { status: phases.operate.status, checks: phases.operate.checks },
            },
            findings_count: allFindings.length,
            ssot_ref: SSOT_REF,
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
        phases: {
          plan: { status: phases.plan.status, checks: phases.plan.checks },
          develop: { status: phases.develop.status, checks: phases.develop.checks },
          deliver: { status: phases.deliver.status, checks: phases.deliver.checks },
          operate: { status: phases.operate.status, checks: phases.operate.checks },
        },
        findings_count: allFindings.length,
      },
      { status: 200, headers: hdrs }
    )
  } catch (err) {
    return NextResponse.json({ error: String(err) }, { status: 500, headers: hdrs })
  }
}
