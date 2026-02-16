import { contextBridge, ipcRenderer } from 'electron';
import type { StatusResponse, ColimaConfig, LifecycleRequest } from '../shared/types';

// Expose secure API to renderer via contextBridge
contextBridge.exposeInMainWorld('colima', {
  // Status
  status: (): Promise<StatusResponse> => ipcRenderer.invoke('colima:status'),

  // Lifecycle
  start: (opts?: LifecycleRequest): Promise<void> => ipcRenderer.invoke('colima:start', opts),
  stop: (): Promise<void> => ipcRenderer.invoke('colima:stop'),
  restart: (opts?: LifecycleRequest): Promise<void> => ipcRenderer.invoke('colima:restart', opts),

  // Config
  getConfig: (): Promise<ColimaConfig> => ipcRenderer.invoke('colima:getConfig'),
  setConfig: (config: Partial<ColimaConfig>): Promise<{ restart_required: boolean }> =>
    ipcRenderer.invoke('colima:setConfig', config),

  // Logs
  tailLogs: (opts: { tail?: number; source?: string }): Promise<string[]> =>
    ipcRenderer.invoke('colima:tailLogs', opts),

  // Diagnostics
  diagnostics: (): Promise<{ bundle_path: string }> => ipcRenderer.invoke('colima:diagnostics'),

  // Events
  onStatusChange: (callback: (status: StatusResponse) => void): (() => void) => {
    const listener = (_event: Electron.IpcRendererEvent, status: StatusResponse) => callback(status);
    ipcRenderer.on('status:changed', listener);
    
    // Return unsubscribe function
    return () => {
      ipcRenderer.removeListener('status:changed', listener);
    };
  },
});
