/**
 * IPC Contracts
 *
 * Electron IPC channel definitions and event types.
 */

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
