# Runbook: Web Debugging Loop

## Purpose

Provide a deterministic agent workflow for debugging `web-site` apps using runtime telemetry, build output, and repo-local patches.

---

## Inputs required

- target app name
- local preview URL
- changed files or suspected surface
- console output
- network failures
- build/lint/typecheck output
- expected vs observed behavior

If console/network/build evidence is missing, collect it first.

---

## Algorithm

### 1. Identify the app boundary
Determine:
- app name
- package name
- preview URL
- framework/runtime
- relevant config files

### 2. Reproduce the issue
Open the exact route/page and verify the reported failure.

### 3. Capture runtime evidence
Collect:
- console errors
- warnings
- network failures
- route/navigation failures
- DOM/render anomalies

### 4. Capture build evidence
Run:
- install if needed
- build
- lint
- typecheck
- relevant app tests if available

### 5. Classify the issue

#### Class A — Build artifact / cache issue
Examples:
- missing chunk
- stale `.next`
- incompatible cache restore

#### Class B — Config / environment issue
Examples:
- wrong env var
- bad hostname
- broken API base URL
- wrong asset/public path

#### Class C — Source code/runtime logic issue
Examples:
- component crash
- hook misuse
- server/client boundary issue
- route import error

#### Class D — Data/API issue
Examples:
- failing fetch
- malformed payload
- auth/session problem
- backend contract drift

### 6. Patch the smallest valid surface
Apply the minimum file change needed to fix the classified issue.

### 7. Re-run verification
Confirm:
- page loads
- console is clean enough
- network failures are resolved
- build/lint/typecheck pass

### 8. Produce closeout
Return:
- root cause
- files changed
- verification result
- remaining risks

---

## Issue classification shortcuts

### Missing numbered Next chunk / webpack-runtime require failure
Assume:
- stale `.next`
- broken cache
- interrupted build
before assuming app logic bug.

### Blank page with clean build but runtime exception
Assume:
- component crash
- client/server misuse
- hydration mismatch

### UI broken but console clean
Assume:
- CSS/layout regression
- DOM/state mismatch
- wrong data shape rendered safely

### API-heavy page failure
Assume:
- auth/session/env drift
- bad request path
- server response mismatch

---

## Output contract

Every debug response must include:

- root cause classification
- exact files to change
- smallest patch direction
- verification checklist

Do not stop at "clear cache" unless cache corruption is proven and hardened against recurrence.

---

## Hard rules

1. Do not diagnose from screenshots only.
2. Do not patch broad surfaces without runtime evidence.
3. Do not trust generated code until validated in local preview.
4. Do not treat build output directories as source of truth.
5. Do not close an issue without re-verification.

---

## Canonical closeout format

- App:
- URL:
- Root cause class:
- Root cause:
- Files changed:
- Verification:
- Remaining risk:
