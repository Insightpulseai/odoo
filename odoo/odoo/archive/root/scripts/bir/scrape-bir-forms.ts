#!/usr/bin/env tsx
/**
 * BIR Forms Registry Scraper
 *
 * Scrapes bir.gov.ph/bir-forms to populate registry.bir_forms table
 * Portfolio Initiative: PORT-2026-011
 * Evidence: EVID-20260212-006
 *
 * Usage:
 *   pnpm --filter scripts tsx scripts/bir/scrape-bir-forms.ts
 *   node --loader tsx scripts/bir/scrape-bir-forms.ts
 */

import { chromium, type Browser, type Page } from 'playwright';
import { createClient } from '@supabase/supabase-js';
import * as fs from 'fs';
import * as path from 'path';

// Configuration
const BIR_FORMS_URL = 'https://www.bir.gov.ph/bir-forms';
const SUPABASE_URL = process.env.SUPABASE_URL || 'https://spdtwktxdalcfigzeqrz.supabase.co';
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;
const SCREENSHOT_DIR = path.join(__dirname, '../../docs/evidence/20260212-2000/bir-forms-registry');
const MAX_RETRIES = 3;
const RETRY_DELAY_MS = 2000;

// Types
interface BIRForm {
    form_code: string;
    title: string;
    description?: string;
    category?: string;
    file_url?: string;
    last_updated: string;
    metadata: {
        scraped_at: string;
        source_url: string;
        scraper_version: string;
        [key: string]: any;
    };
}

interface ScraperResult {
    success: boolean;
    forms_count: number;
    errors: string[];
    screenshot_path?: string;
}

// Supabase client
const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY!, {
    auth: { persistSession: false }
});

/**
 * Scrape BIR forms from website
 */
