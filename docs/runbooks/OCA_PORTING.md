# OCA Module Porting Runbook

**Target**: Odoo 19.0 CE
**SSOT**: `ssot/odoo/oca_repos.yaml`
**CI gate**: `.github/workflows/oca-19-readiness-report.yml`
**Scanner**: `scripts/ci/scan_oca_repos.py`

---

## Rules (enforced by CI)

1. **No empty repos in `addons_path`** — repos with 0 modules waste discovery time and fail the gate (`exit 2`).
2. **No 18.0-pinned repos in `addons_path`** — repos on branch `18.0` are `status: blocked` and must be ported first.
3. **All `ssot/odoo/oca_repos.yaml` entries must resolve to `ok`, `pinned`, `empty`, or `blocked`** — never `unknown`.
4. **`_git_aggregated` is acceptable** if and only if all manifest versions are `19.0.x` (scanner validates automatically).

---

## Current Status (as of 2026-02-28)

| Status | Repos | Notes |
|--------|-------|-------|
| `pinned` (19.0 branch) | mail, manufacture, payroll | Cleanest state |
| `ok` (_git_aggregated + 19.0 manifests) | 26 repos, ~190 modules | Acceptable |
| `blocked` (18.0 branch, not in addons_path) | bank-statement-import, server-env | Port required |
| `empty` (0 modules, removed from addons_path) | automation, contract, hr-expense, social, spreadsheet | Never activate |

---

## Running the Scanner Locally

```bash
# Full report with JSON artifact
python3 scripts/ci/scan_oca_repos.py --json /tmp/oca_readiness.json

# Non-fatal (warnings only) — useful during porting
python3 scripts/ci/scan_oca_repos.py --warn-only
```

**Exit codes**:
- `0` — all repos clean
- `1` — blocked repos present (warn-only mode: exits `0`)
- `2` — empty repos found in scan (always fatal)

---

## Porting a Blocked Repo (18.0 → 19.0)

### Option A: OCA official port (preferred)

```bash
# Check if 19.0 branch exists upstream
git ls-remote --heads https://github.com/OCA/<repo>.git 19.0

# If it exists, update submodule to point to 19.0
cd addons/oca/<repo>
git fetch origin
git checkout origin/19.0
cd ../../../
git add addons/oca/<repo>
git commit -m "chore(oca): pin <repo> to OCA 19.0 branch"
```

### Option B: Use `oca-port` CLI (if no official 19.0 port yet)

```bash
pip install oca-port
oca-port --source-branch 18.0 --target-branch 19.0 --addon <module_name> --repo OCA/<repo>
```

### After porting

1. Update `ssot/odoo/oca_repos.yaml`:
   - Set `branch: "19.0"` (or `_git_aggregated` if using aggregated checkout)
   - Set `status: pinned` or `status: ok`
   - Clear `notes` of the blocking reason
2. Add the repo to `addons_path` in `config/dev/odoo.conf`, `config/prod/odoo.conf`, `config/stage/odoo.conf`
3. Run `python3 scripts/ci/scan_oca_repos.py` — must exit `0`
4. Commit: `chore(oca): port <repo> to 19.0; activate in addons_path`

---

## Adding a New OCA Repo

1. Add as git submodule on the 19.0 branch:
   ```bash
   git submodule add -b 19.0 https://github.com/OCA/<repo>.git addons/oca/<repo>
   ```
2. Verify it has modules:
   ```bash
   find addons/oca/<repo> -maxdepth 2 -name "__manifest__.py" | wc -l
   ```
3. Add entry to `ssot/odoo/oca_repos.yaml` with `status: ok` or `pinned`
4. Add to `addons_path` in all three conf files
5. Run scanner — must be clean

---

## Removing an Empty Repo

1. Remove from `addons_path` in all three conf files
2. Set `status: empty` in `ssot/odoo/oca_repos.yaml`
3. Optionally remove submodule entirely:
   ```bash
   git submodule deinit -f addons/oca/<repo>
   git rm -f addons/oca/<repo>
   rm -rf .git/modules/addons/oca/<repo>
   ```
4. Remove from `ssot/odoo/oca_repos.yaml`
5. Run scanner — must exit `0`

---

## CI Failure Triage

| Error | Cause | Fix |
|-------|-------|-----|
| `FATAL: N empty repo(s)` | Empty repo in `addons_path` | Remove from addons_path + set `status: empty` in SSOT |
| `BLOCKED: repo on 18.0` | 18.0-pinned repo in `addons_path` | Port to 19.0 first; do not add to addons_path until done |
| `FAIL: config still contains empty repo` | addons_path cleanup missed | Edit conf files to remove the repo path |
| `SSOT not found` | `ssot/odoo/oca_repos.yaml` missing | Create it (template above) |
