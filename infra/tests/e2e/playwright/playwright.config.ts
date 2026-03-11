import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright configuration for Odoo E2E tests.
 *
 * Usage:
 *   npx playwright test
 *   npx playwright test --headed
 *   npx playwright test --ui
 */
export default defineConfig({
  testDir: './',
  fullyParallel: false, // Odoo tests may have state dependencies
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1, // Single worker for Odoo to avoid conflicts
  reporter: [
    ['html', { open: 'never' }],
    ['json', { outputFile: 'test-results/results.json' }],
    ['list'],
  ],
  use: {
    baseURL: process.env.ODOO_URL || 'http://localhost:8069',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'on-first-retry',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  // Web server configuration (optional - use if running locally)
  // webServer: {
  //   command: 'docker compose up odoo-core',
  //   url: 'http://localhost:8069',
  //   reuseExistingServer: !process.env.CI,
  //   timeout: 120000,
  // },
});
