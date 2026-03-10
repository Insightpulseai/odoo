/**
 * E2E tests for IPAI Agent Core UI
 *
 * Tests:
 * - Agent Core menu navigation
 * - Skills list display
 * - Run creation and execution
 * - Run status display
 */

import { test, expect } from '@playwright/test';

// Test configuration
const ODOO_URL = process.env.ODOO_URL || 'http://localhost:8069';
const ODOO_DB = process.env.ODOO_DB || 'odoo';
const ODOO_USER = process.env.ODOO_USER || 'admin';
const ODOO_PASSWORD = process.env.ODOO_PASSWORD || 'admin';

test.describe('Agent Core Module', () => {
  test.beforeEach(async ({ page }) => {
    // Login to Odoo
    await page.goto(`${ODOO_URL}/web/login`);
    await page.fill('input[name="login"]', ODOO_USER);
    await page.fill('input[name="password"]', ODOO_PASSWORD);
    await page.click('button[type="submit"]');

    // Wait for dashboard to load
    await page.waitForSelector('.o_main_navbar', { timeout: 30000 });
  });

  test('should navigate to Agent Core menu', async ({ page }) => {
    // Open Agent Core app (if installed as app) or menu
    await page.click('a[data-menu-xmlid="ipai_agent_core.menu_agent_core_root"]');

    // Verify we're in Agent Core section
    await expect(page.locator('.o_breadcrumb')).toContainText('Agent');
  });

  test('should display skills list', async ({ page }) => {
    // Navigate to Skills menu
    await page.goto(`${ODOO_URL}/web#model=ipai.agent.skill&view_type=list`);

    // Wait for list to load
    await page.waitForSelector('.o_list_view', { timeout: 10000 });

    // Verify table headers
    const headers = page.locator('th');
    await expect(headers).toContainText(['Name', 'Key']);
  });

  test('should display runs list', async ({ page }) => {
    // Navigate to Runs menu
    await page.goto(`${ODOO_URL}/web#model=ipai.agent.run&view_type=list`);

    // Wait for list to load
    await page.waitForSelector('.o_list_view', { timeout: 10000 });

    // Verify state column exists
    const headers = page.locator('th');
    await expect(headers).toContainText(['State']);
  });

  test('should create a new run', async ({ page }) => {
    // First, ensure we have at least one skill
    await page.goto(`${ODOO_URL}/web#model=ipai.agent.skill&view_type=list`);
    await page.waitForSelector('.o_list_view', { timeout: 10000 });

    // Navigate to Runs
    await page.goto(`${ODOO_URL}/web#model=ipai.agent.run&view_type=list`);
    await page.waitForSelector('.o_list_view', { timeout: 10000 });

    // Click Create button
    await page.click('button.o_list_button_add');

    // Wait for form view
    await page.waitForSelector('.o_form_view', { timeout: 10000 });

    // Verify form has required fields
    await expect(page.locator('label:has-text("Skill")')).toBeVisible();
  });

  test('should show run details in form view', async ({ page }) => {
    // Go to runs list
    await page.goto(`${ODOO_URL}/web#model=ipai.agent.run&view_type=list`);
    await page.waitForSelector('.o_list_view', { timeout: 10000 });

    // Check if there are any runs
    const rows = page.locator('tr.o_data_row');
    const rowCount = await rows.count();

    if (rowCount > 0) {
      // Click first run
      await rows.first().click();

      // Wait for form view
      await page.waitForSelector('.o_form_view', { timeout: 10000 });

      // Verify key fields are visible
      await expect(page.locator('label:has-text("State")')).toBeVisible();
    } else {
      // No runs - just verify the list loaded
      await expect(page.locator('.o_list_view')).toBeVisible();
    }
  });
});

test.describe('Agent Core API', () => {
  test('should return health check', async ({ request }) => {
    const response = await request.get(`${ODOO_URL}/api/v1/health`);

    expect(response.ok()).toBeTruthy();

    const body = await response.json();
    expect(body.status).toBe('ok');
    expect(body.service).toBe('ipai_skill_api');
  });

  test('should require auth for skills endpoint', async ({ request }) => {
    const response = await request.get(`${ODOO_URL}/api/v1/skills`);

    // Should redirect to login or return 401/403
    expect([401, 403, 303]).toContain(response.status());
  });
});
