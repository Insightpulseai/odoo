/**
 * Retail-Intel (SariCoach/Scout) Engine Seeder
 *
 * Seeds dimension tables, reference data, and demo analytics for retail intelligence.
 *
 * Usage:
 *   npx tsx tools/seed_retail_intel.ts
 *   npx tsx tools/seed_retail_intel.ts --dry-run
 */

import { createClient, SupabaseClient } from '@supabase/supabase-js';

// ============================================================================
// TYPES
// ============================================================================

interface SeedContext {
  supabase: SupabaseClient;
  tenantId: string;
  environment: 'dev' | 'staging' | 'prod';
  dryRun: boolean;
}

// ============================================================================
// REFERENCE DATA
// ============================================================================

const BRANDS = [
  { brand_code: 'NESTLE', name: 'Nestlé', category: 'FMCG' },
  { brand_code: 'UNILEVER', name: 'Unilever', category: 'FMCG' },
  { brand_code: 'PG', name: 'Procter & Gamble', category: 'FMCG' },
  { brand_code: 'COKE', name: 'Coca-Cola', category: 'Beverages' },
  { brand_code: 'PEPSI', name: 'PepsiCo', category: 'Beverages' },
  { brand_code: 'SMC', name: 'San Miguel Corporation', category: 'Beverages' },
  { brand_code: 'URC', name: 'Universal Robina', category: 'Snacks' },
  { brand_code: 'MONDE', name: 'Monde Nissin', category: 'Snacks' },
];

const PRODUCT_CATEGORIES = [
  { code: 'BEV', name: 'Beverages' },
  { code: 'SNACKS', name: 'Snacks & Confectionery' },
  { code: 'DAIRY', name: 'Dairy & Refrigerated' },
  { code: 'PERS', name: 'Personal Care' },
  { code: 'HOME', name: 'Home Care' },
  { code: 'GROC', name: 'Grocery & Pantry' },
];

const REGIONS = [
  { code: 'NCR', name: 'National Capital Region' },
  { code: 'CAR', name: 'Cordillera Administrative Region' },
  { code: 'I', name: 'Ilocos Region' },
  { code: 'II', name: 'Cagayan Valley' },
  { code: 'III', name: 'Central Luzon' },
  { code: 'IV-A', name: 'CALABARZON' },
  { code: 'IV-B', name: 'MIMAROPA' },
  { code: 'V', name: 'Bicol Region' },
  { code: 'VI', name: 'Western Visayas' },
  { code: 'VII', name: 'Central Visayas' },
];

// ============================================================================
// UTILITIES
// ============================================================================

function log(message: string, ...args: unknown[]) {
  console.log(`[Retail-Intel Seed] ${message}`, ...args);
}

async function upsertMany<T extends Record<string, unknown>>(
  ctx: SeedContext,
  table: string,
  records: T[],
  conflictColumns: string[] = ['id']
): Promise<void> {
  if (ctx.dryRun) {
    log(`[DRY RUN] Would upsert ${records.length} records to ${table}`);
    return;
  }

  const { error } = await ctx.supabase
    .from(table)
    .upsert(records, { onConflict: conflictColumns.join(',') });

  if (error) {
    throw new Error(`Failed to upsert to ${table}: ${error.message}`);
  }

  log(`Upserted ${records.length} records to ${table}`);
}

function randomChoice<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)];
}

// ============================================================================
// SEED FUNCTIONS
// ============================================================================

async function seedBrands(ctx: SeedContext): Promise<void> {
  log('Seeding brands...');

  const records = BRANDS.map(brand => ({
    tenant_id: ctx.tenantId,
    ...brand,
    is_active: true,
  }));

  await upsertMany(ctx, 'dim.brands', records, ['tenant_id', 'brand_code']);
}

async function seedProductCategories(ctx: SeedContext): Promise<void> {
  log('Seeding product categories...');

  const records = PRODUCT_CATEGORIES.map(cat => ({
    tenant_id: ctx.tenantId,
    ...cat,
  }));

  await upsertMany(ctx, 'dim.product_categories', records, ['tenant_id', 'code']);
}

async function seedDemoStores(ctx: SeedContext): Promise<void> {
  if (ctx.environment === 'prod') {
    log('Skipping demo stores in production');
    return;
  }

  log('Seeding demo stores...');

  const storeTypes = ['sari-sari', 'mini-mart', 'grocery'];
  const cities = ['Manila', 'Quezon City', 'Makati', 'Cebu City', 'Davao City'];

  const stores = Array.from({ length: 100 }, (_, idx) => ({
    tenant_id: ctx.tenantId,
    external_store_code: `STORE-DEMO-${String(idx + 1).padStart(4, '0')}`,
    name: `Demo Store ${idx + 1}`,
    store_type: randomChoice(storeTypes),
    region: randomChoice(REGIONS).code,
    city: randomChoice(cities),
    barangay: `Barangay ${Math.floor(Math.random() * 50) + 1}`,
    latitude: 14.5 + Math.random() * 2,
    longitude: 120.9 + Math.random() * 1,
    is_active: true,
  }));

  await upsertMany(ctx, 'dim.stores', stores, ['tenant_id', 'external_store_code']);
}

