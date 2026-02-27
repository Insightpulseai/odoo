/**
 * Vercel team integrations registry.
 * Source of truth for integration metadata displayed across the console.
 *
 * Update this file when integrations are added/removed from the Vercel dashboard.
 */

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
