/**
 * Doc-OCR (Document Processing) Engine Seeder
 *
 * Seeds parser profiles, document type definitions, and extraction templates.
 *
 * Usage:
 *   npx tsx tools/seed_doc_ocr.ts
 *   npx tsx tools/seed_doc_ocr.ts --dry-run
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

const DOCUMENT_TYPES = [
  {
    code: 'RECEIPT',
    name: 'Receipt',
    description: 'Purchase receipts from retail establishments',
    category: 'expense',
  },
  {
    code: 'INVOICE',
    name: 'Invoice',
    description: 'Supplier invoices for accounts payable',
    category: 'expense',
  },
  {
    code: 'ID_CARD',
    name: 'ID Card',
    description: 'Government-issued identification cards',
    category: 'identity',
  },
  {
    code: 'BIR_FORM',
    name: 'BIR Form',
    description: 'Bureau of Internal Revenue tax forms',
    category: 'tax',
  },
  {
    code: 'CONTRACT',
    name: 'Contract',
    description: 'Legal contracts and agreements',
    category: 'legal',
  },
  {
    code: 'BANK_STMT',
    name: 'Bank Statement',
    description: 'Bank account statements',
    category: 'finance',
  },
];

const PARSER_PROFILES = [
  {
    code: 'RECEIPT_PH_STANDARD',
    name: 'Philippine Standard Receipt',
    document_type: 'RECEIPT',
    ocr_engine: 'azure_form_recognizer',
    post_processor: 'receipt_ph',
    confidence_threshold: 0.75,
  },
  {
    code: 'RECEIPT_HANDWRITTEN',
    name: 'Handwritten Receipt',
    document_type: 'RECEIPT',
    ocr_engine: 'google_vision',
    post_processor: 'receipt_handwritten',
    confidence_threshold: 0.65,
  },
  {
    code: 'INVOICE_STANDARD',
    name: 'Standard Invoice',
    document_type: 'INVOICE',
    ocr_engine: 'azure_form_recognizer',
    post_processor: 'invoice_standard',
    confidence_threshold: 0.80,
  },
  {
    code: 'ID_PH_NATIONAL',
    name: 'Philippine National ID',
    document_type: 'ID_CARD',
    ocr_engine: 'azure_form_recognizer',
    post_processor: 'id_ph_national',
    confidence_threshold: 0.85,
  },
  {
    code: 'BIR_2307',
    name: 'BIR Form 2307',
    document_type: 'BIR_FORM',
    ocr_engine: 'azure_form_recognizer',
    post_processor: 'bir_2307',
    confidence_threshold: 0.80,
  },
];

const EXTRACTION_FIELDS = {
  RECEIPT: [
    { field_name: 'merchant_name', field_type: 'text', required: true },
    { field_name: 'merchant_tin', field_type: 'text', required: false },
    { field_name: 'merchant_address', field_type: 'text', required: false },
    { field_name: 'transaction_date', field_type: 'date', required: true },
    { field_name: 'total_amount', field_type: 'currency', required: true },
    { field_name: 'vat_amount', field_type: 'currency', required: false },
    { field_name: 'vatable_sales', field_type: 'currency', required: false },
    { field_name: 'receipt_number', field_type: 'text', required: false },
    { field_name: 'payment_method', field_type: 'enum', required: false },
    { field_name: 'line_items', field_type: 'array', required: false },
  ],
  INVOICE: [
    { field_name: 'vendor_name', field_type: 'text', required: true },
    { field_name: 'vendor_tin', field_type: 'text', required: true },
    { field_name: 'invoice_number', field_type: 'text', required: true },
    { field_name: 'invoice_date', field_type: 'date', required: true },
    { field_name: 'due_date', field_type: 'date', required: false },
    { field_name: 'subtotal', field_type: 'currency', required: true },
    { field_name: 'vat_amount', field_type: 'currency', required: false },
    { field_name: 'total_amount', field_type: 'currency', required: true },
    { field_name: 'line_items', field_type: 'array', required: true },
  ],
  ID_CARD: [
    { field_name: 'full_name', field_type: 'text', required: true },
    { field_name: 'date_of_birth', field_type: 'date', required: true },
    { field_name: 'sex', field_type: 'enum', required: true },
    { field_name: 'address', field_type: 'text', required: false },
    { field_name: 'id_number', field_type: 'text', required: true },
    { field_name: 'issue_date', field_type: 'date', required: false },
    { field_name: 'expiry_date', field_type: 'date', required: false },
  ],
};

// ============================================================================
// UTILITIES
// ============================================================================

function log(message: string, ...args: unknown[]) {
  console.log(`[Doc-OCR Seed] ${message}`, ...args);
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

async function seedDocumentTypes(ctx: SeedContext): Promise<void> {
  log('Seeding document types...');

  const records = DOCUMENT_TYPES.map(docType => ({
    tenant_id: ctx.tenantId,
    ...docType,
    is_active: true,
  }));

  await upsertMany(ctx, 'doc.document_types', records, ['tenant_id', 'code']);
}

async function seedParserProfiles(ctx: SeedContext): Promise<void> {
  log('Seeding parser profiles...');

  const records = PARSER_PROFILES.map(profile => ({
    tenant_id: ctx.tenantId,
    ...profile,
    is_active: true,
    config: {},
  }));

  await upsertMany(ctx, 'doc.parser_profiles', records, ['tenant_id', 'code']);
}

async function seedExtractionFields(ctx: SeedContext): Promise<void> {
  log('Seeding extraction field templates...');

  const records: Record<string, unknown>[] = [];

  for (const [docType, fields] of Object.entries(EXTRACTION_FIELDS)) {
    fields.forEach((field, idx) => {
      records.push({
        tenant_id: ctx.tenantId,
        document_type: docType,
        sequence: idx + 1,
        ...field,
        validation_rules: {},
      });
    });
  }

  await upsertMany(ctx, 'doc.extraction_field_templates', records, ['tenant_id', 'document_type', 'field_name']);
}

async function seedDemoParsedDocuments(ctx: SeedContext): Promise<void> {
  if (ctx.environment === 'prod') {
    log('Skipping demo parsed documents in production');
    return;
  }

  log('Seeding demo parsed documents...');

  const statuses = ['parsed', 'reviewed', 'failed'];
  const docs: Record<string, unknown>[] = [];

  for (const docType of ['RECEIPT', 'INVOICE']) {
    for (const status of statuses) {
      for (let i = 0; i < 3; i++) {
        docs.push({
          tenant_id: ctx.tenantId,
          doc_type: docType,
          parser_profile: docType === 'RECEIPT' ? 'RECEIPT_PH_STANDARD' : 'INVOICE_STANDARD',
          status,
          confidence_score: status === 'failed' ? 0.4 : 0.75 + Math.random() * 0.2,
          parsed_data: {
            demo: true,
            merchant_name: `Demo Merchant ${i + 1}`,
            total_amount: Math.floor(Math.random() * 5000) + 100,
          },
        });
      }
    }
  }

  await upsertMany(ctx, 'doc.parsed_documents', docs, ['id']);
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

  log(`Starting Doc-OCR seed (env: ${ctx.environment}, dry-run: ${ctx.dryRun})`);

  try {
    // Reference data
    await seedDocumentTypes(ctx);
    await seedParserProfiles(ctx);
    await seedExtractionFields(ctx);

    // Demo data
    await seedDemoParsedDocuments(ctx);

    log('Doc-OCR seeding complete!');
  } catch (error) {
    console.error('Seed failed:', error);
    process.exit(1);
  }
}

main();
