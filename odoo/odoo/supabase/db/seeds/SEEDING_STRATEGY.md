# Database Seeding Strategy

**Version:** 1.0.0
**Last Updated:** 2025-12-07

---

## 1. Overview

This document defines the seeding strategy for InsightPulseAI engines. Each engine has its own seed script that populates reference data, test fixtures, and demo data.

---

## 2. Seeding Principles

1. **Idempotent** — Running a seed multiple times produces the same result
2. **Environment-aware** — Different data for dev/staging/prod
3. **Engine-scoped** — Each engine manages its own seeds
4. **Order-independent** — Seeds should handle dependencies gracefully

---

## 3. Seed Categories

| Category | Description | Environments |
|----------|-------------|--------------|
| **Reference** | Lookup tables, categories, policies | All |
| **Config** | Engine configuration, feature flags | All |
| **Demo** | Sample data for testing/demos | Dev, Staging |
| **Fixtures** | Test fixtures for automated testing | Dev only |

---

## 4. Seed Scripts

### 4.1 Entry Points

```bash
# Seed all engines
npm run db:seed

# Seed specific engine
npm run db:seed:te-cheq
npm run db:seed:retail-intel
npm run db:seed:ppm
npm run db:seed:doc-ocr
```

### 4.2 Package.json Scripts

```json
{
  "scripts": {
    "db:seed": "tsx tools/seed_all.ts",
    "db:seed:te-cheq": "tsx tools/seed_te_cheq.ts",
    "db:seed:retail-intel": "tsx tools/seed_retail_intel.ts",
    "db:seed:ppm": "tsx tools/seed_ppm.ts",
    "db:seed:doc-ocr": "tsx tools/seed_doc_ocr.ts"
  }
}
```

---

## 5. Seed Data by Engine

### 5.1 TE-Cheq (Travel & Expense)

**Reference Data:**
- `ref.expense_policies` — Expense policy rules
- `ref.expense_categories` — Category master
- `ref.cost_centers` — Cost center hierarchy
- `ref.currencies` — Currency master (PHP, USD, EUR)

**Demo Data (dev/staging):**
- Sample expense reports (5 per status)
- Sample cash advances (10 records)
- Sample receipts with OCR data

**Seed Order:**
1. `ref.currencies`
2. `ref.cost_centers`
3. `ref.expense_categories`
4. `ref.expense_policies`
5. Demo expense reports

---

### 5.2 Retail-Intel (SariCoach/Scout)

**Reference Data:**
- `dim.brands` — Brand master
- `dim.products` — Product/SKU master
- `dim.stores` — Store dimension seed

**Demo Data (dev/staging):**
- Sample stores (100 records)
- Sample daily sales (30 days × 100 stores)
- External indices (weather, holidays)
- Sample recommendations

**Seed Order:**
1. `dim.brands`
2. `dim.products`
3. `dim.stores`
4. `analytics.sales_daily`
5. `intel.external_indices_daily`

---

### 5.3 PPM (Project Portfolio)

**Reference Data:**
- Project status stages
- Budget category codes
- Role definitions

**Demo Data (dev/staging):**
- Sample projects (10 records)
- Project members
- Budget allocations

---

### 5.4 Doc-OCR (Document Processing)

**Reference Data:**
- Parser profiles
- Document type definitions
- Field extraction templates

**Demo Data (dev/staging):**
- Sample parsed documents
- Confidence score distributions

---

## 6. Seed Script Structure

### 6.1 Base Seed Function

```typescript
// tools/lib/seed_utils.ts
import { createClient } from '@supabase/supabase-js';

export interface SeedContext {
  supabase: SupabaseClient;
  tenantId: string;
  environment: 'dev' | 'staging' | 'prod';
  dryRun: boolean;
}

export async function runSeed(
  name: string,
  fn: (ctx: SeedContext) => Promise<void>,
  ctx: SeedContext
): Promise<void> {
  console.log(`[${name}] Starting seed...`);
  const start = Date.now();

  try {
    await fn(ctx);
    console.log(`[${name}] Completed in ${Date.now() - start}ms`);
  } catch (error) {
    console.error(`[${name}] Failed:`, error);
    throw error;
  }
}

export async function upsertMany<T extends { id?: string }>(
  ctx: SeedContext,
  table: string,
  records: T[],
  conflictColumns: string[] = ['id']
): Promise<void> {
  if (ctx.dryRun) {
    console.log(`[DRY RUN] Would upsert ${records.length} records to ${table}`);
    return;
  }

  const { error } = await ctx.supabase
    .from(table)
    .upsert(records, { onConflict: conflictColumns.join(',') });

  if (error) throw error;
  console.log(`Upserted ${records.length} records to ${table}`);
}
```

### 6.2 Engine Seed Template

