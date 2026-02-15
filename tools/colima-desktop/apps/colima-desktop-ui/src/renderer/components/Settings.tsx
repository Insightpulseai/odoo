import React, { useState, useEffect } from 'react';
import type { ColimaConfig, ConfigUpdateResponse, CONSTRAINTS } from '../../../../../src/shared/contracts/index.js';

const CPU_MIN = 1;
const CPU_MAX = 16;
const MEMORY_MIN = 1;
const MEMORY_MAX = 32;
const DISK_MIN = 20;
const DISK_MAX = 200;

interface SettingsProps {
  onClose: () => void;
}

export function Settings({ onClose }: SettingsProps) {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [originalConfig, setOriginalConfig] = useState<ColimaConfig | null>(null);
  const [cpu, setCpu] = useState(4);
  const [memory, setMemory] = useState(8);
  const [disk, setDisk] = useState(60);
  const [kubernetes, setKubernetes] = useState(false);
  const [autostart, setAutostart] = useState(false);

  const [cpuError, setCpuError] = useState<string | null>(null);
  const [memoryError, setMemoryError] = useState<string | null>(null);
  const [diskError, setDiskError] = useState<string | null>(null);

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      setLoading(true);
      setError(null);
      const config = await window.colima.getConfig();
      setOriginalConfig(config);
      setCpu(config.colima.cpu);
      setMemory(config.colima.memory);
      setDisk(config.colima.disk);
      setKubernetes(config.colima.kubernetes);
      setAutostart(config.daemon.autostart);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load configuration');
    } finally {
      setLoading(false);
    }
  };

  const validateCpu = (value: number): boolean => {
    if (value < CPU_MIN || value > CPU_MAX) {
      setCpuError(`CPU must be between ${CPU_MIN} and ${CPU_MAX}`);
      return false;
    }
    setCpuError(null);
    return true;
  };

  const validateMemory = (value: number): boolean => {
    if (value < MEMORY_MIN || value > MEMORY_MAX) {
      setMemoryError(`Memory must be between ${MEMORY_MIN} and ${MEMORY_MAX} GB`);
      return false;
    }
    setMemoryError(null);
    return true;
  };

  const validateDisk = (value: number): boolean => {
    if (value < DISK_MIN || value > DISK_MAX) {
      setDiskError(`Disk must be between ${DISK_MIN} and ${DISK_MAX} GB`);
      return false;
    }
    setDiskError(null);
    return true;
  };

  const handleCpuChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value, 10);
    setCpu(value);
    validateCpu(value);
  };

  const handleMemoryChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value, 10);
    setMemory(value);
    validateMemory(value);
  };

  const handleDiskChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value, 10);
    setDisk(value);
    validateDisk(value);
  };

  const hasChanges = () => {
    if (!originalConfig) return false;
    return (
      cpu !== originalConfig.colima.cpu ||
      memory !== originalConfig.colima.memory ||
      disk !== originalConfig.colima.disk ||
      kubernetes !== originalConfig.colima.kubernetes ||
      autostart !== originalConfig.daemon.autostart
    );
  };

  const handleApply = async () => {
    if (!validateCpu(cpu) || !validateMemory(memory) || !validateDisk(disk)) {
      return;
    }

    try {
      setSaving(true);
      setError(null);

      const result: ConfigUpdateResponse = await window.colima.setConfig({
        cpu,
        memory,
        disk,
        kubernetes,
        autostart,
      });

      if (result.restart_required) {
        const confirmed = confirm(
          'Changes require VM restart. This will stop all running containers.\n\n' +
          `Changes:\n${result.changes.join('\n')}\n\n` +
          'Continue with restart?'
        );

        if (confirmed) {
          await window.colima.restart();
          onClose();
        } else {
          await loadConfig();
        }
      } else {
        onClose();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save configuration');
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    onClose();
  };

  if (loading) {
    return (
      <div className="settings-modal">
        <div className="settings-header">
          <h2>Settings</h2>
        </div>
        <div className="settings-loading">
          <div className="spinner" />
          <p>Loading configuration...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="settings-modal">
      <div className="settings-header">
        <h2>Settings</h2>
        <button className="close-button" onClick={onClose} disabled={saving}>
          ×
        </button>
      </div>

      {error && (
        <div className="error-banner">
          <span className="error-icon">⚠️</span>
          <span>{error}</span>
        </div>
      )}

      <div className="settings-body">
        <div className="setting-group">
          <label htmlFor="cpu-slider">
            <span className="setting-label">CPU Cores</span>
            <span className="setting-value">{cpu}</span>
          </label>
          <input
            id="cpu-slider"
            type="range"
            min={CPU_MIN}
            max={CPU_MAX}
            value={cpu}
            onChange={handleCpuChange}
            disabled={saving}
            className={cpuError ? 'error' : ''}
          />
          <div className="slider-labels">
            <span>{CPU_MIN}</span>
            <span>{CPU_MAX}</span>
          </div>
          {cpuError && <div className="validation-error">{cpuError}</div>}
        </div>

        <div className="setting-group">
          <label htmlFor="memory-slider">
            <span className="setting-label">Memory (GB)</span>
            <span className="setting-value">{memory}</span>
          </label>
          <input
            id="memory-slider"
            type="range"
            min={MEMORY_MIN}
            max={MEMORY_MAX}
            value={memory}
            onChange={handleMemoryChange}
            disabled={saving}
            className={memoryError ? 'error' : ''}
          />
          <div className="slider-labels">
            <span>{MEMORY_MIN}</span>
            <span>{MEMORY_MAX}</span>
          </div>
          {memoryError && <div className="validation-error">{memoryError}</div>}
        </div>

        <div className="setting-group">
          <label htmlFor="disk-slider">
            <span className="setting-label">Disk (GB)</span>
            <span className="setting-value">{disk}</span>
          </label>
          <input
            id="disk-slider"
            type="range"
            min={DISK_MIN}
            max={DISK_MAX}
            value={disk}
            onChange={handleDiskChange}
            disabled={saving}
            className={diskError ? 'error' : ''}
          />
          <div className="slider-labels">
            <span>{DISK_MIN}</span>
            <span>{DISK_MAX}</span>
          </div>
          {diskError && <div className="validation-error">{diskError}</div>}
        </div>

        <div className="setting-group toggle-group">
          <label htmlFor="kubernetes-toggle">
            <span className="setting-label">Kubernetes</span>
            <span className="setting-description">Enable Kubernetes cluster</span>
          </label>
          <input
            id="kubernetes-toggle"
            type="checkbox"
            checked={kubernetes}
            onChange={(e) => setKubernetes(e.target.checked)}
            disabled={saving}
            className="toggle-input"
          />
        </div>

        <div className="setting-group toggle-group">
          <label htmlFor="autostart-toggle">
            <span className="setting-label">Launch at Login</span>
            <span className="setting-description">Start daemon automatically on system boot</span>
          </label>
          <input
            id="autostart-toggle"
            type="checkbox"
            checked={autostart}
            onChange={(e) => setAutostart(e.target.checked)}
            disabled={saving}
            className="toggle-input"
          />
        </div>
      </div>

      <div className="settings-footer">
        <button
          className="button button-secondary"
          onClick={handleCancel}
          disabled={saving}
        >
          Cancel
        </button>
        <button
          className="button button-primary"
          onClick={handleApply}
          disabled={saving || !hasChanges() || cpuError !== null || memoryError !== null || diskError !== null}
        >
          {saving ? (
            <>
              <span className="spinner-small" />
              Saving...
            </>
          ) : (
            'Apply'
          )}
        </button>
      </div>
    </div>
  );
}
