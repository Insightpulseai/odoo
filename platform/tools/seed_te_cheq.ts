/**
 * TE-Cheq (Travel & Expense) Engine Seeder
 *
 * Seeds reference data, policies, and demo data for the TE-Cheq engine.
 *
 * Usage:
 *   npx tsx tools/seed_te_cheq.ts
 *   npx tsx tools/seed_te_cheq.ts --dry-run
 *
 * Environment variables:
 *   SUPABASE_URL - Supabase project URL
 *   SUPABASE_SERVICE_ROLE_KEY - Service role key for admin access
 *   SEED_TENANT_ID - Target tenant UUID
 *   NODE_ENV - Environment (dev | staging | prod)
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

const CURRENCIES = [
  { code: 'PHP', name: 'Philippine Peso', symbol: '₱', decimal_places: 2 },
  { code: 'USD', name: 'US Dollar', symbol: '$', decimal_places: 2 },
  { code: 'EUR', name: 'Euro', symbol: '€', decimal_places: 2 },
  { code: 'SGD', name: 'Singapore Dollar', symbol: 'S$', decimal_places: 2 },
  { code: 'JPY', name: 'Japanese Yen', symbol: '¥', decimal_places: 0 },
];

const EXPENSE_CATEGORIES = [
  { code: 'MEALS', name: 'Meals & Entertainment', max_amount: 1500, requires_receipt: true },
  { code: 'TRAVEL', name: 'Travel & Transportation', max_amount: 5000, requires_receipt: true },
  { code: 'LODGING', name: 'Lodging', max_amount: 8000, requires_receipt: true },
  { code: 'AIRFARE', name: 'Airfare', max_amount: 50000, requires_receipt: true },
  { code: 'SUPPLIES', name: 'Office Supplies', max_amount: 2000, requires_receipt: true },
  { code: 'COMMS', name: 'Communications', max_amount: 1000, requires_receipt: false },
  { code: 'PARKING', name: 'Parking & Tolls', max_amount: 500, requires_receipt: false },
  { code: 'OTHER', name: 'Other', max_amount: null, requires_receipt: true },
];

const COST_CENTERS = [
  { code: 'CORP', name: 'Corporate', parent_code: null },
  { code: 'SALES', name: 'Sales & Marketing', parent_code: 'CORP' },
  { code: 'OPS', name: 'Operations', parent_code: 'CORP' },
  { code: 'TECH', name: 'Technology', parent_code: 'CORP' },
  { code: 'FIN', name: 'Finance', parent_code: 'CORP' },
  { code: 'HR', name: 'Human Resources', parent_code: 'CORP' },
];

// ============================================================================
// UTILITIES
// ============================================================================

function log(message: string, ...args: unknown[]) {
  console.log(`[TE-Cheq Seed] ${message}`, ...args);
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

// ============================================================================
// SEED FUNCTIONS
// ============================================================================

async function seedCurrencies(ctx: SeedContext): Promise<void> {
  log('Seeding currencies...');
  await upsertMany(ctx, 'ref.currencies', CURRENCIES, ['code']);
}

async function seedCostCenters(ctx: SeedContext): Promise<void> {
  log('Seeding cost centers...');

  const records = COST_CENTERS.map(cc => ({
    tenant_id: ctx.tenantId,
    ...cc,
  }));

  await upsertMany(ctx, 'ref.cost_centers', records, ['tenant_id', 'code']);
}

async function seedExpenseCategories(ctx: SeedContext): Promise<void> {
  log('Seeding expense categories...');

  const records = EXPENSE_CATEGORIES.map(cat => ({
    tenant_id: ctx.tenantId,
    ...cat,
  }));

  await upsertMany(ctx, 'ref.expense_categories', records, ['tenant_id', 'code']);
}

async function seedExpensePolicies(ctx: SeedContext): Promise<void> {
  log('Seeding expense policies...');

  const policies = [
    {
      tenant_id: ctx.tenantId,
      policy_code: 'DEFAULT',
      name: 'Default Expense Policy',
      description: 'Standard expense policy for all employees',
      requires_receipt_above: 500,
      requires_approval_above: 5000,
      max_daily_meals: 1500,
      max_daily_lodging: 8000,
      is_active: true,
    },
    {
      tenant_id: ctx.tenantId,
      policy_code: 'EXEC',
      name: 'Executive Policy',
      description: 'Enhanced limits for executives',
      requires_receipt_above: 1000,
      requires_approval_above: 10000,
      max_daily_meals: 3000,
      max_daily_lodging: 15000,
      is_active: true,
    },
    {
      tenant_id: ctx.tenantId,
      policy_code: 'INTERN',
      name: 'Intern Policy',
      description: 'Limited policy for interns',
      requires_receipt_above: 100,
      requires_approval_above: 1000,
      max_daily_meals: 500,
      max_daily_lodging: 3000,
      is_active: true,
    },
  ];

  await upsertMany(ctx, 'ref.expense_policies', policies, ['tenant_id', 'policy_code']);
}

async function seedDemoExpenseReports(ctx: SeedContext): Promise<void> {
  if (ctx.environment === 'prod') {
    log('Skipping demo expense reports in production');
    return;
  }

  log('Seeding demo expense reports...');

  const statuses = ['draft', 'submitted', 'approved', 'rejected', 'paid'];
  const reports = statuses.flatMap((status, statusIdx) =>
    Array.from({ length: 5 }, (_, idx) => ({
      tenant_id: ctx.tenantId,
      report_number: `EXP-DEMO-${status.toUpperCase()}-${idx + 1}`,
      description: `Demo ${status} expense report ${idx + 1}`,
      status,
      total_amount: Math.floor(Math.random() * 10000) + 1000,
      currency: 'PHP',
      policy_flagged: Math.random() > 0.8,
      submitted_at: status !== 'draft' ? new Date().toISOString() : null,
      approved_at: ['approved', 'paid'].includes(status) ? new Date().toISOString() : null,
    }))
  );

  await upsertMany(ctx, 'expense.expense_reports', reports, ['tenant_id', 'report_number']);
}

async function seedDemoCashAdvances(ctx: SeedContext): Promise<void> {
  if (ctx.environment === 'prod') {
    log('Skipping demo cash advances in production');
    return;
  }

  log('Seeding demo cash advances...');

  const statuses = ['pending', 'approved', 'disbursed', 'reconciled'];
  const advances = statuses.flatMap((status, _) =>
    Array.from({ length: 3 }, (_, idx) => ({
      tenant_id: ctx.tenantId,
      advance_number: `CA-DEMO-${status.toUpperCase()}-${idx + 1}`,
      amount: Math.floor(Math.random() * 20000) + 5000,
      currency: 'PHP',
      purpose: `Demo ${status} cash advance for business travel`,
      status,
      trip_start_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      trip_end_date: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    }))
  );

  await upsertMany(ctx, 'expense.cash_advances', advances, ['tenant_id', 'advance_number']);
}

// ============================================================================
// MAIN
// ============================================================================

async function main(): Promise<void> {
  const supabaseUrl = process.env.SUPABASE_URL;
  const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
  const tenantId = process.env.SEED_TENANT_ID;

  if (!supabaseUrl || !supabaseKey) {
    console.error('Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY');
    process.exit(1);
  }

  if (!tenantId) {
    console.error('Missing SEED_TENANT_ID');
    process.exit(1);
  }

  const supabase = createClient(supabaseUrl, supabaseKey);

  const ctx: SeedContext = {
    supabase,
    tenantId,
    environment: (process.env.NODE_ENV as SeedContext['environment']) || 'dev',
    dryRun: process.argv.includes('--dry-run'),
  };

  log(`Starting TE-Cheq seed (env: ${ctx.environment}, dry-run: ${ctx.dryRun})`);

  try {
    // Reference data (all environments)
    await seedCurrencies(ctx);
    await seedCostCenters(ctx);
    await seedExpenseCategories(ctx);
    await seedExpensePolicies(ctx);

    // Demo data (dev/staging only)
    await seedDemoExpenseReports(ctx);
    await seedDemoCashAdvances(ctx);

    log('TE-Cheq seeding complete!');
  } catch (error) {
    console.error('Seed failed:', error);
    process.exit(1);
  }
}

main();
