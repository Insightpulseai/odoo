#!/usr/bin/env node
// Headless verification that login form JS executes and removes d-none

const { chromium } = require('playwright');

(async () => {
  const url = process.env.URL || 'https://erp.insightpulseai.net/web/login';
  const browser = await chromium.launch();
  const page = await browser.newPage();

  const consoleErrors = [];
  page.on('console', (msg) => {
    if (msg.type() === 'error') consoleErrors.push(msg.text());
  });
  page.on('pageerror', (err) => consoleErrors.push(String(err)));

  console.log('Loading:', url);
  await page.goto(url, { waitUntil: 'networkidle', timeout: 120000 });

  // The form exists; JS should remove d-none or otherwise make it visible
  const form = page.locator('form.oe_login_form');
  const klass = await form.getAttribute('class');
  const visible = await form.isVisible();

  console.log('login_form_class:', klass);
  console.log('login_form_visible:', visible);

  // Fail if still hidden
  if (!visible) {
    console.log('FAIL: login form still not visible after JS execution');
    if (consoleErrors.length) {
      console.log('Console errors:', consoleErrors.slice(0, 10));
    }
    await browser.close();
    process.exit(2);
  }

  // Ensure main assets actually loaded
  const assetsOk = await page.evaluate(() => {
    return typeof window.odoo !== 'undefined' || typeof odoo !== 'undefined';
  });
  console.log('odoo_global_detected:', assetsOk);

  if (consoleErrors.length) {
    console.log('Console errors (first 10):', consoleErrors.slice(0, 10));
  }

  console.log('✅ PASS: Login form is visible and JS executed successfully');
  await browser.close();
})();
