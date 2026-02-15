import { ipcMain, BrowserWindow } from 'electron';
import type { StatusResponse, ColimaConfig, LifecycleRequest } from '../../../../tools/colima-desktop/src/shared/contracts/index.js';

const BASE_URL = 'http://localhost:35100';
let statusPollInterval: NodeJS.Timeout | null = null;
let lastStatus: StatusResponse | null = null;

export function setupIPCHandlers(window: BrowserWindow) {
  // Status
  ipcMain.handle('colima:status', async () => {
    const res = await fetch(`${BASE_URL}/v1/status`);
    if (!res.ok) throw new Error(`Status request failed: ${res.statusText}`);
    return res.json();
  });

  // Start
  ipcMain.handle('colima:start', async (_event, opts?: LifecycleRequest) => {
    const res = await fetch(`${BASE_URL}/v1/lifecycle/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(opts || {}),
    });
    if (!res.ok) throw new Error(`Start request failed: ${res.statusText}`);
    return res.json();
  });

  // Stop
  ipcMain.handle('colima:stop', async () => {
    const res = await fetch(`${BASE_URL}/v1/lifecycle/stop`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error(`Stop request failed: ${res.statusText}`);
    return res.json();
  });

  // Restart
  ipcMain.handle('colima:restart', async (_event, opts?: LifecycleRequest) => {
    const res = await fetch(`${BASE_URL}/v1/lifecycle/restart`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(opts || {}),
    });
    if (!res.ok) throw new Error(`Restart request failed: ${res.statusText}`);
    return res.json();
  });

  // Get config
  ipcMain.handle('colima:getConfig', async () => {
    const res = await fetch(`${BASE_URL}/v1/config`);
    if (!res.ok) throw new Error(`Get config failed: ${res.statusText}`);
    return res.json();
  });

  // Set config
  ipcMain.handle('colima:setConfig', async (_event, config: Partial<ColimaConfig>) => {
    const res = await fetch(`${BASE_URL}/v1/config`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config),
    });
    if (!res.ok) throw new Error(`Set config failed: ${res.statusText}`);
    return res.json();
  });

  // Tail logs
  ipcMain.handle('colima:tailLogs', async (_event, opts: { tail?: number; source?: string }) => {
    const params = new URLSearchParams();
    if (opts.tail) params.set('tail', opts.tail.toString());
    if (opts.source) params.set('source', opts.source);
    
    const res = await fetch(`${BASE_URL}/v1/logs?${params}`);
    if (!res.ok) throw new Error(`Tail logs failed: ${res.statusText}`);
    const data = await res.json();
    return data.lines || [];
  });

  // Diagnostics
  ipcMain.handle('colima:diagnostics', async () => {
    const res = await fetch(`${BASE_URL}/v1/diagnostics`, { method: 'POST' });
    if (!res.ok) throw new Error(`Diagnostics failed: ${res.statusText}`);
    return res.json();
  });

  // Start status polling
  startStatusPolling(window);
}

export function cleanupIPCHandlers() {
  if (statusPollInterval) {
    clearInterval(statusPollInterval);
    statusPollInterval = null;
  }
  
  ipcMain.removeHandler('colima:status');
  ipcMain.removeHandler('colima:start');
  ipcMain.removeHandler('colima:stop');
  ipcMain.removeHandler('colima:restart');
  ipcMain.removeHandler('colima:getConfig');
  ipcMain.removeHandler('colima:setConfig');
  ipcMain.removeHandler('colima:tailLogs');
  ipcMain.removeHandler('colima:diagnostics');
}

function startStatusPolling(window: BrowserWindow) {
  statusPollInterval = setInterval(async () => {
    try {
      const res = await fetch(`${BASE_URL}/v1/status`);
      if (res.ok) {
        const status: StatusResponse = await res.json();
        
        // Only emit if status changed
        if (JSON.stringify(status) !== JSON.stringify(lastStatus)) {
          window.webContents.send('status:changed', status);
          lastStatus = status;
        }
      }
    } catch (err) {
      // Silently ignore polling errors
    }
  }, 5000);
}
