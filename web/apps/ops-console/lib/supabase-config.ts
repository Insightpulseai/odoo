/**
 * Supabase Project Configuration
 *
 * Resolves the Supabase project reference from:
 * 1. URL query parameter (?project_ref=xxx or ?ref=xxx)
 * 2. URL path segment (/project/<ref>/...)
 * 3. Environment variable (NEXT_PUBLIC_SUPABASE_PROJECT_REF)
 */

/**
 * Resolves the Supabase project reference from URL or environment.
 * Call this on the client side only (requires window.location).
 *
 * @returns The project ref string, or null if not found
 */
export function resolveProjectRef(): string | null {
  // Server-side: return env var only
  if (typeof window === 'undefined') {
    return process.env.NEXT_PUBLIC_SUPABASE_PROJECT_REF || null
  }

  const url = new URL(window.location.href)

  // 1) Query param: ?project_ref=xxx or ?ref=xxx
  const queryRef = url.searchParams.get('project_ref') || url.searchParams.get('ref')
  if (queryRef && isValidProjectRef(queryRef)) {
    return queryRef
  }

  // 2) Path segment: /project/<ref>/...
  const pathMatch = url.pathname.match(/\/project\/([a-z0-9]+)(\/|$)/i)
  if (pathMatch?.[1] && isValidProjectRef(pathMatch[1])) {
    return pathMatch[1]
  }

  // 3) Environment variable fallback
  const envRef = process.env.NEXT_PUBLIC_SUPABASE_PROJECT_REF
  if (envRef && isValidProjectRef(envRef)) {
    return envRef
  }

  return null
}

/**
 * Validates that a string looks like a valid Supabase project ref.
 * Project refs are typically 20 lowercase alphanumeric characters.
 */
export function isValidProjectRef(ref: string): boolean {
  // Supabase project refs are typically 20 chars, lowercase alphanumeric
  // Allow some flexibility: 10-30 chars, alphanumeric
  return /^[a-z0-9]{10,30}$/i.test(ref)
}

/**
 * Hook-friendly version that returns project ref with validation status.
 */
export function getProjectRefConfig(): {
  projectRef: string | null
  isValid: boolean
  source: 'url_query' | 'url_path' | 'env' | 'none'
  error?: string
} {
  if (typeof window === 'undefined') {
    const envRef = process.env.NEXT_PUBLIC_SUPABASE_PROJECT_REF
    if (envRef && isValidProjectRef(envRef)) {
      return { projectRef: envRef, isValid: true, source: 'env' }
    }
    return {
      projectRef: null,
      isValid: false,
      source: 'none',
      error: 'NEXT_PUBLIC_SUPABASE_PROJECT_REF environment variable is not set',
    }
  }

  const url = new URL(window.location.href)

  // Check query param
  const queryRef = url.searchParams.get('project_ref') || url.searchParams.get('ref')
  if (queryRef) {
    if (isValidProjectRef(queryRef)) {
      return { projectRef: queryRef, isValid: true, source: 'url_query' }
    }
    return {
      projectRef: queryRef,
      isValid: false,
      source: 'url_query',
      error: `Invalid project ref in URL: "${queryRef}"`,
    }
  }

  // Check path
  const pathMatch = url.pathname.match(/\/project\/([a-z0-9]+)(\/|$)/i)
  if (pathMatch?.[1]) {
    if (isValidProjectRef(pathMatch[1])) {
      return { projectRef: pathMatch[1], isValid: true, source: 'url_path' }
    }
    return {
      projectRef: pathMatch[1],
      isValid: false,
      source: 'url_path',
      error: `Invalid project ref in path: "${pathMatch[1]}"`,
    }
  }

  // Check env
  const envRef = process.env.NEXT_PUBLIC_SUPABASE_PROJECT_REF
  if (envRef) {
    if (isValidProjectRef(envRef)) {
      return { projectRef: envRef, isValid: true, source: 'env' }
    }
    return {
      projectRef: envRef,
      isValid: false,
      source: 'env',
      error: `Invalid NEXT_PUBLIC_SUPABASE_PROJECT_REF: "${envRef}"`,
    }
  }

  return {
    projectRef: null,
    isValid: false,
    source: 'none',
    error: 'No Supabase project ref found. Set NEXT_PUBLIC_SUPABASE_PROJECT_REF or add ?ref=<project_ref> to URL.',
  }
}
