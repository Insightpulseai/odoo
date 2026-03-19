import React, { useState, useEffect } from 'react';
import type { StatusResponse, VMState } from '../../../../tools/colima-desktop/src/shared/contracts/status';

interface StatusIndicatorProps {
  state: VMState;
}

function StatusIndicator({ state }: StatusIndicatorProps) {
  const getColor = () => {
    switch (state) {
      case 'running':
        return '#34c759';
      case 'stopped':
        return '#8e8e93';
      case 'starting':
      case 'stopping':
        return '#ff9500';
      case 'error':
        return '#ff3b30';
      default:
        return '#8e8e93';
    }
  };

  const getLabel = () => {
    return state.charAt(0).toUpperCase() + state.slice(1);
  };

  return (
    <div className="status-indicator">
      <div
        className="status-dot"
        style={{ backgroundColor: getColor() }}
        aria-label={`VM status: ${getLabel()}`}
      />
      <span className="status-label">{getLabel()}</span>
    </div>
  );
}

function formatUptime(seconds: number): string {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;

  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  } else if (minutes > 0) {
    return `${minutes}m ${secs}s`;
  } else {
    return `${secs}s`;
  }
}

function formatBytes(gb: number): string {
  return `${gb.toFixed(2)} GB`;
}

export function Status() {
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        setError(null);
        const data = await window.colima.status();
        setStatus(data);
        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch status');
        setLoading(false);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="status-panel" role="status" aria-live="polite">
        <div className="status-loading">Loading status...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="status-panel" role="alert">
        <div className="status-error">
          <strong>Error:</strong> {error}
        </div>
      </div>
    );
  }

  if (!status) {
    return null;
  }

  return (
    <div className="status-panel" role="region" aria-label="VM Status">
      <div className="status-header">
        <StatusIndicator state={status.state} />
        {status.state === 'running' && (
          <span className="status-uptime">
            Uptime: {formatUptime(status.uptime_seconds)}
          </span>
        )}
      </div>

      <div className="status-resources">
        <div className="resource-card">
          <div className="resource-label">CPU</div>
          <div className="resource-value">
            <strong>{status.cpu.allocated}</strong> cores
          </div>
          {status.state === 'running' && (
            <div className="resource-usage">
              <div className="usage-bar">
                <div
                  className="usage-fill"
                  style={{ width: `${status.cpu.usage_percent}%` }}
                  role="progressbar"
                  aria-valuenow={status.cpu.usage_percent}
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-label={`CPU usage: ${status.cpu.usage_percent}%`}
                />
              </div>
              <span className="usage-text">{status.cpu.usage_percent.toFixed(1)}%</span>
            </div>
          )}
        </div>

        <div className="resource-card">
          <div className="resource-label">Memory</div>
          <div className="resource-value">
            <strong>{formatBytes(status.memory.allocated_gb)}</strong>
          </div>
          {status.state === 'running' && (
            <div className="resource-usage">
              <div className="usage-bar">
                <div
                  className="usage-fill"
                  style={{
                    width: `${(status.memory.used_gb / status.memory.allocated_gb) * 100}%`,
                  }}
                  role="progressbar"
                  aria-valuenow={status.memory.used_gb}
                  aria-valuemin={0}
                  aria-valuemax={status.memory.allocated_gb}
                  aria-label={`Memory usage: ${formatBytes(status.memory.used_gb)} of ${formatBytes(status.memory.allocated_gb)}`}
                />
              </div>
              <span className="usage-text">
                {formatBytes(status.memory.used_gb)} / {formatBytes(status.memory.allocated_gb)}
              </span>
            </div>
          )}
        </div>

        <div className="resource-card">
          <div className="resource-label">Disk</div>
          <div className="resource-value">
            <strong>{formatBytes(status.disk.allocated_gb)}</strong>
          </div>
          {status.state === 'running' && (
            <div className="resource-usage">
              <div className="usage-bar">
                <div
                  className="usage-fill"
                  style={{
                    width: `${(status.disk.used_gb / status.disk.allocated_gb) * 100}%`,
                  }}
                  role="progressbar"
                  aria-valuenow={status.disk.used_gb}
                  aria-valuemin={0}
                  aria-valuemax={status.disk.allocated_gb}
                  aria-label={`Disk usage: ${formatBytes(status.disk.used_gb)} of ${formatBytes(status.disk.allocated_gb)}`}
                />
              </div>
              <span className="usage-text">
                {formatBytes(status.disk.used_gb)} / {formatBytes(status.disk.allocated_gb)}
              </span>
            </div>
          )}
        </div>
      </div>

      <div className="status-info">
        <div className="info-row">
          <span className="info-label">Kubernetes:</span>
          <span className="info-value">
            {status.kubernetes.enabled ? (
              <>
                Enabled
                {status.kubernetes.context && (
                  <span className="info-detail"> ({status.kubernetes.context})</span>
                )}
              </>
            ) : (
              'Disabled'
            )}
          </span>
        </div>
        <div className="info-row">
          <span className="info-label">Docker Context:</span>
          <span className="info-value">{status.docker_context.active}</span>
        </div>
        <div className="info-row">
          <span className="info-label">Version:</span>
          <span className="info-value">{status.colima_version}</span>
        </div>
      </div>
    </div>
  );
}
