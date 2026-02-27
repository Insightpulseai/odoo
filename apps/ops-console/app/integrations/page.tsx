import {
  INTEGRATIONS,
  CATEGORY_LABELS,
  CATEGORY_ORDER,
  type Integration,
  type IntegrationCategory,
} from "@/lib/integrations"
import { Badge } from "@/components/ui/badge"
import {
  Database,
  Cpu,
  Bot,
  MessageSquare,
  Wrench,
  Zap,
  ExternalLink,
  CheckCircle2,
  AlertCircle,
  Clock,
} from "lucide-react"

export const dynamic = "force-static"

const CATEGORY_ICONS: Record<IntegrationCategory, React.ComponentType<{ className?: string }>> = {
  auth: Database,
  ai: Cpu,
  agents: Bot,
  messaging: MessageSquare,
  devtools: Wrench,
}

const STATUS_CONFIG = {
  active: { label: "Active", icon: CheckCircle2, className: "bg-green-500/10 text-green-400 border-green-500/20" },
  inactive: { label: "Inactive", icon: AlertCircle, className: "bg-red-500/10 text-red-400 border-red-500/20" },
  "setup-required": { label: "Setup Required", icon: Clock, className: "bg-yellow-500/10 text-yellow-400 border-yellow-500/20" },
}

const BILLING_LABELS = {
  vercel: "Billed via Vercel",
  direct: "Direct billing",
  free: "Free",
}

function IntegrationCard({ integration }: { integration: Integration }) {
  const status = STATUS_CONFIG[integration.status]
  const StatusIcon = status.icon

  return (
    <div className="glass-card rounded-xl p-5 space-y-3">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center">
            <Zap className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h3 className="text-sm font-bold">{integration.name}</h3>
            <span className="text-[10px] text-muted-foreground uppercase tracking-wider">
              {BILLING_LABELS[integration.billing]}
            </span>
          </div>
        </div>
        <Badge
          variant="outline"
          className={`text-[10px] font-bold border ${status.className}`}
        >
          <StatusIcon className="h-3 w-3 mr-1" />
          {status.label}
        </Badge>
      </div>

      <p className="text-xs text-muted-foreground leading-relaxed">
        {integration.description}
      </p>

      <div className="flex items-center justify-between pt-1">
        <div className="flex flex-wrap gap-1">
          {integration.surfaces.map((s) => (
            <Badge
              key={s}
              variant="secondary"
              className="text-[9px] font-mono px-1.5 py-0"
            >
              {s}
            </Badge>
          ))}
          {integration.surfaces.length === 0 && (
            <span className="text-[10px] text-muted-foreground/50">No console surfaces yet</span>
          )}
        </div>
        {integration.docsUrl && (
          <a
            href={integration.docsUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary hover:underline text-[10px] flex items-center gap-1"
          >
            Docs <ExternalLink className="h-2.5 w-2.5" />
          </a>
        )}
      </div>
    </div>
  )
}

export default function IntegrationsPage() {
  const grouped = CATEGORY_ORDER.reduce(
    (acc, cat) => {
      const items = INTEGRATIONS.filter((i) => i.category === cat)
      if (items.length > 0) acc.push({ category: cat, items })
      return acc
    },
    [] as { category: IntegrationCategory; items: Integration[] }[]
  )

  const activeCount = INTEGRATIONS.filter((i) => i.status === "active").length

  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-gradient">Integrations</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Vercel marketplace integrations connected to this team.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant="outline" className="text-xs font-mono">
            {activeCount} active
          </Badge>
          <Badge variant="secondary" className="text-xs">
            {INTEGRATIONS.length} total
          </Badge>
        </div>
      </div>

      {grouped.map(({ category, items }) => {
        const Icon = CATEGORY_ICONS[category]
        return (
          <div key={category}>
            <div className="flex items-center gap-2 mb-4">
              <Icon className="h-4 w-4 text-muted-foreground" />
              <h2 className="text-xs font-bold uppercase tracking-[0.2em] text-muted-foreground">
                {CATEGORY_LABELS[category]}
              </h2>
              <span className="text-[10px] text-muted-foreground/50 ml-1">
                ({items.length})
              </span>
            </div>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {items.map((integration) => (
                <IntegrationCard key={integration.id} integration={integration} />
              ))}
            </div>
          </div>
        )
      })}
    </div>
  )
}
