"use client"

import { getIntegrationsForSurface, type Integration } from "@/lib/integrations"
import { usePathname } from "next/navigation"
import { Zap } from "lucide-react"

function IntegrationPill({ integration }: { integration: Integration }) {
  const statusColor =
    integration.status === "active"
      ? "bg-green-500/10 text-green-400 border-green-500/20"
      : integration.status === "setup-required"
        ? "bg-yellow-500/10 text-yellow-400 border-yellow-500/20"
        : "bg-white/5 text-muted-foreground border-white/10"

  return (
    <span
      className={`inline-flex items-center gap-1.5 text-[10px] font-semibold px-2 py-1 rounded-full border ${statusColor}`}
    >
      <Zap className="h-2.5 w-2.5" />
      {integration.name}
    </span>
  )
}

/**
 * Renders integration badges relevant to the current page.
 * Place this in page headers to show which integrations power that surface.
 */
export function IntegrationBadges() {
  const pathname = usePathname()
  const integrations = getIntegrationsForSurface(pathname)

  if (integrations.length === 0) return null

  return (
    <div className="flex flex-wrap items-center gap-1.5">
      {integrations.map((i) => (
        <IntegrationPill key={i.id} integration={i} />
      ))}
    </div>
  )
}
