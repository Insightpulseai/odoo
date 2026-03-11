# Implementation Plan: ops-automation-sweep

**Spec**: ops-automation-sweep
**Version**: 1.0.0

---

## Phase 1: Inventory

**Goal**: Discover and classify ALL automation artifacts repo-wide.

**Steps**:
1. Walk repo tree excluding `.git/`, `node_modules/`, `__pycache__/`, `.cache/`, `.gemini/`.
2. Collect all `*.json` files, check for n8n workflow shape (`name`, `nodes`, `connections` keys).
3. Collect all `*.sh`, `*.py`, `*.yml` files referencing n8n URLs, API paths, or workflow imports.
4. SHA256-hash each workflow JSON for deduplication.
5. Classify: `canonical | stray | duplicate | stale_reference | unreferenced`.
6. Map existing script `n8n-gitops.sh` capabilities — determine if extend or supplement.

**Outputs**:
- `inventory.json` (all artifacts with paths, hashes, classifications, references)

**Pass criteria**: All 28+ known workflow JSONs appear in inventory.

---

## Phase 2: Deploy Readiness

**Goal**: Validate workflow JSONs are deployable and credentials placeholders are identified.

**Steps**:
1. Validate JSON schema: each workflow must have `name`, `nodes` (array), `connections` (object).
2. Detect hardcoded URLs or environment-specific values that should be parameterized.
3. Detect credential references in workflow nodes — flag missing credential names.
4. Check `N8N_BASE_URL` and `N8N_API_KEY` availability (env var check, no value read).
5. For each canonical workflow, attempt dry-run diff against live n8n (if env vars available).

**Outputs**:
- Deploy readiness section in `report.md`
- List of workflows with credential gaps

**Pass criteria**: Each workflow validated or flagged with specific reason.

---

## Phase 3: Staleness & Opportunity Detection

**Goal**: Identify automation debt and new automation opportunities.

**Steps**:
1. **Stale detection heuristics**:
   - References to `.net` domains
   - References to moved path roots (`/n8n/`, `/mcp/` root-level)
   - GitHub Actions not referenced by any calling workflow
   - Scripts that replicate CI job behavior (fetch → push pattern)
2. **Opportunity scoring heuristics**:
   - Multi-step scripts with fetch → transform → notify pattern (n8n candidate)
   - Periodic bash cron jobs → scheduled n8n workflows
   - `psql` / Supabase calls in scripts → event-driven n8n triggers
3. Score each opportunity: ROI (H/M/L), Risk (H/M/L), Effort (days).
4. Rank by P0 (immediate value, low risk) → P1 → P2.

**Outputs**:
- `backlog.md` with ranked opportunities
- `patches/*.diff` for stale file moves/fixes

**Pass criteria**: ≥5 opportunities identified and ranked.

---

## Phase 4: Apply (Optional, `--apply` flag)

**Goal**: Deploy all eligible canonical workflows idempotently.

**Steps**:
1. Confirm `--apply` flag passed (abort if not).
2. For each canonical workflow in `automations/n8n/`:
   a. GET existing workflow from n8n API by name match.
   b. If not exists: POST (create).
   c. If exists: compute JSON diff. Skip if identical. PUT (update) if different.
3. Emit `deploy_results.json` with per-workflow outcome.
4. Exit non-zero if any deploy fails.

**Outputs**:
- `deploy_results.json`
- Updated `report.md` with deploy section

**Pass criteria**: All deploys idempotent (re-running produces no changes).

---

## Phase 5: PR

**Goal**: Commit all artifacts and open PR for review.

**Steps**:
1. Stage new files: spec/, scripts/automations/, docs/architecture/, out/automation_sweep/, .github/workflows/automation-sweep.yml.
2. Commit: `feat(automations): repo-wide n8n sweep + deploy tooling + stale automation backlog`.
3. Push branch and open PR with `report.md` as PR body summary.
4. List any skipped deploys (missing tokens) in PR description.

**Pass criteria**: PR created, CI automation-sweep.yml runs audit-only on PR.

---

## File Map

| File | Phase | Action |
|------|-------|--------|
| `spec/ops-automation-sweep/constitution.md` | 0 | Create ✅ |
| `spec/ops-automation-sweep/prd.md` | 0 | Create ✅ |
| `spec/ops-automation-sweep/plan.md` | 0 | Create ✅ |
| `spec/ops-automation-sweep/tasks.md` | 0 | Create ✅ |
| `scripts/automations/sweep_repo.py` | 1-3 | Implement |
| `scripts/automations/deploy_n8n_all.py` | 2,4 | Implement |
| `docs/architecture/AUTOMATIONS_SWEEP.md` | 5 | Create |
| `.github/workflows/automation-sweep.yml` | 5 | Create |
| `out/automation_sweep/inventory.json` | 1 | Generated |
| `out/automation_sweep/report.md` | 1-4 | Generated |
| `out/automation_sweep/backlog.md` | 3 | Generated |
| `out/automation_sweep/patches/*.diff` | 3 | Generated |
