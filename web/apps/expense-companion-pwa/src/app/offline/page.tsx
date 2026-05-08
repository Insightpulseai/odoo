export default function OfflinePage() {
  return (
    <main className="flex min-h-screen items-center justify-center px-6 py-10">
      <section className="glass-panel max-w-md rounded-4xl p-8 text-center">
        <p className="text-sm uppercase tracking-[0.32em] text-slate-500">Offline mode</p>
        <h1 className="editorial mt-4 text-4xl font-semibold text-ink">
          Receipts can wait. Your queue will not.
        </h1>
        <p className="mt-4 text-sm leading-6 text-slate-600">
          The companion shell is available, but Odoo is unreachable right now. Reconnect to resume
          live expense sync and approval updates.
        </p>
      </section>
    </main>
  );
}
