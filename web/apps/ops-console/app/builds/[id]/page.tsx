import Link from "next/link"

export const dynamic = "force-dynamic"

export default async function BuildDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params

  const steps = [
    { step: 'Install dependencies', status: 'Success', duration: '45s' },
    { step: 'Lint & typecheck', status: 'Success', duration: '18s' },
    { step: 'Unit tests', status: 'Success', duration: '1m 02s' },
    { step: 'Migration check', status: 'Success', duration: '12s' },
    { step: 'Policy gate', status: 'Success', duration: '8s' },
    { step: 'Artifact upload', status: 'Success', duration: '7s' },
  ]

  return (
    <div className="max-w-6xl mx-auto">
      {/* Breadcrumb */}
      <div className="flex items-center space-x-2 mb-8 text-sm">
        <Link href="/builds" className="text-blue-600 hover:underline">Builds</Link>
        <span className="text-gray-300">/</span>
        <span className="font-bold text-gray-700">{id}</span>
      </div>

      {/* Status header */}
      <div className="bg-white rounded-lg border shadow-sm p-6 mb-6">
        <div className="flex flex-wrap items-center gap-3 mb-3">
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-green-100 text-green-700">SUCCESS</span>
          <span className="font-bold text-lg">{id}</span>
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-100 text-blue-700">STAGE</span>
          <span className="text-xs font-mono text-gray-500 bg-gray-100 px-1.5 py-0.5 rounded">9c3d2e1</span>
          <span className="text-xs text-gray-400">by tbwa</span>
          <span className="text-xs text-gray-400">· 3m 12s</span>
          <span className="text-xs text-gray-400">· 1h ago</span>
        </div>
        <div className="text-sm text-gray-500">
          Branch: <span className="font-mono font-medium text-gray-700">main</span>
          <span className="mx-2 text-gray-300">·</span>
          Trigger: <span className="font-medium text-gray-700">push</span>
          <span className="mx-2 text-gray-300">·</span>
          Correlation: <span className="font-mono text-gray-500 text-xs">corr_9c3d2e1</span>
        </div>
        <div className="mt-4 flex items-center gap-3">
          <a href="https://github.com/Insightpulseai/odoo/actions" target="_blank" rel="noopener noreferrer"
            className="text-xs text-blue-600 hover:underline">Open in GitHub Actions →</a>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b mb-6">
        <nav className="-mb-px flex space-x-8">
          {['Summary', 'Logs', 'Artifacts', 'Audit'].map((tab) => (
            <button key={tab} className={`py-2 text-sm font-medium border-b-2 transition-colors ${
              tab === 'Summary'
                ? 'border-primary text-primary'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}>
              {tab}
            </button>
          ))}
        </nav>
      </div>

      {/* Summary tab content */}
      <div className="space-y-4">
        <div className="bg-white rounded-lg border shadow-sm overflow-hidden">
          <div className="px-6 py-3 bg-gray-50 border-b text-xs font-semibold text-gray-500 uppercase tracking-wider">
            Build Steps
          </div>
          {steps.map((s) => (
            <div key={s.step} className="px-6 py-3 flex justify-between items-center border-b last:border-0">
              <span className="text-sm text-gray-700">{s.step}</span>
              <div className="flex items-center space-x-4">
                <span className="text-xs text-gray-400">{s.duration}</span>
                <span className="text-sm font-medium text-green-600">{s.status}</span>
              </div>
            </div>
          ))}
        </div>

        <p className="text-xs text-muted-foreground">
          Data source: <code>ops.builds</code> · <code>ops.jobs</code> · GitHub Actions CI.
        </p>
      </div>
    </div>
  )
}
