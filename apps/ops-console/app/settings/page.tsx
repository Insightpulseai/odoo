export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-gradient">Settings</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Platform configuration and secrets management.
        </p>
      </div>

      <div className="grid gap-4">
        <div className="glass-card rounded-xl p-6">
          <h2 className="text-sm font-semibold uppercase tracking-wider mb-3">Supabase</h2>
          <dl className="space-y-2 text-xs text-muted-foreground">
            <div className="flex justify-between">
              <dt>Project ref</dt>
              <dd className="font-mono text-foreground">
                {process.env.NEXT_PUBLIC_SUPABASE_PROJECT_REF ?? '—'}
              </dd>
            </div>
            <div className="flex justify-between">
              <dt>URL</dt>
              <dd className="font-mono text-foreground truncate max-w-xs">
                {process.env.NEXT_PUBLIC_SUPABASE_URL ?? '—'}
              </dd>
            </div>
          </dl>
        </div>

        <div className="glass-card rounded-xl p-6">
          <h2 className="text-sm font-semibold uppercase tracking-wider mb-3">AI Gateway</h2>
          <p className="text-xs text-muted-foreground">
            {process.env.NEXT_PUBLIC_ENABLE_AI_QUERIES === 'true'
              ? '✓ AI SQL queries enabled via Vercel AI Gateway.'
              : 'Set AI_GATEWAY_API_KEY to enable AI SQL queries.'}
          </p>
        </div>
      </div>
    </div>
  )
}
