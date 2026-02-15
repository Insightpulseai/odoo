/**
 * Shared Types for Colima Desktop
 *
 * These types are shared across:
 * - Daemon (REST API server)
 * - CLI (yargs commands)
 * - Electron UI (renderer + main)
 *
 * All API contracts, config schemas, and state models defined here.
 */

// ============================================================================
// API Response Types
// ============================================================================

/**
 * VM State
 */
export type VMState = 'running' | 'stopped' | 'starting' | 'stopping' | 'error';

/**
 * Log Source
 */
export type LogSource = 'colima' | 'lima' | 'daemon';

/**
 * Log Level
 */
export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

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
 * Lifecycle Request
 * POST /v1/lifecycle/{start,stop,restart}
 */
export interface LifecycleRequest {
  cpu?: number;
  memory?: number;
  disk?: number;
}

/**
 * Lifecycle Response
 */
export interface LifecycleResponse {
  success: boolean;
  message: string;
  restart_required?: boolean;
  changes_applied?: string[];
}

/**
 * Config Response
 * GET /v1/config
 */
export interface ConfigResponse {
  cpu: number;
  memory: number;
  disk: number;
  kubernetes: boolean;
  autostart: boolean;
}

/**
 * Config Update Request
 * PUT /v1/config
 */
export interface ConfigUpdateRequest {
  cpu?: number;
  memory?: number;
  disk?: number;
  kubernetes?: boolean;
  autostart?: boolean;
}

/**
 * Config Update Response
 */
export interface ConfigUpdateResponse {
  success: boolean;
  restart_required: boolean;
  changes: string[];
}

/**
 * Logs Request Query Params
 * GET /v1/logs?tail=N&source=colima
 */
export interface LogsRequest {
  tail?: number;
  source?: LogSource;
}

/**
 * Logs Response
 */
export interface LogsResponse {
  source: LogSource;
  lines: string[];
  total_lines: number;
  truncated: boolean;
}

/**
 * Diagnostics Response
 * POST /v1/diagnostics
 */
export interface DiagnosticsResponse {
  bundle_path: string;
  size_bytes: number;
  timestamp: string;
  contents: string[];
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

// ============================================================================
// Configuration Schema
// ============================================================================

/**
 * Daemon Configuration
 */
export interface DaemonConfig {
  port: number;
  host: string;
  autostart: boolean;
}

/**
 * Colima VM Configuration
 */
export interface ColimaVMConfig {
  cpu: number;
  memory: number;
  disk: number;
  kubernetes: boolean;
  runtime: 'docker' | 'containerd';
}

/**
 * Logging Configuration
 */
export interface LogsConfig {
  retention_days: number;
  max_lines: number;
  level: LogLevel;
}

/**
 * Complete Configuration Schema
 * ~/.colima-desktop/config.yaml
 */
export interface ColimaConfig {
  daemon: DaemonConfig;
  colima: ColimaVMConfig;
  logs: LogsConfig;
}

/**
 * Default Configuration
 */
export const DEFAULT_CONFIG: ColimaConfig = {
  daemon: {
    port: 35100,
    host: 'localhost',
    autostart: false,
  },
  colima: {
    cpu: 4,
    memory: 8,
    disk: 60,
    kubernetes: false,
    runtime: 'docker',
  },
  logs: {
    retention_days: 7,
    max_lines: 1000,
    level: 'info',
  },
};

// ============================================================================
// State Models
// ============================================================================

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

// ============================================================================
// Error Types
// ============================================================================

/**
 * API Error Response
 */
export interface APIError {
  error: string;
  message: string;
  statusCode: number;
  details?: Record<string, unknown>;
}

/**
 * Validation Error
 */
export interface ValidationError {
  field: string;
  message: string;
  received?: unknown;
}

/**
 * Colima CLI Error
 */
export interface ColimaCliError {
  command: string;
  exitCode: number;
  stdout: string;
  stderr: string;
}

// ============================================================================
// Utility Types
// ============================================================================

/**
 * Paths
 */
export interface Paths {
  home: string;
  state_dir: string;
  config_file: string;
  pid_file: string;
  logs_dir: string;
  daemon_log: string;
  colima_log: string;
  lima_log: string;
  diagnostics_dir: string;
}

/**
 * Daemon State
 */
export interface DaemonState {
  running: boolean;
  pid?: number;
  uptime_seconds?: number;
}

/**
 * CLI Command Options
 */
export interface CLIOptions {
  verbose?: boolean;
  quiet?: boolean;
  json?: boolean;
}

/**
 * Start Options
 */
export interface StartOptions extends CLIOptions {
  cpu?: number;
  memory?: number;
  disk?: number;
  kubernetes?: boolean;
}

/**
 * Config Get Options
 */
export interface ConfigGetOptions extends CLIOptions {
  key?: string;
}

/**
 * Config Set Options
 */
export interface ConfigSetOptions extends CLIOptions {
  cpu?: number;
  memory?: number;
  disk?: number;
  kubernetes?: boolean;
  autostart?: boolean;
}

/**
 * Logs Options
 */
export interface LogsOptions extends CLIOptions {
  tail?: number;
  source?: LogSource;
  follow?: boolean;
}

// ============================================================================
// IPC Types (Electron)
// ============================================================================

/**
 * IPC Channels (main <-> renderer)
 */
export enum IPCChannel {
  // Status
  STATUS = 'colima:status',