async function scrapeBIRForms(): Promise<ScraperResult> {
    let browser: Browser | null = null;
    let page: Page | null = null;
    const errors: string[] = [];
    const forms: BIRForm[] = [];

    try {
        console.log(`[INFO] Starting BIR forms scraper`);
        console.log(`[INFO] Target URL: ${BIR_FORMS_URL}`);

        // Launch browser
        browser = await chromium.launch({
            headless: true,
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });

        page = await browser.newPage();
        page.setDefaultTimeout(30000);

        // Navigate to BIR forms page
        console.log(`[INFO] Navigating to BIR forms page...`);
        const response = await page.goto(BIR_FORMS_URL, {
            waitUntil: 'networkidle'
        });

        if (!response || !response.ok()) {
            throw new Error(`Failed to load page: ${response?.status()}`);
        }

        // Wait for content to render (BIR website uses JavaScript)
        console.log(`[INFO] Waiting for page content to render...`);
        await page.waitForSelector('body', { state: 'visible' });
        await page.waitForTimeout(3000); // Additional wait for JS rendering

        // Extract forms data
        console.log(`[INFO] Extracting forms data...`);
        const extractedForms = await page.evaluate(() => {
            const formsData: Array<{
                form_code: string;
                title: string;
                description?: string;
                category?: string;
                file_url?: string;
            }> = [];

            // Strategy 1: Look for table rows with form data
            const tables = document.querySelectorAll('table');
            tables.forEach(table => {
                const rows = table.querySelectorAll('tr');
                rows.forEach(row => {
                    const cells = row.querySelectorAll('td');
                    if (cells.length >= 2) {
                        const formCode = cells[0]?.textContent?.trim() || '';
                        const title = cells[1]?.textContent?.trim() || '';
                        const link = row.querySelector('a')?.href;

                        if (formCode && title) {
                            formsData.push({
                                form_code: formCode,
                                title: title,
                                file_url: link,
                                category: cells[2]?.textContent?.trim()
                            });
                        }
                    }
                });
            });

            // Strategy 2: Look for links with BIR form patterns
            if (formsData.length === 0) {
                const links = document.querySelectorAll('a[href*=".pdf"], a[href*=".xls"], a[href*=".xlsx"]');
                links.forEach(link => {
                    const text = link.textContent?.trim() || '';
                    const href = (link as HTMLAnchorElement).href;

                    // Extract form code from text (e.g., "1601-C", "2550Q")
                    const formCodeMatch = text.match(/\b\d{4}[A-Z-]*\b/);
                    if (formCodeMatch) {
                        formsData.push({
                            form_code: formCodeMatch[0],
                            title: text,
                            file_url: href
                        });
                    }
                });
            }

            // Strategy 3: Look for divs/lists with form information
            if (formsData.length === 0) {
                const formElements = document.querySelectorAll('div[class*="form"], li[class*="form"]');
                formElements.forEach(elem => {
                    const text = elem.textContent?.trim() || '';
                    const formCodeMatch = text.match(/\b\d{4}[A-Z-]*\b/);
                    const link = elem.querySelector('a')?.href;

                    if (formCodeMatch) {
                        formsData.push({
                            form_code: formCodeMatch[0],
                            title: text,
                            file_url: link
                        });
                    }
                });
            }

            return formsData;
        });

        console.log(`[INFO] Extracted ${extractedForms.length} forms from page`);

        // Transform to canonical schema
        const timestamp = new Date().toISOString();
        extractedForms.forEach(form => {
            forms.push({
                form_code: form.form_code,
                title: form.title,
                description: form.description,
                category: form.category || categorizeForm(form.form_code),
                file_url: form.file_url,
                last_updated: timestamp,
                metadata: {
                    scraped_at: timestamp,
                    source_url: BIR_FORMS_URL,
                    scraper_version: '1.0.0'
                }
            });
        });

        // Take screenshot for evidence
        const screenshotPath = path.join(SCREENSHOT_DIR, `scrape-${Date.now()}.png`);
        await page.screenshot({ path: screenshotPath, fullPage: true });
        console.log(`[INFO] Screenshot saved: ${screenshotPath}`);

        // Close browser
        await browser.close();

        // Upsert to Supabase
        if (forms.length > 0) {
            console.log(`[INFO] Upserting ${forms.length} forms to Supabase...`);
            const { data, error } = await supabase
                .from('registry.bir_forms')
                .upsert(forms, { onConflict: 'form_code' });

            if (error) {
                console.error(`[ERROR] Supabase upsert failed:`, error);
                errors.push(`Supabase upsert failed: ${error.message}`);
            } else {
                console.log(`[SUCCESS] Upserted ${forms.length} forms successfully`);
            }
        } else {
            console.warn(`[WARN] No forms extracted - check page structure`);
            errors.push('No forms extracted from page');
        }

        return {
            success: errors.length === 0,
            forms_count: forms.length,
            errors,
            screenshot_path: screenshotPath
        };

    } catch (error) {
        const errorMsg = error instanceof Error ? error.message : String(error);
        console.error(`[ERROR] Scraper failed:`, errorMsg);
        errors.push(errorMsg);

        // Take failure screenshot
        if (page) {
            try {
                const failureScreenshot = path.join(SCREENSHOT_DIR, `failure-${Date.now()}.png`);
                await page.screenshot({ path: failureScreenshot, fullPage: true });
                console.log(`[INFO] Failure screenshot saved: ${failureScreenshot}`);
            } catch (screenshotError) {
                console.error(`[ERROR] Failed to capture screenshot:`, screenshotError);
            }
        }

        return {
            success: false,
            forms_count: 0,
            errors
        };
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}

/**
 * Categorize form by code pattern
 */
function categorizeForm(formCode: string): string {
    if (formCode.startsWith('1601')) return 'Withholding Tax';
    if (formCode.startsWith('1602')) return 'Withholding Tax';
    if (formCode.startsWith('1603')) return 'Withholding Tax';
    if (formCode.startsWith('1604')) return 'Withholding Tax';
    if (formCode.startsWith('1606')) return 'Withholding Tax';
    if (formCode.startsWith('1702')) return 'Income Tax';
    if (formCode.startsWith('1701')) return 'Income Tax';
    if (formCode.startsWith('2550')) return 'VAT';
    if (formCode.startsWith('2551')) return 'Percentage Tax';
    return 'Other';
}

/**
 * Retry wrapper with exponential backoff
 */
async function retryWithBackoff<T>(
    fn: () => Promise<T>,
    retries: number = MAX_RETRIES,
    delay: number = RETRY_DELAY_MS
): Promise<T> {
    try {
        return await fn();
    } catch (error) {
        if (retries <= 1) throw error;

        console.log(`[RETRY] Retrying in ${delay}ms... (${retries - 1} retries left)`);
        await new Promise(resolve => setTimeout(resolve, delay));
        return retryWithBackoff(fn, retries - 1, delay * 2);
    }
}

/**
 * Main execution
 */
async function main() {
    // Ensure screenshot directory exists
    if (!fs.existsSync(SCREENSHOT_DIR)) {
        fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
    }

    // Validate environment variables
    if (!SUPABASE_SERVICE_ROLE_KEY) {
        console.error('[ERROR] SUPABASE_SERVICE_ROLE_KEY environment variable not set');
        process.exit(1);
    }

    // Run scraper with retry logic
    const result = await retryWithBackoff(scrapeBIRForms);

    // Write result log
    const logPath = path.join(SCREENSHOT_DIR, `scrape-log-${Date.now()}.json`);
    fs.writeFileSync(logPath, JSON.stringify(result, null, 2));
    console.log(`[INFO] Result log saved: ${logPath}`);

    // Verify data
    const { count, error } = await supabase
        .from('registry.bir_forms')
        .select('*', { count: 'exact', head: true });

    if (error) {
        console.error(`[ERROR] Verification query failed:`, error);
    } else {
        console.log(`[INFO] Total forms in registry: ${count}`);
    }

    // Exit with appropriate code
    process.exit(result.success ? 0 : 1);
}

// Execute
main().catch(error => {
    console.error('[FATAL]', error);
    process.exit(1);
});
