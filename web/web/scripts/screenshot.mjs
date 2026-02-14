import puppeteer from 'puppeteer';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';
import { mkdirSync, readdirSync, statSync } from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

async function generateScreenshots() {
  console.log('🚀 Starting screenshot generation...\n');

  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1600, height: 1200, deviceScaleFactor: 2 });

  const htmlPath = resolve(__dirname, '../public/odoo-copilot-cards.html');
  await page.goto(`file://${htmlPath}`, { waitUntil: 'networkidle0' });

  const outputDir = resolve(__dirname, '../public/use-case-cards');
  mkdirSync(outputDir, { recursive: true });

  // Get all cards
  const cards = await page.$$('.card');
  console.log(`📦 Found ${cards.length} cards\n`);

  const names = [
    'crm-pipeline-analysis',
    'invoice-processing',
    'manufacturing-costs',
    'project-tasks-kanban',
    'sales-quote-generation',
    'financial-reconciliation'
  ];

  for (let i = 0; i < cards.length; i++) {
    const card = cards[i];
    const name = names[i];

    console.log(`📸 Capturing: ${name}.png`);

    await page.evaluate(el => {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, card);

    await new Promise(r => setTimeout(r, 300));

    await card.screenshot({
      path: resolve(outputDir, `${name}.png`),
      type: 'png'
    });

    console.log(`   ✅ Saved\n`);
  }

  // Full page screenshot
  console.log('📸 Capturing full page...');
  await page.screenshot({
    path: resolve(outputDir, 'all-cards.png'),
    type: 'png',
    fullPage: true
  });
  console.log('   ✅ Saved\n');

  await browser.close();

  console.log('✨ Complete!\n');
  console.log(`📁 Output: ${outputDir}\n`);
  console.log('Generated files:');
  readdirSync(outputDir).forEach(file => {
    const stats = statSync(resolve(outputDir, file));
    console.log(`   • ${file} (${(stats.size / 1024 / 1024).toFixed(2)} MB)`);
  });
}

generateScreenshots().catch(err => {
  console.error('❌ Error:', err.message);
  process.exit(1);
});
