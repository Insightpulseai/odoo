/**
 * Status Contracts
 *
 * VM status and resource monitoring API contracts.
 */

// ============================================================================
// Status Types
// ============================================================================

/**
 * VM State
 */
export type VMState = 'running' | 'stopped' | 'starting' | 'stopping' | 'error';

/**
 * Status Response
 * GET /v1/status
 */
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

/**
 * Colima CLI Status Output (parsed)
 */
export interface ColimaStatus {
  state: VMState;
  cpu: number;
  memory: number;
  disk: number;
  kubernetes: boolean;
  arch: string;
  runtime: 'docker' | 'containerd';
}

/**
 * Colima Version Info
 */
export interface ColimaVersionInfo {
  colima_version: string;
  lima_version: string;
  qemu_version: string;
}

/**
 * Docker Context Info
 */
export interface DockerContextInfo {
  name: string;
  endpoint: string;
  docker_endpoint: string;
}

/**
 * Docker Context Response
 * GET /v1/docker/context
 */
export interface DockerContextResponse {
  active: string;
  socket_path: string;
  socket_exists: boolean;
  colima_running: boolean;
}

/**
 * Docker Context Set Request
 * POST /v1/docker/context/set
 */
export interface DockerContextSetRequest {
  context: 'colima' | 'default';
}

/**
 * Docker Context Set Response
 */
export interface DockerContextSetResponse {
  success: boolean;
  previous: string;
  current: string;
}

/**
 * Daemon State
 */
export interface DaemonState {
  running: boolean;
  pid?: number;
  uptime_seconds?: number;
}

// ============================================================================
// Type Guards
// ============================================================================

/**
 * Check if VMState is valid
 */
export function isVMState(value: unknown): value is VMState {
  return (
    typeof value === 'string' &&
    ['running', 'stopped', 'starting', 'stopping', 'error'].includes(value)
  );
}
