import {
  fetchIntegrations,
  INTEGRATIONS,
  type CatalogEntry,
  type DbStatus,
} from "@/lib/integrations"
import { IntegrationsClient } from "./integrations-client"

// 5-minute revalidation — integrations catalog is stable.
export const revalidate = 300

// ── Static fallback shape mapper ──────────────────────────────────────────────
// Converts the legacy static INTEGRATIONS array into CatalogEntry shape so
// IntegrationsClient always receives a uniform data type regardless of source.
function staticFallback(): CatalogEntry[] {
  return INTEGRATIONS.map((i) => ({
    key:              i.id,
    name:             i.name,
    category:         (i.category === "auth" ? "auth_data" : i.category === "ai" ? "ai_inference" : i.category) as CatalogEntry["category"],
    provider:         (i.billing === "vercel" ? "vercel_marketplace" : "direct") as CatalogEntry["provider"],
    description:      i.description,
    baseline_allowed: true,
    plan_tier:        "baseline",
    cost_band:        (i.billing === "free" ? "free" : "included") as CatalogEntry["cost_band"],
    vendor_lock_in:   "low",
    capabilities:     [],
    surfaces:         i.surfaces,
    env_keys:         i.envKeys,
    docs_url:         i.docsUrl ?? null,
    status:           i.status.replace("-", "_") as DbStatus,
    billing:          i.billing,
    evidence:         {},
    last_checked_at:  null,
  }))
}

export default async function IntegrationsPage() {
  // Prefer live DB data; fall back to static array if unavailable
  const entries: CatalogEntry[] = (await fetchIntegrations()) ?? staticFallback()
  return <IntegrationsClient entries={entries} />
}
