/**
 * Contracts Barrel Export
 *
 * Centralized export of all API contracts, types, and constants.
 * This is the stable public API surface for daemon, CLI, and UI.
 */

// Status contracts
export type {
  VMState,
  StatusResponse,
  ColimaStatus,
  ColimaVersionInfo,
  DockerContextInfo,
  DockerContextResponse,
  DockerContextSetRequest,
  DockerContextSetResponse,
  DaemonState,
} from './status.js';
export { isVMState } from './status.js';

// Config contracts
export type {
  LogLevel,
  DaemonConfig,
  ColimaVMConfig,
  LogsConfig,
  ColimaConfig,
  ConfigResponse,
  ConfigUpdateRequest,
  ConfigUpdateResponse,
  Paths,
} from './config.js';
export {
  DEFAULT_CONFIG,
  CONSTRAINTS,
  STATE_DIR,
  CONFIG_FILE,
  PID_FILE,
  LOG_FILES,
  isLogLevel,
} from './config.js';

// Lifecycle contracts
export type {
  LifecycleRequest,
  LifecycleResponse,
  CLIOptions,
  StartOptions,
  ConfigGetOptions,
  ConfigSetOptions,
} from './lifecycle.js';

// Logs contracts
export type {
  LogSource,
  LogsRequest,
  LogsResponse,
  LogsOptions,
} from './logs.js';
export { isLogSource } from './logs.js';

// Diagnostics contracts
export type {
  DiagnosticsResponse,
} from './diagnostics.js';

// Error contracts
export type {
  APIError,
  ValidationError,
  ColimaCliError,
} from './errors.js';

// IPC contracts
export {
  IPCChannel,
} from './ipc.js';
export type {
  IPCEventData,
} from './ipc.js';

// Constants
export {
  API_VERSION,
  DEFAULTS,
} from './constants.js';
