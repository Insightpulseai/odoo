"use client"

import { useEffect, useState } from "react"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  KeyRound,
  RefreshCw,
  AlertCircle,
  CheckCircle2,
  Clock,
  HelpCircle,
  ShieldAlert,
} from "lucide-react"

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type SecretStatus = "ok" | "missing" | "stale" | "unknown"
type SecretSeverity = "critical" | "high" | "medium" | "low"

interface SecretInventoryRow {
  id: string
  key: string
  purpose: string | null
  severity_if_missing: SecretSeverity | null
  desired_consumers: Array<{ kind: string; project?: string; name: string }> | null
  observed: Record<string, string> | null
  status: SecretStatus
  probe_status_code: number | null
  probe_error: string | null
  last_checked_at: string | null
  next_rotation_at: string | null
  notes: string | null
}

// ---------------------------------------------------------------------------
// Status badge
// ---------------------------------------------------------------------------

const STATUS_CONFIG: Record<
  SecretStatus,
  { label: string; icon: React.ElementType; variant: string; className: string }
> = {
  ok: {
    label: "ok",
    icon: CheckCircle2,
    variant: "outline",
    className:
      "border-green-500/40 bg-green-500/10 text-green-600 dark:text-green-400",
  },
  missing: {
    label: "missing",
    icon: AlertCircle,
    variant: "outline",
    className:
      "border-red-500/40 bg-red-500/10 text-red-600 dark:text-red-400",
  },
  stale: {
    label: "stale",
    icon: Clock,
    variant: "outline",
    className:
      "border-amber-500/40 bg-amber-500/10 text-amber-600 dark:text-amber-400",
  },
  unknown: {
    label: "unknown",
    icon: HelpCircle,
    variant: "outline",
    className:
      "border-gray-400/40 bg-gray-500/10 text-gray-500 dark:text-gray-400",
  },
}

function StatusBadge({ status }: { status: SecretStatus }) {
  const cfg = STATUS_CONFIG[status] ?? STATUS_CONFIG.unknown
  const Icon = cfg.icon
  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold border ${cfg.className}`}
    >
      <Icon className="h-3 w-3" />
      {cfg.label}
    </span>
  )
}

// ---------------------------------------------------------------------------
// Severity badge
// ---------------------------------------------------------------------------

const SEVERITY_CLASSES: Record<SecretSeverity, string> = {
  critical: "border-red-600/40 bg-red-600/10 text-red-600 dark:text-red-400",
  high: "border-orange-500/40 bg-orange-500/10 text-orange-600 dark:text-orange-400",
  medium: "border-yellow-500/40 bg-yellow-500/10 text-yellow-600 dark:text-yellow-500",
  low: "border-gray-400/40 bg-gray-500/10 text-gray-500",
}

function SeverityBadge({ severity }: { severity: SecretSeverity | null }) {
  if (!severity) return <span className="text-muted-foreground text-xs">—</span>
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold border ${SEVERITY_CLASSES[severity]}`}
    >
      {severity}
    </span>
  )
}

// ---------------------------------------------------------------------------
// Date formatter
// ---------------------------------------------------------------------------

function fmtDate(iso: string | null): string {
  if (!iso) return "—"
  const d = new Date(iso)
  return d.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  })
}

// ---------------------------------------------------------------------------
// Consumer pills
// ---------------------------------------------------------------------------

function ConsumerPill({ consumer }: { consumer: { kind: string; name: string; project?: string } }) {
  return (
    <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-muted text-[10px] font-mono text-muted-foreground border border-border">
      {consumer.kind === "github_secret" && "GH"}
      {consumer.kind === "vercel_env" && "VCL"}
      {consumer.kind === "supabase_vault" && "SB"}
      {consumer.kind === "keychain" && "KC"}
      {consumer.kind === "odoo_config" && "OD"}
      {!["github_secret", "vercel_env", "supabase_vault", "keychain", "odoo_config"].includes(
        consumer.kind
      ) && consumer.kind.slice(0, 2).toUpperCase()}
      :{consumer.name}
    </span>
  )
}

// ---------------------------------------------------------------------------
// Summary cards
// ---------------------------------------------------------------------------

