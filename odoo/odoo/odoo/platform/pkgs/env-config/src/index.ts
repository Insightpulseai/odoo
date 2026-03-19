/**
 * Universal environment configuration for IPAI monorepo
 * Handles Vite, Next.js, and Expo environment variable prefixes
 */

type EnvSource = Record<string, string | undefined>

/**
 * Pick the first defined value from multiple possible env var names
 * Supports: VITE_PUBLIC_, VITE_, NEXT_PUBLIC_, EXPO_PUBLIC_, and unprefixed
 */
function pick(sources: EnvSource[], ...keys: string[]): string {
  for (const key of keys) {
    for (const source of sources) {
      const value = source[key]
      if (typeof value === 'string' && value.length > 0) {
        return value
      }
    }
  }
  return ''
}

/**
 * Get all available env sources based on runtime
 */
function getEnvSources(): EnvSource[] {
  const sources: EnvSource[] = []

  // Vite compile-time env (import.meta.env)
  if (typeof import.meta !== 'undefined' && (import.meta as any).env) {
    sources.push((import.meta as any).env)
  }

  // Node.js / Next.js runtime env
  if (typeof process !== 'undefined' && process.env) {
    sources.push(process.env as EnvSource)
  }

  // Global fallback (for some edge runtimes)
  if (typeof globalThis !== 'undefined') {
    sources.push(globalThis as unknown as EnvSource)
  }

  return sources
}

/**
 * Supabase configuration with multi-prefix support
 */
export function getSupabaseConfig() {
  const sources = getEnvSources()

  const url = pick(
    sources,
    'VITE_PUBLIC_SUPABASE_URL',
    'VITE_SUPABASE_URL',
    'NEXT_PUBLIC_SUPABASE_URL',
    'EXPO_PUBLIC_SUPABASE_URL',
    'SUPABASE_URL'
  )

  const anonKey = pick(
    sources,
    'VITE_PUBLIC_SUPABASE_ANON_KEY',
    'VITE_SUPABASE_ANON_KEY',
    'NEXT_PUBLIC_SUPABASE_ANON_KEY',
    'EXPO_PUBLIC_SUPABASE_ANON_KEY',
    'SUPABASE_ANON_KEY'
  )

  const serviceRoleKey = pick(
    sources,
    'SUPABASE_SERVICE_ROLE_KEY'
  )

  return { url, anonKey, serviceRoleKey }
}

/**
 * OpenAI/AI provider configuration
 */
export function getAIConfig() {
  const sources = getEnvSources()

  return {
    openaiApiKey: pick(sources, 'OPENAI_API_KEY'),
    anthropicApiKey: pick(sources, 'ANTHROPIC_API_KEY'),
    geminiApiKey: pick(sources, 'GEMINI_API_KEY', 'GOOGLE_AI_API_KEY'),
  }
}

/**
 * General app configuration
 */
export function getAppConfig() {
  const sources = getEnvSources()

  return {
    appUrl: pick(
      sources,
      'VITE_PUBLIC_APP_URL',
      'NEXT_PUBLIC_APP_URL',
      'EXPO_PUBLIC_APP_URL',
      'APP_URL'
    ),
    siteUrl: pick(
      sources,
      'VITE_PUBLIC_SITE_URL',
      'NEXT_PUBLIC_SITE_URL',
      'SITE_URL'
    ),
    tenantId: pick(sources, 'TENANT_ID'),
  }
}

/**
 * Validate required environment variables and throw if missing
 */
export function validateEnv(config: Record<string, string>, required: string[]): void {
  const missing = required.filter((key) => !config[key])
  if (missing.length > 0) {
    throw new Error(`Missing or invalid environment variables: ${missing.join(', ')}`)
  }
}

/**
 * Get and validate Supabase config - throws if required vars missing
 */
export function getRequiredSupabaseConfig() {
  const config = getSupabaseConfig()
  validateEnv(config, ['url', 'anonKey'])
  return config as { url: string; anonKey: string; serviceRoleKey: string }
}

/**
 * Environment type detection
 */
export function getEnvType(): 'vite' | 'next' | 'expo' | 'node' | 'unknown' {
  if (typeof import.meta !== 'undefined' && (import.meta as any).env?.MODE) {
    return 'vite'
  }
  if (typeof process !== 'undefined' && process.env.NEXT_RUNTIME) {
    return 'next'
  }
  if (typeof process !== 'undefined' && process.env.EXPO_PUBLIC_URL) {
    return 'expo'
  }
  if (typeof process !== 'undefined' && process.versions?.node) {
    return 'node'
  }
  return 'unknown'
}

/**
 * Check if running in production
 */
export function isProduction(): boolean {
  const sources = getEnvSources()
  const nodeEnv = pick(sources, 'NODE_ENV')
  const mode = pick(sources, 'MODE')
  return nodeEnv === 'production' || mode === 'production'
}

/**
 * Check if running in development
 */
export function isDevelopment(): boolean {
  const sources = getEnvSources()
  const nodeEnv = pick(sources, 'NODE_ENV')
  const mode = pick(sources, 'MODE')
  return nodeEnv === 'development' || mode === 'development'
}

// Re-export types
export type { EnvSource }
