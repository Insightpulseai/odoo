# Constitution: GitHub Advanced Security (GHAS) Rollout

> Non-negotiable governance rules for the InsightPulse AI GHAS rollout.
> Edit only via PR with CODEOWNERS approval.
> Last updated: 2026-02-22

---

## Non-Negotiables

### R-01 — Default-On for Critical Repos

GHAS features (Code Scanning, Secret Scanning, Dependabot) must be enabled on
`Insightpulseai/odoo` before any other repo. All new repos created under the
`Insightpulseai` org inherit this posture automatically.

### R-02 — Merge-Blocking on Critical / High

PRs **must not merge** if they introduce:
- Any Secret Scanning alert (regardless of severity)
- A Critical-severity CodeQL alert
- A High-severity alert in paths: `addons/ipai/`, `supabase/migrations/`, `.github/workflows/`

Exception process: written justification in PR + `security-exception` label + CODEOWNERS sign-off.

### R-03 — No Secrets in Repo (Ever)

Secret scanning push protection is enabled. Force-pushing to bypass is forbidden.
No CI job may print secrets, tokens, or passwords — even partially.

### R-04 — Dependabot Always On

`dependabot.yml` must exist. Auto-merge is permitted for patch-level non-security
updates only. Major/minor updates require human review.

### R-05 — Evidence Required

All GHAS gate runs produce a JSON evidence artifact saved to
`web/docs/evidence/<YYYYMMDD-HHMM+0800>/ghas/` and referenced in PR description.

### R-06 — No UI-Only Gates

All enforcement is via GitHub Actions workflows and branch protection rules configured
as code (`infra/policy/`). UI-only changes to org security settings must be mirrored
in `infra/policy/` within 24 hours.

### R-07 — Audit Cadence

Security posture reviewed monthly. Evidence bundle required for each audit:
- Dependabot alert close rate
- CodeQL scan pass rate
- Secret scanning block rate