  // Lifecycle
  START = 'colima:start',
  STOP = 'colima:stop',
  RESTART = 'colima:restart',

  // Config
  GET_CONFIG = 'colima:getConfig',
  SET_CONFIG = 'colima:setConfig',

  // Logs
  TAIL_LOGS = 'colima:tailLogs',

  // Diagnostics
  DIAGNOSTICS = 'colima:diagnostics',

  // Docker
  DOCKER_CONTEXT = 'colima:dockerContext',
  SET_DOCKER_CONTEXT = 'colima:setDockerContext',

  // Events (main -> renderer)
  STATUS_CHANGED = 'status:changed',
  ERROR_OCCURRED = 'error:occurred',
}

/**
 * IPC Event Data
 */
export interface IPCEventData {
  timestamp: string;
  type: string;
  payload: unknown;
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

/**
 * Check if LogSource is valid
 */
export function isLogSource(value: unknown): value is LogSource {
  return (
    typeof value === 'string' &&
    ['colima', 'lima', 'daemon'].includes(value)
  );
}

/**
 * Check if LogLevel is valid
 */
export function isLogLevel(value: unknown): value is LogLevel {
  return (
    typeof value === 'string' &&
    ['debug', 'info', 'warn', 'error'].includes(value)
  );
}

// ============================================================================
// Constants
// ============================================================================

/**
 * API Version
 */
export const API_VERSION = 'v1';

/**
 * Default Values
 */
export const DEFAULTS = {
  PORT: 35100,
  HOST: 'localhost',
  TIMEOUT_MS: 5000,
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY_MS: 1000,
  LOG_TAIL_DEFAULT: 200,
  LOG_MAX_LINES: 1000,
} as const;

/**
 * Validation Constraints
 */
export const CONSTRAINTS = {
  CPU: { min: 1, max: 16 },
  MEMORY: { min: 1, max: 32 },
  DISK: { min: 20, max: 200 },
  PORT: { min: 1024, max: 65535 },
} as const;

/**
 * State Directory (relative to user home)
 */
export const STATE_DIR = '.colima-desktop';

/**
 * Config File Name
 */
export const CONFIG_FILE = 'config.yaml';

/**
 * PID File Name
 */
export const PID_FILE = 'daemon.pid';

/**
 * Log File Names
 */
export const LOG_FILES = {
  DAEMON: 'daemon.log',
  COLIMA: 'colima.log',
  LIMA: 'lima.log',
} as const;
