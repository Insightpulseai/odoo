# SaaS Landing E2E Tests

Playwright-based end-to-end testing for the InsightPulse.ai SaaS landing page dashboard.

## Setup

```bash
cd templates/saas-landing

# Install dependencies
pnpm install

# Install Playwright browsers
pnpm playwright install
```

## Running Tests

### Local Development

```bash
# Run all tests (all browsers)
pnpm test:e2e

# Run specific browser
pnpm test:e2e --project=chromium
pnpm test:e2e --project=firefox
pnpm test:e2e --project=webkit

# Interactive UI mode
pnpm test:e2e --ui

# Debug mode
pnpm test:e2e --debug

# Run specific test file
pnpm test:e2e dashboard-theme.spec.ts

# View last test report
pnpm test:e2e:report
```

### Update Visual Baselines

```bash
# Generate/update baseline screenshots
pnpm playwright test dashboard-visual.spec.ts --update-snapshots

# Commit updated baselines
git add tests/e2e/specs/*.spec.ts-snapshots
git commit -m "test: update visual regression baselines"
```

## Test Coverage

### Dashboard Theme Selector (`dashboard-theme.spec.ts`)
- Default theme loading (shine)
- Theme persistence in localStorage
- Chart re-rendering on theme change
- Cycling through all 6 themes
- Dynamic theme script loading

### Dashboard Navigation (`dashboard-navigation.spec.ts`)
- Tab switching (Commits, Logs, Monitoring, Shell)
- Environment switching (Production, Staging, Development)
- Sidebar rendering (Environments, Recent Builds)
- Deploy button interaction

### Visual Regression (`dashboard-visual.spec.ts`)
- Full-page screenshots for shine theme
- Full-page screenshots for dark theme
- Theme selector component screenshot

## CI/CD Integration

### E2E Tests Workflow
**File**: `.github/workflows/saas-landing-e2e.yml`

**Triggers**:
- Push to `main`/`develop` affecting `templates/saas-landing/**`
- Pull requests to `main`/`develop`

**Matrix**:
- Browsers: Chromium, Firefox, WebKit
- Parallel execution across browsers

**Artifacts**:
- HTML test reports (30 days)
- Screenshots on failure (7 days)

### Visual Regression Workflow
**File**: `.github/workflows/saas-landing-visual-regression.yml`

**Triggers**:
- Pull requests to `main` affecting `templates/saas-landing/**`

**Behavior**:
- Runs visual regression tests in Chromium
- Uploads diff images on failure
- Non-blocking (allows PRs to merge with visual changes)

## Manual Testing

See `tests/manual/chrome-integration.md` for Claude Code Chrome extension integration patterns.

## Troubleshooting

### Flaky Tests
- Increase timeouts in `playwright.config.ts`
- Add explicit `waitForLoadState('networkidle')` calls
- Use `waitForSelector` with higher timeout values

### Screenshot Drift
- Pin Playwright version in `package.json`
- Use consistent viewport sizes
- Disable animations: `animations: 'disabled'`

### CI Failures
- Check uploaded artifacts for screenshots
- Review test logs for timing issues
- Consider increasing `timeout` in workflow

## Best Practices

1. **Wait for stability**: Use `waitForLoadState('networkidle')` before screenshots
2. **Explicit waits**: Prefer `waitForSelector` over `waitForTimeout`
3. **Descriptive tests**: Clear test names that explain what's being tested
4. **Isolated tests**: Each test should be independent
5. **Cleanup**: Reset state between tests using `beforeEach`

## Resources

- [Playwright Docs](https://playwright.dev/)
- [Test Best Practices](https://playwright.dev/docs/best-practices)
- [Visual Comparisons](https://playwright.dev/docs/test-snapshots)