function SummaryCard({
  label,
  count,
  colorClass,
}: {
  label: string
  count: number
  colorClass: string
}) {
  return (
    <div className={`rounded-lg border p-4 ${colorClass}`}>
      <div className="text-2xl font-bold">{count}</div>
      <div className="text-xs text-muted-foreground uppercase tracking-wider mt-0.5">
        {label}
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Main page component
// ---------------------------------------------------------------------------

export default function SecretsPage() {
  const [secrets, setSecrets] = useState<SecretInventoryRow[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null)

  async function fetchSecrets() {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch("/api/secrets-inventory")
      if (!res.ok) {
        const body = await res.json().catch(() => ({ error: res.statusText }))
        throw new Error(body.error ?? `HTTP ${res.status}`)
      }
      const data = await res.json()
      setSecrets(data.secrets ?? [])
      setLastRefresh(new Date())
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchSecrets()
  }, [])

  const counts = {
    ok: secrets.filter((s) => s.status === "ok").length,
    missing: secrets.filter((s) => s.status === "missing").length,
    stale: secrets.filter((s) => s.status === "stale").length,
    unknown: secrets.filter((s) => s.status === "unknown").length,
  }

  const criticalMissing = secrets.filter(
    (s) =>
      (s.status === "missing" || s.status === "stale") &&
      (s.severity_if_missing === "critical" || s.severity_if_missing === "high")
  ).length

  return (
    <div className="space-y-6 animate-in zoom-in-95 duration-700">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <KeyRound className="h-7 w-7 text-primary" />
            Secrets Inventory
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Observed state of registry-tracked secrets vs. desired state.
            Sourced from{" "}
            <code className="text-xs bg-muted rounded px-1">
              ssot/secrets/registry.yaml
            </code>
          </p>
          {lastRefresh && (
            <p className="text-xs text-muted-foreground mt-0.5">
              Last refreshed: {lastRefresh.toLocaleTimeString()}
            </p>
          )}
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={fetchSecrets}
          disabled={loading}
          className="h-8 gap-1.5"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </div>

      {/* Critical alert banner */}
      {criticalMissing > 0 && (
        <div className="flex items-center gap-3 rounded-lg border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-600 dark:text-red-400">
          <ShieldAlert className="h-4 w-4 shrink-0" />
          <span>
            <strong>{criticalMissing}</strong> critical/high severity secret
            {criticalMissing !== 1 ? "s" : ""} are missing or stale.
            Check convergence findings for remediation steps.
          </span>
        </div>
      )}

      {/* Summary cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <SummaryCard label="ok" count={counts.ok} colorClass="border-green-500/20" />
        <SummaryCard
          label="missing"
          count={counts.missing}
          colorClass="border-red-500/20"
        />
        <SummaryCard
          label="stale"
          count={counts.stale}
          colorClass="border-amber-500/20"
        />
        <SummaryCard
          label="unknown"
          count={counts.unknown}
          colorClass="border-muted"
        />
      </div>

      {/* Error state */}
      {error && (
        <Card className="border-red-500/30 bg-red-500/5">
          <CardContent className="pt-4 text-sm text-red-600 dark:text-red-400">
            Failed to load secrets inventory: {error}
          </CardContent>
        </Card>
      )}

      {/* Table */}
      {!error && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Registry Entries</CardTitle>
            <CardDescription className="text-xs">
              {secrets.length} secret{secrets.length !== 1 ? "s" : ""} tracked
              {loading ? " — refreshing..." : ""}
            </CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border bg-muted/30">
                    <th className="text-left px-4 py-2.5 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                      Key
                    </th>
                    <th className="text-left px-4 py-2.5 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                      Purpose
                    </th>
                    <th className="text-left px-4 py-2.5 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                      Consumers
                    </th>
                    <th className="text-left px-4 py-2.5 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                      Status
                    </th>
                    <th className="text-left px-4 py-2.5 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                      Last Checked
                    </th>
                    <th className="text-left px-4 py-2.5 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                      Next Rotation
                    </th>
                    <th className="text-left px-4 py-2.5 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                      Severity
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {loading && secrets.length === 0 ? (
                    <tr>
                      <td
                        colSpan={7}
                        className="px-4 py-8 text-center text-muted-foreground text-xs"
                      >
                        Loading...
                      </td>
                    </tr>
                  ) : secrets.length === 0 ? (
                    <tr>
                      <td
                        colSpan={7}
                        className="px-4 py-8 text-center text-muted-foreground text-xs"
                      >
                        No secrets found. Run the ops-secrets-scan Edge Function to populate.
                      </td>
                    </tr>
                  ) : (
                    secrets.map((secret) => (
                      <tr
                        key={secret.id}
                        className="border-b border-border/50 hover:bg-muted/20 transition-colors"
                      >
                        {/* Key */}
                        <td className="px-4 py-3 font-mono text-xs text-foreground font-medium whitespace-nowrap">
                          {secret.key}
                        </td>

                        {/* Purpose */}
                        <td className="px-4 py-3 text-xs text-muted-foreground max-w-[240px]">
                          <span className="line-clamp-2">{secret.purpose ?? "—"}</span>
                          {secret.probe_error && (
                            <span className="block text-[10px] text-red-500 mt-0.5">
                              {secret.probe_error.slice(0, 80)}
                            </span>
                          )}
                        </td>

                        {/* Consumers */}
                        <td className="px-4 py-3">
                          <div className="flex flex-wrap gap-1">
                            {(secret.desired_consumers ?? []).slice(0, 3).map((c, i) => (
                              <ConsumerPill key={i} consumer={c} />
                            ))}
                            {(secret.desired_consumers ?? []).length > 3 && (
                              <span className="text-[10px] text-muted-foreground">
                                +{(secret.desired_consumers ?? []).length - 3}
                              </span>
                            )}
                          </div>
                        </td>

                        {/* Status */}
                        <td className="px-4 py-3">
                          <StatusBadge status={secret.status} />
                        </td>

                        {/* Last Checked */}
                        <td className="px-4 py-3 text-xs text-muted-foreground whitespace-nowrap">
                          {fmtDate(secret.last_checked_at)}
                        </td>

                        {/* Next Rotation */}
                        <td className="px-4 py-3 text-xs text-muted-foreground whitespace-nowrap">
                          {fmtDate(secret.next_rotation_at)}
                        </td>

                        {/* Severity */}
                        <td className="px-4 py-3">
                          <SeverityBadge severity={secret.severity_if_missing} />
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Footer note */}
      <p className="text-[11px] text-muted-foreground">
        Status is updated by the{" "}
        <code className="bg-muted rounded px-0.5">ops-secrets-scan</code> Edge
        Function (scheduled every 6 hours). Trigger manually via{" "}
        <code className="bg-muted rounded px-0.5">
          POST /functions/v1/ops-secrets-scan
        </code>
        .
      </p>
    </div>
  )
}
