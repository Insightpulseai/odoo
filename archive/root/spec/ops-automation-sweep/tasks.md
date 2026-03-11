# Tasks: ops-automation-sweep

**Spec**: ops-automation-sweep
**Version**: 1.0.0

---

## T1: Implement `scripts/automations/sweep_repo.py`

**Owner**: automation agent
**Priority**: P0
**Blocked by**: none

**Acceptance criteria**:
- [ ] Scans all `*.json` for n8n workflow shape (name/nodes/connections keys)
- [ ] Classifies each: `canonical | stray | duplicate | stale_reference | unreferenced`
- [ ] Scans `.sh`, `.py`, `.yml` for n8n references
- [ ] Detects deprecated domain references (`.net`) and old path roots
- [ ] SHA256-hashes each workflow for deduplication
- [ ] Scores staleness and opportunity heuristics
- [ ] Outputs `out/automation_sweep/inventory.json`, `report.md`, `backlog.md`, `patches/*.diff`
- [ ] CLI: `--env`, `--out`, `--apply`, `--verbose`
- [ ] Exit codes: 0=clean, 1=issues found, 2=apply failures
- [ ] No secrets in output (mask any accidental token captures)

---

## T2: Implement `scripts/automations/deploy_n8n_all.py`

**Owner**: automation agent
**Priority**: P0
**Blocked by**: T1 (inventory must exist before deploy)

**Acceptance criteria**:
- [ ] Loads workflow JSONs from `automations/n8n/` (canonical only)
- [ ] Requires `N8N_BASE_URL` + `N8N_API_KEY` env vars (abort if missing)
- [ ] Fetches existing workflow from n8n API by name, computes diff
- [ ] Skips if identical, creates if new, updates if different (idempotent)
- [ ] Supports `--env {dev,stage,prod}` and `--apply` / `--dry-run` (default: dry-run)
- [ ] Emits `out/automation_sweep/deploy_results.json`
- [ ] Exit non-zero if any deploy fails under `--apply`
- [ ] Re-run produces identical output (deterministic)

---

## T3: Add `docs/architecture/AUTOMATIONS_SWEEP.md`

**Owner**: automation agent
**Priority**: P1
**Blocked by**: T1, T2

**Acceptance criteria**:
- [ ] Documents what is scanned (all categories)
- [ ] Lists required env vars for each mode
- [ ] Explains dry-run vs apply behavior
- [ ] Lists common failure modes and fixes
- [ ] Links to spec files

---

## T4: Add `.github/workflows/automation-sweep.yml`

**Owner**: automation agent
**Priority**: P1
**Blocked by**: T1

**Acceptance criteria**:
- [ ] Triggered on PR touching `automations/**`, `scripts/**`, `infra/**`
- [ ] Runs `sweep_repo.py --env stage --out out/automation_sweep --verbose` (no `--apply`)
- [ ] Uploads `inventory.json`, `report.md`, `backlog.md` as CI artifacts
- [ ] Uses only `GITHUB_TOKEN` (no privileged secrets required for audit-only)
- [ ] Exits non-zero if sweep finds critical issues (P0 staleness)

---

## T5: Run sweep dry-run and commit artifacts

**Owner**: automation agent
**Priority**: P0
**Blocked by**: T1

**Acceptance criteria**:
- [ ] `inventory.json` includes all known workflow JSONs (≥28)
- [ ] `report.md` is readable and links to specific files
- [ ] `backlog.md` has ≥5 opportunities with P-tags, ROI, risk, owner, next action
- [ ] `patches/` contains diff suggestions for any stray files found

---

## T6: Extend or document `scripts/n8n-gitops.sh` relationship

**Owner**: automation agent
**Priority**: P2
**Blocked by**: T2

**Acceptance criteria**:
- [ ] Add comment block to `n8n-gitops.sh` documenting what `deploy_n8n_all.py` supplements vs replaces
- [ ] OR integrate `deploy_n8n_all.py` logic into `n8n-gitops.sh` if shell is sufficient
- [ ] No duplicate functionality without justification
