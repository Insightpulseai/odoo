/**
 * Offline-first draft queue for expense submissions.
 *
 * Backed by IndexedDB (via idb). When the PWA is offline OR the
 * /api/odoo/expense call fails, the draft is enqueued locally with a
 * status of "queued". When connectivity returns, drainQueue() flushes
 * pending drafts.
 *
 * The queue stores ONLY the user-confirmed draft payload — no raw OCR
 * blobs, no auth tokens, no PII beyond what the user typed.
 */

import { openDB, type IDBPDatabase } from 'idb';

const DB_NAME = 'expense-companion';
const DB_VERSION = 1;
const STORE = 'expense-drafts';

export type QueuedStatus = 'queued' | 'sent' | 'failed';

export interface ExpenseDraftPayload {
  name: string;
  total_amount: number;
  date?: string | null;
  reference?: string | null;
  description?: string | null;
  payment_mode?: 'own_account' | 'company_account';
  merchant_name?: string | null;
}

export interface QueuedDraft {
  id?: number;
  payload: ExpenseDraftPayload;
  created_at: string;
  status: QueuedStatus;
  attempts: number;
  last_error: string | null;
  remote_id: number | null;
}

async function db(): Promise<IDBPDatabase> {
  return openDB(DB_NAME, DB_VERSION, {
    upgrade(database) {
      if (!database.objectStoreNames.contains(STORE)) {
        const store = database.createObjectStore(STORE, {
          keyPath: 'id',
          autoIncrement: true,
        });
        store.createIndex('status', 'status');
        store.createIndex('created_at', 'created_at');
      }
    },
  });
}

export async function enqueueDraft(payload: ExpenseDraftPayload): Promise<number> {
  const conn = await db();
  const draft: QueuedDraft = {
    payload,
    created_at: new Date().toISOString(),
    status: 'queued',
    attempts: 0,
    last_error: null,
    remote_id: null,
  };
  return (await conn.add(STORE, draft)) as number;
}

export async function listDrafts(): Promise<QueuedDraft[]> {
  const conn = await db();
  return (await conn.getAll(STORE)) as QueuedDraft[];
}

export async function deleteDraft(id: number): Promise<void> {
  const conn = await db();
  await conn.delete(STORE, id);
}

async function updateDraft(id: number, patch: Partial<QueuedDraft>): Promise<void> {
  const conn = await db();
  const tx = conn.transaction(STORE, 'readwrite');
  const existing = (await tx.store.get(id)) as QueuedDraft | undefined;
  if (!existing) {
    await tx.done;
    return;
  }
  await tx.store.put({ ...existing, ...patch });
  await tx.done;
}

/**
 * Best-effort drain of the queue. Caller decides when to invoke (e.g. on
 * `online` event, on app focus, after a manual button press).
 *
 * Returns counts of {flushed, failed, remaining}.
 */
export async function drainQueue(): Promise<{
  flushed: number;
  failed: number;
  remaining: number;
}> {
  const conn = await db();
  const all = (await conn.getAll(STORE)) as QueuedDraft[];
  const pending = all.filter((d) => d.status === 'queued');

  let flushed = 0;
  let failed = 0;

  for (const draft of pending) {
    if (typeof draft.id !== 'number') continue;
    try {
      const response = await fetch('/api/odoo/expense', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(draft.payload),
      });
      const json = (await response.json()) as { ok?: boolean; id?: number; error?: string };
      if (response.ok && json.ok && typeof json.id === 'number') {
        await updateDraft(draft.id, {
          status: 'sent',
          attempts: draft.attempts + 1,
          remote_id: json.id,
          last_error: null,
        });
        flushed += 1;
      } else {
        await updateDraft(draft.id, {
          status: 'queued',
          attempts: draft.attempts + 1,
          last_error: json.error ?? `HTTP ${response.status}`,
        });
        failed += 1;
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'network error';
      await updateDraft(draft.id, {
        status: 'queued',
        attempts: draft.attempts + 1,
        last_error: message,
      });
      failed += 1;
    }
  }

  const remaining = (await conn.getAll(STORE)).filter(
    (d) => (d as QueuedDraft).status === 'queued',
  ).length;

  return { flushed, failed, remaining };
}
