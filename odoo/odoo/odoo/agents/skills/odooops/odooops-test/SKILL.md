---
name: odooops-test
description: Run E2E tests against OdooOps environments using Playwright. Use this skill when the user requests "Run tests", "Test my deployment", "Check if the app works", or "Run E2E suite". Returns test results with artifacts (traces, videos, screenshots).
metadata:
  author: insightpulseai
  version: "1.0.0"
  platform: odooops
---

# OdooOps E2E Test

Run Playwright E2E tests against any OdooOps environment (preview, staging, production).

## How It Works

1. Fetches environment URL from OdooOps API
2. Installs Playwright dependencies (if needed)
3. Runs Playwright test suite with BASE_URL set to environment
4. Collects artifacts: traces, videos, screenshots
5. Returns test results + artifact links

## Usage

```bash
bash /mnt/skills/user/odooops-test/scripts/test.sh <env-id> [options]
```

**Arguments:**
- `env-id` - Environment ID (e.g., `env_preview_abc123`)

**Options:**
- `--grep <pattern>` - Run only tests matching pattern
- `--headed` - Run browser in headed mode (with Xvfb in CI)
- `--extension` - Enable Chrome extension mode (Phase 3)

**Environment Variables:**
- `ODOOOPS_API_BASE` - API base URL
- `ODOOOPS_TOKEN` - Authentication token
- `BASE_URL` - Override environment URL (optional)

**Examples:**

```bash
# Run full E2E suite against preview environment
bash /mnt/skills/user/odooops-test/scripts/test.sh env_preview_abc123

# Run only smoke tests
bash /mnt/skills/user/odooops-test/scripts/test.sh env_staging_xyz789 --grep "smoke"

# Run with Chrome extension mode
bash /mnt/skills/user/odooops-test/scripts/test.sh env_preview_abc123 --extension
```

## Output

```
Fetching environment URL for env_preview_abc123...
✓ Environment URL: https://preview-abc123.odooops.app

Installing Playwright dependencies...
✓ Playwright ready

Running E2E suite...
[chromium] › smoke.spec.ts:3:1 › smoke: web responds ✓ (2.1s)
[chromium] › dashboard.spec.ts:5:1 › Dashboard › should load ✓ (3.4s)
[chromium] › auth.spec.ts:10:1 › Authentication › login flow ✓ (4.2s)

✓ All tests passed! (9.7s)

Test Results:
- Total:  3 tests
- Passed: 3
- Failed: 0
- Skipped: 0

Artifacts uploaded:
- Traces:      tests/e2e/test-results/traces/
- Screenshots: tests/e2e/test-results/screenshots/
- Videos:      tests/e2e/test-results/videos/
```

The script also outputs JSON to stdout:

```json
{
  "environmentId": "env_preview_abc123",
  "environmentUrl": "https://preview-abc123.odooops.app",
  "testResults": {
    "total": 3,
    "passed": 3,
    "failed": 0,
    "skipped": 0,
    "duration": 9700
  },
  "artifacts": {
    "traces": ["tests/e2e/test-results/traces/smoke-spec-ts-chromium.zip"],
    "screenshots": [],
    "videos": []
  }
}
```

## Test Modes

### Default (Headless)
- Fastest execution
- CI-friendly
- Screenshots on failure only

### Headed Mode (`--headed`)
- Visual debugging
- Uses Xvfb in CI (no display required)
- Captures video on failure

### Extension Mode (`--extension`)
- Loads Chrome extension in Chromium
- Headful mode (requires Xvfb in CI)
- For testing flows requiring extension runtime

## Test Categories

E2E suite includes:

1. **Smoke Tests** (`smoke.spec.ts`)
   - Health check
   - Login flow
   - Basic navigation

2. **Dashboard Tests** (`dashboard.spec.ts`)
   - Tab navigation
   - Chart theme switching
   - Environment info display

3. **Module Tests** (optional)
   - Per-module E2E specs
   - Custom workflow validation

## Present Results to User

Always show test summary and artifact links:

```
✓ E2E suite passed!

Test Results:
- Total:  3 tests
- Passed: 3
- Failed: 0
- Duration: 9.7s

Artifacts:
- Traces:      tests/e2e/test-results/traces/
- Screenshots: (none - all tests passed)
- Videos:      (none - all tests passed)

Environment tested: https://preview-abc123.odooops.app
```

For failures, highlight failed tests:

```
✗ E2E suite failed

Failed Tests:
1. auth.spec.ts › Authentication › login flow
   Error: Timeout 60000ms exceeded waiting for selector "#login-button"

   Artifacts:
   - Trace:      tests/e2e/test-results/traces/auth-spec-ts-chromium.zip
   - Screenshot: tests/e2e/test-results/screenshots/login-flow-failure.png
   - Video:      tests/e2e/test-results/videos/auth-spec-ts-chromium.webm

Review trace: npx playwright show-trace tests/e2e/test-results/traces/auth-spec-ts-chromium.zip
```

## Integration with GitHub Actions

Tests are automatically triggered on PR/push via `.github/workflows/e2e-playwright.yml`. Manual test runs via this skill use the same test suite.

## Troubleshooting

### Environment Not Ready

If tests fail with connection errors:

```
Error: Environment not responding

Troubleshoot:
1. Check environment status: bash /mnt/skills/user/odooops-status/scripts/status.sh <env-id>
2. Wait for readiness: bash /mnt/skills/user/odooops-deploy/scripts/wait.sh <env-id>
3. Check logs: bash /mnt/skills/user/odooops-logs/scripts/logs.sh <env-id>
```

### Test Flakes

If tests fail intermittently:

```
Test flake detected. Common causes:

- Network timeouts (increase timeout in playwright.config.ts)
- Race conditions (add explicit waits)
- Animation timing (wait for animations to complete)

Rerun tests: bash /mnt/skills/user/odooops-test/scripts/test.sh <env-id> --grep "<test-name>"
```

### Browser Not Found

If Playwright browser is missing:

```
Browser binary not found. Install with:

cd tests/e2e
npx playwright install --with-deps chromium
```

## Related Skills

- **odooops-deploy**: Deploy environments for testing
- **odooops-logs**: Fetch logs for test debugging
- **odooops-status**: Check test history and trends

## API Reference

See [`tests/e2e/playwright.config.ts`](../../tests/e2e/playwright.config.ts) for test configuration.
