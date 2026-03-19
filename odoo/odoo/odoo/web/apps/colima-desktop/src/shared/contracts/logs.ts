/**
 * Logs Contracts
 *
 * Log retrieval and streaming API contracts.
 */

// ============================================================================
// Logs Types
// ============================================================================

/**
 * Log Source
 */
export type LogSource = 'colima' | 'lima' | 'daemon';

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

// ============================================================================
// CLI Options
// ============================================================================

/**
 * Logs Options
 */
export interface LogsOptions {
  tail?: number;
  source?: LogSource;
  follow?: boolean;
  verbose?: boolean;
  quiet?: boolean;
  json?: boolean;
}

// ============================================================================
// Type Guards
// ============================================================================

/**
 * Check if LogSource is valid
 */
export function isLogSource(value: unknown): value is LogSource {
  return (
    typeof value === 'string' &&
    ['colima', 'lima', 'daemon'].includes(value)
  );
}
