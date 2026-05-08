'use client';

/**
 * Camera capture -> OCR -> review -> confirm -> save flow.
 *
 * Approval-gated per project_pulser_real_agentic_erp:
 *   1. User snaps a photo or picks an image.
 *   2. Image is POSTed to /api/ocr/receipt (Azure Document Intelligence).
 *   3. Extracted fields are rendered in an editable form.
 *   4. User reviews + edits, then clicks "Save as Odoo expense draft".
 *   5. Draft payload is POSTed to /api/odoo/expense (or queued offline).
 */

import { useCallback, useEffect, useRef, useState, type ChangeEvent } from 'react';

import {
  drainQueue,
  enqueueDraft,
  type ExpenseDraftPayload,
} from '@/lib/offline/draft-queue';
import {
  base64ToFile,
  haptic,
  isNative,
  nativeBridge,
} from '@/lib/native-bridge';

interface OcrResponse {
  ok: boolean;
  receipt?: {
    merchant_name: string | null;
    transaction_date: string | null;
    transaction_time: string | null;
    total: number | null;
    subtotal: number | null;
    tax: number | null;
    tip: number | null;
    currency: string | null;
    items: Array<{
      name: string | null;
      quantity: number | null;
      price: number | null;
      total: number | null;
    }>;
  };
  error?: string;
  code?: string;
}

interface DraftForm {
  name: string;
  total_amount: string;
  date: string;
  description: string;
  merchant_name: string;
  payment_mode: 'own_account' | 'company_account';
}

const blankForm: DraftForm = {
  name: '',
  total_amount: '',
  date: '',
  description: '',
  merchant_name: '',
  payment_mode: 'own_account',
};

type Status =
  | { kind: 'idle' }
  | { kind: 'extracting' }
  | { kind: 'review' }
  | { kind: 'saving' }
  | { kind: 'saved'; id: number; url?: string }
  | { kind: 'queued'; queueId: number }
  | { kind: 'error'; message: string };

