/**
 * Get or create a request correlation ID.
 * Reads x-request-id from incoming headers; generates a UUID if absent.
 */
export function getOrCreateRequestId(existing?: string | null): string {
  return existing?.trim() ? existing : crypto.randomUUID()
}

/**
 * Build standard response headers including correlation ID and cache control.
 */
export function correlationHeaders(
  requestId: string,
  extra?: Record<string, string>
): Record<string, string> {
  return {
    "x-request-id": requestId,
    ...extra,
  }
}
