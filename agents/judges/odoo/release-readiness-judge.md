# Judge: release-readiness-judge

## Scope

Determines if a build is eligible for staging or production promotion.

## Verdict: PASS when

- dependency-integrity-judge PASS
- ci-signal-judge PASS
- Evidence pack exists and complete
- Rollback path documented
- No open P0 blockers

## Verdict: FAIL when

- Any upstream judge fails
- Evidence pack incomplete
- No rollback plan
- Open P0 blockers exist

## Checks

1. Upstream judge verdicts
2. Evidence directory contains deploy.json, test results, config diffs
3. Rollback documented (previous image tag, DB backup reference)
4. Blocker list empty or all classified as non-blocking
