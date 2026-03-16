# Web Debugging Architecture

## Purpose

Define the canonical debugging loop for the `web-site` stack so agents and developers do not diagnose frontend issues from screenshots alone.

The debugging architecture must treat runtime/browser telemetry as first-class input alongside code and build output.

---

## Core principle

Visual symptoms are not root cause.

The canonical debugging input order is:

1. build output
2. browser console output
3. failed network requests
4. runtime stack traces
5. DOM/rendered page state
6. changed files
7. screenshot only as supporting evidence

---

## Canonical tool roles

### Figma Make
Use for:
- design-native generation
- rapid UI iteration
- code edits within generated app context
- visual preview of the generated app

Do not use as the sole source of runtime truth.

### Bolt
Use for:
- fast runnable app generation
- terminal/build troubleshooting
- quick recovery from broken preview states

### ChatGPT Canvas
Use for:
- structured patch planning
- copy/layout iteration
- targeted code edits once runtime/build evidence is available

### Chrome DevTools MCP / CDP
Use for:
- console errors
- runtime exceptions
- failed network requests
- DOM inspection
- source-mapped stack traces
- request/response debugging

This is the canonical runtime truth source.

### Repo + CI
Use for:
- reproducible fixes
- durable source of truth
- regression validation

---

## Canonical debugging loop

### Step 1 — Reproduce
Open the local preview for the target app.

Examples:
- `apps/marketing` -> `http://localhost:3000`
- other apps -> environment-specific local preview URL

### Step 2 — Capture runtime truth
Collect:
- `console.error`
- `console.warn`
- uncaught exceptions
- rejected promises
- failed fetch/XHR requests
- 4xx/5xx responses
- hydration/render warnings
- route/navigation failures

### Step 3 — Capture build truth
Run:
- install
- build
- lint
- typecheck
- test if present

### Step 4 — Build a debug packet
Normalize the issue into one machine-readable packet containing:
- app name
- preview URL
- console errors
- network failures
- build errors
- changed files
- expected behavior
- observed behavior

### Step 5 — Patch only the smallest valid surface
Prefer:
- local file fixes
- config fixes
- cache/build hygiene fixes
- route/component fixes

Avoid speculative rewrites.

### Step 6 — Re-verify
Re-run:
- preview
- console/network inspection
- build/lint/typecheck
- focused smoke verification

---

## Canonical debug packet shape

```json
{
  "app": "marketing",
  "url": "http://localhost:3000",
  "expected": "Homepage renders successfully",
  "observed": "Blank page after navigation",
  "console_errors": [
    {
      "message": "Cannot find module './870.js'",
      "source": ".next/server/webpack-runtime.js"
    }
  ],
  "network_failures": [],
  "build_errors": [],
  "changed_files": [
    "apps/marketing/app/page.tsx"
  ]
}
```

---

## Debugging surface hierarchy

### Highest priority

* build failures
* runtime exceptions
* network failures
* hydration errors

### Medium priority

* DOM mismatch
* style regressions
* visual breakage with clean console

### Lowest priority

* screenshot-only complaints without runtime evidence

---

## Build hygiene policy

For Next.js / React apps:

* `.next` is build output, not source of truth
* stale `.next` artifacts must be invalidated before deep diagnosis
* monorepo caching must not restore incompatible `.next` output
* no fix is considered complete until clean build succeeds

---

## Browser truth policy

Every significant frontend bug report should be paired with:

* console capture
* network capture
* route/page URL
* changed file list
* exact app/package name

Screenshots alone are insufficient for root-cause work.

---

## Figma-to-code debugging policy

Figma Make output must be validated through:

* local repo integration
* local preview
* DevTools console/network capture
* build/lint/typecheck

Generated UI must not bypass the standard runtime validation loop.

---

## Bolt/Canvas usage policy

Bolt and Canvas should receive:

* distilled debug packet
* exact changed files
* build/runtime evidence
* desired behavior

They should not be asked to infer root cause from screenshots only.

---

## CI alignment

The same architecture should feed CI:

* build
* lint
* typecheck
* optional browser smoke checks
* saved artifacts/logs for agent repair loops

---

## Done definition

A web bug is only considered resolved when:

1. the issue reproduces no longer
2. browser console is clean or understood
3. failing network requests are resolved or expected
4. build/lint/typecheck pass
5. the patch exists in the repo
6. the fix is reproducible outside the chat session
