/**
 * InsightPulseAI Platform SDK - Error Handling
 * Phase 5B: SaaS Platform Kit - SDK Creation
 */

import { AIError, AIErrorCode } from './types';

/**
 * Parse HTTP error response and create AIError
 */
export function parseHTTPError(
  response: Response,
  body?: string
): AIError {
  // Map HTTP status to error code
  const statusCode = response.status;

  let code: AIErrorCode;
  let message: string;

  switch (statusCode) {
    case 400:
      code = AIErrorCode.INVALID_REQUEST;
      message = 'Invalid request parameters';
      break;

    case 401:
    case 403:
      code = AIErrorCode.AUTH_ERROR;
      message = 'Authentication failed - check API key';
      break;

    case 404:
      code = AIErrorCode.SERVICE_UNAVAILABLE;
      message = 'AI service not found - Edge Function may not be deployed';
      break;

    case 429:
      code = AIErrorCode.RATE_LIMIT_ERROR;
      message = 'Rate limit exceeded - try again later';
      break;

    case 500:
    case 502:
    case 503:
    case 504:
      code = AIErrorCode.SERVICE_UNAVAILABLE;
      message = 'AI service temporarily unavailable';
      break;

    default:
      code = AIErrorCode.UNKNOWN_ERROR;
      message = `HTTP ${statusCode}: ${response.statusText}`;
  }

  // Try to parse error details from body
  let details: any;
  if (body) {
    try {
      details = JSON.parse(body);
      // Supabase Edge Function error format
      if (details.message) {
        message = details.message;
      }
    } catch {
      // Body not JSON, use as-is
      if (body.length < 200) {
        message += `: ${body}`;
      }
    }
  }

  return new AIError(code, message, statusCode, details);
}

/**
 * Parse network/fetch error and create AIError
 */
export function parseNetworkError(error: Error): AIError {
  // Timeout
  if (error.name === 'AbortError') {
    return new AIError(
      AIErrorCode.NETWORK_ERROR,
      'Request timeout - AI service took too long to respond'
    );
  }

  // Connection refused / DNS failure
  if (error.message.includes('fetch') || error.message.includes('network')) {
    return new AIError(
      AIErrorCode.NETWORK_ERROR,
      `Network error: ${error.message}`
    );
  }

  // Generic error
  return new AIError(
    AIErrorCode.UNKNOWN_ERROR,
    error.message
  );
}

/**
 * Validate client configuration
 */
export function validateConfig(
  supabaseUrl?: string,
  apiKey?: string
): AIError | null {
  if (!supabaseUrl || !supabaseUrl.trim()) {
    return new AIError(
      AIErrorCode.CONFIG_ERROR,
      'Supabase URL is required'
    );
  }

  if (!apiKey || !apiKey.trim()) {
    return new AIError(
      AIErrorCode.CONFIG_ERROR,
      'API key is required'
    );
  }

  // Validate URL format
  try {
    const url = new URL(supabaseUrl);
    if (!url.hostname.includes('supabase.co') && !url.hostname.includes('localhost')) {
      return new AIError(
        AIErrorCode.CONFIG_ERROR,
        'Invalid Supabase URL format'
      );
    }
  } catch {
    return new AIError(
      AIErrorCode.CONFIG_ERROR,
      'Invalid Supabase URL format'
    );
  }

  return null;
}
