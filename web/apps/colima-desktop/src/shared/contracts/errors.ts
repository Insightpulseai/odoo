/**
 * Error Contracts
 *
 * Error types and validation error structures.
 */

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
