/**
 * App Store Connect API v1 source for the Ops Advisor scorer.
 *
 * Checks app state, build status, TestFlight groups, and privacy labels.
 * Requires an App Store Connect API key (JWT-based, not Apple ID/password).
 *
 * Environment variables:
 *   ASC_KEY_ID       — API key ID
 *   ASC_ISSUER_ID    — Issuer ID
 *   ASC_KEY_CONTENT  — Base64-encoded .p8 key content
 *   ASC_APP_ID       — App ID (numeric, from App Store Connect URL)
 */

const ASC_BASE = "https://api.appstoreconnect.apple.com/v1"

export interface AppStoreConnectConfig {
  keyId: string
  issuerId: string
  keyContent: string // base64-encoded .p8 PEM
  appId: string
}

// ── JWT generation (requires jsonwebtoken — installed if scorer runs in Node 18+) ──

/** Generate a short-lived App Store Connect JWT token (10 minutes). */
async function generateToken(cfg: AppStoreConnectConfig): Promise<string> {
  // TODO: implement JWT signing with ES256 algorithm using ASC_KEY_CONTENT
  // Payload: { iss: issuerId, iat, exp: iat+600, aud: "appstoreconnect-v1" }
  // Header: { alg: "ES256", kid: keyId, typ: "JWT" }
  throw new Error("generateToken: JWT signing not yet implemented — install jsonwebtoken")
}

/** Fetch helper with ASC JWT auth. */
async function ascFetch(path: string, cfg: AppStoreConnectConfig): Promise<unknown> {
  const token = await generateToken(cfg)
  const res = await fetch(`${ASC_BASE}${path}`, {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  })
  if (!res.ok) throw new Error(`ASC API error ${res.status}: ${await res.text()}`)
  return res.json()
}

// ── Source checks ──────────────────────────────────────────────────────────────

/** Check if a build has been submitted to TestFlight (status = VALID). */
export async function checkBuildSubmitted(cfg: AppStoreConnectConfig): Promise<boolean> {
  try {
    const data = (await ascFetch(
      `/apps/${cfg.appId}/builds?filter[processingState]=VALID&limit=1`,
      cfg
    )) as { data: unknown[] }
    return data.data.length > 0
  } catch {
    return false
  }
}

/** Check if Privacy Nutrition Labels have been completed. */
export async function checkPrivacyLabelsComplete(cfg: AppStoreConnectConfig): Promise<boolean> {
  try {
    const data = (await ascFetch(
      `/apps/${cfg.appId}/appDataUsages?limit=1`,
      cfg
    )) as { data: unknown[] }
    // If at least one privacy category is declared, labels are considered started.
    // Full completeness check requires reviewing all required categories.
    return data.data.length > 0
  } catch {
    return false
  }
}

/** Check if at least one external TestFlight group exists. */
export async function checkTestFlightGroupExists(cfg: AppStoreConnectConfig): Promise<boolean> {
  try {
    const data = (await ascFetch(
      `/apps/${cfg.appId}/betaGroups?filter[isInternalGroup]=false&limit=1`,
      cfg
    )) as { data: unknown[] }
    return data.data.length > 0
  } catch {
    return false
  }
}

/** Get crash-free rate from App Store Connect analytics (requires separate analytics API). */
export async function getCrashFreeRate(cfg: AppStoreConnectConfig): Promise<number | null> {
  // TODO: implement via App Store Connect Analytics API
  // https://developer.apple.com/documentation/appstoreconnectapi/app_analytics
  return null
}

/** Check if age rating questionnaire is complete. */
export async function checkAgeRatingSet(cfg: AppStoreConnectConfig): Promise<boolean> {
  try {
    const data = (await ascFetch(
      `/apps/${cfg.appId}/ageRatingDeclaration`,
      cfg
    )) as { data: { attributes?: Record<string, unknown> } }
    return Object.keys(data.data?.attributes ?? {}).length > 0
  } catch {
    return false
  }
}

/** Check if screenshots exist for required device sizes. */
export async function checkScreenshotsExist(cfg: AppStoreConnectConfig): Promise<boolean> {
  try {
    const versions = (await ascFetch(
      `/apps/${cfg.appId}/appStoreVersions?filter[platform]=IOS&limit=1`,
      cfg
    )) as { data: { id: string }[] }
    if (versions.data.length === 0) return false

    const versionId = versions.data[0].id
    const localizations = (await ascFetch(
      `/appStoreVersions/${versionId}/appStoreVersionLocalizations?limit=1`,
      cfg
    )) as { data: { id: string }[] }
    if (localizations.data.length === 0) return false

    const locId = localizations.data[0].id
    const screenshots = (await ascFetch(
      `/appStoreVersionLocalizations/${locId}/appScreenshotSets?limit=1`,
      cfg
    )) as { data: unknown[] }
    return screenshots.data.length > 0
  } catch {
    return false
  }
}

/** Get ASC config from environment variables. Returns null if not configured. */
export function getAscConfig(): AppStoreConnectConfig | null {
  const keyId = process.env.ASC_KEY_ID
  const issuerId = process.env.ASC_ISSUER_ID
  const keyContent = process.env.ASC_KEY_CONTENT
  const appId = process.env.ASC_APP_ID
  if (!keyId || !issuerId || !keyContent || !appId) return null
  return { keyId, issuerId, keyContent, appId }
}
