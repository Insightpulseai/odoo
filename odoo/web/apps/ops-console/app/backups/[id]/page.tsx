import Link from "next/link"

export const dynamic = "force-dynamic"

export default async function BackupDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params

  const details = [
    { label: 'Database', value: 'odoo_prod' },
    { label: 'PostgreSQL', value: '16.x' },
    { label: 'Size', value: '1.2 GB' },
    { label: 'Created by', value: 'scheduler (auto)' },
    { label: 'Storage ref', value: `supabase-bucket/backups/${id}.pgdump` },
    { label: 'Correlation ID', value: `corr_bk${id.toLowerCase()}` },
  ]

  return (
    <div className="max-w-6xl mx-auto">
      {/* Breadcrumb */}
      <div className="flex items-center space-x-2 mb-8 text-sm">
        <Link href="/backups" className="text-blue-600 hover:underline">Backups</Link>
        <span className="text-gray-300">/</span>
        <span className="font-bold text-gray-700">{id}</span>
      </div>

      {/* Status header */}
      <div className="bg-white rounded-lg border shadow-sm p-6 mb-6">
        <div className="flex flex-wrap items-center gap-3 mb-3">
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-green-100 text-green-700">AVAILABLE</span>
          <span className="font-bold text-lg">{id}</span>
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-green-100 text-green-700">PROD</span>
          <span className="text-xs text-gray-400">auto · 2026-02-27 03:00</span>
          <span className="text-xs text-gray-400">· Retention: 30d</span>
        </div>
        <div className="mt-4 flex items-center gap-3">
          <button className="px-4 py-2 text-sm font-semibold bg-primary text-white rounded-lg hover:opacity-90 transition-opacity">
            Restore to STAGE
          </button>
          <button className="px-4 py-2 text-sm font-semibold border rounded-lg hover:bg-gray-50 transition-colors">
            Clone PROD → STAGE
          </button>
        </div>
        <p className="mt-3 text-xs text-amber-600">
          ⚠ Restore and clone operations are gated by Policy Gates and require maintainer role.
        </p>
      </div>

      {/* Details */}
      <div className="space-y-4">
        <div className="bg-white rounded-lg border shadow-sm overflow-hidden">
          <div className="px-6 py-3 bg-gray-50 border-b text-xs font-semibold text-gray-500 uppercase tracking-wider">
            Snapshot Details
          </div>
          {details.map((r) => (
            <div key={r.label} className="px-6 py-3 flex justify-between items-center border-b last:border-0">
              <span className="text-sm text-gray-500">{r.label}</span>
              <span className="text-sm font-mono text-gray-700">{r.value}</span>
            </div>
          ))}
        </div>

        <p className="text-xs text-muted-foreground">
          Actions create <code>ops.backup_jobs</code> rows with actor, timestamps, and evidence.
        </p>
      </div>
    </div>
  )
}
