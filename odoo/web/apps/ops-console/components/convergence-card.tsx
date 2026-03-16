"use client"

/**
 * ConvergenceCard — client component
 *
 * Surfaces deployment convergence state on the Overview page.
 * Fetches from /api/convergence which reads ops.convergence_findings.
 * Gracefully degrades when Supabase is not configured.
 */

import { useEffect, useState } from "react"
import Link from "next/link"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { GitMerge, AlertTriangle, CheckCircle2, HelpCircle, Clock, ExternalLink } from "lucide-react"
import { cn } from "@/lib/utils"

type ConvergenceFinding = {
  id: string
  env: string
  kind: string
  key: string
  status: string
  suggested_action?: string
  last_seen: string
}

type ConvergenceState = "Converged" | "Blocked" | "Unknown"
type FetchState = "loading" | "ok" | "error" | "unconfigured"

function deriveState(findings: ConvergenceFinding[] | null, fetchState: FetchState): ConvergenceState {
  if (fetchState === "loading" || fetchState === "error" || fetchState === "unconfigured") return "Unknown"
  if (findings === null || findings.length === 0) return "Converged"
  return "Blocked"
}

function StateIcon({ state }: { state: ConvergenceState }) {
  if (state === "Converged") return <CheckCircle2 className="h-4 w-4 text-green-500" />
  if (state === "Blocked") return <AlertTriangle className="h-4 w-4 text-red-500" />
  return <HelpCircle className="h-4 w-4 text-yellow-500" />
}

function StateBadge({ state }: { state: ConvergenceState }) {
  const styles: Record<ConvergenceState, string> = {
    Converged: "bg-green-500/10 text-green-500 border-green-500/20",
    Blocked:   "bg-red-500/10 text-red-500 border-red-500/20",
    Unknown:   "bg-yellow-500/10 text-yellow-500 border-yellow-500/20",
  }
  return (
    <span className={cn(
      "text-[10px] font-bold uppercase tracking-widest px-2 py-1 rounded-full border",
      styles[state]
    )}>
      {state}
    </span>
  )
}

function kindLabel(kind: string): string {
  return kind.replace(/_/g, " ")
}

function relativeTime(iso: string): string {
  try {
    const diff = Date.now() - new Date(iso).getTime()
    const mins = Math.floor(diff / 60_000)
    if (mins < 1) return "just now"
    if (mins < 60) return `${mins}m ago`
    const hrs = Math.floor(mins / 60)
    if (hrs < 24) return `${hrs}h ago`
    return `${Math.floor(hrs / 24)}d ago`
  } catch {
    return "unknown"
  }
}

export function ConvergenceCard() {
  const [findings, setFindings] = useState<ConvergenceFinding[] | null>(null)
  const [fetchState, setFetchState] = useState<FetchState>("loading")

  useEffect(() => {
    let cancelled = false

    async function load() {
      try {
        const res = await fetch("/api/convergence?limit=5")
        if (!res.ok) {
          if (res.status === 503) {
            if (!cancelled) setFetchState("unconfigured")
          } else {
            if (!cancelled) setFetchState("error")
          }
          return
        }
        const data = await res.json()
        if (!cancelled) {
          setFindings(data.findings ?? [])
          setFetchState("ok")
        }
      } catch {
        if (!cancelled) setFetchState("error")
      }
    }

    load()
    return () => { cancelled = true }
  }, [])

  const state = deriveState(findings, fetchState)
  const topBlockers = (findings ?? []).slice(0, 3)

  return (
    <Card className="overflow-hidden border-none shadow-xl glass-card relative">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
        <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
          Convergence State
        </CardTitle>
        <div className="p-2 rounded-full bg-primary/10">
          <GitMerge className="h-4 w-4 text-primary" />
        </div>
      </CardHeader>

      <CardContent className="space-y-3">
        {/* Status row */}
        <div className="flex items-center space-x-2">
          {fetchState === "loading" ? (
            <span className="text-[10px] text-muted-foreground animate-pulse font-medium uppercase tracking-wider">
              Loading…
            </span>
          ) : (
            <>
              <StateIcon state={state} />
              <StateBadge state={state} />
              {fetchState === "unconfigured" && (
                <span className="text-[10px] text-muted-foreground font-medium">Coming online</span>
              )}
            </>
          )}
        </div>

        {/* Blocker list */}
        {topBlockers.length > 0 && (
          <ul className="space-y-2">
            {topBlockers.map((f) => (
              <li key={f.id} className="flex items-start space-x-2 text-xs">
                <span className={cn(
                  "mt-0.5 h-1.5 w-1.5 rounded-full shrink-0",
                  f.env === "prod" ? "bg-purple-500" : "bg-blue-500"
                )} />
                <div className="flex-1 min-w-0">
                  <span className="font-semibold uppercase text-[10px] tracking-wider text-muted-foreground">
                    {f.env}
                  </span>
                  {" · "}
                  <span className="font-medium capitalize">{kindLabel(f.kind)}</span>
                  <div className="flex items-center text-muted-foreground mt-0.5">
                    <Clock className="h-2.5 w-2.5 mr-1" />
                    {relativeTime(f.last_seen)}
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}

        {fetchState === "ok" && state === "Converged" && (
          <p className="text-xs text-muted-foreground font-medium">
            All environments in sync.
          </p>
        )}

        {fetchState === "error" && (
          <p className="text-xs text-muted-foreground font-medium">
            Could not reach convergence data.
          </p>
        )}

        {/* Footer links */}
        <div className="flex items-center space-x-3 pt-1 border-t border-border">
          <Link
            href="/users/platform-engineers"
            className="flex items-center space-x-1 text-[10px] font-bold uppercase tracking-wider text-primary hover:underline"
          >
            <span>Full View</span>
            <ExternalLink className="h-2.5 w-2.5" />
          </Link>
          <span className="text-muted-foreground/30 text-xs">·</span>
          <Link
            href="/use-cases/ai-apps"
            className="flex items-center space-x-1 text-[10px] font-bold uppercase tracking-wider text-primary hover:underline"
          >
            <span>AI Apps</span>
            <ExternalLink className="h-2.5 w-2.5" />
          </Link>
        </div>
      </CardContent>

      <div className="absolute -bottom-6 -right-6 h-24 w-24 rounded-full bg-primary/5 blur-2xl" />
    </Card>
  )
}
