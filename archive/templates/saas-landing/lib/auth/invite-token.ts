import crypto from 'crypto'

/**
 * Generate a secure 256-bit invite token (64 hex characters)
 */
export function generateInviteToken(): string {
  return crypto.randomBytes(32).toString('hex')
}

/**
 * Validate token format (64 hex characters)
 */
export function isValidTokenFormat(token: string): boolean {
  return /^[0-9a-f]{64}$/.test(token)
}

/**
 * Hash token with SHA-256 (for database storage)
 * Note: This is done in the database via RPC function
 */
export function hashToken(token: string): string {
  return crypto.createHash('sha256').update(token).digest('hex')
}
