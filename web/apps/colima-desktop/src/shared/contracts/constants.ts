/**
 * Constants
 *
 * API version, defaults, and constraint definitions.
 */

// ============================================================================
// API Constants
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
