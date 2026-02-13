/**
 * Environment-scoped secret resolver for single Supabase project
 *
 * Enforces STAGE__/PROD__ prefixing to prevent accidental secret mixing.
 *
 * Usage:
 *   import { getEnvSecret } from "../_shared/env.ts";
 *   const apiKey = getEnvSecret("OPENAI_API_KEY");
 *   // Resolves to STAGE__OPENAI_API_KEY or PROD__OPENAI_API_KEY
 */

export type Environment = "staging" | "prod";
export type Prefix = "STAGE__" | "PROD__";

/**
 * Determine environment prefix from ENVIRONMENT variable.
 * Throws if ENVIRONMENT is not set or invalid.
 */
export function envPrefix(): Prefix {
  const env = (Deno.env.get("ENVIRONMENT") || "").toLowerCase();

  if (env === "staging" || env === "stage") {
    return "STAGE__";
  }

  if (env === "prod" || env === "production") {
    return "PROD__";
  }

  throw new Error(
    `ENVIRONMENT must be set to 'staging' or 'prod' (got: '${env}'). ` +
    `This function refuses to run without explicit environment specification ` +
    `to prevent accidental stage/prod secret mixing.`
  );
}

/**
 * Get environment name (staging or prod).
 * Throws if ENVIRONMENT is not set or invalid.
 */
export function getEnvironment(): Environment {
  const env = (Deno.env.get("ENVIRONMENT") || "").toLowerCase();

  if (env === "staging" || env === "stage") {
    return "staging";
  }

  if (env === "prod" || env === "production") {
    return "prod";
  }

  throw new Error(
    `ENVIRONMENT must be set to 'staging' or 'prod' (got: '${env}')`
  );
}

/**
 * Get a secret by exact name.
 * Throws if the secret is not set.
 */
export function getSecret(name: string): string {
  const value = Deno.env.get(name);
  if (!value) {
    throw new Error(`Missing required secret: ${name}`);
  }
  return value;
}

/**
 * Get an environment-scoped secret.
 * Automatically prefixes with STAGE__ or PROD__ based on ENVIRONMENT.
 *
 * Example:
 *   getEnvSecret("OPENAI_API_KEY")
 *   // Returns STAGE__OPENAI_API_KEY in staging
 *   // Returns PROD__OPENAI_API_KEY in prod
 */
export function getEnvSecret(key: string): string {
  const prefix = envPrefix();
  const fullName = `${prefix}${key}`;
  return getSecret(fullName);
}

/**
 * Get an optional environment-scoped secret.
 * Returns undefined if not set.
 */
export function getOptionalEnvSecret(key: string): string | undefined {
  try {
    return getEnvSecret(key);
  } catch {
    return undefined;
  }
}

/**
 * Check if running in staging environment.
 */
export function isStaging(): boolean {
  return getEnvironment() === "staging";
}

/**
 * Check if running in production environment.
 */
export function isProduction(): boolean {
  return getEnvironment() === "prod";
}
