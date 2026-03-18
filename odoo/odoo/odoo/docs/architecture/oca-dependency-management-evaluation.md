# OCA Dependency Management — Evaluation & Decision

**Date:** 2026-02-20
**Status:** Decision made — `gitaggregate` (OCA standard)
**Scope:** 21 OCA modules from 10+ repos, Odoo 19.0 CE

---

## Problem Statement

The repo has **35 git submodule entries** (`.gitmodules`) targeting **18.0**, spread
across **3 conflicting path conventions**:

| Path Convention | Count | State |
|-----------------|-------|-------|
| `external-src/<repo>` | 14 | Empty dirs (never populated) |
| `vendor/oca/<repo>` | 7 | Empty dirs (shallow=true) |
| `vendor/oca/OCA/<repo>` | 13 | Empty dirs |
| `branding/fluentui-system-icons` | 1 | Unrelated |

**None are populated.** The project targets Odoo **19.0** but all submodules pin
**18.0**. The `gen_addons_path.sh` script only reads from `external-src/`, ignoring
the other two paths entirely. This is dead weight that confuses contributors and
blocks CI.

---

## Options Evaluated

### Option 1: Git Submodules (current, broken)

**How it works:** Each OCA repo is a git submodule entry in `.gitmodules`. The
parent repo pins a specific commit SHA. Contributors run `git submodule update
--init --recursive` to populate.

**Pros:**
- Native git — no extra tooling
- Exact commit pinning out of the box
- GitHub UI shows submodule links

