# CI Gate: Orphan Addons Guard

> **Status**: Active — triggered on `pull_request`, `push` to `main`, `merge_group`
> **Gate file**: `.github/workflows/orphan-addons-gate.yml`
> **Validator**: `scripts/ci/check_orphan_addons.py`
> **SSOT**: `ssot/odoo/orphan_addons_allowlist.yaml`

---

## Purpose

The Odoo `addons-path` points to **`addons/ipai/`** and **`addons/oca/*/`** only.

Any directory matching `addons/ipai_*/` at the **repo root** is **invisible to
Odoo at runtime**. These directories accumulate as dead code — they are never
installed, never tested, never executed. The gate prevents new ones from being
silently introduced.

---

## What it scans

The validator walks `addons/` and collects every directory whose name matches
`ipai_*` and is **not** the canonical `addons/ipai/` subtree. It then compares
that list against the allowlist.

```
addons/
├── ipai/               ← canonical: in addons-path ✅
│   ├── ipai_agent/
│   └── ...
├── oca/                ← canonical: in addons-path ✅
├── ipai_bir_data/      ← orphan: NOT in addons-path ⚠ (allowlisted)
└── ipai_workos_core/   ← orphan: NOT in addons-path ⚠ (allowlisted)
```

---

## Allowlist format

File: `ssot/odoo/orphan_addons_allowlist.yaml`

```yaml
schema: ssot.odoo.orphan_addons_allowlist.v1
version: "1.0"

modules:
  - name: ipai_bir_tax_compliance          # required — directory name
    reason: "18.0; needs 19.0 port"        # required — why not migrated yet
    migration_target: "addons/ipai/ipai_bir_tax_compliance/ (19.0 port)"
    ticket: "docs/audits/custom_addons_reassessment.md"
```

### Required keys per entry

| Key | Required | Description |
|-----|----------|-------------|
| `name` | ✅ | Exact directory name (no `addons/` prefix) |
| `reason` | ✅ | Why this module is not in `addons/ipai/` yet |
| `migration_target` | — | Where it should end up; omit only for archives |
| `ticket` | — | Tracking issue or audit doc |

**Rules:**
- `reason` must be non-empty (validator enforces this)
- Duplicate names fail the schema check (validator enforces this)
- Unknown top-level or per-entry keys fail the schema check
- Do **not** add entries to silence CI without a real migration plan

---

## Exit codes

| Code | Meaning | Action |
|------|---------|--------|
| `0` | PASS — no unlisted orphans | None |
| `2` | ERROR — allowlist missing, YAML parse error, or schema violation | Fix the allowlist file |
| `3` | FAIL — one or more unlisted orphan directories found | Add to allowlist OR move to `addons/ipai/` |

---

## Current state (2026-02-27)

```
PASS: orphan-addons-gate — 40 orphan directories found, all allowlisted
```

40 legacy `18.0` modules exist at the repo root. All 40 are documented in the
allowlist with migration targets. The gate passes; no new orphans may be added
without a corresponding allowlist entry.

---

## How to add a new module (correct paths)

```
# ✅ Correct: create inside the canonical path
mkdir -p addons/ipai/ipai_my_new_feature/
# Gate: no change needed

# ⚠ Incorrect: creates an orphan at repo root
mkdir -p addons/ipai_my_new_feature/
# Gate: FAILS CI — add to allowlist or move the module
```

---

## How to shrink the allowlist over time

Each allowlisted entry represents technical debt. To retire an entry:

1. Port the module to `addons/ipai/<name>/` (19.0 compatible), OR
2. Move it to `addons/_deprecated/<name>/` (explicit archive), OR
3. Delete it if it has no consumers and no migration value.
4. Remove the entry from `ssot/odoo/orphan_addons_allowlist.yaml`.
5. Run the validator locally to confirm exit 0.
6. Open a PR — the gate will pass without the entry once the directory is gone.

**Goal**: When all 40 entries are resolved, the allowlist becomes empty and the
gate auto-rejects any future orphan without any config changes.

---

## Running locally

```bash
pip install pyyaml
python3 scripts/ci/check_orphan_addons.py --repo-root .
```

Expected output (current state):
```
PASS: orphan-addons-gate — 40 orphan directories found, all allowlisted (ssot/odoo/orphan_addons_allowlist.yaml)
```

---

## Related docs

| Document | Purpose |
|----------|---------|
| `docs/audits/custom_addons_reassessment_DECISIONS.md §P1-E` | Policy decision and rationale |
| `docs/audits/custom_addons_reassessment.md §Root-Level Legacy` | Full audit of the 40 orphans |
| `ssot/odoo/orphan_addons_allowlist.yaml` | Allowlist source of truth |
| `.github/workflows/orphan-addons-gate.yml` | CI workflow definition |