export default function ReceiptCapture() {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [form, setForm] = useState<DraftForm>(blankForm);
  const [status, setStatus] = useState<Status>({ kind: 'idle' });

  // Best-effort drain when the app comes back online.
  useEffect(() => {
    const handler = () => {
      void drainQueue();
    };
    window.addEventListener('online', handler);
    return () => window.removeEventListener('online', handler);
  }, []);

  const reset = useCallback(() => {
    setForm(blankForm);
    setPreviewUrl((url) => {
      if (url) URL.revokeObjectURL(url);
      return null;
    });
    setStatus({ kind: 'idle' });
    if (fileInputRef.current) fileInputRef.current.value = '';
  }, []);

  const processFile = useCallback(async (file: File) => {
    setPreviewUrl((prev) => {
      if (prev) URL.revokeObjectURL(prev);
      return URL.createObjectURL(file);
    });
    setStatus({ kind: 'extracting' });

    const fd = new FormData();
    fd.append('receipt', file);

    try {
      const response = await fetch('/api/ocr/receipt', { method: 'POST', body: fd });
      const json = (await response.json()) as OcrResponse;

      if (!response.ok || !json.ok || !json.receipt) {
        setStatus({
          kind: 'error',
          message: json.error ?? 'Could not read the receipt. Try again.',
        });
        return;
      }

      const r = json.receipt;
      setForm({
        name: r.merchant_name ? `${r.merchant_name} receipt` : 'Receipt',
        total_amount: r.total != null ? String(r.total) : '',
        date: r.transaction_date ?? '',
        description: buildDescription(r),
        merchant_name: r.merchant_name ?? '',
        payment_mode: 'own_account',
      });
      setStatus({ kind: 'review' });
      haptic('light');
    } catch (err) {
      setStatus({
        kind: 'error',
        message: err instanceof Error ? err.message : 'Network error during OCR.',
      });
    }
  }, []);

  const handleFile = useCallback(
    async (event: ChangeEvent<HTMLInputElement>) => {
      const file = event.target.files?.[0];
      if (!file) return;
      await processFile(file);
    },
    [processFile],
  );

  /** Native iOS path — bypass the file input, call the WKWebView bridge. */
  const handleNativeCapture = useCallback(async () => {
    const bridge = nativeBridge();
    if (!bridge) return;
    try {
      const { imageBase64 } = await bridge.captureReceipt();
      const file = base64ToFile(imageBase64);
      await processFile(file);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Capture failed.';
      if (message === 'capture_cancelled') {
        // User backed out — stay on idle screen, no error toast.
        return;
      }
      setStatus({ kind: 'error', message });
    }
  }, [processFile]);

  const handleConfirm = useCallback(async () => {
    const totalAmount = Number(form.total_amount);
    if (!form.name.trim() || !Number.isFinite(totalAmount) || totalAmount < 0) {
      setStatus({
        kind: 'error',
        message: 'Description and a non-negative total are required.',
      });
      return;
    }

    const payload: ExpenseDraftPayload = {
      name: form.name.trim(),
      total_amount: totalAmount,
      date: form.date || null,
      description: form.description || null,
      merchant_name: form.merchant_name || null,
      payment_mode: form.payment_mode,
    };

    setStatus({ kind: 'saving' });

    try {
      const response = await fetch('/api/odoo/expense', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const json = (await response.json()) as {
        ok?: boolean;
        id?: number;
        url?: string;
        error?: string;
      };

      if (response.ok && json.ok && typeof json.id === 'number') {
        setStatus({ kind: 'saved', id: json.id, url: json.url });
        haptic('heavy');
        return;
      }

      // Live but rejected — surface the Odoo error.
      if (response.status >= 400 && response.status < 500) {
        setStatus({
          kind: 'error',
          message: json.error ?? 'Odoo rejected the draft.',
        });
        return;
      }

      // Server / network — queue offline.
      const queueId = await enqueueDraft(payload);
      setStatus({ kind: 'queued', queueId });
    } catch {
      const queueId = await enqueueDraft(payload);
      setStatus({ kind: 'queued', queueId });
    }
  }, [form]);

  return (
    <section className="glass-panel rounded-[32px] p-5 sm:p-6">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-sm font-semibold text-ink">AI receipt capture</p>
          <p className="text-xs text-slate-500">
            Snap a photo. We extract the fields. You review and save the draft to Odoo.
          </p>
        </div>
        {status.kind !== 'idle' ? (
          <button
            type="button"
            onClick={reset}
            className="rounded-full border border-black/10 px-3 py-1.5 text-xs font-semibold text-slate-600"
          >
            New receipt
          </button>
        ) : null}
      </div>

      {status.kind === 'idle' ? (
        isNative() ? (
          <button
            type="button"
            onClick={() => void handleNativeCapture()}
            className="mt-4 block w-full cursor-pointer rounded-[28px] bg-ink px-4 py-5 text-left text-white"
          >
            <span className="block text-sm font-semibold">Open camera</span>
            <span className="mt-1 block text-xs text-white/70">
              Native iOS camera. Receipts are queued offline if needed.
            </span>
          </button>
        ) : (
          <label className="mt-4 block cursor-pointer rounded-[28px] bg-ink px-4 py-5 text-white">
            <span className="block text-sm font-semibold">Open camera</span>
            <span className="mt-1 block text-xs text-white/70">
              JPEG, PNG, HEIC, or PDF. Max 10 MB.
            </span>
            <input
              ref={fileInputRef}
              className="sr-only"
              type="file"
              accept="image/*,application/pdf"
              capture="environment"
              onChange={handleFile}
            />
          </label>
        )
      ) : null}

      {previewUrl ? (
        <div className="mt-4 overflow-hidden rounded-[24px] border border-black/10">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={previewUrl} alt="Receipt preview" className="max-h-72 w-full object-contain" />
        </div>
      ) : null}

      {status.kind === 'extracting' ? (
        <p className="mt-4 rounded-[24px] bg-white/70 px-4 py-3 text-sm text-slate-600">
          Reading receipt with Azure Document Intelligence…
        </p>
      ) : null}

      {status.kind === 'review' || status.kind === 'saving' ? (
        <form
          className="mt-4 space-y-3"
          onSubmit={(event) => {
            event.preventDefault();
            void handleConfirm();
          }}
        >
          <Field
            label="Description"
            value={form.name}
            onChange={(v) => setForm((s) => ({ ...s, name: v }))}
            required
          />
          <div className="grid gap-3 sm:grid-cols-2">
            <Field
              label="Total"
              type="number"
              step="0.01"
              value={form.total_amount}
              onChange={(v) => setForm((s) => ({ ...s, total_amount: v }))}
              required
            />
            <Field
              label="Date"
              type="date"
              value={form.date}
              onChange={(v) => setForm((s) => ({ ...s, date: v }))}
            />
          </div>
          <Field
            label="Merchant"
            value={form.merchant_name}
            onChange={(v) => setForm((s) => ({ ...s, merchant_name: v }))}
          />
          <Field
            label="Notes"
            value={form.description}
            onChange={(v) => setForm((s) => ({ ...s, description: v }))}
            multiline
          />

          <fieldset className="rounded-2xl border border-black/10 px-3 py-2">
            <legend className="px-1 text-xs uppercase tracking-[0.28em] text-slate-400">
              Payment
            </legend>
            <label className="mr-4 text-sm">
              <input
                type="radio"
                name="payment_mode"
                value="own_account"
                checked={form.payment_mode === 'own_account'}
                onChange={() => setForm((s) => ({ ...s, payment_mode: 'own_account' }))}
              />{' '}
              Employee
            </label>
            <label className="text-sm">
              <input
                type="radio"
                name="payment_mode"
                value="company_account"
                checked={form.payment_mode === 'company_account'}
                onChange={() => setForm((s) => ({ ...s, payment_mode: 'company_account' }))}
              />{' '}
              Company
            </label>
          </fieldset>

          <button
            type="submit"
            disabled={status.kind === 'saving'}
            className="w-full rounded-full bg-ink px-4 py-3 text-sm font-semibold text-white disabled:opacity-60"
          >
            {status.kind === 'saving' ? 'Saving…' : 'Save as Odoo expense draft'}
          </button>
        </form>
      ) : null}

      {status.kind === 'saved' ? (
        <div className="mt-4 rounded-[24px] bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
          Saved as draft (id #{status.id}).{' '}
          {status.url ? (
            <a className="underline" href={status.url} target="_blank" rel="noreferrer">
              Open in Odoo
            </a>
          ) : null}
        </div>
      ) : null}

      {status.kind === 'queued' ? (
        <div className="mt-4 rounded-[24px] bg-amber-50 px-4 py-3 text-sm text-amber-900">
          Saved offline (queue #{status.queueId}). Will sync when connection returns.
        </div>
      ) : null}

      {status.kind === 'error' ? (
        <div className="mt-4 rounded-[24px] bg-rose-50 px-4 py-3 text-sm text-rose-900">
          {status.message}
        </div>
      ) : null}
    </section>
  );
}

function buildDescription(receipt: NonNullable<OcrResponse['receipt']>): string {
  const lines: string[] = [];
  if (receipt.merchant_name) lines.push(`Merchant: ${receipt.merchant_name}`);
  if (receipt.transaction_date) {
    const time = receipt.transaction_time ? ` ${receipt.transaction_time}` : '';
    lines.push(`Date: ${receipt.transaction_date}${time}`);
  }
  if (receipt.subtotal != null) lines.push(`Subtotal: ${receipt.subtotal}`);
  if (receipt.tax != null) lines.push(`Tax: ${receipt.tax}`);
  if (receipt.tip != null) lines.push(`Tip: ${receipt.tip}`);
  if (receipt.items.length > 0) {
    lines.push('Items:');
    for (const item of receipt.items.slice(0, 20)) {
      const parts: string[] = [];
      if (item.name) parts.push(item.name);
      if (item.quantity != null) parts.push(`x${item.quantity}`);
      if (item.total != null) parts.push(`= ${item.total}`);
      if (parts.length > 0) lines.push(`  - ${parts.join(' ')}`);
    }
  }
  return lines.join('\n');
}

interface FieldProps {
  label: string;
  value: string;
  onChange: (next: string) => void;
  type?: string;
  step?: string;
  required?: boolean;
  multiline?: boolean;
}

function Field({ label, value, onChange, type = 'text', step, required, multiline }: FieldProps) {
  const baseClass =
    'mt-1 w-full rounded-2xl border border-black/10 bg-white px-3 py-2 text-sm outline-none focus:border-ink';
  return (
    <label className="block">
      <span className="text-xs uppercase tracking-[0.28em] text-slate-400">{label}</span>
      {multiline ? (
        <textarea
          className={`${baseClass} min-h-24`}
          value={value}
          onChange={(event) => onChange(event.target.value)}
          required={required}
        />
      ) : (
        <input
          className={baseClass}
          type={type}
          step={step}
          value={value}
          onChange={(event) => onChange(event.target.value)}
          required={required}
        />
      )}
    </label>
  );
}
