# PRD: GitHub Advanced Security Rollout

> Product Requirements Document for staged GHAS adoption.
> Owner: DevOps / Security
> Last updated: 2026-02-22

---

## Problem Statement

The `Insightpulseai/odoo` repo has 195 open Dependabot alerts (8 critical, 87 high)
and no enforced CodeQL or Secret Scanning baseline. Merges are not gated on security
findings. This creates unacceptable supply-chain and secrets exposure risk.

## Goals

1. **Zero secret leaks**: Push protection prevents credential commits before they land.
2. **Critical alert SLA**: Critical Dependabot/CodeQL alerts resolved within 5 business days.
3. **High alert SLA**: High-severity alerts resolved within 15 business days.
4. **Merge quality gate**: No PR merges with open Critical alerts in sensitive paths.

## Non-Goals

- Custom CodeQL queries (Phase 3+)
- Third-party SAST tools (Snyk, SonarQube) — evaluate post Phase 2
- Auto-remediation bots — post Phase 3

## Scope

| Feature | Phase |
|---------|-------|
| Dependabot alerts visible to team | P0 (now) |
| Secret Scanning enabled | P0 |
| Push protection (block secret pushes) | P1 |
| CodeQL baseline (Python, JavaScript, TypeScript) | P1 |
| Merge-blocking on Critical alerts | P2 |
| Merge-blocking on High in sensitive paths | P2 |
| Org-wide rollout + reporting dashboard | P3 |

## Success Metrics

| Metric | Target |
|--------|--------|
| Secret leaks in main branch | 0 |
| Critical vuln TTR | ≤ 5 business days |
| High vuln TTR | ≤ 15 business days |
| CodeQL pass rate on PRs | ≥ 95% |
| GHAS coverage (repos under org) | 100% within 90 days |

## Constraints

- Must run on `ubuntu-latest` GitHub-hosted runners (no self-hosted required)
- Must not add >3 min to PR CI time at P2
- Exception process must be documented and auditable (label + CODEOWNERS)
