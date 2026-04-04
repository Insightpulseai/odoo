# Evidence Publishing Contract

## Purpose

Every pipeline run that includes verification steps must produce a deterministic,
auditable evidence bundle. Evidence is not optional — it is the proof that the
system verified itself.

## Evidence lifecycle

```
verification step → evidence dir → evidence pack → pipeline artifact → reviewable
```

1. **Verification steps** (Playwright, PG resilience, module tests) write to `docs/evidence/<YYYYMMDD-HHMM>/<scope>/`
2. **Evidence pack** (`automations/scripts/evidence_pack.sh`) collects all evidence dirs into `.artifacts/evidence-pack/`
3. **Pipeline** publishes the pack as a named artifact
4. **Reviewers** can download the artifact and inspect screenshots, logs, and the machine-readable manifest

## Directory structure

### Per-verification output (written by each check)

```
docs/evidence/<YYYYMMDD-HHMM>/<scope>/
  verification.json       # Machine-readable: verdict, counts, paths
  playwright.log          # Full test runner output (if Playwright)
  screenshots/            # Visual proof (PNG)
    01-login-page.png
    02-assets-loaded.png
    ...
```

### Evidence pack (assembled by evidence_pack.sh)

```
.artifacts/evidence-pack/
  evidence-pack.json                    # Pack manifest (overall verdict, counts, sources)
  screenshots/                          # All screenshots, prefixed by scope
    prod-verify-01-login-page.png
    edge-resilience-01-fqdn-check.png
  logs/                                 # All logs
    prod-verify-playwright.log
    odoo-test-odoo_test_12345_1.log
  evidence-pack-<BUILD_ID>.tar.gz      # Complete bundle as tarball
```

## Pack manifest schema

```json
{
  "pack_version": "1.0",
  "build_id": "12345",
  "timestamp": "20260404-1530",
  "target": "https://erp.insightpulseai.com",
  "overall_verdict": "PASS",
  "counts": {
    "evidence_dirs": 2,
    "verification_manifests": 2,
    "screenshots": 6,
    "logs": 3
  },
  "sources": [
    {"scope": "prod-verify", "timestamp": "20260404-1525", "has_manifest": true},
    {"scope": "edge-resilience", "timestamp": "20260404-1528", "has_manifest": true}
  ],
  "artifacts": {
    "screenshots": ".artifacts/evidence-pack/screenshots/",
    "logs": ".artifacts/evidence-pack/logs/",
    "manifest": ".artifacts/evidence-pack/evidence-pack.json"
  }
}
```

## Verdict semantics

| `overall_verdict` | Meaning | Pipeline effect |
|-------------------|---------|----------------|
| `PASS` | All verification manifests report PASS | `exit 0` — pipeline continues |
| `FAIL` | Any verification manifest reports FAIL | `exit 1` — pipeline fails |

The evidence pack is **always published** regardless of verdict (`condition: always()` in pipeline).
A failed verification does not prevent evidence collection — the evidence is the proof of the failure.

## Pipeline integration

### Azure DevOps

```yaml
# After all verification steps, before cleanup
- bash: |
    set -euo pipefail
    chmod +x automations/scripts/evidence_pack.sh
    automations/scripts/evidence_pack.sh
  displayName: Assemble evidence pack
  condition: always()
  env:
    BUILD_ID: $(Build.BuildId)
    BASE_URL: $(BASE_URL)

- publish: .artifacts/evidence-pack
  artifact: evidence-pack-$(Build.BuildId)
  displayName: Publish evidence pack
  condition: always()
```

## Environment variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `BUILD_ID` | Yes | — | Pipeline build identifier |
| `EVIDENCE_ROOT` | No | `docs/evidence` | Source root for evidence artifacts |
| `OUTPUT_DIR` | No | `.artifacts/evidence-pack` | Bundle output directory |
| `BASE_URL` | No | `unknown` | Target URL for manifest metadata |

## Rules

1. **Evidence is append-only** — never overwrite or delete previous evidence dirs
2. **Screenshots are required** — any visual verification must capture screenshots
3. **Manifests are required** — every verification step must write `verification.json`
4. **Pack is always published** — even on failure, especially on failure
5. **No evidence, no claim** — never assert "tests passed" without citing the evidence pack

## What goes into evidence (and what does not)

### Include

- Screenshots from Playwright tests
- Playwright runner logs
- Odoo module test logs
- PG resilience check output
- Verification JSON manifests
- Pass/fail summaries

### Exclude

- Source code diffs (use git for that)
- Secrets, tokens, credentials (never)
- Full database dumps
- User data
