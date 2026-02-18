import React, { useState, useEffect, useRef } from 'react';

export function Logs() {
  const [source, setSource] = useState<'colima' | 'lima' | 'daemon'>('colima');
  const [logs, setLogs] = useState<string[]>([]);
  const [autoScroll, setAutoScroll] = useState(true);
  const [loading, setLoading] = useState(false);
  const logsEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 2000);
    return () => clearInterval(interval);
  }, [source]);

  useEffect(() => {
    if (autoScroll) {
      logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, autoScroll]);

  const fetchLogs = async () => {
    try {
      const lines = await window.colima.tailLogs({ tail: 200, source });
      setLogs(lines);
    } catch (err) {
      console.error('Failed to fetch logs:', err);
    }
  };

  const handleClear = () => {
    setLogs([]);
  };

  const handleExport = () => {
    const blob = new Blob([logs.join('\n')], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `colima-${source}-logs.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="logs">
      <div className="logs-header">
        <h2>Logs</h2>
        <div className="logs-tabs">
          <button
            onClick={() => setSource('colima')}
            className={source === 'colima' ? 'active' : ''}
          >
            Colima
          </button>
          <button
            onClick={() => setSource('lima')}
            className={source === 'lima' ? 'active' : ''}
          >
            Lima
          </button>
          <button
            onClick={() => setSource('daemon')}
            className={source === 'daemon' ? 'active' : ''}
          >
            Daemon
          </button>
        </div>
        <div className="logs-controls">
          <label>
            <input
              type="checkbox"
              checked={autoScroll}
              onChange={(e) => setAutoScroll(e.target.checked)}
            />
            Auto-scroll
          </label>
          <button onClick={handleClear} className="btn btn-sm">
            Clear
          </button>
          <button onClick={handleExport} className="btn btn-sm">
            Export
          </button>
        </div>
      </div>

      <div className="logs-content">
        {logs.length === 0 ? (
          <div className="logs-empty">No logs available</div>
        ) : (
          logs.map((line, i) => (
            <div key={i} className="log-line">
              <span className="log-number">{i + 1}</span>
              <span className="log-text">{line}</span>
            </div>
          ))
        )}
        <div ref={logsEndRef} />
      </div>
    </div>
  );
}
