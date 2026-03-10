# OCA Installer SSOT Flow

## Canonical installation path

```
ssot/odoo/oca_repos.yaml     ← registry (lifecycle, branch, source)
        ↓ filter by status
ssot/odoo/oca_lock.yaml      ← lock (pinned SHA refs)
        ↓ resolve refs
Install Plan (deterministic)
        ↓ --dry-run or execute
addons/oca/<repo>/           ← cloned repos
        ↓ verify
CI gate (dry-run --strict)
```

## Entry points

| Command | Purpose |
|---------|---------|
| `scripts/odoo/install-oca-modules.sh` | Shell wrapper (delegates to Python) |
| `scripts/odoo/install_oca_from_ssot.py` | Main installer |
| `scripts/odoo/render_oca_install_plan.py` | Read-only plan renderer |

## Lifecycle states

| Status | Installable | Behavior |
|--------|-------------|----------|
| `pinned` | Yes | Use 19.0 branch; prefer lock SHA if available |
| `ok` | Yes | Use `_git_aggregated` branch; prefer lock SHA if available |
| `blocked` | No | Skip with warning (18.0 branch, needs porting) |
| `empty` | No | Skip with warning (0 modules, forbidden in addons_path) |
| `pending_vendor` | No | Skip with warning (not yet vendored) |

## Lock resolution

1. If repo has entry in `oca_lock.yaml` → checkout pinned SHA
2. If no lock entry → use branch from registry (warn: unpinned)
3. `--strict` mode → fail if any installable repo lacks a lock entry

## CLI flags

```
--dry-run     Resolve plan, print it, do not clone
--json        Output plan as JSON (for CI consumption)
--strict      Fail if any installable repo lacks a lock entry
--target-dir  Override clone target (default: addons/oca)
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Success, all repos pinned |
| 1 | Error (malformed SSOT, unknown state, clone failure) |
| 2 | Success with warnings (unpinned repos) |

## CI integration

Add to OCA validation workflow:
```yaml
- name: OCA install plan dry-run
  run: python scripts/odoo/install_oca_from_ssot.py --dry-run --strict
```

## What this replaces

The SSOT-driven installer replaces 8 fragmented scripts that hardcoded OCA repo/module lists. Legacy scripts remain in the repo but are no longer the canonical path.
