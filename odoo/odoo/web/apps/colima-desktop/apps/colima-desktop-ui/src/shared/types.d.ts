/**
 * Type definitions for Colima Desktop UI
 *
 * Re-exports types from daemon shared contracts
 */

// Import types from daemon
import type {
  StatusResponse,
  ColimaConfig,
  LifecycleRequest,
} from '../../../../tools/colima-desktop/src/shared/contracts/index.js';

// Re-export for convenience
export type { StatusResponse, ColimaConfig, LifecycleRequest };

// Window API declaration
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
      setConfig(config: Partial<ColimaConfig>): Promise<{
        restart_required: boolean;
      }>;

      // Logs
      tailLogs(opts: {
        tail?: number;
        source?: 'colima' | 'lima' | 'daemon';
      }): Promise<string[]>;

      // Diagnostics
      diagnostics(): Promise<{ bundle_path: string }>;

      // Events
      onStatusChange(callback: (status: StatusResponse) => void): () => void;
    };
  }
}

export {};
