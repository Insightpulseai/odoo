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

/**
 * POST /api/advisor/scans/github
 *
 * Runs a GitHub security and governance scan against the Insightpulseai/odoo repo.
 * Checks:
 *   - Dependabot alerts enabled
 *   - Secret scanning status
 *   - Push protection status
 *   - Branch protection on main
 *   - Required status checks include ci/lint
 *   - CODEOWNERS file exists
 *
 * Returns { scan_id, findings_count, findings }
 */
export async function POST(req: NextRequest) {
  const rid = getOrCreateRequestId(req.headers.get("x-request-id"))
  const hdrs = correlationHeaders(rid)

  if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
    return NextResponse.json({ error: "Supabase not configured" }, { status: 503, headers: hdrs })
  }

  const GITHUB_TOKEN = process.env.GITHUB_TOKEN ?? ""
  if (!GITHUB_TOKEN) {
    return NextResponse.json(
      {
        error: "KEY_MISSING",
        key: "GITHUB_TOKEN",
        ssot_ref: "ssot/integrations/github_features.yaml",
      },
      { status: 503, headers: hdrs }
    )
  }

  try {
    // 1. Create advisor_scans row
    const scanRes = await fetch(`${SUPABASE_URL}/rest/v1/ops.advisor_scans`, {
      method: "POST",
      headers: { ...supabaseHeaders(), Prefer: "return=representation" },
      body: JSON.stringify({
        provider: "github",
        status: "running",
      }),
    })
    if (!scanRes.ok) {
      const text = await scanRes.text()
      return NextResponse.json({ error: text }, { status: scanRes.status, headers: hdrs })
    }
    const [scan] = await scanRes.json()
    const scanId: string = scan.id

    const githubHeaders = {
      Authorization: `Bearer ${GITHUB_TOKEN}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
    }

    const findings: Array<{
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
    const checkResults: Record<string, boolean | string> = {}

    // 2a. Check Dependabot alerts enabled (204 = enabled, 404 = disabled)
    const dependabotRes = await fetch(
      `https://api.github.com/repos/${GITHUB_ORG}/${GITHUB_REPO}/vulnerability-alerts`,
      { headers: githubHeaders }
    )
    const dependabotEnabled = dependabotRes.status === 204
    checkResults.dependabot_enabled = dependabotEnabled
    if (!dependabotEnabled) {
      findings.push({
        scan_id: scanId,
        pillar: "security",
        severity: "high",
        title: "Dependabot alerts disabled",
        description: "Dependabot vulnerability alerts are not enabled for this repository.",
        resource_ref: `github.com/${GITHUB_ORG}/${GITHUB_REPO}`,
        evidence_json: { http_status: dependabotRes.status },
        recommendation: "Enable via GitHub Security tab",
        citation_url: "https://docs.github.com/en/code-security/dependabot",
      })
    }

    // 2b. Check secret scanning and push protection
    const repoRes = await fetch(
      `https://api.github.com/repos/${GITHUB_ORG}/${GITHUB_REPO}`,
      { headers: githubHeaders }
    )
    let secretScanningActive = false
    let pushProtectionEnabled = false
    if (repoRes.ok) {
      const repoData = await repoRes.json()
      const secAnalysis = repoData?.security_and_analysis ?? {}
      secretScanningActive =
        secAnalysis?.secret_scanning?.status === "enabled"
      pushProtectionEnabled =
        secAnalysis?.secret_scanning_push_protection?.status === "enabled"
      checkResults.secret_scanning_active = secretScanningActive
      checkResults.push_protection_enabled = pushProtectionEnabled
    } else {
      checkResults.secret_scanning_active = false
      checkResults.push_protection_enabled = false
    }

    if (!secretScanningActive) {
      findings.push({
        scan_id: scanId,
        pillar: "security",
        severity: "critical",
        title: "Secret scanning not active",
        description:
          "GitHub secret scanning is not enabled. Leaked credentials may go undetected.",
        resource_ref: `github.com/${GITHUB_ORG}/${GITHUB_REPO}`,
        evidence_json: {
          security_and_analysis: repoRes.ok
            ? (await repoRes.clone().json().catch(() => null))
                ?.security_and_analysis ?? null
            : null,
          http_status: repoRes.status,
        },
        recommendation: "Enable secret scanning in repository Security settings.",
        citation_url: "https://docs.github.com/en/code-security/secret-scanning",
      })
    }

    if (!pushProtectionEnabled) {
      findings.push({
        scan_id: scanId,
        pillar: "security",
        severity: "high",
        title: "Push protection not enabled",
        description:
          "Secret scanning push protection is disabled. Secrets may be pushed before detection.",
        resource_ref: `github.com/${GITHUB_ORG}/${GITHUB_REPO}`,
        evidence_json: { push_protection_status: "disabled" },
        recommendation:
          "Enable push protection under Repository Settings → Code security and analysis.",
        citation_url:
          "https://docs.github.com/en/code-security/secret-scanning/push-protection-for-repositories-and-organizations",
      })
    }

    // 2c. Check branch protection on main
    const branchProtRes = await fetch(
      `https://api.github.com/repos/${GITHUB_ORG}/${GITHUB_REPO}/branches/main/protection`,
      { headers: githubHeaders }
    )
    const branchProtected = branchProtRes.status === 200
    checkResults.branch_protection = branchProtected

    let branchProtData: Record<string, unknown> | null = null
    if (branchProtected) {
      branchProtData = await branchProtRes.json()
    }

    if (!branchProtected) {
      findings.push({
        scan_id: scanId,
        pillar: "ops_excellence",
        severity: "high",
        title: "main branch not protected",
        description:
          "The main branch has no branch protection rules configured.",
        resource_ref: `github.com/${GITHUB_ORG}/${GITHUB_REPO}/tree/main`,
        evidence_json: { http_status: branchProtRes.status },
        recommendation:
          "Enable branch protection rules for main in Repository Settings → Branches.",
        citation_url:
          "https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches",
      })
    }

    // 2d. Check required status checks include ci/lint
    let ciLintRequired = false
    if (branchProtected && branchProtData) {
      const contexts: string[] =
        (branchProtData?.required_status_checks as { contexts?: string[] } | null)
          ?.contexts ?? []
      ciLintRequired = contexts.includes("ci/lint")
      checkResults.ci_lint_required = ciLintRequired
    } else {
      checkResults.ci_lint_required = false
    }

    if (!ciLintRequired) {
      findings.push({
        scan_id: scanId,
        pillar: "ops_excellence",
        severity: "medium",
        title: "ci/lint not a required status check",
        description:
          "The ci/lint check is not in the required status checks for the main branch.",
        resource_ref: `github.com/${GITHUB_ORG}/${GITHUB_REPO}/tree/main`,
        evidence_json: {
          required_contexts: branchProtected
            ? (branchProtData?.required_status_checks as { contexts?: string[] } | null)
                ?.contexts ?? []
            : [],
        },
        recommendation:
          "Add ci/lint to the required status checks in branch protection settings.",
        citation_url:
          "https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-required-status-checks",
      })
    }

    // 2e. Check CODEOWNERS file exists
    const codeownersRes = await fetch(
      `https://api.github.com/repos/${GITHUB_ORG}/${GITHUB_REPO}/contents/.github/CODEOWNERS`,
      { headers: githubHeaders }
    )
    const codeownersExists = codeownersRes.status === 200
    checkResults.codeowners_exists = codeownersExists

    if (!codeownersExists) {
      findings.push({
        scan_id: scanId,
        pillar: "ops_excellence",
        severity: "medium",
        title: "CODEOWNERS file missing",
        description:
          "No CODEOWNERS file found at .github/CODEOWNERS. Code ownership is undefined.",
        resource_ref: `github.com/${GITHUB_ORG}/${GITHUB_REPO}/blob/main/.github/CODEOWNERS`,
        evidence_json: { http_status: codeownersRes.status },
        recommendation:
          "Create a .github/CODEOWNERS file mapping paths to responsible teams.",
        citation_url:
          "https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners",
      })
    }

    // 3. Insert findings into ops.advisor_findings
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

    // 4. Update scan to completed with summary_json
    const updateRes = await fetch(
      `${SUPABASE_URL}/rest/v1/ops.advisor_scans?id=eq.${scanId}`,
      {
        method: "PATCH",
        headers: { ...supabaseHeaders(), Prefer: "return=representation" },
        body: JSON.stringify({
          status: "completed",
          finished_at: new Date().toISOString(),
          summary_json: {
            checks: checkResults,
            findings_count: findings.length,
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
        findings_count: findings.length,
        findings,
      },
      { status: 200, headers: hdrs }
    )
  } catch (err) {
    return NextResponse.json({ error: String(err) }, { status: 500, headers: hdrs })
  }
}