```typescript
// tools/seed_te_cheq.ts
import { createClient } from '@supabase/supabase-js';
import { runSeed, upsertMany, SeedContext } from './lib/seed_utils';

// Reference data
const CURRENCIES = [
  { code: 'PHP', name: 'Philippine Peso', symbol: '₱' },
  { code: 'USD', name: 'US Dollar', symbol: '$' },
  { code: 'EUR', name: 'Euro', symbol: '€' },
];

const EXPENSE_CATEGORIES = [
  { code: 'MEALS', name: 'Meals & Entertainment', max_amount: 1500 },
  { code: 'TRAVEL', name: 'Travel & Transportation', max_amount: 5000 },
  { code: 'LODGING', name: 'Lodging', max_amount: 8000 },
  { code: 'SUPPLIES', name: 'Office Supplies', max_amount: 2000 },
  { code: 'OTHER', name: 'Other', max_amount: null },
];

async function seedCurrencies(ctx: SeedContext) {
  await upsertMany(ctx, 'ref.currencies', CURRENCIES, ['code']);
}

async function seedExpenseCategories(ctx: SeedContext) {
  const records = EXPENSE_CATEGORIES.map(cat => ({
    tenant_id: ctx.tenantId,
    ...cat,
  }));
  await upsertMany(ctx, 'ref.expense_categories', records, ['tenant_id', 'code']);
}

async function seedExpensePolicies(ctx: SeedContext) {
  const policies = [
    {
      tenant_id: ctx.tenantId,
      policy_code: 'DEFAULT',
      name: 'Default Policy',
      requires_receipt_above: 500,
      requires_approval_above: 5000,
      is_active: true,
    },
    {
      tenant_id: ctx.tenantId,
      policy_code: 'EXEC',
      name: 'Executive Policy',
      requires_receipt_above: 1000,
      requires_approval_above: 10000,
      is_active: true,
    },
  ];
  await upsertMany(ctx, 'ref.expense_policies', policies, ['tenant_id', 'policy_code']);
}

async function seedDemoExpenseReports(ctx: SeedContext) {
  if (ctx.environment === 'prod') {
    console.log('Skipping demo data in production');
    return;
  }

  // Create sample expense reports
  const statuses = ['draft', 'submitted', 'approved', 'rejected', 'paid'];
  const reports = statuses.flatMap((status, i) =>
    Array.from({ length: 5 }, (_, j) => ({
      tenant_id: ctx.tenantId,
      report_number: `EXP-${status.toUpperCase()}-${j + 1}`,
      description: `Sample ${status} expense report ${j + 1}`,
      status,
      total_amount: Math.floor(Math.random() * 10000) + 1000,
      currency: 'PHP',
    }))
  );

  await upsertMany(ctx, 'expense.expense_reports', reports, ['tenant_id', 'report_number']);
}

// Main seed function
async function main() {
  const supabase = createClient(
    process.env.SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!
  );

  const ctx: SeedContext = {
    supabase,
    tenantId: process.env.SEED_TENANT_ID || 'default-tenant-uuid',
    environment: (process.env.NODE_ENV as any) || 'dev',
    dryRun: process.argv.includes('--dry-run'),
  };

  await runSeed('currencies', seedCurrencies, ctx);
  await runSeed('expense-categories', seedExpenseCategories, ctx);
  await runSeed('expense-policies', seedExpensePolicies, ctx);
  await runSeed('demo-expense-reports', seedDemoExpenseReports, ctx);

  console.log('TE-Cheq seeding complete!');
}

main().catch(console.error);
```

---

## 7. Environment Configuration

### 7.1 Environment Variables

```bash
# .env.seed
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SEED_TENANT_ID=your-tenant-uuid
NODE_ENV=dev  # dev | staging | prod
```

### 7.2 Environment-Specific Behavior

| Setting | Dev | Staging | Prod |
|---------|-----|---------|------|
| Demo data | ✅ | ✅ | ❌ |
| Fixtures | ✅ | ❌ | ❌ |
| Volume | Low | Medium | Minimal |
| Real UUIDs | ❌ | ✅ | ✅ |

---

## 8. Running Seeds

### 8.1 Development

```bash
# Full seed
npm run db:seed

# Specific engine
npm run db:seed:te-cheq

# Dry run (no actual writes)
npm run db:seed:te-cheq -- --dry-run
```

### 8.2 CI/CD

```yaml
# .github/workflows/seed.yml
name: Database Seed

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        required: true
        type: choice
        options:
          - dev
          - staging
      engine:
        description: 'Engine to seed (or "all")'
        required: true
        default: 'all'

jobs:
  seed:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npm run db:seed:${{ inputs.engine }}
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_KEY }}
          NODE_ENV: ${{ inputs.environment }}
```

---

## 9. Validation

### 9.1 Post-Seed Checks

```typescript
// tools/validate_seed.ts
async function validateSeed(ctx: SeedContext) {
  const checks = [
    { table: 'ref.currencies', minCount: 3 },
    { table: 'ref.expense_categories', minCount: 5 },
    { table: 'ref.expense_policies', minCount: 1 },
  ];

  for (const check of checks) {
    const { count, error } = await ctx.supabase
      .from(check.table)
      .select('*', { count: 'exact', head: true });

    if (error) throw error;
    if ((count || 0) < check.minCount) {
      throw new Error(`${check.table} has ${count} rows, expected >= ${check.minCount}`);
    }
    console.log(`✅ ${check.table}: ${count} rows`);
  }
}
```

---

## 10. Related Documents

- [DB_TARGET_ARCHITECTURE.md](../DB_TARGET_ARCHITECTURE.md)
- [Engine Specs](../../engines/)
- [Migration Files](../migrations/)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-07 | Initial release |
