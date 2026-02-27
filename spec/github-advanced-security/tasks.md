# Tasks: GHAS Rollout

> Actionable task breakdown. Update status as work completes.
> Last updated: 2026-02-22

---

## Phase 0 — Inventory

| ID | Task | Owner | Status | Evidence |
|----|------|-------|--------|----------|
| T-01 | Enable Dependabot alerts on org | DevOps | ⬜ pending | GitHub Security tab export |
| T-02 | Enable Secret Scanning (alert-only) | DevOps | ⬜ pending | Settings confirmation |
| T-03 | Enable CodeQL (warning-only, no block) | DevOps | ⬜ pending | First CodeQL run log |
| T-04 | Triage existing 195 alerts → assign owners | Security | ⬜ pending | `reports/ghas_inventory_<date>.json` |
| T-05 | Label Critical alerts `security-p0` | Security | ⬜ pending | GitHub alert list export |

## Phase 1 — Enforce

| ID | Task | Owner | Status | Evidence |
|----|------|-------|--------|----------|
| T-06 | Enable Push Protection | DevOps | ⬜ pending | Settings + test push |
| T-07 | Commit `dependabot.yml` (Python, JS, Actions) | Dev | ⬜ pending | File in repo |
| T-08 | Commit `.github/workflows/ghas-gates.yml` (warn-only) | Dev | ⬜ pending | Workflow run |
| T-09 | Close false-positive Dependabot alerts | Dev | ⬜ pending | Alert list delta |
| T-10 | Fix all Critical Dependabot alerts | Dev | ⬜ pending | PRs merged, alerts closed |
| T-11 | Document exception process | DevOps | ⬜ pending | `docs/ops/GHAS_EXCEPTION_PROCESS.md` |

## Phase 2 — Gate

| ID | Task | Owner | Status | Evidence |
|----|------|-------|--------|----------|
| T-12 | Update `ghas-gates.yml` to block on Critical + sensitive-path High | Dev | ⬜ pending | Workflow diff + test PR |
| T-13 | Configure Dependabot auto-merge for patch updates | Dev | ⬜ pending | `dependabot.yml` update |
| T-14 | Remediate all Critical alerts (TTR ≤ 5d) | Dev | ⬜ pending | Alert closure evidence |
| T-15 | First monthly audit evidence bundle | Security | ⬜ pending | `web/docs/evidence/<stamp>/ghas/` |

## Phase 3 — Scale

| ID | Task | Owner | Status | Evidence |
|----|------|-------|--------|----------|
| T-16 | Org-level security policy GitHub setting | DevOps | ⬜ pending | GitHub policy export |
| T-17 | Evaluate org reusable GHAS workflow | Dev | ⬜ pending | ADR in `docs/architecture/` |
| T-18 | Monthly posture report automation | DevOps | ⬜ pending | Report artifact in CI |

---

## Dependencies

- T-06 (Push Protection) must precede T-12 (merge gate)
- T-10 (fix Criticals) must precede T-12 (merge gate) — avoid blocking own team
- T-07 (`dependabot.yml`) must precede T-13 (auto-merge config)
