export default function EnvironmentsPage() {
  const envs = [
    { name: 'PROD', host: '178.128.112.214', db: 'odoo-db-sgp1 (odoo_prod)', sha: 'v1.4.2', health: 'Green', lastDeploy: '2h ago', protected: true },
    { name: 'STAGE', host: 'Local/Dev', db: 'odoo_stage', sha: 'main (9c3d2e)', health: 'Green', lastDeploy: '4h ago', protected: false },
  ];

  return (
    <div className="max-w-6xl mx-auto">
      <h2 className="text-2xl font-bold mb-8">Environments</h2>

      <div className="bg-white rounded-lg border shadow-sm overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Env</th>
              <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Host</th>
              <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Database</th>
              <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Current SHA</th>
              <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Health</th>
              <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {envs.map((env) => (
              <tr key={env.name} className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <span className={`px-2 py-0.5 rounded text-xs font-bold ${env.name === 'PROD' ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'}`}>
                    {env.name}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">{env.host}</td>
                <td className="px-6 py-4 text-sm font-mono text-gray-500">{env.db}</td>
                <td className="px-6 py-4 text-sm font-medium">{env.sha}</td>
                <td className="px-6 py-4">
                  <span className="flex items-center space-x-2">
                    <span className="w-2 h-2 rounded-full bg-green-500"></span>
                    <span className="text-sm">{env.health}</span>
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-blue-600 font-medium">
                  <button className="hover:underline mr-4">Healthcheck</button>
                  {env.name === 'PROD' && <button className="hover:underline text-red-600">Rollback</button>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
