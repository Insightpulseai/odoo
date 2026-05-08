/**
 * Azure Document Intelligence wrapper — prebuilt-receipt model.
 *
 * Auth contract (per ~/.claude/CLAUDE.md OAuth-first rule):
 *   - DefaultAzureCredential ONLY (managed identity in production,
 *     az-cli / VS Code login in dev).
 *   - No AzureKeyCredential, no static API keys.
 *
 * SDK: @azure-rest/ai-document-intelligence (modern REST client, replaces
 *   the legacy @azure/ai-form-recognizer package).
 */

import DocumentIntelligence, {
  isUnexpected,
  getLongRunningPoller,
  type AnalyzeOperationOutput,
  type DocumentIntelligenceClient,
} from '@azure-rest/ai-document-intelligence';
import { DefaultAzureCredential } from '@azure/identity';

export interface ReceiptLineItem {
  name: string | null;
  quantity: number | null;
  price: number | null;
  total: number | null;
}

export interface ExtractedReceipt {
  merchant_name: string | null;
  transaction_date: string | null;
  transaction_time: string | null;
  total: number | null;
  subtotal: number | null;
  tax: number | null;
  tip: number | null;
  currency: string | null;
  items: ReceiptLineItem[];
  confidence: number | null;
  // Raw doc type ("receipt", "receipt.creditCard", "receipt.hotel", ...).
  doc_type: string | null;
}

let cachedClient: DocumentIntelligenceClient | null = null;

function getClient(): DocumentIntelligenceClient {
  if (cachedClient) return cachedClient;

  const endpoint = process.env.DOCUMENT_INTELLIGENCE_ENDPOINT;
  if (!endpoint) {
    throw new Error('DOCUMENT_INTELLIGENCE_ENDPOINT_MISSING');
  }

  cachedClient = DocumentIntelligence(endpoint, new DefaultAzureCredential());
  return cachedClient;
}

/**
 * Analyse a receipt image with the prebuilt-receipt model.
 *
 * @param imageBytes - Raw bytes of the receipt image (jpeg/png/pdf/tiff).
 * @returns Structured fields with conservative null handling.
 * @throws Error with stable code-like message; the API route maps it to a
 *   user-facing message and never leaks the raw Azure error.
 */
export async function analyzeReceipt(imageBytes: Buffer): Promise<ExtractedReceipt> {
  const client = getClient();
  const base64Source = imageBytes.toString('base64');

  const initialResponse = await client
    .path('/documentModels/{modelId}:analyze', 'prebuilt-receipt')
    .post({
      contentType: 'application/json',
      body: { base64Source },
    });

  if (isUnexpected(initialResponse)) {
    // Don't leak raw Azure error structure upstream.
    const status = initialResponse.status;
    const azureCode = (initialResponse.body as { error?: { code?: string } } | undefined)?.error
      ?.code;
    throw new Error(`DI_ANALYZE_FAILED:${status}:${azureCode ?? 'unknown'}`);
  }

  const poller = getLongRunningPoller(client, initialResponse);
  const result = (await poller.pollUntilDone()).body as AnalyzeOperationOutput;

  const document = result.analyzeResult?.documents?.[0];
  if (!document) {
    throw new Error('DI_NO_RECEIPT_FOUND');
  }

  const fields = (document.fields ?? {}) as Record<string, FieldLike | undefined>;

  return {
    merchant_name: stringField(fields.MerchantName),
    transaction_date: stringField(fields.TransactionDate),
    transaction_time: stringField(fields.TransactionTime),
    total: numberField(fields.Total),
    subtotal: numberField(fields.Subtotal),
    tax: numberField(fields.TotalTax),
    tip: numberField(fields.Tip),
    currency: currencyCode(fields.Total) ?? currencyCode(fields.Subtotal),
    items: extractItems(fields.Items),
    confidence: typeof document.confidence === 'number' ? document.confidence : null,
    doc_type: typeof document.docType === 'string' ? document.docType : null,
  };
}

// --- Field extraction helpers ----------------------------------------------

interface FieldLike {
  type?: string;
  content?: string;
  valueString?: string;
  valueDate?: string;
  valueTime?: string;
  valueNumber?: number;
  valueInteger?: number;
  valueCurrency?: { amount?: number; currencyCode?: string; currencySymbol?: string };
  valueArray?: FieldLike[];
  valueObject?: Record<string, FieldLike>;
}

function stringField(field: FieldLike | undefined): string | null {
  if (!field) return null;
  if (typeof field.valueString === 'string') return field.valueString;
  if (typeof field.valueDate === 'string') return field.valueDate;
  if (typeof field.valueTime === 'string') return field.valueTime;
  if (typeof field.content === 'string') return field.content;
  return null;
}

function numberField(field: FieldLike | undefined): number | null {
  if (!field) return null;
  if (typeof field.valueCurrency?.amount === 'number') return field.valueCurrency.amount;
  if (typeof field.valueNumber === 'number') return field.valueNumber;
  if (typeof field.valueInteger === 'number') return field.valueInteger;
  // Fall back to parsing content if numeric extraction failed.
  if (typeof field.content === 'string') {
    const parsed = Number(field.content.replace(/[^\d.\-]/g, ''));
    return Number.isFinite(parsed) ? parsed : null;
  }
  return null;
}

function currencyCode(field: FieldLike | undefined): string | null {
  return field?.valueCurrency?.currencyCode ?? null;
}

function extractItems(field: FieldLike | undefined): ReceiptLineItem[] {
  const values = field?.valueArray ?? [];
  return values.map((entry) => {
    const props = entry.valueObject ?? {};
    return {
      // prebuilt-receipt uses "Description" — map to a friendlier "name" key.
      name: stringField(props.Description) ?? stringField(props.Name) ?? null,
      quantity: numberField(props.Quantity),
      price: numberField(props.Price),
      total: numberField(props.TotalPrice),
    };
  });
}
