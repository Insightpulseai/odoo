// Type definitions for Colima Desktop Electron app
// These mirror the daemon's contract types

export type VMState = 'running' | 'stopped' | 'starting' | 'stopping' | 'error';

export interface StatusResponse {
  state: VMState;
  cpu: {
    allocated: number;
    usage_percent: number;
  };
  memory: {
    allocated_gb: number;
    used_gb: number;
  };
  disk: {
    allocated_gb: number;
    used_gb: number;
  };
  kubernetes: {
    enabled: boolean;
    context: string | null;
  };
  docker_context: {
    active: string;
    socket: string;
  };
  uptime_seconds: number;
  colima_version: string;
  lima_version: string;
}

export interface ColimaConfig {
  daemon: {
    port: number;
    host: string;
    autostart: boolean;
  };
  colima: {
    cpu: number;
    memory: number;
    disk: number;
    kubernetes: boolean;
    runtime: 'docker' | 'containerd';
  };
  logs: {
    retention_days: number;
    max_lines: number;
    level: 'debug' | 'info' | 'warn' | 'error';
  };
}

export interface LifecycleRequest {
  cpu?: number;
  memory?: number;
  disk?: number;
}
