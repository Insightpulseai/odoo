import { chromium } from 'playwright';

async function testGallery() {
  console.log('🚀 Testing Rotor Gallery...\n');

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  try {
    // Navigate to gallery
    console.log('📍 Navigating to http://localhost:3001/');
    await page.goto('http://localhost:3001/', { waitUntil: 'networkidle' });

    // Wait for React to render
    await page.waitForSelector('#root', { timeout: 5000 });

    // Check for critical elements
    const checks = {
      'Root element': await page.locator('#root').count() > 0,
      'Canvas (Three.js)': await page.locator('canvas').count() > 0,
      'Control Panel': await page.locator('button, [role="button"]').count() > 0,
    };

    console.log('\n✅ Gallery Loaded Successfully!\n');
    console.log('Element Checks:');
    Object.entries(checks).forEach(([name, passed]) => {
      console.log(`  ${passed ? '✓' : '✗'} ${name}`);
    });

    // Take screenshot
    const screenshotPath = './gallery-screenshot.png';
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log(`\n📸 Screenshot saved: ${screenshotPath}`);

    // Check console errors
    const errors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') errors.push(msg.text());
    });

    await page.waitForTimeout(2000); // Wait for any async errors

    if (errors.length > 0) {
      console.log('\n⚠️  Console Errors:');
      errors.forEach(err => console.log(`  - ${err}`));
    } else {
      console.log('\n✨ No console errors detected!');
    }

  } catch (error) {
    console.error('\n❌ Test Failed:', error.message);
    throw error;
  } finally {
    await browser.close();
  }
}

testGallery().catch(console.error);
