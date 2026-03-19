const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

async function generateCardImages() {
  console.log('🚀 Starting card image generation...');

  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();

  // Set viewport for consistent card sizing
  await page.setViewport({
    width: 1600,
    height: 1200,
    deviceScaleFactor: 2 // 2x for retina
  });

  // Load the HTML file
  const htmlPath = path.resolve(__dirname, '../public/odoo-copilot-cards.html');
  await page.goto(`file://${htmlPath}`, { waitUntil: 'networkidle0' });

  // Create output directory
  const outputDir = path.resolve(__dirname, '../public/use-case-cards');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  // Get all cards
  const cards = await page.$$('.card');
  console.log(`📦 Found ${cards.length} cards to capture`);

  const cardNames = [
    'sales-quote-generation',
    'invoice-reconciliation',
    'pipeline-insights',
    'manufacturing-cost-analysis',
    'document-processing',
    'timesheet-automation'
  ];

  for (let i = 0; i < cards.length; i++) {
    const card = cards[i];
    const fileName = cardNames[i] || `card-${i + 1}`;

    console.log(`📸 Capturing: ${fileName}.png`);

    // Scroll card into view
    await page.evaluate((element) => {
      element.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, card);

    await page.waitForTimeout(200); // Wait for scroll

    // Take screenshot of individual card
    await card.screenshot({
      path: path.join(outputDir, `${fileName}.png`),
      type: 'png'
    });

    console.log(`   ✅ Saved: ${fileName}.png`);
  }

  // Also capture full page
  console.log('📸 Capturing full page...');
  await page.screenshot({
    path: path.join(outputDir, 'all-cards.png'),
    type: 'png',
    fullPage: true
  });
  console.log('   ✅ Saved: all-cards.png');

  await browser.close();

  console.log('\n✨ Image generation complete!');
  console.log(`📁 Images saved to: ${outputDir}`);
  console.log(`\nGenerated files:`);
  fs.readdirSync(outputDir).forEach(file => {
    const stats = fs.statSync(path.join(outputDir, file));
    const sizeMB = (stats.size / 1024 / 1024).toFixed(2);
    console.log(`   • ${file} (${sizeMB} MB)`);
  });
}

generateCardImages().catch(error => {
  console.error('❌ Error generating images:', error);
  process.exit(1);
});
