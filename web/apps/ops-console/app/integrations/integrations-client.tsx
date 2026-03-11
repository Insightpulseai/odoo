"use client"

import { useState } from "react"
import { Badge } from "@/components/ui/badge"
import {
  Database,
  Cpu,
  Bot,
  MessageSquare,
  Wrench,
  Zap,
  Eye,
  Activity,
  Shield,
  BarChart2,
  GitMerge,
  ExternalLink,
  CheckCircle2,
  AlertCircle,
  Clock,
  XCircle,
  Filter,
} from "lucide-react"
import {
  DB_CATEGORY_LABELS,
  DB_CATEGORY_ORDER,
  PLAN_TIER_LABELS,
  type CatalogEntry,
  type DbCategory,
  type DbStatus,
  type PlanTier,
} from "@/lib/integrations"

// ── Icon map (DB categories) ──────────────────────────────────────────────────
const CATEGORY_ICONS: Record<DbCategory, React.ComponentType<{ className?: string }>> = {
  auth_data:    Database,
  ai_inference: Cpu,
  agents:       Bot,
  devtools:     Wrench,
  messaging:    MessageSquare,
  observability:Eye,
  storage:      Database,
  security:     Shield,
  analytics:    BarChart2,
  workflow:     GitMerge,
}

const STATUS_CONFIG: Record<DbStatus, { label: string; icon: React.ComponentType<{ className?: string }>; className: string }> = {
  active:         { label: "Active",         icon: CheckCircle2, className: "bg-green-500/10  text-green-400  border-green-500/20" },
  inactive:       { label: "Inactive",       icon: AlertCircle,  className: "bg-zinc-500/10   text-zinc-400   border-zinc-500/20"  },
  error:          { label: "Error",          icon: XCircle,      className: "bg-red-500/10    text-red-400    border-red-500/20"   },
  setup_required: { label: "Setup Required", icon: Clock,        className: "bg-yellow-500/10 text-yellow-400 border-yellow-500/20"},
}

const BILLING_LABELS: Record<string, string> = {
  vercel: "Billed via Vercel",
  direct: "Direct billing",
  free:   "Free",
}

const PLAN_TIER_BADGE: Record<PlanTier, string> = {
  baseline:        "bg-blue-500/10  text-blue-400  border-blue-500/20",
  optional:        "bg-amber-500/10 text-amber-400 border-amber-500/20",
  enterprise_only: "bg-red-500/10   text-red-400   border-red-500/20",
}

// ── IntegrationCard ───────────────────────────────────────────────────────────
function IntegrationCard({ entry }: { entry: CatalogEntry }) {
  const statusCfg = STATUS_CONFIG[entry.status] ?? STATUS_CONFIG.inactive
  const StatusIcon = statusCfg.icon

  return (
    <div className="glass-card rounded-xl p-5 space-y-3">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center">
            <Zap className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h3 className="text-sm font-bold">{entry.name}</h3>
            <span className="text-[10px] text-muted-foreground uppercase tracking-wider">
              {BILLING_LABELS[entry.billing] ?? entry.billing}
            </span>
          </div>
        </div>
        <Badge variant="outline" className={`text-[10px] font-bold border ${statusCfg.className}`}>
          <StatusIcon className="h-3 w-3 mr-1" />
          {statusCfg.label}
        </Badge>
      </div>

      <p className="text-xs text-muted-foreground leading-relaxed">
        {entry.description}
      </p>

      <div className="flex items-center justify-between pt-1">
        <div className="flex flex-wrap gap-1">
          {entry.surfaces.length > 0
            ? entry.surfaces.map((s) => (
                <Badge key={s} variant="secondary" className="text-[9px] font-mono px-1.5 py-0">
                  {s.replace("/", "")}
                </Badge>
              ))
            : <span className="text-[10px] text-muted-foreground/50">No console surfaces yet</span>
          }
        </div>
        <div className="flex items-center gap-1.5">
          {entry.plan_tier !== "baseline" && (
            <Badge variant="outline" className={`text-[9px] border ${PLAN_TIER_BADGE[entry.plan_tier]}`}>
              {PLAN_TIER_LABELS[entry.plan_tier]}
            </Badge>
          )}
          {entry.docs_url && (
            <a
              href={entry.docs_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:underline text-[10px] flex items-center gap-1"
            >
              Docs <ExternalLink className="h-2.5 w-2.5" />
            </a>
          )}
        </div>
      </div>
    </div>
  )
}

// ── Main client component ─────────────────────────────────────────────────────
interface Props {
  entries: CatalogEntry[]
}

export function IntegrationsClient({ entries }: Props) {
  const [baselineOnly, setBaselineOnly] = useState(true)

  const visible = baselineOnly ? entries.filter((e) => e.baseline_allowed) : entries

  const activeCount = visible.filter((e) => e.status === "active").length
  const totalCount  = visible.length

  // Group by DB category order (skip empty categories)
  const grouped = DB_CATEGORY_ORDER.reduce<{ category: DbCategory; items: CatalogEntry[] }[]>(
    (acc, cat) => {
      const items = visible.filter((e) => e.category === cat)
      if (items.length > 0) acc.push({ category: cat, items })
      return acc
    },
    []
  )

  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      {/* ── Header ── */}
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
            {totalCount} total
          </Badge>
        </div>
      </div>

      {/* ── PlanGuard filter toggle ── */}
      <div className="flex items-center gap-2">
        <button
          onClick={() => setBaselineOnly(!baselineOnly)}
          className={`flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg border transition-colors ${
            baselineOnly
              ? "bg-primary/10 border-primary/20 text-primary"
              : "bg-white/5 border-white/10 text-muted-foreground hover:text-foreground"
          }`}
        >
          <Filter className="h-3 w-3" />
          {baselineOnly ? "Baseline-ready only" : "Showing all"}
        </button>
        {!baselineOnly && (
          <span className="text-[10px] text-muted-foreground">
            Includes optional + enterprise-only integrations
          </span>
        )}
      </div>

      {/* ── Category sections ── */}
      {grouped.map(({ category, items }) => {
        const Icon = CATEGORY_ICONS[category]
        return (
          <div key={category}>
            <div className="flex items-center gap-2 mb-4">
              <Icon className="h-4 w-4 text-muted-foreground" />
              <h2 className="text-xs font-bold uppercase tracking-[0.2em] text-muted-foreground">
                {DB_CATEGORY_LABELS[category]}
              </h2>
              <span className="text-[10px] text-muted-foreground/50 ml-1">
                ({items.length})
              </span>
            </div>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {items.map((entry) => (
                <IntegrationCard key={entry.key} entry={entry} />
              ))}
            </div>
          </div>
        )
      })}
    </div>
  )
}
