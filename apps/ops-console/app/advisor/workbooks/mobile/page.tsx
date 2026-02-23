"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { ArrowLeft, Smartphone, CheckCircle2, XCircle, Loader2, AlertTriangle } from "lucide-react"
import { cn } from "@/lib/utils"

interface WorkbookRule {
  id: string
  title: string
  description: string
  remediation: string
  severity: string
  pillar: string
  tags: string[]
}

interface WorkbookResult {
  rule: WorkbookRule
  passed: boolean | null
  skipped: boolean
  reason?: string
}

interface WorkbookResponse {
  workbook_id: string
  run_id: string | null
  results: WorkbookResult[]
  pass_count: number
  fail_count: number
  skip_count: number
  ready: boolean
}

const SEVERITY_COLORS: Record<string, string> = {
  critical: "text-red-400",
  high: "text-orange-400",
  medium: "text-yellow-400",
  low: "text-blue-400",
  info: "text-muted-foreground",
}

function StatusIcon({ passed, skipped }: { passed: boolean | null; skipped: boolean }) {
  if (skipped) return <AlertTriangle className="h-4 w-4 text-yellow-500 shrink-0" />
  if (passed === null) return <Loader2 className="h-4 w-4 text-muted-foreground animate-spin shrink-0" />
  if (passed) return <CheckCircle2 className="h-4 w-4 text-green-400 shrink-0" />
  return <XCircle className="h-4 w-4 text-red-400 shrink-0" />
}

export default function MobileWorkbookPage() {
  const [data, setData] = useState<WorkbookResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch("/api/advisor/workbooks/mobile")
      .then((r) => r.json())
      .then((d) => setData(d))
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false))
  }, [])

  const readinessPercent = data
    ? Math.round(((data.pass_count) / Math.max(data.pass_count + data.fail_count, 1)) * 100)
    : 0

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Link href="/advisor/workbooks" className="text-muted-foreground hover:text-white transition-colors">
          <ArrowLeft className="h-4 w-4" />
        </Link>
        <Smartphone className="h-5 w-5 text-muted-foreground" />
        <h2 className="text-2xl font-bold">Mobile Release Readiness</h2>
        {!loading && data && (
          <span
            className={cn(
              "text-xs px-2 py-0.5 rounded font-bold uppercase",
              data.ready
                ? "bg-green-500/20 text-green-400"
                : "bg-red-500/20 text-red-400"
            )}
          >
            {data.ready ? "Ready" : "Not Ready"}
          </span>
        )}
      </div>

      <p className="text-sm text-muted-foreground">
        Evaluates 10 rules across CI, code signing, security, privacy, and QA before App Store submission.
      </p>

      {/* Summary bar */}
      {!loading && data && (
        <div className="glass border border-white/5 rounded-xl p-5">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-semibold">Release Readiness</span>
            <span className="text-2xl font-bold">{readinessPercent}%</span>
          </div>
          <div className="h-2 bg-white/10 rounded-full overflow-hidden">
            <div
              className={cn(
                "h-full rounded-full transition-all",
                readinessPercent >= 90 ? "bg-green-400" :
                readinessPercent >= 70 ? "bg-yellow-400" : "bg-red-400"
              )}
              style={{ width: `${readinessPercent}%` }}
            />
          </div>
          <div className="flex gap-4 mt-3 text-xs text-muted-foreground">
            <span className="text-green-400">✓ {data.pass_count} passed</span>
            <span className="text-red-400">✗ {data.fail_count} failed</span>
            {data.skip_count > 0 && (
              <span className="text-yellow-500">⚠ {data.skip_count} skipped</span>
            )}
          </div>
        </div>
      )}

      {/* Rules list */}
      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-20 glass rounded-xl animate-pulse" />
          ))}
        </div>
      ) : error ? (
        <div className="glass border border-red-500/20 rounded-xl p-8 text-center text-red-400 text-sm">
          Failed to load workbook: {error}
        </div>
      ) : data && (
        <div className="space-y-3">
          {data.results.map(({ rule, passed, skipped, reason }) => (
            <div
              key={rule.id}
              className={cn(
                "glass border rounded-xl p-4",
                passed === true ? "border-green-500/20" :
                skipped ? "border-yellow-500/20" :
                "border-red-500/20"
              )}
            >
              <div className="flex items-start gap-3">
                <StatusIcon passed={passed} skipped={skipped} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-semibold">{rule.title}</span>
                    <span className={cn("text-[10px] font-bold uppercase", SEVERITY_COLORS[rule.severity])}>
                      {rule.severity}
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground">{rule.description}</p>

                  {skipped && reason && (
                    <p className="text-[10px] text-yellow-500 mt-1">Skipped: {reason}</p>
                  )}

                  {passed === false && !skipped && (
                    <div className="mt-2 p-2 rounded-lg bg-white/5 border border-white/5">
                      <span className="text-[10px] font-semibold text-muted-foreground uppercase tracking-widest">
                        Remediation
                      </span>
                      <p className="text-xs mt-1">{rule.remediation}</p>
                    </div>
                  )}
                </div>
                <div className="flex gap-1 shrink-0">
                  {rule.tags.slice(0, 2).map((t) => (
                    <span key={t} className="text-[10px] bg-white/5 text-muted-foreground px-1.5 py-0.5 rounded font-mono">
                      {t}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Export scaffold */}
      {!loading && data && (
        <div className="flex gap-3">
          <button
            className="text-xs text-muted-foreground hover:text-white transition-colors border border-white/10 rounded-lg px-3 py-1.5"
            onClick={() => {
              const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" })
              const url = URL.createObjectURL(blob)
              const a = document.createElement("a")
              a.href = url
              a.download = `mobile-release-readiness-${new Date().toISOString().slice(0, 10)}.json`
              a.click()
              URL.revokeObjectURL(url)
            }}
          >
            Export JSON
          </button>
        </div>
      )}
    </div>
  )
}
