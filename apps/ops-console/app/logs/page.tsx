export const dynamic = "force-dynamic"

export default function LogsPage() {
  const logs = [
    { ts: '2026-02-27 09:01:23', level: 'INFO', service: 'ci', message: 'Build CI-142 started — branch: main', correlation_id: 'corr_9c3d2e1' },
    { ts: '2026-02-27 09:04:35', level: 'INFO', service: 'ci', message: 'Build CI-142 completed — 3m 12s', correlation_id: 'corr_9c3d2e1' },
    { ts: '2026-02-27 09:05:01', level: 'INFO', service: 'deploy', message: 'Deployment DP-893 queued — env: STAGE', correlation_id: 'corr_9c3d2e1' },
    { ts: '2026-02-27 08:30:11', level: 'ERROR', service: 'runtime', message: 'HTTP 500 — /api/supabase-proxy/v1/projects (see trace)', correlation_id: 'corr_err001' },
    { ts: '2026-02-27 08:30:12', level: 'WARN', service: 'db', message: 'Slow query detected — 2.4s — SELECT FROM res_partner', correlation_id: 'corr_err001' },
    { ts: '2026-02-27 03:00:02', level: 'INFO', service: 'backup', message: 'Snapshot BK-044 created — 1.2 GB — PROD', correlation_id: 'corr_bk044' },
  ]

  const levelColor = (level: string) => {
    if (level === 'ERROR') return 'bg-red-100 text-red-700'
    if (level === 'WARN') return 'bg-yellow-100 text-yellow-700'
    return 'bg-gray-100 text-gray-600'
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold">Logs</h2>
          <p className="text-sm text-muted-foreground mt-1">Unified log stream — CI, runtime, DB, audit.</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-4 mb-6 p-4 bg-white rounded-lg border shadow-sm items-end">
        <div className="flex flex-col space-y-1">
          <label className="text-[10px] font-bold text-gray-500 uppercase tracking-wider">Env</label>
          <select className="text-xs border rounded px-2 py-1.5 bg-white min-w-[80px]">
            <option>All</option>
            <option>PROD</option>
            <option>STAGE</option>
          </select>
        </div>
        <div className="flex flex-col space-y-1">
          <label className="text-[10px] font-bold text-gray-500 uppercase tracking-wider">Service</label>
          <select className="text-xs border rounded px-2 py-1.5 bg-white min-w-[90px]">
            <option>All</option>
            <option>ci</option>
            <option>deploy</option>
            <option>runtime</option>
            <option>db</option>
            <option>backup</option>
          </select>
        </div>
        <div className="flex flex-col space-y-1">
          <label className="text-[10px] font-bold text-gray-500 uppercase tracking-wider">Level</label>
          <select className="text-xs border rounded px-2 py-1.5 bg-white min-w-[80px]">
            <option>All</option>
            <option>INFO</option>
            <option>WARN</option>
            <option>ERROR</option>
          </select>
        </div>
        <div className="flex flex-col space-y-1 flex-1 min-w-[200px]">
          <label className="text-[10px] font-bold text-gray-500 uppercase tracking-wider">Correlation ID</label>
          <input
            type="text"
            placeholder="corr_..."
            className="text-xs border rounded px-2 py-1.5 w-full max-w-xs"
          />
        </div>
        <div className="flex flex-col space-y-1 min-w-[160px]">
          <label className="text-[10px] font-bold text-gray-500 uppercase tracking-wider">Time Range</label>
          <select className="text-xs border rounded px-2 py-1.5 bg-white">
            <option>Last 1h</option>
            <option>Last 6h</option>
            <option>Last 24h</option>
            <option>Last 7d</option>
          </select>
        </div>
      </div>

      {/* Log table */}
      <div className="bg-white rounded-lg border shadow-sm overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider whitespace-nowrap">Timestamp</th>
              <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Level</th>
              <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Service</th>
              <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Message</th>
              <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider whitespace-nowrap">Correlation</th>
            </tr>
          </thead>
          <tbody className="divide-y font-mono">
            {logs.map((log, i) => (
              <tr key={i} className="hover:bg-gray-50">
                <td className="px-4 py-2.5 text-xs text-gray-400 whitespace-nowrap">{log.ts}</td>
                <td className="px-4 py-2.5">
                  <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${levelColor(log.level)}`}>
                    {log.level}
                  </span>
                </td>
                <td className="px-4 py-2.5 text-xs text-gray-500">{log.service}</td>
                <td className="px-4 py-2.5 text-xs text-gray-700 max-w-lg">{log.message}</td>
                <td className="px-4 py-2.5 text-[10px] text-gray-400 whitespace-nowrap">{log.correlation_id}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <p className="mt-3 text-xs text-muted-foreground">
        Data source: <code>ops.platform_events</code> · <code>ops.jobs</code> · runtime log aggregator.
      </p>
    </div>
  )
}
