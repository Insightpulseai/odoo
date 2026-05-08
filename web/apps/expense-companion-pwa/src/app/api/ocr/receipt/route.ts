/**
 * POST /api/ocr/receipt
 *
 * Multipart upload of a receipt image. Calls Azure Document Intelligence
 * prebuilt-receipt via DefaultAzureCredential and returns structured fields.
 *
 * Auth: managed identity in production (Azure Container Apps),
 * AzureCliCredential / VS Code login in dev — both via DefaultAzureCredential.
 *
 * Hard rules:
 *   - Never echo Azure error bodies to the client.
 *   - Never include OCR keys in code (we don't use them).
 *   - Approval-gated: this endpoint is PURE EXTRACTION. It does not write
 *     to Odoo. The user reviews the JSON and a separate UI step posts to
 *     /api/odoo/expense to create a draft hr.expense.
 */

import { NextRequest, NextResponse } from 'next/server';

import { analyzeReceipt } from '@/lib/document-intelligence';

// Receipts are binary uploads — force Node.js runtime (Edge can't load
// @azure/identity reliably and we need Buffer).
export const runtime = 'nodejs';
// Don't cache — every receipt is unique.
export const dynamic = 'force-dynamic';

const MAX_BYTES = 10 * 1024 * 1024; // 10 MB matches Document Intelligence limit.
const ACCEPTED_TYPES = new Set([
  'image/jpeg',
  'image/jpg',
  'image/png',
  'image/tiff',
  'image/heic',
  'image/heif',
  'application/pdf',
]);

interface ErrorBody {
  error: string;
  code: 'BAD_REQUEST' | 'UNSUPPORTED_TYPE' | 'TOO_LARGE' | 'NO_RECEIPT' | 'CONFIG' | 'UPSTREAM';
}

function fail(code: ErrorBody['code'], status: number, error: string) {
  return NextResponse.json<ErrorBody>({ code, error }, { status });
}

export async function POST(request: NextRequest): Promise<NextResponse> {
  let formData: FormData;
  try {
    formData = await request.formData();
  } catch {
    return fail('BAD_REQUEST', 400, 'Expected multipart/form-data with a "receipt" file.');
  }

  const file = formData.get('receipt');
  if (!(file instanceof File)) {
    return fail('BAD_REQUEST', 400, 'Missing "receipt" file in form data.');
  }

  if (file.size === 0) {
    return fail('BAD_REQUEST', 400, 'Receipt file is empty.');
  }

  if (file.size > MAX_BYTES) {
    return fail('TOO_LARGE', 413, `Receipt too large (max ${MAX_BYTES / 1024 / 1024} MB).`);
  }

  const contentType = (file.type || '').toLowerCase();
  if (contentType && !ACCEPTED_TYPES.has(contentType)) {
    return fail(
      'UNSUPPORTED_TYPE',
      415,
      'Unsupported receipt type. Use JPEG, PNG, TIFF, HEIC, or PDF.',
    );
  }

  const arrayBuffer = await file.arrayBuffer();
  const buffer = Buffer.from(arrayBuffer);

  try {
    const extracted = await analyzeReceipt(buffer);
    return NextResponse.json({
      ok: true,
      receipt: extracted,
      meta: {
        bytes: buffer.byteLength,
        content_type: contentType || 'application/octet-stream',
      },
    });
  } catch (err) {
    const message = err instanceof Error ? err.message : 'unknown';

    // Map internal error codes to user-safe messages without leaking details.
    if (message === 'DOCUMENT_INTELLIGENCE_ENDPOINT_MISSING') {
      return fail(
        'CONFIG',
        503,
        'Receipt OCR is not configured for this environment. Contact your administrator.',
      );
    }
    if (message === 'DI_NO_RECEIPT_FOUND') {
      return fail(
        'NO_RECEIPT',
        422,
        'Could not detect a receipt in the image. Try a clearer photo.',
      );
    }
    if (message.startsWith('DI_ANALYZE_FAILED:')) {
      // Server logs get the detail; client gets a generic message.
      console.error('[ocr/receipt] document intelligence analyze failed:', message);
      return fail(
        'UPSTREAM',
        502,
        'Receipt OCR service is temporarily unavailable. Try again shortly.',
      );
    }

    // Catch-all — credential failure, network, etc. Log server-side, sanitise.
    console.error('[ocr/receipt] unexpected error:', err);
    return fail('UPSTREAM', 500, 'Could not process receipt. Try again.');
  }
}
