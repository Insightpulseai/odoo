"use client"

import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import Link from "next/link"
import { ArrowLeft } from "lucide-react"
import { cn } from "@/lib/utils"

interface Finding {
  id: string
  rule_id: string
  pillar: string
  severity: string
  title: string
  description?: string
  remediation?: string
  resource_ref?: string
  created_at: string
}

const SEVERITY_COLORS: Record<string, string> = {
  critical: "border-red-500/30 bg-red-500/5 text-red-400",
  high: "border-orange-500/30 bg-orange-500/5 text-orange-400",
  medium: "border-yellow-500/30 bg-yellow-500/5 text-yellow-400",
  low: "border-blue-500/30 bg-blue-500/5 text-blue-400",
  info: "border-white/10 bg-white/5 text-muted-foreground",
}

const SEVERITY_ORDER = ["critical", "high", "medium", "low", "info"]

const PILLAR_LABELS: Record<string, string> = {
  security: "Security",
  cost: "Cost",
  reliability: "Reliability",
  operational_excellence: "Operational Excellence",
  performance: "Performance",
}

export default function PillarPage() {
  const { pillar } = useParams<{ pillar: string }>()
  const [findings, setFindings] = useState<Finding[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    fetch(`/api/advisor/findings?pillar=${pillar}`)
      .then((r) => r.json())
      .then(({ findings: f }) => setFindings(f ?? []))
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [pillar])

  const sorted = [...findings].sort(
    (a, b) => SEVERITY_ORDER.indexOf(a.severity) - SEVERITY_ORDER.indexOf(b.severity)
  )

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <Link href="/advisor" className="text-muted-foreground hover:text-white transition-colors">
          <ArrowLeft className="h-4 w-4" />
        </Link>
        <h2 className="text-2xl font-bold">{PILLAR_LABELS[pillar] ?? pillar}</h2>
        <span className="text-xs text-muted-foreground">
          {loading ? "…" : `${findings.length} finding${findings.length !== 1 ? "s" : ""}`}
        </span>
      </div>

      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-24 glass rounded-xl animate-pulse" />
          ))}
        </div>
      ) : sorted.length === 0 ? (
        <div className="glass border border-white/5 rounded-xl p-12 text-center text-muted-foreground">
          <div className="text-2xl mb-2">✅</div>
          <div className="text-sm">No findings for this pillar in the latest run.</div>
          <div className="text-xs mt-1">Run a scan from the Advisor dashboard to check current state.</div>
        </div>
      ) : (
        <div className="space-y-3">
          {sorted.map((f) => (
            <div
              key={f.id}
              className={cn(
                "glass border rounded-xl p-5 space-y-2",
                SEVERITY_COLORS[f.severity] ?? "border-white/10"
              )}
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className={cn(
                      "text-[10px] font-bold uppercase px-1.5 py-0.5 rounded",
                      SEVERITY_COLORS[f.severity]
                    )}>
                      {f.severity}
                    </span>
                    <span className="text-[10px] text-muted-foreground font-mono">{f.rule_id}</span>
                  </div>
                  <h3 className="text-sm font-semibold">{f.title}</h3>
                </div>
                {f.resource_ref && (
                  <span className="text-[10px] text-muted-foreground font-mono shrink-0">{f.resource_ref}</span>
                )}
              </div>

              {f.description && (
                <p className="text-xs text-muted-foreground">{f.description}</p>
              )}

              {f.remediation && (
                <div className="mt-2 p-3 rounded-lg bg-white/5 border border-white/5">
                  <span className="text-[10px] font-semibold text-muted-foreground uppercase tracking-widest">
                    Remediation
                  </span>
                  <p className="text-xs mt-1">{f.remediation}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