**Cons:**
- Detached HEAD by default — confusing for contributors
- `--recursive` needed everywhere (clone, CI, deploy scripts)
- Forgot `git submodule update`? Silent empty directories, runtime `ModuleNotFoundError`
- Each OCA repo brings **all** modules (50–200 per repo) when you need 2–3
- Branch tracking is fragile (`branch = 19.0` in `.gitmodules` doesn't auto-update)
- CI clone times scale linearly with submodule count
- Current state proves the failure mode: 35 entries, 0 populated, 3 conflicting paths

**Verdict:** Not recommended. The current broken state demonstrates exactly why
submodules are a poor fit for OCA dependency management.

### Option 2: `gitaggregate` (OCA standard) — RECOMMENDED

**How it works:** A single YAML file (`oca-aggregate.yml`) declares all OCA repos,
branches, and optional cherry-picks/patches. Running `gitaggregate -c oca-aggregate.yml`
clones them into a target directory (`addons/oca/<repo>/`). The output is gitignored.

**Pros:**
- OCA's own recommended approach (used by most OCA integrators)
- Single YAML = single source of truth
- Supports: branch pins, commit SHA pins, cherry-picks, patches, multiple remotes
- Parallel cloning (`-j 4`)
- Output is gitignored — clean repo, no submodule state
- `Makefile` target: `make oca-aggregate` — one command
- Works identically in CI, Docker build, local dev
- Can target a single repo: `gitaggregate -c oca-aggregate.yml -d ./addons/oca/web`

**Cons:**
- Extra pip dependency (`git-aggregator`)
- Clones full repos (not individual modules) — same disk usage as submodules
- No native git UI integration (submodule links in GitHub)

**Verdict:** Recommended. Already partially adopted in the repo (`oca-aggregate.yml`
exists with 25 repos targeting 19.0, `.gitignore` references it).

### Option 3: Direct Vendor Copy

**How it works:** Copy only the specific module folders you need directly into the
repo. Pin by committing them as regular files.

**Pros:**
- Simplest possible approach — no tooling
- Only the modules you use are in the repo
- `git log` shows full history of what changed

**Cons:**
- Manual updates — no upstream tracking
- No way to apply upstream security patches automatically
- Bloats the repo (OCA module code in your git history forever)
- Loses OCA commit metadata (author, original PR references)
- Updating requires: clone OCA repo, copy module, diff manually, commit
- 21 modules × manual process = significant maintenance burden

**Verdict:** Not recommended for 21+ modules. Viable for 1–2 emergency patches.

---

## Decision Matrix

| Criterion | Submodules | gitaggregate | Vendor Copy |
|-----------|:---------:|:------------:|:-----------:|
| OCA standard | No | **Yes** | No |
| Single SSOT file | .gitmodules (messy) | **oca-aggregate.yml** | N/A |
| Upstream tracking | Fragile | **Native** | Manual |
| CI simplicity | Needs --recursive | **pip install + 1 cmd** | None needed |
| Cherry-pick support | No | **Yes** | Manual |
| Repo cleanliness | Submodule noise | **Gitignored output** | Bloated history |
| Contributor friction | High (forget update) | **Low (make target)** | Low |
| Already started | ~~35 broken entries~~ | **25 repos in YAML** | No |

---

## Decision

**Use `gitaggregate`** via `oca-aggregate.yml`.

### What Changed

| File | Change |
|------|--------|
| `oca-aggregate.yml` | Updated: 30 OCA repos (was 25), organized by tier, added `bank-payment`, `server-auth`, `hr`, `manufacture`, `partner-contact` |
| `scripts/gen_addons_path.sh` | Updated: reads from `addons/oca/` instead of `external-src/` |
| `Makefile` | Added: `oca-aggregate`, `oca-aggregate-single` targets |
| `requirements.txt` | Added: `git-aggregator==4.0` |
| `scripts/migrate_submodules_to_aggregate.sh` | New: removes all 35 stale submodule entries |

### Migration Steps

```bash
# 1. Remove stale submodules (dry-run first)
./scripts/migrate_submodules_to_aggregate.sh
./scripts/migrate_submodules_to_aggregate.sh --apply

# 2. Install git-aggregator
pip install git-aggregator

# 3. Clone all OCA repos
make oca-aggregate

# 4. Regenerate addons path
make gen-addons-path

# 5. Render odoo.conf
make render-odoo-conf

# 6. Commit
git add -A
git commit -m "chore(oca): migrate from git submodules to gitaggregate"
```

### Module → Repo Mapping (21 Modules, 10 Repos)

| Module | OCA Repo | Wave |
|--------|----------|------|
| `report_xlsx` | `reporting-engine` | 2 |
| `report_xlsx_helper` | `reporting-engine` | 2 |
| `web_responsive` | `web` | 2 |
| `web_dialog_size` | `web` | 2 |
| `web_environment_ribbon` | `web` | 2 |
| `date_range` | `server-ux` | 2 |
| `base_substate` | `server-ux` | 2 |
| `auth_session_timeout` | `server-auth` | 2 |
| `account_move_name_sequence` | `account-financial-tools` | 3 |
| `account_journal_restrict_mode` | `account-financial-tools` | 3 |
| `account_usability` | `account-financial-tools` | 3 |
| `account_tax_balance` | `account-financial-tools` | 3 |
| `account_payment_mode` | `bank-payment` | 3 |
| `account_payment_order` | `bank-payment` | 3 |
| `account_payment_order_grouped` | `bank-payment` | 3 |
| `account_payment_purchase` | `bank-payment` | 3 |
| `account_payment_sale` | `bank-payment` | 3 |
| `hr_employee_firstname` | `hr` | 4 |
| `document_url` | `knowledge` | 4 |
| `hr_timesheet_task_stage` | `timesheet` | 4 |
| `quality_control_oca` | `manufacture` | 1 |
| `quality_control_stock_oca` | `manufacture` | 1 |
| `account_statement_base` | `account-reconcile` | 1 |
| `account_stmt_import_file_oca` | `account-reconcile` | 1 |

### Production Pinning (Future)

For production stability, pin specific commit SHAs in `oca-aggregate.yml`:

```yaml
./addons/oca/web:
  remotes:
    oca: https://github.com/OCA/web.git
  merges:
    - oca 19.0
  # Pin to a specific SHA for production:
  # merges:
  #   - oca abc123def456
```

---

## References

- [git-aggregator](https://github.com/acsone/git-aggregator) — OCA-maintained tool
- [OCA Guidelines: Repository layout](https://github.com/OCA/odoo-community.org/blob/master/website/Ede/guidelines/develop.md)
- `.gitignore:64-67` — already references `oca-aggregate.yml` as SSOT
