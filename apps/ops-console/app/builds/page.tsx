import Link from "next/link"

export const dynamic = "force-dynamic"

export default function BuildsPage() {
  const builds = [
    { id: 'CI-142', branch: 'main', commit: '9c3d2e1', trigger: 'push', status: 'Success', duration: '3m 12s', time: '1h ago', env: 'STAGE' },
    { id: 'CI-141', branch: 'fix/invoice-pdf', commit: 'a4f8b3c', trigger: 'push', status: 'Failed', duration: '1m 45s', time: '3h ago', env: 'DEV' },
    { id: 'CI-140', branch: 'main', commit: 'f1e2d3a', trigger: 'schedule', status: 'Success', duration: '2m 58s', time: '6h ago', env: 'STAGE' },
  ]

  const statusColor = (status: string) =>
    status === 'Success' ? 'text-green-600' : status === 'Failed' ? 'text-red-600' : 'text-yellow-600'

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-2xl font-bold">Builds</h2>
          <p className="text-sm text-muted-foreground mt-1">CI pipeline — branch → install → tests → policy gates → artifact.</p>
        </div>
      </div>

      <div className="bg-white rounded-lg border shadow-sm overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Build</th>
              <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Branch</th>
              <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Commit</th>
              <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Trigger</th>
              <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Status</th>
              <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Duration</th>
              <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Time</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {builds.map((b) => (
              <tr key={b.id} className="hover:bg-gray-50 cursor-pointer">
                <td className="px-6 py-4 text-sm font-bold text-blue-600">
                  <Link href={`/builds/${b.id}`}>{b.id}</Link>
                </td>
                <td className="px-6 py-4 text-sm font-mono text-gray-600">{b.branch}</td>
                <td className="px-6 py-4 text-sm font-mono text-gray-400">{b.commit}</td>
                <td className="px-6 py-4 text-sm text-gray-500">{b.trigger}</td>
                <td className="px-6 py-4">
                  <span className={`text-sm font-medium ${statusColor(b.status)}`}>{b.status}</span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-400">{b.duration}</td>
                <td className="px-6 py-4 text-sm text-gray-400">{b.time}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <p className="mt-3 text-xs text-muted-foreground">
        Data source: <code>ops.builds</code> populated by GitHub Actions CI.
      </p>
    </div>
  )
}
