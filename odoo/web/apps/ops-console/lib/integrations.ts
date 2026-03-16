/**
 * Vercel team integrations registry.
 *
 * Static fallback: INTEGRATIONS array (used when DB is unavailable).
 * Runtime source:  ops.integrations_view (Supabase) via fetchIntegrations().
 *
 * PlanGuard fields (plan_tier, cost_band, baseline_allowed) control
 * which integrations appear in the default "Baseline-ready" view.
 */

// ── Legacy types (keep for backward compat with IntegrationBadges, etc.) ─────
export type IntegrationCategory = "ai" | "auth" | "agents" | "messaging" | "devtools"
export type IntegrationStatus = "active" | "inactive" | "setup-required"
export type IntegrationBilling = "vercel" | "direct" | "free"

export interface Integration {
  id: string
  name: string
  category: IntegrationCategory
  billing: IntegrationBilling
  status: IntegrationStatus
  description: string
  /** Console pages where this integration is relevant */
  surfaces: string[]
  /** Env vars required for this integration to function */
  envKeys: string[]
  docsUrl?: string
}

// ── Extended catalog types (ops.integrations_catalog) ─────────────────────────
export type PlanTier   = "baseline" | "optional" | "enterprise_only"
export type CostBand   = "free" | "included" | "low" | "medium" | "high"
export type VendorLockIn = "low" | "medium" | "high"
export type DbCategory =
  | "auth_data" | "ai_inference" | "agents" | "devtools" | "messaging"
  | "observability" | "storage" | "security" | "analytics" | "workflow"
export type DbStatus  = "active" | "inactive" | "error" | "setup_required"
export type Provider  = "vercel_marketplace" | "supabase_native" | "direct" | "custom_bridge"

/** Full row from ops.integrations_view */
export interface CatalogEntry {
  key: string
  name: string
  category: DbCategory
  provider: Provider
  description: string | null
  baseline_allowed: boolean
  plan_tier: PlanTier
  cost_band: CostBand
  vendor_lock_in: VendorLockIn
  capabilities: string[]
  surfaces: string[]
  env_keys: string[]
  docs_url: string | null
  status: DbStatus
  billing: string
  evidence: Record<string, unknown>
  last_checked_at: string | null
}

export const INTEGRATIONS: Integration[] = [
  {
    id: "supabase",
    name: "Supabase",
    category: "auth",
    billing: "vercel",
    status: "active",
    description: "Authentication, database, storage, and edge functions. Primary backend for ops data.",
    surfaces: ["/database", "/platform", "/settings"],
    envKeys: ["NEXT_PUBLIC_SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_MANAGEMENT_API_TOKEN"],
  },
  {
    id: "groq",
    name: "Groq",
    category: "ai",
    billing: "vercel",
    status: "active",
    description: "Ultra-fast LLM inference for real-time AI operations and scoring.",
    surfaces: ["/advisor"],
    envKeys: ["GROQ_API_KEY"],
  },
  {
    id: "fal",
    name: "fal",
    category: "ai",
    billing: "vercel",
    status: "active",
    description: "Serverless AI for media processing, image generation, and multimodal tasks.",
    surfaces: ["/advisor"],
    envKeys: ["FAL_KEY"],
  },
  {
    id: "inngest",
    name: "Inngest",
    category: "devtools",
    billing: "vercel",
    status: "active",
    description: "Event-driven background functions, workflows, and scheduled jobs.",
    surfaces: ["/deployments", "/advisor"],
    envKeys: ["INNGEST_EVENT_KEY", "INNGEST_SIGNING_KEY"],
  },
  {
    id: "browserbase",
    name: "Browserbase",
    category: "agents",
    billing: "vercel",
    status: "active",
    description: "Headless browser infrastructure for AI agents and automated testing.",
    surfaces: [],
    envKeys: ["BROWSERBASE_API_KEY"],
  },
  {
    id: "autonoma",
    name: "Autonoma AI",
    category: "agents",
    billing: "vercel",
    status: "active",
    description: "Autonomous AI agents for platform operations and monitoring tasks.",
    surfaces: [],
    envKeys: ["AUTONOMA_API_KEY"],
  },
  {
    id: "slack",
    name: "Slack",
    category: "messaging",
    billing: "direct",
    status: "active",
    description: "Team notifications for deployments, alerts, and gate failures.",
    surfaces: ["/settings"],
    envKeys: ["SLACK_WEBHOOK_URL"],
  },
]

export function getIntegrationsByCategory(category: IntegrationCategory): Integration[] {
  return INTEGRATIONS.filter((i) => i.category === category)
}

export function getIntegrationsForSurface(pathname: string): Integration[] {
  return INTEGRATIONS.filter((i) => i.surfaces.includes(pathname))
}

export const CATEGORY_LABELS: Record<IntegrationCategory, string> = {
  ai: "AI & Inference",
  auth: "Authentication & Data",
  agents: "Agents",
  messaging: "Messaging",
  devtools: "Developer Tools",
}

export const CATEGORY_ORDER: IntegrationCategory[] = ["auth", "ai", "agents", "devtools", "messaging"]

// ── DB category labels (extended set) ────────────────────────────────────────
export const DB_CATEGORY_LABELS: Record<DbCategory, string> = {
  auth_data:    "Authentication & Data",
  ai_inference: "AI & Inference",
  agents:       "Agents",
  devtools:     "Developer Tools",
  messaging:    "Messaging",
  observability:"Observability",
  storage:      "Storage",
  security:     "Security",
  analytics:    "Analytics",
  workflow:     "Workflow",
}

export const DB_CATEGORY_ORDER: DbCategory[] = [
  "auth_data", "ai_inference", "agents", "devtools", "messaging",
  "observability", "workflow", "analytics", "storage", "security",
]

export const PLAN_TIER_LABELS: Record<PlanTier, string> = {
  baseline:        "Baseline",
  optional:        "Optional spend",
  enterprise_only: "Enterprise only",
}

// ── Runtime fetch from ops.integrations_view ─────────────────────────────────
/**
 * Fetches the full catalog + installation status from Supabase.
 * Returns null on any error so callers can fall back to static data.
 * Only safe to call from Server Components or API routes (uses service role key).
 */
export async function fetchIntegrations(): Promise<CatalogEntry[] | null> {
  const supabaseUrl = process.env.SUPABASE_URL ?? process.env.NEXT_PUBLIC_SUPABASE_URL ?? ""
  const serviceKey  = process.env.SUPABASE_SERVICE_ROLE_KEY ?? ""
  if (!supabaseUrl || !serviceKey) return null

  try {
    const res = await fetch(
      `${supabaseUrl}/rest/v1/integrations_view?select=*`,
      {
        headers: {
          apikey:        serviceKey,
          Authorization: `Bearer ${serviceKey}`,
          Accept:        "application/json",
        },
        // 5-minute cache — integrations status doesn't change frequently
        next: { revalidate: 300 },
      }
    )
    if (!res.ok) return null
    return (await res.json()) as CatalogEntry[]
  } catch {
    return null
  }
}
