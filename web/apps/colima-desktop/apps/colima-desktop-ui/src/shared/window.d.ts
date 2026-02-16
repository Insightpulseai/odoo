// Global type definitions for window.colima API exposed by preload script
import type { StatusResponse, ColimaConfig, LifecycleRequest } from './types';

declare global {
  interface Window {
    colima: {
      // Status
      status(): Promise<StatusResponse>;

      // Lifecycle
      start(opts?: LifecycleRequest): Promise<void>;
      stop(): Promise<void>;
      restart(opts?: LifecycleRequest): Promise<void>;

      // Config
      getConfig(): Promise<ColimaConfig>;
      setConfig(config: Partial<ColimaConfig>): Promise<{ restart_required: boolean }>;

      // Logs
      tailLogs(opts: { tail?: number; source?: string }): Promise<string[]>;

      // Diagnostics
      diagnostics(): Promise<{ bundle_path: string }>;

      // Events
      onStatusChange(callback: (status: StatusResponse) => void): () => void;
    };
  }
}

export {};
