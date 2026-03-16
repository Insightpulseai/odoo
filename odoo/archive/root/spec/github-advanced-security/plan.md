# Implementation Plan: GHAS Rollout

> Staged rollout plan. Each phase must produce verifiable evidence before the next begins.
> Last updated: 2026-02-22

---

## Phase 0 — Inventory & Quiet Mode (Week 1)

**Goal**: Visibility without blocking anything.

1. Enable Dependabot alerts on `Insightpulseai/odoo` (if not already visible)
2. Enable Secret Scanning in **alert-only** mode (no push protection yet)
3. Enable CodeQL scanning in **warning-only** mode (no merge block)
4. Triage existing 195 Dependabot alerts → assign to owners, label `security-backlog`
5. Produce evidence snapshot: `reports/ghas_inventory_<date>.json`

**Evidence required**: alert counts by severity, language coverage report

---

## Phase 1 — Enforce Secrets + CodeQL Baseline (Week 2-3)

**Goal**: Stop new secrets from entering; establish code scanning baseline.

1. Enable **Push Protection** (secret scanning blocks pushes with detected credentials)
2. Add `dependabot.yml` at repo root (Python, JavaScript/TypeScript, GitHub Actions)
3. Add CodeQL workflow `.github/workflows/ghas-gates.yml`:
   - Languages: `python`, `javascript`, `typescript`
   - Schedule: on push to `main`, on PR to `main`
   - Mode: scan only (no merge block yet)
4. Triage Phase 0 alerts: close false positives, create fix PRs for Critical/High
5. Document exception process in `docs/ops/GHAS_EXCEPTION_PROCESS.md`

**Evidence required**: CodeQL run log, push protection block event (if any), dependabot.yml committed

---

## Phase 2 — Merge Gates (Week 4-6)

**Goal**: Block merges that introduce new Critical/High alerts in sensitive paths.

1. Update `ghas-gates.yml` to **fail the workflow** on:
   - Any new Secret Scanning alert
   - New CodeQL Critical alerts (any path)
   - New CodeQL High alerts in `addons/ipai/`, `supabase/migrations/`, `.github/workflows/`
2. Update branch protection rules (via `infra/policy/branch-protection.yaml` if available)
3. Auto-merge Dependabot PRs for patch-level updates (configure in `dependabot.yml`)
4. Remediate all Critical Dependabot alerts (TTR: 5 days from phase start)
5. First monthly audit: evidence bundle with metrics

**Evidence required**: ghas-gates.yml run showing merge block, Critical alert close list

---

## Phase 3 — Org-Wide Rollout (Month 2)

**Goal**: All repos in `Insightpulseai` org at Phase 2 posture.

1. Create org-level security policy (GitHub Security tab → Policy)
2. Extend `ghas-gates.yml` or create org-level reusable workflow
3. Reporting: monthly GHAS posture report (automated via Actions → artifact)
4. Evaluate custom CodeQL queries for Odoo-specific patterns (e.g., SQL construction)

**Evidence required**: org-level alert dashboard export, posture report artifact

---

## Rollback / Exception

If GHAS gates block critical hotfixes:
1. Add `security-exception` label to PR
2. Get CODEOWNERS approval (documented in PR comment)
3. Merge allowed — alert remains open with 5-day SLA clock
4. Exception logged in `docs/ops/GHAS_EXCEPTIONS_LOG.md`
