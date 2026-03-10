import { chromium } from '@playwright/test';

const cdpURL = process.env.CDP_URL || 'http://127.0.0.1:9222';
const targetURL = process.env.TARGET_URL || 'http://localhost:3000/dashboard';
const outPath = process.env.OUT_PATH || 'cdp-dashboard.png';

(async () => {
  const browser = await chromium.connectOverCDP(cdpURL);
  const context = browser.contexts()[0] || await browser.newContext();
  const page = context.pages()[0] || await context.newPage();
  await page.goto(targetURL, { waitUntil: 'domcontentloaded' });
  await page.screenshot({ path: outPath, fullPage: true });
  await browser.close();
  console.log(`Wrote screenshot: ${outPath}`);
})();
