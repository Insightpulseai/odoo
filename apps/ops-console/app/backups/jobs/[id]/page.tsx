import Link from "next/link"

export const dynamic = "force-dynamic"

export default async function BackupJobDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params

  const details = [
    { label: 'Action', value: 'restore' },
    { label: 'Source snapshot', value: 'BK-044 (PROD)' },
    { label: 'Target environment', value: 'STAGE' },
    { label: 'Target database', value: 'odoo_stage' },
    { label: 'Actor', value: 'tbwa' },
    { label: 'Runner', value: 'GitHub Actions' },
    { label: 'Duration', value: '8m 33s' },
    { label: 'Started at', value: '2026-02-27 10:12:04' },
    { label: 'Finished at', value: '2026-02-27 10:20:37' },
    { label: 'Correlation ID', value: `corr_job_${id.toLowerCase()}` },
    { label: 'Run URL', value: 'https://github.com/Insightpulseai/odoo/actions/runs/...' },
  ]

  return (
    <div className="max-w-6xl mx-auto">
      {/* Breadcrumb */}
      <div className="flex items-center space-x-2 mb-8 text-sm">
        <Link href="/backups" className="text-blue-600 hover:underline">Backups</Link>
        <span className="text-gray-300">/</span>
        <span className="text-gray-500">jobs</span>
        <span className="text-gray-300">/</span>
        <span className="font-bold text-gray-700">{id}</span>
      </div>

      {/* Status header */}
      <div className="bg-white rounded-lg border shadow-sm p-6 mb-6">
        <div className="flex flex-wrap items-center gap-3">
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-green-100 text-green-700">COMPLETED</span>
          <span className="font-bold text-lg">Job {id}</span>
          <span className="text-xs text-gray-500">restore · PROD → STAGE</span>
          <span className="text-xs text-gray-400">· by tbwa</span>
          <span className="text-xs text-gray-400">· 8m 33s</span>
        </div>
      </div>

      {/* Details */}
      <div className="space-y-4">
        <div className="bg-white rounded-lg border shadow-sm overflow-hidden">
          <div className="px-6 py-3 bg-gray-50 border-b text-xs font-semibold text-gray-500 uppercase tracking-wider">
            Job Details
          </div>
          {details.map((r) => (
            <div key={r.label} className="px-6 py-3 flex justify-between items-start border-b last:border-0">
              <span className="text-sm text-gray-500 shrink-0 mr-4">{r.label}</span>
              <span className="text-sm font-mono text-gray-700 text-right break-all">{r.value}</span>
            </div>
          ))}
        </div>

        <p className="text-xs text-muted-foreground">
          Immutable audit record from <code>ops.backup_jobs</code>.
        </p>
      </div>
    </div>
  )
}
