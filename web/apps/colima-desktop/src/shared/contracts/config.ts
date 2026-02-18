/**
 * Configuration Contracts
 *
 * Configuration schema, validation, and update API contracts.
 */

// ============================================================================
// Configuration Schema
// ============================================================================

/**
 * Log Level
 */
export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

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

/**
 * Validation Constraints
 */
export const CONSTRAINTS = {
  CPU: { min: 1, max: 16 },
  MEMORY: { min: 1, max: 32 },
  DISK: { min: 20, max: 200 },
  PORT: { min: 1024, max: 65535 },
} as const;

// ============================================================================
// API Contracts
// ============================================================================

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

// ============================================================================
// Type Guards
// ============================================================================

/**
 * Check if LogLevel is valid
 */
export function isLogLevel(value: unknown): value is LogLevel {
  return (
    typeof value === 'string' &&
    ['debug', 'info', 'warn', 'error'].includes(value)
  );
}
