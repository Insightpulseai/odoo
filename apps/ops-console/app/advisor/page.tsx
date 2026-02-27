"use client"

import { useEffect, useState } from "react"
import { RadialBarChart, RadialBar, ResponsiveContainer } from "recharts"
import { Shield, DollarSign, Zap, Settings, Activity, RefreshCw, AlertTriangle } from "lucide-react"
import Link from "next/link"
import { cn } from "@/lib/utils"
import { IntegrationBadges } from "@/components/platform/IntegrationBadges"

// ─── Types ────────────────────────────────────────────────────────────────────

interface AdvisorScore {
  pillar: string
  score: number
  finding_counts: {
    critical: number
    high: number
    medium: number
    low: number
    info: number
  }
}

interface AdvisorRun {
  id: string
  status: string
  started_at: string
  finished_at: string | null
  summary: {
    total_findings: number
    by_severity: Record<string, number>
    by_pillar: Record<string, number>
  } | null
}

// ─── Pillar Config ────────────────────────────────────────────────────────────

const PILLARS = [
  { key: "security", label: "Security", icon: Shield, color: "#ef4444" },
  { key: "cost", label: "Cost", icon: DollarSign, color: "#f59e0b" },
  { key: "reliability", label: "Reliability", icon: Activity, color: "#3b82f6" },
  { key: "operational_excellence", label: "Ops Excellence", icon: Settings, color: "#8b5cf6" },
  { key: "performance", label: "Performance", icon: Zap, color: "#10b981" },
]

// ─── Score Ring ───────────────────────────────────────────────────────────────

function ScoreRing({ score, color, size = 80 }: { score: number; color: string; size?: number }) {
  const data = [{ name: "score", value: score, fill: color }]
  return (
    <div style={{ width: size, height: size }} className="relative">
      <ResponsiveContainer width="100%" height="100%">
        <RadialBarChart
          cx="50%" cy="50%"
          innerRadius="70%" outerRadius="100%"
          barSize={8}
          data={data}
          startAngle={90} endAngle={-270}
        >
          <RadialBar dataKey="value" cornerRadius={4} background={{ fill: "#ffffff10" }} />
        </RadialBarChart>
      </ResponsiveContainer>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-sm font-bold tabular-nums">{score}</span>
      </div>
    </div>
  )
}

// ─── Severity Badge ───────────────────────────────────────────────────────────

function SeverityBadge({ count, severity }: { count: number; severity: string }) {
  if (count === 0) return null
  const colors: Record<string, string> = {
    critical: "bg-red-500/20 text-red-400",
    high: "bg-orange-500/20 text-orange-400",
    medium: "bg-yellow-500/20 text-yellow-400",
    low: "bg-blue-500/20 text-blue-400",
  }
  return (
    <span className={cn("text-[10px] font-bold px-1.5 py-0.5 rounded", colors[severity] ?? "bg-white/10 text-white/60")}>
      {count} {severity}
    </span>
  )
}

// ─── Page ─────────────────────────────────────────────────────────────────────

