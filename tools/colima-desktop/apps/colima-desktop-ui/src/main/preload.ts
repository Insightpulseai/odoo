import { contextBridge, ipcRenderer } from 'electron';
import type {
  StatusResponse,
  ConfigResponse,
  ConfigUpdateRequest,
  ConfigUpdateResponse,
  LogsRequest,
  LogsResponse,
  DiagnosticsResponse,
  LifecycleRequest,
  LifecycleResponse,
} from '../../../../src/shared/contracts/index.js';
import { IPCChannel } from '../../../../src/shared/contracts/index.js';

/**
 * Colima Desktop API
 * Exposed to renderer via contextBridge
 */
export interface ColimaAPI {
  status(): Promise<StatusResponse>;
  start(opts?: LifecycleRequest): Promise<LifecycleResponse>;
  stop(): Promise<LifecycleResponse>;
  restart(opts?: LifecycleRequest): Promise<LifecycleResponse>;
  getConfig(): Promise<ConfigResponse>;
  setConfig(cfg: ConfigUpdateRequest): Promise<ConfigUpdateResponse>;
  tailLogs(opts?: LogsRequest): Promise<LogsResponse>;
  diagnostics(): Promise<DiagnosticsResponse>;
  onStatusChange(callback: (status: StatusResponse) => void): () => void;
}

/**
 * Preload Script
 * Security boundary between main and renderer
 *
 * Security requirements:
 * - contextIsolation: enabled
 * - nodeIntegration: disabled
 * - sandbox: enabled
 * - Only expose safe API via contextBridge
 */
const api: ColimaAPI = {
  /**
   * Get current VM status
   */
  status: () => ipcRenderer.invoke(IPCChannel.STATUS),

  /**
   * Start VM with optional resource overrides
   */
  start: (opts?: LifecycleRequest) => ipcRenderer.invoke(IPCChannel.START, opts),

  /**
   * Stop VM
   */
  stop: () => ipcRenderer.invoke(IPCChannel.STOP),

  /**
   * Restart VM with optional resource overrides
   */
  restart: (opts?: LifecycleRequest) => ipcRenderer.invoke(IPCChannel.RESTART, opts),

  /**
   * Get current configuration
   */
  getConfig: () => ipcRenderer.invoke(IPCChannel.GET_CONFIG),

  /**
   * Update configuration
   */
  setConfig: (cfg: ConfigUpdateRequest) => ipcRenderer.invoke(IPCChannel.SET_CONFIG, cfg),

  /**
   * Tail logs
   */
  tailLogs: (opts?: LogsRequest) => ipcRenderer.invoke(IPCChannel.TAIL_LOGS, opts),

  /**
   * Generate diagnostics bundle
   */
  diagnostics: () => ipcRenderer.invoke(IPCChannel.DIAGNOSTICS),

  /**
   * Listen for status changes
   */
  onStatusChange: (callback: (status: StatusResponse) => void) => {
    const listener = (_event: Electron.IpcRendererEvent, status: StatusResponse) => {
      callback(status);
    };

    ipcRenderer.on(IPCChannel.STATUS_CHANGED, listener);

    // Return unsubscribe function
    return () => {
      ipcRenderer.removeListener(IPCChannel.STATUS_CHANGED, listener);
    };
  },
};

/**
 * Expose API to renderer
 */
contextBridge.exposeInMainWorld('colima', api);

/**
 * Type declaration for renderer
 */
declare global {
  interface Window {
    colima: ColimaAPI;
  }
}
