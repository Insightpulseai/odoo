/**
 * POST /api/odoo/expense
 *
 * Approval-gated draft hr.expense creation.
 *
 * Per project_pulser_real_agentic_erp doctrine: the PWA never silently
 * writes to Odoo. The user reviews extracted OCR fields, edits them,
 * and explicitly clicks "Save as draft". This endpoint:
 *
 *   1. Validates the payload (no auto-confirm, state stays 'draft').
 *   2. Forwards a JSON-RPC `create` call for hr.expense via the
 *      Next.js rewrite to the user's Odoo session.
 *   3. Returns the created record id + url.
 *
 * It does NOT submit, approve, or post any move lines. Those remain
 * Odoo-side workflows that require human action in the UI.
 */

import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

interface CreateExpensePayload {
  name: string;
  total_amount: number;
  date?: string | null; // YYYY-MM-DD
  reference?: string | null;
  description?: string | null;
  payment_mode?: 'own_account' | 'company_account';
  // The PWA may want to pass through the merchant for auditability.
  merchant_name?: string | null;
}

function isPayload(value: unknown): value is CreateExpensePayload {
  if (!value || typeof value !== 'object') return false;
  const v = value as Record<string, unknown>;
  return (
    typeof v.name === 'string' &&
    v.name.trim().length > 0 &&
    typeof v.total_amount === 'number' &&
    Number.isFinite(v.total_amount) &&
    v.total_amount >= 0
  );
}

export async function POST(request: NextRequest): Promise<NextResponse> {
  const odooUrl = process.env.NEXT_PUBLIC_ODOO_URL;
  if (!odooUrl) {
    return NextResponse.json(
      {
        ok: false,
        error: 'Odoo URL not configured (NEXT_PUBLIC_ODOO_URL).',
      },
      { status: 503 },
    );
  }

  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ ok: false, error: 'Invalid JSON body.' }, { status: 400 });
  }

  if (!isPayload(body)) {
    return NextResponse.json(
      {
        ok: false,
        error: 'Missing required fields: name (string) and total_amount (number).',
      },
      { status: 400 },
    );
  }

  // Build the hr.expense payload. State is implicit 'draft' — we do NOT
  // call action_submit_expenses or any approval hook from this route.
  const expenseValues: Record<string, unknown> = {
    name: body.name.trim(),
    total_amount: body.total_amount,
    payment_mode: body.payment_mode === 'company_account' ? 'company_account' : 'own_account',
  };
  if (body.date) expenseValues.date = body.date;
  if (body.reference) expenseValues.reference = body.reference;
  if (body.description) expenseValues.description = body.description;
  // Surface merchant in the description if provided (Odoo CE hr.expense
  // doesn't have a dedicated merchant field; the ipai_hr_expense_liquidation
  // module extends with policy fields, but we stay lowest-common-denominator
  // here for portability).
  if (body.merchant_name && !expenseValues.description) {
    expenseValues.description = `Merchant: ${body.merchant_name}`;
  }

  // Forward the user's session cookie so the call lands as the logged-in
  // Odoo user — this is what makes "approval-gated" real: only that user's
  // permissions apply.
  const cookie = request.headers.get('cookie') ?? '';

  const rpcBody = {
    jsonrpc: '2.0',
    method: 'call',
    params: {
      model: 'hr.expense',
      method: 'create',
      args: [expenseValues],
      kwargs: {},
    },
  };

  let upstream: Response;
  try {
    upstream = await fetch(`${odooUrl}/web/dataset/call_kw`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        cookie,
      },
      body: JSON.stringify(rpcBody),
    });
  } catch (err) {
    console.error('[api/odoo/expense] upstream fetch failed', err);
    return NextResponse.json(
      { ok: false, error: 'Could not reach Odoo. Saved locally for retry.' },
      { status: 502 },
    );
  }

  let upstreamJson: { result?: unknown; error?: { data?: { message?: string } } } | null = null;
  try {
    upstreamJson = await upstream.json();
  } catch {
    return NextResponse.json(
      { ok: false, error: 'Odoo returned a non-JSON response.' },
      { status: 502 },
    );
  }

  if (upstreamJson?.error) {
    const odooMessage = upstreamJson.error.data?.message ?? 'Odoo rejected the request.';
    return NextResponse.json({ ok: false, error: odooMessage }, { status: 400 });
  }

  const newId = typeof upstreamJson?.result === 'number' ? upstreamJson.result : null;
  if (!newId) {
    return NextResponse.json(
      { ok: false, error: 'Odoo did not return a record id.' },
      { status: 502 },
    );
  }

  return NextResponse.json({
    ok: true,
    id: newId,
    url: `${odooUrl}/odoo/expenses/${newId}`,
    state: 'draft',
  });
}