async function seedDemoProducts(ctx: SeedContext): Promise<void> {
  if (ctx.environment === 'prod') {
    log('Skipping demo products in production');
    return;
  }

  log('Seeding demo products...');

  const products = BRANDS.flatMap((brand, brandIdx) =>
    Array.from({ length: 10 }, (_, idx) => ({
      tenant_id: ctx.tenantId,
      sku_code: `${brand.brand_code}-SKU-${String(idx + 1).padStart(3, '0')}`,
      name: `${brand.name} Product ${idx + 1}`,
      brand_code: brand.brand_code,
      category_code: randomChoice(PRODUCT_CATEGORIES).code,
      unit_price: Math.floor(Math.random() * 200) + 10,
      is_active: true,
    }))
  );

  await upsertMany(ctx, 'dim.products', products, ['tenant_id', 'sku_code']);
}

async function seedDemoSalesDaily(ctx: SeedContext): Promise<void> {
  if (ctx.environment === 'prod') {
    log('Skipping demo sales in production');
    return;
  }

  log('Seeding demo daily sales (this may take a moment)...');

  // Generate 30 days of sales for 100 stores
  const today = new Date();
  const sales: Record<string, unknown>[] = [];

  for (let dayOffset = 0; dayOffset < 30; dayOffset++) {
    const date = new Date(today);
    date.setDate(date.getDate() - dayOffset);
    const dateStr = date.toISOString().split('T')[0];

    for (let storeIdx = 0; storeIdx < 100; storeIdx++) {
      const storeCode = `STORE-DEMO-${String(storeIdx + 1).padStart(4, '0')}`;
      const brand = randomChoice(BRANDS);

      sales.push({
        tenant_id: ctx.tenantId,
        store_code: storeCode,
        brand_code: brand.brand_code,
        date: dateStr,
        units_sold: Math.floor(Math.random() * 50) + 5,
        revenue: Math.floor(Math.random() * 5000) + 500,
        transactions: Math.floor(Math.random() * 20) + 3,
      });
    }
  }

  // Insert in batches to avoid timeout
  const batchSize = 500;
  for (let i = 0; i < sales.length; i += batchSize) {
    const batch = sales.slice(i, i + batchSize);
    await upsertMany(ctx, 'analytics.sales_daily', batch, ['tenant_id', 'store_code', 'brand_code', 'date']);
  }
}

async function seedExternalIndices(ctx: SeedContext): Promise<void> {
  if (ctx.environment === 'prod') {
    log('Skipping external indices in production');
    return;
  }

  log('Seeding external indices (weather, holidays)...');

  const today = new Date();
  const indices: Record<string, unknown>[] = [];

  for (let dayOffset = 0; dayOffset < 30; dayOffset++) {
    const date = new Date(today);
    date.setDate(date.getDate() - dayOffset);
    const dateStr = date.toISOString().split('T')[0];

    for (const region of REGIONS) {
      // Weather index
      indices.push({
        tenant_id: ctx.tenantId,
        agg_level: 'region',
        agg_key: region.code,
        date: dateStr,
        index_name: 'weather_temp_avg',
        index_value: 28 + Math.random() * 6, // 28-34°C
      });

      indices.push({
        tenant_id: ctx.tenantId,
        agg_level: 'region',
        agg_key: region.code,
        date: dateStr,
        index_name: 'weather_rain_mm',
        index_value: Math.random() > 0.7 ? Math.random() * 50 : 0,
      });
    }
  }

  await upsertMany(ctx, 'intel.external_indices_daily', indices, ['tenant_id', 'agg_level', 'agg_key', 'date', 'index_name']);
}

// ============================================================================
// MAIN
// ============================================================================

async function main(): Promise<void> {
  const supabaseUrl = process.env.SUPABASE_URL;
  const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
  const tenantId = process.env.SEED_TENANT_ID;

  if (!supabaseUrl || !supabaseKey || !tenantId) {
    console.error('Missing required environment variables');
    process.exit(1);
  }

  const supabase = createClient(supabaseUrl, supabaseKey);

  const ctx: SeedContext = {
    supabase,
    tenantId,
    environment: (process.env.NODE_ENV as SeedContext['environment']) || 'dev',
    dryRun: process.argv.includes('--dry-run'),
  };

  log(`Starting Retail-Intel seed (env: ${ctx.environment}, dry-run: ${ctx.dryRun})`);

  try {
    // Reference data
    await seedBrands(ctx);
    await seedProductCategories(ctx);

    // Demo data
    await seedDemoStores(ctx);
    await seedDemoProducts(ctx);
    await seedDemoSalesDaily(ctx);
    await seedExternalIndices(ctx);

    log('Retail-Intel seeding complete!');
  } catch (error) {
    console.error('Seed failed:', error);
    process.exit(1);
  }
}

main();
