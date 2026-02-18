/**
 * Lifecycle Contracts
 *
 * VM lifecycle management API contracts (start/stop/restart).
 */

// ============================================================================
// Lifecycle Types
// ============================================================================

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

// ============================================================================
// CLI Options
// ============================================================================

/**
 * Base CLI Options
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