export default function AdvisorPage() {
  const [latestRun, setLatestRun] = useState<AdvisorRun | null>(null)
  const [scores, setScores] = useState<AdvisorScore[]>([])
  const [scanning, setScanning] = useState(false)
  const [loading, setLoading] = useState(true)

  async function loadData() {
    setLoading(true)
    try {
      const res = await fetch("/api/advisor/runs?limit=1")
      if (!res.ok) throw new Error(await res.text())
      const { runs, scores: scoreData } = await res.json()
      setLatestRun(runs?.[0] ?? null)
      setScores(scoreData ?? [])
    } catch (err) {
      console.error("Failed to load advisor data:", err)
    } finally {
      setLoading(false)
    }
  }

  async function triggerScan() {
    setScanning(true)
    try {
      await fetch("/api/advisor/runs", { method: "POST" })
      await loadData()
    } finally {
      setScanning(false)
    }
  }

  useEffect(() => { loadData() }, [])

  const scoreMap = Object.fromEntries(scores.map((s) => [s.pillar, s]))
  const overallScore = scores.length > 0
    ? Math.round(scores.reduce((sum, s) => sum + s.score, 0) / scores.length)
    : null

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Ops Advisor</h2>
          <p className="text-sm text-muted-foreground mt-1">
            Platform health across 5 pillars · Azure Advisor–style recommendations
          </p>
          <div className="mt-2">
            <IntegrationBadges />
          </div>
        </div>
        <div className="flex items-center gap-3">
          {latestRun && (
            <span className="text-xs text-muted-foreground">
              Last scan: {new Date(latestRun.started_at).toLocaleString()}
            </span>
          )}
          <button
            onClick={triggerScan}
            disabled={scanning}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-white text-xs font-semibold hover:bg-primary/80 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={cn("h-3.5 w-3.5", scanning && "animate-spin")} />
            {scanning ? "Scanning…" : "Run Scan"}
          </button>
        </div>
      </div>

      {/* Overall score + pillar cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {/* Overall */}
        <div className="glass border border-white/5 rounded-xl p-4 flex flex-col items-center justify-center col-span-1 gap-2">
          <span className="text-xs text-muted-foreground uppercase tracking-widest">Overall</span>
          {loading ? (
            <div className="h-16 w-16 rounded-full bg-white/5 animate-pulse" />
          ) : overallScore !== null ? (
            <ScoreRing score={overallScore} color="#6366f1" size={72} />
          ) : (
            <span className="text-muted-foreground text-xs">No data</span>
          )}
        </div>

        {/* Per-pillar */}
        {PILLARS.map(({ key, label, icon: Icon, color }) => {
          const s = scoreMap[key]
          const topFindings = s
            ? Object.entries(s.finding_counts)
                .filter(([, n]) => (n as number) > 0)
                .slice(0, 2)
            : []
          return (
            <Link
              key={key}
              href={`/advisor/${key}`}
              className="glass border border-white/5 rounded-xl p-4 flex flex-col items-center gap-2 hover:border-white/20 transition-all group"
            >
              <Icon className="h-4 w-4 text-muted-foreground group-hover:text-white transition-colors" style={{ color }} />
              <span className="text-[10px] text-muted-foreground uppercase tracking-widest">{label}</span>
              {loading ? (
                <div className="h-14 w-14 rounded-full bg-white/5 animate-pulse" />
              ) : s ? (
                <>
                  <ScoreRing score={s.score} color={color} size={64} />
                  <div className="flex flex-wrap gap-1 justify-center">
                    {topFindings.map(([sev, n]) => (
                      <SeverityBadge key={sev} count={n as number} severity={sev} />
                    ))}
                  </div>
                </>
              ) : (
                <span className="text-xs text-muted-foreground">—</span>
              )}
            </Link>
          )
        })}
      </div>

      {/* Last run summary */}
      {latestRun?.summary && (
        <div className="glass border border-white/5 rounded-xl p-6">
          <h3 className="text-sm font-semibold mb-4 text-muted-foreground uppercase tracking-widest">
            Last Run Summary
          </h3>
          <div className="flex items-center gap-6 flex-wrap">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm">{latestRun.summary.total_findings} total findings</span>
            </div>
            {Object.entries(latestRun.summary.by_severity)
              .filter(([, n]) => n > 0)
              .map(([sev, n]) => (
                <SeverityBadge key={sev} count={n} severity={sev} />
              ))}
            <Link href="/advisor/findings" className="ml-auto text-xs text-primary hover:underline">
              View all findings →
            </Link>
          </div>
        </div>
      )}

      {/* Quick nav */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <Link href="/advisor/findings" className="glass border border-white/5 rounded-xl p-4 hover:border-white/20 transition-all">
          <div className="text-sm font-semibold">All Findings</div>
          <div className="text-xs text-muted-foreground mt-1">Filter by pillar, severity, status</div>
        </Link>
        <Link href="/advisor/workbooks" className="glass border border-white/5 rounded-xl p-4 hover:border-white/20 transition-all">
          <div className="text-sm font-semibold">Workbooks</div>
          <div className="text-xs text-muted-foreground mt-1">Structured release checklists</div>
        </Link>
      </div>
    </div>
  )
}
