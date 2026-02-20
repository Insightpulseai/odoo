# Dependabot Triage Policy (Monorepo)

## Objective

Prevent repo-wide vulnerability noise from blocking unrelated PRs while ensuring high-risk vulnerabilities are remediated on a predictable cadence.

## Triage Rules

- Vulnerabilities are addressed in dedicated PRs scoped to the affected app/package area.
- PRs unrelated to `web/**`, `sandbox/**/.artifacts/**`, or `package.json` surfaces must not be blocked by repo-wide vulnerability counts.
- Critical/High findings: target remediation PR within 7 days.
- Moderate/Low: batch weekly.

## Scope Isolation

Vulnerability remediation PRs must include:
- Affected package lock diff
- Minimal runtime verification notes
- Rollback note (lockfile revert)

## CI Guidance

- Security scans should be path-filtered to only run when JS dependency surfaces change.
- Do not introduce global "fail on any vuln" gates for a 2.2GB monorepo without path filters.

## Current Status (2026-02-20)

**Repo-wide count:** 184 vulnerabilities (6 critical, 86 high, 68 moderate, 24 low)

**Known surfaces:**
- `web/` - Node.js/TypeScript packages (primary surface)
- `sandbox/` - Development artifacts (not deployed)
- Root `package.json` - Workspace metadata

**Remediation Strategy:**
1. Path-filter security scans to `web/**/*.json`, `package*.json`
2. Create focused remediation PRs per workspace package
3. Document acceptance criteria for each severity level
4. Establish weekly batch process for moderate/low findings

## Severity Response Times

| Severity | Target Remediation | Batching Allowed | Blocker for Production Deploy |
|----------|-------------------|------------------|-------------------------------|
| Critical | 24 hours | No | Yes |
| High | 7 days | No | Yes |
| Moderate | 30 days | Yes (weekly batch) | No |
| Low | 90 days | Yes (monthly batch) | No |

## Verification Requirements

All vulnerability remediation PRs must include:
- [ ] Package lock diff showing resolved dependency
- [ ] `npm audit` or `pnpm audit` output showing reduced count
- [ ] Runtime verification (build passes, app starts)
- [ ] Rollback note (lockfile revert command)
- [ ] No unrelated changes (scope limited to dependency update)

## References

- GitHub Security: https://github.com/Insightpulseai/odoo/security/dependabot
- Path filtering: `.github/workflows/*-security.yml` (future)
- Vulnerability tracking: GitHub Security tab (projects/labels for severity)
