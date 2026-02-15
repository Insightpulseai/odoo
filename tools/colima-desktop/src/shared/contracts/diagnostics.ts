/**
 * Diagnostics Contracts
 *
 * Diagnostics bundle generation API contracts.
 */

// ============================================================================
// Diagnostics Types
// ============================================================================

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
