import Link from "next/link"

export const dynamic = "force-dynamic"

export default function BackupsPage() {
  const backups = [
    { id: 'BK-044', env: 'PROD', type: 'auto', db: 'odoo_prod', size: '1.2 GB', timestamp: '2026-02-27 03:00', retention: '30d', status: 'Available' },
    { id: 'BK-043', env: 'PROD', type: 'manual', db: 'odoo_prod', size: '1.1 GB', timestamp: '2026-02-26 18:45', retention: 'forever', status: 'Available' },
    { id: 'BK-042', env: 'STAGE', type: 'auto', db: 'odoo_stage', size: '340 MB', timestamp: '2026-02-27 02:00', retention: '7d', status: 'Available' },
  ]

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-2xl font-bold">Backups</h2>
          <p className="text-sm text-muted-foreground mt-1">Database snapshots, restore, and environment clone operations.</p>
        </div>
        <button className="px-4 py-2 text-sm font-semibold bg-primary text-white rounded-lg hover:opacity-90 transition-opacity">
          + Create Snapshot
        </button>
      </div>

      <div className="bg-white rounded-lg border shadow-sm overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Snapshot</th>
              <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Env</th>
              <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Type</th>
              <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Size</th>
              <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Created</th>
              <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Retention</th>
              <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {backups.map((b) => (
              <tr key={b.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 text-sm font-bold text-blue-600">
                  <Link href={`/backups/${b.id}`}>{b.id}</Link>
                </td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${b.env === 'PROD' ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'}`}>
                    {b.env}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-500">{b.type}</td>
                <td className="px-6 py-4 text-sm font-mono text-gray-600">{b.size}</td>
                <td className="px-6 py-4 text-sm text-gray-500 font-mono">{b.timestamp}</td>
                <td className="px-6 py-4 text-sm text-gray-400">{b.retention}</td>
                <td className="px-6 py-4 text-sm">
                  <Link href={`/backups/${b.id}`} className="text-blue-600 hover:underline mr-3">Restore</Link>
                  <button className="text-blue-600 hover:underline">Clone →</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <p className="mt-3 text-xs text-muted-foreground">
        Data source: <code>ops.backups</code> · <code>ops.backup_jobs</code> · job executor.
      </p>
    </div>
  )
}
