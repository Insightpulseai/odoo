# MOVED — Legacy Evidence Directory

This directory (`docs/evidence/`) is **legacy-only**.

## Canonical Evidence Location

All new evidence must be written to:

```
web/docs/evidence/<YYYYMMDD-HHMM+0800>/<topic>/logs/
```

## Why

The canonical evidence root was standardized to `web/docs/evidence/` to:
- Consolidate documentation artifacts under `web/docs/`
- Prevent artifact scatter across `docs/`, `sandbox/`, and `web/docs/`
- Enforce a single evidence path in SSOT + tooling

## Legacy Entries Here

The following entries predate the canonical path. Do not add new entries here.

| Entry | Date | Notes |
|-------|------|-------|
| `2026-02-15/` | 2026-02-15 | Pre-canonicalization |
| `20260110-0927/` | 2026-01-10 | Pre-canonicalization |
| `20260112-0300/` | 2026-01-12 | Pre-canonicalization |
| `20260112-0358/` | 2026-01-12 | Pre-canonicalization |
| `20260217-0215+0800/` | 2026-02-17 | Pre-canonicalization (SSOT tightening pass) |

## Reference

See `docs/agent_instructions/SSOT.md` → Evidence Rules for the canonical path contract.
