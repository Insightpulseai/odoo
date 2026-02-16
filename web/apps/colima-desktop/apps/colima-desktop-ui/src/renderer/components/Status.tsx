import React, { useState, useEffect } from 'react';
import type { StatusResponse } from '../../shared/types';

export function Status() {
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const data = await window.colima.status();
        setStatus(data);
        setError(null);
      } catch (err) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <div className="status loading">Loading status...</div>;
  }

  if (error) {
    return <div className="status error">Error: {error}</div>;
  }

  if (!status) {
    return <div className="status">No status available</div>;
  }

  const getStatusColor = () => {
    switch (status.state) {
      case 'running':
        return 'green';
      case 'stopped':
        return 'red';
      case 'starting':
      case 'stopping':
        return 'yellow';
      default:
        return 'gray';
    }
  };

  const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  return (
    <div className="status">
      <div className="status-header">
        <div className={`status-indicator ${getStatusColor()}`} />
        <span className="status-state">{status.state}</span>
      </div>

      <div className="status-metrics">
        <div className="metric">
          <label>CPU</label>
          <div className="metric-bar">
            <div
              className="metric-fill"
              style={{ width: `${status.cpu.usage_percent}%` }}
            />
          </div>
          <span>
            {status.cpu.usage_percent.toFixed(1)}% of {status.cpu.allocated} cores
          </span>
        </div>

        <div className="metric">
          <label>Memory</label>
          <div className="metric-bar">
            <div
              className="metric-fill"
              style={{ width: `${(status.memory.used_gb / status.memory.allocated_gb) * 100}%` }}
            />
          </div>
          <span>
            {status.memory.used_gb.toFixed(1)} GB / {status.memory.allocated_gb} GB
          </span>
        </div>

        <div className="metric">
          <label>Disk</label>
          <div className="metric-bar">
            <div
              className="metric-fill"
              style={{ width: `${(status.disk.used_gb / status.disk.allocated_gb) * 100}%` }}
            />
          </div>
          <span>
            {status.disk.used_gb.toFixed(1)} GB / {status.disk.allocated_gb} GB
          </span>
        </div>
      </div>

      <div className="status-info">
        <div><strong>Kubernetes:</strong> {status.kubernetes.enabled ? 'Enabled' : 'Disabled'}</div>
        <div><strong>Docker Context:</strong> {status.docker_context.active}</div>
        <div><strong>Uptime:</strong> {formatUptime(status.uptime_seconds)}</div>
        <div className="status-versions">
          <small>Colima {status.colima_version} · Lima {status.lima_version}</small>
        </div>
      </div>
    </div>
  );
}
