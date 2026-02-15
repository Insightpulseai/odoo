import React, { useState, useEffect, useRef } from 'react';
import type { LogSource } from '../../../../../src/shared/contracts/index.js';

type Tab = 'colima' | 'lima' | 'daemon';

interface LogsProps {
  onClose: () => void;
}

export function Logs({ onClose }: LogsProps) {
  const [activeTab, setActiveTab] = useState<Tab>('colima');
  const [logs, setLogs] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [autoScroll, setAutoScroll] = useState(true);
  const [isLive, setIsLive] = useState(true);

  const logsEndRef = useRef<HTMLDivElement>(null);
  const logsContainerRef = useRef<HTMLDivElement>(null);
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    loadLogs();

    if (isLive) {
      startPolling();
    } else {
      stopPolling();
    }

    return () => {
      stopPolling();
    };
  }, [activeTab, isLive]);

  useEffect(() => {
    if (autoScroll && logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, autoScroll]);

  const loadLogs = async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await window.colima.tailLogs({
        tail: 200,
        source: activeTab as LogSource,
      });
      setLogs(result.lines);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load logs');
      setLogs([]);
    } finally {
      setLoading(false);
    }
  };

  const startPolling = () => {
    pollIntervalRef.current = setInterval(() => {
      loadLogs();
    }, 2000);
  };

  const stopPolling = () => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }
  };

  const handleClear = () => {
    setLogs([]);
  };

  const handleExport = async () => {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
    const filename = `colima-${activeTab}-${timestamp}.log`;
    const content = logs.join('\n');

    try {
      const blob = new Blob([content], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to export logs');
    }
  };

  const handleScroll = () => {
    if (!logsContainerRef.current) return;

    const { scrollTop, scrollHeight, clientHeight } = logsContainerRef.current;
    const isAtBottom = Math.abs(scrollHeight - scrollTop - clientHeight) < 10;

    if (!isAtBottom && autoScroll) {
      setAutoScroll(false);
    } else if (isAtBottom && !autoScroll) {
      setAutoScroll(true);
    }
  };

  return (
    <div className="logs-modal">
      <div className="logs-header">
        <h2>Logs</h2>
        <button className="close-button" onClick={onClose}>
          ×
        </button>
      </div>

      <div className="logs-tabs">
        <button
          className={`tab ${activeTab === 'colima' ? 'active' : ''}`}
          onClick={() => setActiveTab('colima')}
        >
          Colima
        </button>
        <button
          className={`tab ${activeTab === 'lima' ? 'active' : ''}`}
          onClick={() => setActiveTab('lima')}
        >
          Lima
        </button>
        <button
          className={`tab ${activeTab === 'daemon' ? 'active' : ''}`}
          onClick={() => setActiveTab('daemon')}
        >
          Daemon
        </button>
      </div>

      <div className="logs-toolbar">
        <div className="toolbar-left">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={autoScroll}
              onChange={(e) => setAutoScroll(e.target.checked)}
            />
            <span>Auto-scroll</span>
          </label>
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={isLive}
              onChange={(e) => setIsLive(e.target.checked)}
            />
            <span>Live updates</span>
          </label>
        </div>
        <div className="toolbar-right">
          <button
            className="button button-small button-secondary"
            onClick={handleClear}
            disabled={logs.length === 0}
          >
            Clear
          </button>
          <button
            className="button button-small button-secondary"
            onClick={handleExport}
            disabled={logs.length === 0}
          >
            Export
          </button>
          <button
            className="button button-small button-primary"
            onClick={loadLogs}
            disabled={loading}
          >
            {loading ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </div>

      {error && (
        <div className="error-banner">
          <span className="error-icon">⚠️</span>
          <span>{error}</span>
        </div>
      )}

      <div
        ref={logsContainerRef}
        className="logs-content"
        onScroll={handleScroll}
      >
        {loading && logs.length === 0 ? (
          <div className="logs-loading">
            <div className="spinner" />
            <p>Loading logs...</p>
          </div>
        ) : logs.length === 0 ? (
          <div className="logs-empty">
            <p>No logs available</p>
          </div>
        ) : (
          <div className="logs-lines">
            {logs.map((line, index) => (
              <div key={index} className="log-line">
                <span className="log-line-number">{index + 1}</span>
                <span className="log-line-content">{line}</span>
              </div>
            ))}
            <div ref={logsEndRef} />
          </div>
        )}
      </div>

      <div className="logs-footer">
        <span className="logs-info">
          {logs.length} lines
          {isLive && <span className="live-indicator"> • Live</span>}
        </span>
      </div>
    </div>
  );
}
