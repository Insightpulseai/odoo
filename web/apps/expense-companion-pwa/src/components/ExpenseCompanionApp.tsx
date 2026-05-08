'use client';

import { useDeferredValue, useEffect, useState } from 'react';
import InstallPrompt from '@/components/InstallPrompt';
import ReceiptCapture from '@/components/ReceiptCapture';
import SignInBar from '@/components/SignInBar';
import {
  type ExpenseRecord,
  loadExpenseDashboard,
  summarizeStatusBreakdown,
} from '@/lib/expense-data';

const currency = new Intl.NumberFormat('en-PH', {
  style: 'currency',
  currency: 'PHP',
  maximumFractionDigits: 0,
});

const statusTone: Record<ExpenseRecord['status'], string> = {
  Draft: 'bg-white text-slate-600',
  Submitted: 'bg-amber-100 text-amber-800',
  'Manager Review': 'bg-blue-100 text-blue-800',
  Approved: 'bg-emerald-100 text-emerald-800',
  Paid: 'bg-mint text-emerald-950',
};

export default function ExpenseCompanionApp() {
  const [snapshot, setSnapshot] = useState<Awaited<ReturnType<typeof loadExpenseDashboard>> | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [query, setQuery] = useState('');
  const deferredQuery = useDeferredValue(query);

  useEffect(() => {
    let active = true;

    const load = async () => {
      setIsLoading(true);
      const nextSnapshot = await loadExpenseDashboard();
      if (active) {
        setSnapshot(nextSnapshot);
        setIsLoading(false);
      }
    };

    void load();

    return () => {
      active = false;
    };
  }, []);

  const normalizedQuery = deferredQuery.trim().toLowerCase();
  const expenses = snapshot?.expenses ?? [];
  const filteredExpenses = !normalizedQuery
    ? expenses
    : expenses.filter((expense) => {
        return (
          expense.title.toLowerCase().includes(normalizedQuery) ||
          expense.merchant.toLowerCase().includes(normalizedQuery) ||
          expense.category.toLowerCase().includes(normalizedQuery)
        );
      });
  const submitted = expenses.filter((item) => item.status !== 'Paid');
  const reimbursable = expenses.filter((item) => item.paymentMode === 'Employee');
  const totals = {
    outstanding: submitted.reduce((sum, item) => sum + item.amount, 0),
    reimbursable: reimbursable.reduce((sum, item) => sum + item.amount, 0),
    reports: new Set(expenses.map((item) => item.reportName)).size,
  };
  const breakdown = summarizeStatusBreakdown(expenses);

  return (
    <main className="min-h-screen px-4 pb-10 pt-6 sm:px-6">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-6">
        <section className="glass-panel overflow-hidden rounded-[36px] px-5 py-6 sm:px-7">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-2xl">
              <div className="flex items-center justify-between gap-3">
                <p className="text-xs uppercase tracking-[0.36em] text-slate-500">Odoo Expense Companion</p>
                <SignInBar />
              </div>
              <h1 className="editorial mt-3 text-4xl font-semibold tracking-tight text-ink sm:text-6xl">
                Travel, spend, and receipts without the ERP drag.
              </h1>
              <p className="mt-4 max-w-xl text-sm leading-6 text-slate-600 sm:text-base">
                A Concur-style mobile PWA for Odoo employees: snap receipts, track report status,
                and clear reimbursement blockers before month-end.
              </p>
            </div>
            <div className="grid grid-cols-3 gap-3 rounded-[28px] bg-ink p-3 text-white shadow-panel">
              <StatCard label="Open spend" value={currency.format(totals.outstanding)} />
              <StatCard label="Reimbursable" value={currency.format(totals.reimbursable)} />
              <StatCard label="Reports" value={String(totals.reports || 0)} />
            </div>
          </div>
        </section>

        <InstallPrompt />

        <section className="grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">
          <div className="space-y-6">
            <div className="glass-panel rounded-[32px] p-5 sm:p-6">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm font-semibold text-ink">Expense feed</p>
                  <p className="text-xs text-slate-500">
                    {snapshot?.source === 'odoo'
                      ? `Live from Odoo for ${snapshot.sessionLabel}.`
                      : 'Demo snapshot shown until an Odoo web session is available.'}
                  </p>
                </div>
                <input
                  className="w-full rounded-full border border-black/10 bg-white/80 px-4 py-3 text-sm outline-none ring-0 placeholder:text-slate-400 sm:max-w-64"
                  placeholder="Search merchant or category"
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                />
              </div>

              <div className="mt-5 grid gap-3 sm:grid-cols-4">
                {breakdown.map((entry) => (
                  <div key={entry.status} className="rounded-[24px] bg-white/80 px-4 py-4">
                    <p className="text-xs uppercase tracking-[0.28em] text-slate-400">{entry.status}</p>
                    <p className="mt-2 text-2xl font-semibold text-ink">{entry.count}</p>
                    <p className="text-xs text-slate-500">{currency.format(entry.total)}</p>
                  </div>
                ))}
              </div>

              <div className="mt-5 space-y-3">
                {isLoading ? (
                  <div className="rounded-[28px] bg-white/70 p-5 text-sm text-slate-500">Loading expense activity…</div>
                ) : null}

                {!isLoading && filteredExpenses.length === 0 ? (
                  <div className="rounded-[28px] bg-white/70 p-5 text-sm text-slate-500">
                    No expenses match that query.
                  </div>
                ) : null}

                {filteredExpenses.map((expense) => (
                  <article
                    key={expense.id}
                    className="rounded-[28px] border border-black/5 bg-white/90 p-4 transition-transform duration-200 hover:-translate-y-0.5"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="text-base font-semibold text-ink">{expense.title}</p>
                        <p className="mt-1 text-sm text-slate-500">
                          {expense.merchant} · {expense.category}
                        </p>
                      </div>
                      <span className={`rounded-full px-3 py-1 text-xs font-semibold ${statusTone[expense.status]}`}>
                        {expense.status}
                      </span>
                    </div>
                    <div className="mt-4 flex flex-wrap items-center gap-3 text-xs text-slate-500">
                      <span>{expense.reportName}</span>
                      <span>{expense.date}</span>
                      <span>{expense.paymentMode}</span>
                    </div>
                    <div className="mt-4 flex items-end justify-between gap-3">
                      <div>
                        <p className="text-xs uppercase tracking-[0.28em] text-slate-400">Amount</p>
                        <p className="mt-1 text-2xl font-semibold text-ink">{currency.format(expense.amount)}</p>
                      </div>
                      <p className="max-w-52 text-right text-xs leading-5 text-slate-500">{expense.policyNote}</p>
                    </div>
                  </article>
                ))}
              </div>
            </div>
          </div>

          <aside className="space-y-6">
            <section className="glass-panel rounded-[32px] p-5 sm:p-6">
              <p className="text-sm font-semibold text-ink">Quick actions</p>
              <p className="mt-1 text-xs text-slate-500">
                Designed for field spend, not desktop back-office flows.
              </p>

              <div className="mt-5 grid gap-3">
                <button className="rounded-[28px] bg-white px-4 py-4 text-left" type="button">
                  <span className="block text-sm font-semibold text-ink">Create mileage claim</span>
                  <span className="mt-1 block text-xs text-slate-500">
                    Prepare the mobile-first path for odometer and route capture.
                  </span>
                </button>

                <button className="rounded-[28px] bg-white px-4 py-4 text-left" type="button">
                  <span className="block text-sm font-semibold text-ink">Check approvals</span>
                  <span className="mt-1 block text-xs text-slate-500">
                    Bring manager review, accounting flags, and payment state into one queue.
                  </span>
                </button>
              </div>
            </section>

            <ReceiptCapture />

            <section className="glass-panel rounded-[32px] p-5 sm:p-6">
              <p className="text-sm font-semibold text-ink">Approval pressure</p>
              <div className="mt-4 space-y-3">
                {snapshot?.alerts.map((alert) => (
                  <div key={alert.title} className="rounded-[24px] bg-white/85 px-4 py-4">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="text-sm font-semibold text-ink">{alert.title}</p>
                        <p className="mt-1 text-xs leading-5 text-slate-500">{alert.detail}</p>
                      </div>
                      <span className="rounded-full bg-[#fff0e6] px-3 py-1 text-xs font-semibold text-[#a1481f]">
                        {alert.severity}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          </aside>
        </section>
      </div>
    </main>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-[22px] bg-white/10 px-4 py-3">
      <p className="text-[11px] uppercase tracking-[0.28em] text-white/60">{label}</p>
      <p className="mt-2 text-lg font-semibold">{value}</p>
    </div>
  );
}
