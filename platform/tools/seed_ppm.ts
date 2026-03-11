/**
 * PPM (Project Portfolio Management) Engine Seeder
 *
 * Seeds project reference data and demo projects.
 *
 * Usage:
 *   npx tsx tools/seed_ppm.ts
 *   npx tsx tools/seed_ppm.ts --dry-run
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

const PROJECT_STAGES = [
  { code: 'DRAFT', name: 'Draft', sequence: 10 },
  { code: 'PLANNING', name: 'Planning', sequence: 20 },
  { code: 'ACTIVE', name: 'In Progress', sequence: 30 },
  { code: 'REVIEW', name: 'Under Review', sequence: 40 },
  { code: 'COMPLETED', name: 'Completed', sequence: 50 },
  { code: 'CANCELLED', name: 'Cancelled', sequence: 60 },
];

const BUDGET_CATEGORIES = [
  { code: 'LABOR', name: 'Labor & Personnel' },
  { code: 'MATERIALS', name: 'Materials & Supplies' },
  { code: 'EQUIPMENT', name: 'Equipment & Tools' },
  { code: 'TRAVEL', name: 'Travel & Transportation' },
  { code: 'SERVICES', name: 'Professional Services' },
  { code: 'OVERHEAD', name: 'Overhead & Admin' },
  { code: 'CONTINGENCY', name: 'Contingency' },
];

const PROJECT_ROLES = [
  { code: 'PM', name: 'Project Manager', is_lead: true },
  { code: 'TECH_LEAD', name: 'Technical Lead', is_lead: true },
  { code: 'ANALYST', name: 'Business Analyst', is_lead: false },
  { code: 'DEV', name: 'Developer', is_lead: false },
  { code: 'QA', name: 'QA Engineer', is_lead: false },
  { code: 'DESIGNER', name: 'Designer', is_lead: false },
];

// ============================================================================
// UTILITIES
// ============================================================================

function log(message: string, ...args: unknown[]) {
  console.log(`[PPM Seed] ${message}`, ...args);
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

function addDays(date: Date, days: number): Date {
  const result = new Date(date);
  result.setDate(result.getDate() + days);
  return result;
}

// ============================================================================
// SEED FUNCTIONS
// ============================================================================

async function seedProjectStages(ctx: SeedContext): Promise<void> {
  log('Seeding project stages...');

  const records = PROJECT_STAGES.map(stage => ({
    tenant_id: ctx.tenantId,
    ...stage,
  }));

  await upsertMany(ctx, 'ref.project_stages', records, ['tenant_id', 'code']);
}

async function seedBudgetCategories(ctx: SeedContext): Promise<void> {
  log('Seeding budget categories...');

  const records = BUDGET_CATEGORIES.map(cat => ({
    tenant_id: ctx.tenantId,
    ...cat,
  }));

  await upsertMany(ctx, 'ref.budget_categories', records, ['tenant_id', 'code']);
}

async function seedProjectRoles(ctx: SeedContext): Promise<void> {
  log('Seeding project roles...');

  const records = PROJECT_ROLES.map(role => ({
    tenant_id: ctx.tenantId,
    ...role,
  }));

  await upsertMany(ctx, 'ref.project_roles', records, ['tenant_id', 'code']);
}

async function seedDemoProjects(ctx: SeedContext): Promise<void> {
  if (ctx.environment === 'prod') {
    log('Skipping demo projects in production');
    return;
  }

  log('Seeding demo projects...');

  const projectNames = [
    'Digital Transformation Initiative',
    'Customer Portal Redesign',
    'ERP Migration Phase 1',
    'Mobile App Development',
    'Data Analytics Platform',
    'Security Enhancement Program',
    'Process Automation',
    'Cloud Migration',
    'API Integration Hub',
    'Employee Experience Platform',
  ];

  const today = new Date();
  const projects = projectNames.map((name, idx) => {
    const startOffset = Math.floor(Math.random() * 90) - 45; // -45 to +45 days
    const duration = Math.floor(Math.random() * 180) + 30; // 30 to 210 days
    const startDate = addDays(today, startOffset);
    const endDate = addDays(startDate, duration);

    return {
      tenant_id: ctx.tenantId,
      project_code: `PRJ-DEMO-${String(idx + 1).padStart(3, '0')}`,
      name,
      description: `Demo project: ${name}. This is a sample project for testing purposes.`,
      status: randomChoice(['draft', 'active', 'active', 'active', 'completed']),
      start_date: startDate.toISOString().split('T')[0],
      end_date: endDate.toISOString().split('T')[0],
      budget_amount: Math.floor(Math.random() * 5000000) + 500000,
      budget_currency: 'PHP',
    };
  });

  await upsertMany(ctx, 'projects.projects', projects, ['tenant_id', 'project_code']);
}

async function seedDemoProjectBudgets(ctx: SeedContext): Promise<void> {
  if (ctx.environment === 'prod') {
    log('Skipping demo project budgets in production');
    return;
  }

  log('Seeding demo project budgets...');

  // Get demo projects
  const { data: projects, error } = await ctx.supabase
    .from('projects.projects')
    .select('id, project_code, budget_amount')
    .eq('tenant_id', ctx.tenantId)
    .like('project_code', 'PRJ-DEMO-%');

  if (error || !projects) {
    log('No demo projects found, skipping budgets');
    return;
  }

  const budgets: Record<string, unknown>[] = [];

  for (const project of projects) {
    let remainingBudget = project.budget_amount || 1000000;

    for (const category of BUDGET_CATEGORIES.slice(0, -1)) { // Exclude contingency
      const allocation = Math.floor(remainingBudget * (0.1 + Math.random() * 0.2));
      remainingBudget -= allocation;

      budgets.push({
        tenant_id: ctx.tenantId,
        project_id: project.id,
        category_code: category.code,
        allocated_amount: allocation,
        spent_amount: Math.floor(allocation * Math.random() * 0.8),
        currency: 'PHP',
      });
    }

    // Contingency gets the rest
    budgets.push({
      tenant_id: ctx.tenantId,
      project_id: project.id,
      category_code: 'CONTINGENCY',
      allocated_amount: remainingBudget,
      spent_amount: 0,
      currency: 'PHP',
    });
  }

  await upsertMany(ctx, 'projects.project_budgets', budgets, ['tenant_id', 'project_id', 'category_code']);
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

  log(`Starting PPM seed (env: ${ctx.environment}, dry-run: ${ctx.dryRun})`);

  try {
    // Reference data
    await seedProjectStages(ctx);
    await seedBudgetCategories(ctx);
    await seedProjectRoles(ctx);

    // Demo data
    await seedDemoProjects(ctx);
    await seedDemoProjectBudgets(ctx);

    log('PPM seeding complete!');
  } catch (error) {
    console.error('Seed failed:', error);
    process.exit(1);
  }
}

main();
