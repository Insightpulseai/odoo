export default function GatesPage() {
  const gates = [
    { name: 'OCA Allowlist', description: 'Modules must be in addons/oca/selected', status: 'Passed', lastRun: '2h ago', result: 'All 42 submodules verified.' },
    { name: 'Risk-Tier Labels', description: 'High-risk modules require manual approval labels', status: 'Passed', lastRun: '2h ago', result: 'No high-risk violations found.' },
    { name: 'Diagram Drift', description: 'Draw.io vs PNG sync', status: 'Warning', lastRun: '1h ago', result: '1 drift in L3_Services.drawio' },
    { name: 'Lint & Tests', description: 'Flake8 and Unit Tests', status: 'Passed', lastRun: '4h ago', result: '0 errors, 126 tests passed.' },
  ];

  return (
    <div className="max-w-6xl mx-auto">
      <h2 className="text-2xl font-bold mb-8">Policy Gates</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {gates.map((gate) => (
          <div key={gate.name} className="bg-white p-6 rounded-lg border shadow-sm">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-lg font-bold">{gate.name}</h3>
                <p className="text-sm text-gray-500">{gate.description}</p>
              </div>
              <span className={`px-2 py-0.5 rounded text-xs font-bold ${gate.status === 'Passed' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>
                {gate.status}
              </span>
            </div>
            <div className="p-4 bg-gray-50 rounded text-sm font-mono text-gray-600 mb-4">
              {gate.result}
            </div>
            <div className="flex items-center justify-between text-xs text-gray-400">
              <span>Last checked: {gate.lastRun}</span>
              <button className="text-blue-600 font-medium hover:underline">View GitHub Run</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
