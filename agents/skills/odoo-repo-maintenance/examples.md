# Examples — odoo-repo-maintenance

## Example 1: Fully conformant module

**Input**: Check `queue_job` from OCA/queue repo

**Output**:
- Module: queue_job (addons/oca/queue/queue_job)
- Manifest conformance:
  - version: `19.0.2.1.0` — PASS
  - license: `LGPL-3` — PASS
  - development_status: `Stable` — PASS
  - depends: `[base, mail]` — PASS (minimal)
- Pre-commit: configured — PASS, hooks current — PASS
- README: generated — PASS
- CI: 19.0 branch green — PASS
- Submodule freshness: pinned 5 days ago — PASS
- Violations: none
- Recommended fixes: none

## Example 2: Module with violations

**Input**: Check `web_favicon` from OCA/web repo

**Output**:
- Module: web_favicon (addons/oca/web/web_favicon)
- Manifest conformance:
  - version: `18.0.1.0.0` — FAIL (no 19.0 version)
  - license: `AGPL-3` — PASS
  - development_status: `Beta` — WARNING (below Stable for production)
- Pre-commit: configured — PASS
- README: generated — PASS
- CI: 19.0 branch missing — FAIL
- Submodule freshness: pinned 45 days ago — FAIL (stale, needs justification)
- Violations:
  - No 19.0 branch (severity: high)
  - Beta maturity (severity: medium for production use)
  - Stale submodule pin (severity: low)
- Recommended fixes: verify 19.0 compatibility, update submodule pin, track in OCA19_COMPATIBILITY_EXCEPTIONS.md

## Example 3: Stale submodule audit

**Input**: Audit all OCA submodule pins for staleness

**Output**:
- Total submodules: 34
- Within 30 days: 28
- Stale (>30 days): 6
  - addons/oca/web: 45 days (justification: web_favicon incompatibility)
  - addons/oca/server-tools: 38 days (no justification — update required)
  - ... (4 more)
- Recommended: update 5 stale pins, keep 1 with documented justification
