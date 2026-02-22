export default function DeploymentsPage() {
  const deployments = [
    { id: 'DP-892', env: 'PROD', version: 'v1.4.2', author: 'tbwa', time: '2h ago', status: 'Success', duration: '4m 12s' },
    { id: 'DP-891', env: 'STAGE', version: 'main', author: 'github-actions', time: '4h ago', status: 'Success', duration: '2m 45s' },
    { id: 'DP-890', env: 'STAGE', version: 'fix/config', author: 'tbwa', time: '6h ago', status: 'Failed', duration: '1m 20s' },
  ];

  return (
    <div className="max-w-6xl mx-auto">
      <h2 className="text-2xl font-bold mb-8">Deployments</h2>

      <div className="bg-white rounded-lg border shadow-sm overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">ID</th>
              <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Env</th>
              <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Version</th>
              <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Author</th>
              <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Status</th>
              <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Duration</th>
              <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Time</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {deployments.map((d) => (
              <tr key={d.id} className="hover:bg-gray-50 cursor-pointer">
                <td className="px-6 py-4 text-sm font-bold text-blue-600">{d.id}</td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${d.env === 'PROD' ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'}`}>
                    {d.env}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm font-mono text-gray-600">{d.version}</td>
                <td className="px-6 py-4 text-sm text-gray-500">{d.author}</td>
                <td className="px-6 py-4">
                  <span className={`text-sm font-medium ${d.status === 'Success' ? 'text-green-600' : 'text-red-600'}`}>
                    {d.status}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-400">{d.duration}</td>
                <td className="px-6 py-4 text-sm text-gray-400">{d.time}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
