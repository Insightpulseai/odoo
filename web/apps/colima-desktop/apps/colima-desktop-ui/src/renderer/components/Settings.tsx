import React, { useState, useEffect } from 'react';
import type { ColimaConfig } from '../../shared/types';

export function Settings() {
  const [config, setConfig] = useState<ColimaConfig | null>(null);
  const [cpu, setCpu] = useState(4);
  const [memory, setMemory] = useState(8);
  const [disk, setDisk] = useState(60);
  const [kubernetes, setKubernetes] = useState(false);
  const [autostart, setAutostart] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      const cfg = await window.colima.getConfig();
      setConfig(cfg);
      setCpu(cfg.colima.cpu);
      setMemory(cfg.colima.memory);
      setDisk(cfg.colima.disk);
      setKubernetes(cfg.colima.kubernetes);
      setAutostart(cfg.daemon.autostart);
    } catch (err) {
      console.error('Failed to load config:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setMessage(null);
    try {
      const result = await window.colima.setConfig({
        colima: { cpu, memory, disk, kubernetes, runtime: 'docker' },
        daemon: { autostart, port: 35100, host: 'localhost' },
        logs: { level: 'info', retention_days: 7, max_lines: 1000 },
      });

      if (result.restart_required) {
        if (confirm('Changes require VM restart. Restart now?')) {
          await window.colima.restart();
          setMessage('VM restarting...');
        } else {
          setMessage('Config saved. Restart required to apply.');
        }
      } else {
        setMessage('Config saved successfully');
      }
    } catch (err) {
      setMessage(`Error: ${(err as Error).message}`);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="settings">Loading settings...</div>;
  }

  return (
    <div className="settings">
      <h2>Settings</h2>
      
      <div className="setting-group">
        <label>
          CPU Cores: {cpu}
          <input
            type="range"
            min="1"
            max="16"
            value={cpu}
            onChange={(e) => setCpu(parseInt(e.target.value))}
          />
        </label>
      </div>

      <div className="setting-group">
        <label>
          Memory (GB): {memory}
          <input
            type="range"
            min="1"
            max="32"
            value={memory}
            onChange={(e) => setMemory(parseInt(e.target.value))}
          />
        </label>
      </div>

      <div className="setting-group">
        <label>
          Disk (GB): {disk}
          <input
            type="range"
            min="20"
            max="200"
            value={disk}
            onChange={(e) => setDisk(parseInt(e.target.value))}
          />
        </label>
      </div>

      <div className="setting-group">
        <label>
          <input
            type="checkbox"
            checked={kubernetes}
            onChange={(e) => setKubernetes(e.target.checked)}
          />
          Enable Kubernetes
        </label>
      </div>

      <div className="setting-group">
        <label>
          <input
            type="checkbox"
            checked={autostart}
            onChange={(e) => setAutostart(e.target.checked)}
          />
          Launch daemon on login
        </label>
      </div>

      <div className="setting-actions">
        <button onClick={handleSave} disabled={saving} className="btn btn-primary">
          {saving ? 'Saving...' : 'Apply'}
        </button>
        <button onClick={loadConfig} disabled={saving} className="btn">
          Reset
        </button>
      </div>

      {message && <div className="setting-message">{message}</div>}
    </div>
  );
}
