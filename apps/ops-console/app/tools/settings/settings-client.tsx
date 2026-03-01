"use client"

import { useState, useEffect, useCallback } from "react"

// ── Types ────────────────────────────────────────────────────────────────────

interface Subdomain {
  name: string
  lifecycle: "active" | "planned" | "deprecated" | "broken"
  type: string
  target?: string
  port?: number
  backing_status?: string
}

interface GithubApp {
  id: string
  status: string
  webhook?: { url: string; active: boolean }
  events?: string[]
  ledger?: { deliveries_table: string; work_items_table: string }
}

interface Integration {
  id: string
  status: string
  display_name?: string
  kind?: string
}

interface ParityFeature {
  id: string
  category: string
  description: string
  required: boolean
  status: "met" | "partial" | "missing" | "waived"
  implementation: string
  module_or_ref?: string
}

interface SettingsSnapshot {
  sha?: string
  branch?: string
  created_at?: string
  generated_at?: string
  project?: {
    name: string
    domain: string
    prod_url: string
    db_names: Record<string, string>
    urls: { url: string; service: string }[]
  }
  dns?: {
    subdomains: Subdomain[]
    active_count: number
    planned_count: number
    broken_count: number
  }
  integrations?: {
    github_apps: GithubApp
    all: Integration[]
  }
  parity?: {
    total: number
    met: number
    partial: number
    missing: number
    waived: number
    required_missing: number
    scope: string
    features?: ParityFeature[]
  }
  capacity?: {
    odoo_workers?: number
    db_max_connections?: number
    note?: string
  }
  staging?: { subdomains: Subdomain[] }
  webhook_stats?: {
    total_24h: number
    failed_24h: number
    last_received_at: string | null
  }
}

interface Delivery {
  delivery_id: string
  event_type: string
  received_at: string
  status: string
  last_error?: string
}

// ── Tab definition ────────────────────────────────────────────────────────────

const TABS = [
  { id: "project",      label: "Project" },
  { id: "collaborators",label: "Collaborators" },
  { id: "public",       label: "Public Access" },
  { id: "ci",           label: "CI Status" },
  { id: "integrations", label: "Integrations" },
  { id: "submodules",   label: "Submodules" },
  { id: "storage",      label: "Storage" },
  { id: "workers",      label: "Workers" },
  { id: "staging",      label: "Staging" },
  { id: "parity",       label: "Parity" },
] as const

type TabId = typeof TABS[number]["id"]

// ── Status badge ─────────────────────────────────────────────────────────────

function Badge({ status }: { status: string }) {
  const map: Record<string, string> = {
    active: "bg-green-500/20 text-green-400 border-green-500/30",
    met:    "bg-green-500/20 text-green-400 border-green-500/30",
    planned:"bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
    partial:"bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
    broken: "bg-red-500/20 text-red-400 border-red-500/30",
    missing:"bg-red-500/20 text-red-400 border-red-500/30",
    not_provisioned: "bg-orange-500/20 text-orange-400 border-orange-500/30",
    waived: "bg-muted text-muted-foreground border-border",
    deprecated:"bg-muted text-muted-foreground border-border",
    processed: "bg-green-500/20 text-green-400 border-green-500/30",
    received: "bg-blue-500/20 text-blue-400 border-blue-500/30",
    failed:  "bg-red-500/20 text-red-400 border-red-500/30",
  }
  const cls = map[status] ?? "bg-muted text-muted-foreground border-border"
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold border ${cls}`}>
      {status}
    </span>
  )
}

// ── KV row ───────────────────────────────────────────────────────────────────

function KV({ label, value, mono = false }: { label: string; value: React.ReactNode; mono?: boolean }) {
  return (
    <div className="flex items-start justify-between py-1.5 border-b border-border/40 last:border-0 gap-4">
      <dt className="text-xs text-muted-foreground shrink-0 w-40">{label}</dt>
      <dd className={`text-xs text-foreground text-right truncate max-w-xs ${mono ? "font-mono" : ""}`}>{value}</dd>
    </div>
  )
}

// ── Empty state ───────────────────────────────────────────────────────────────

function Empty({ message }: { message: string }) {
  return (
    <div className="rounded-lg border border-dashed border-border p-8 text-center">
      <p className="text-xs text-muted-foreground">{message}</p>
      <p className="text-xs text-muted-foreground mt-1">
        Run <code className="font-mono bg-muted px-1 rounded">settings-snapshot.yml</code> to populate.
      </p>
    </div>
  )
}

// ── Tabs ─────────────────────────────────────────────────────────────────────

export function SettingsClient() {
  const [tab, setTab] = useState<TabId>("project")
  const [snapshot, setSnapshot] = useState<SettingsSnapshot | null>(null)
  const [deliveries, setDeliveries] = useState<Delivery[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [ssotRes, intRes] = await Promise.all([
        fetch("/api/settings/ssot"),
        fetch("/api/settings/integrations?limit=20"),
      ])
      const ssot = await ssotRes.json()
      const intData = await intRes.json()
      setSnapshot(ssot.snapshot ?? null)
      setDeliveries(intData.deliveries ?? [])
    } catch (e) {
      setError(String(e))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  const s = snapshot

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gradient">Settings</h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            Platform configuration parity with Odoo.sh — SSOT-backed, CI-enforced.
          </p>
        </div>
        {s?.created_at && (
          <div className="text-right">
            <p className="text-[10px] text-muted-foreground">Snapshot</p>
            <p className="text-xs font-mono text-muted-foreground">{s.sha?.slice(0, 7)}</p>
            <p className="text-[10px] text-muted-foreground">{new Date(s.created_at).toLocaleString()}</p>
          </div>
        )}
      </div>

      {/* Tab bar */}
      <div className="flex flex-wrap gap-1 border-b border-border pb-2">
        {TABS.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
              tab === t.id
                ? "bg-primary text-primary-foreground"
                : "text-muted-foreground hover:text-foreground hover:bg-muted"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Content */}
      {loading && (
        <div className="glass-card rounded-xl p-8 text-center">
          <p className="text-xs text-muted-foreground animate-pulse">Loading settings snapshot…</p>
        </div>
      )}

      {error && (
        <div className="glass-card rounded-xl p-4 border border-red-500/30">
          <p className="text-xs text-red-400">Error: {error}</p>
        </div>
      )}

      {!loading && !error && (
        <>
          {/* ── Project ─────────────────────────────────────────────────── */}
          {tab === "project" && (
            <div className="glass-card rounded-xl p-6 space-y-4">
              <h2 className="text-sm font-semibold uppercase tracking-wider">Project</h2>
              {!s?.project ? <Empty message="No project data in snapshot." /> : (
                <dl>
                  <KV label="Project name" value={s.project.name} mono />
                  <KV label="Domain" value={s.project.domain} mono />
                  <KV label="Production URL" value={
                    <a href={s.project.prod_url} target="_blank" rel="noreferrer" className="text-blue-400 hover:underline">{s.project.prod_url}</a>
                  } />
                  {Object.entries(s.project.db_names ?? {}).map(([env, db]) => (
                    <KV key={env} label={`DB (${env})`} value={db} mono />
                  ))}
                  {(s.project.urls ?? []).map((u) => (
                    <KV key={u.url} label={u.service} value={
                      <a href={u.url} target="_blank" rel="noreferrer" className="text-blue-400 hover:underline">{u.url}</a>
                    } />
                  ))}
                </dl>
              )}
              <p className="text-[10px] text-muted-foreground">
                Source: <code className="font-mono">ssot/runtime/prod_settings.yaml</code> · <code className="font-mono">infra/dns/subdomain-registry.yaml</code>
              </p>
            </div>
          )}

          {/* ── Collaborators ────────────────────────────────────────────── */}
          {tab === "collaborators" && (
            <div className="glass-card rounded-xl p-6 space-y-4">
              <h2 className="text-sm font-semibold uppercase tracking-wider">Collaborators & RBAC</h2>
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-border text-muted-foreground">
                      <th className="text-left py-2 pr-4 font-medium">Stage / Feature</th>
                      <th className="text-center py-2 px-2 font-medium">Developer</th>
                      <th className="text-center py-2 px-2 font-medium">Tester</th>
                      <th className="text-center py-2 px-2 font-medium">Admin</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border/40">
                    {[
                      ["Dev — Connect + Shell",    true,  true,  true ],
                      ["Dev — Logs + Monitor",     true,  true,  true ],
                      ["Dev — Branch settings",    true,  true,  true ],
                      ["Staging — Connect",        false, true,  true ],
                      ["Staging — Shell + Logs",   false, true,  true ],
                      ["Staging — Mails",          false, true,  true ],
                      ["Production — Connect",     false, false, true ],
                      ["Production — Shell",       false, false, true ],
                      ["Production — Logs",        false, false, true ],
                      ["Production — Backups",     false, false, true ],
                      ["Project settings",         false, false, true ],
                      ["Audit logs",               false, false, true ],
                    ].map(([feature, dev, tester, admin]) => (
                      <tr key={String(feature)} className="text-center">
                        <td className="text-left py-1.5 pr-4 text-muted-foreground">{String(feature)}</td>
                        <td className="py-1.5 px-2">{dev ? "✅" : "—"}</td>
                        <td className="py-1.5 px-2">{tester ? "✅" : "—"}</td>
                        <td className="py-1.5 px-2">{admin ? "✅" : "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="text-[10px] text-muted-foreground space-y-0.5">
                <p>GitHub CODEOWNERS: Admins required for <code className="font-mono">ssot/**</code> <code className="font-mono">infra/**</code> <code className="font-mono">supabase/migrations/**</code></p>
                <p>Supabase RLS: <code className="font-mono">ops_admin</code> role mutates <code className="font-mono">ops.*</code> control tables; authenticated = read-only.</p>
              </div>
            </div>
          )}

          {/* ── Public Access ─────────────────────────────────────────────── */}
          {tab === "public" && (
            <div className="glass-card rounded-xl p-6 space-y-4">
              <h2 className="text-sm font-semibold uppercase tracking-wider">Public Access</h2>
              <p className="text-xs text-muted-foreground">
                Routes accessible without authentication. All other routes require a valid Supabase session.
              </p>
              <div className="space-y-2">
                {[
                  { route: "/", description: "Dashboard redirect (redirects to /login if unauthed)" },
                  { route: "/login", description: "Auth entry point — always public" },
                  { route: "/api/health", description: "Health check — no secrets returned" },
                ].map((r) => (
                  <div key={r.route} className="flex items-center justify-between py-2 border-b border-border/40 last:border-0">
                    <code className="text-xs font-mono text-blue-400">{r.route}</code>
                    <span className="text-xs text-muted-foreground ml-4">{r.description}</span>
                  </div>
                ))}
              </div>
              <p className="text-[10px] text-muted-foreground">
                Enforcement: Next.js middleware <code className="font-mono">apps/ops-console/middleware.ts</code> allowlist.
                Production + staging builds are always private (no public data).
              </p>
            </div>
          )}

          {/* ── CI Status Checks ──────────────────────────────────────────── */}
          {tab === "ci" && (
            <div className="glass-card rounded-xl p-6 space-y-4">
              <h2 className="text-sm font-semibold uppercase tracking-wider">CI Status Checks</h2>
              <p className="text-xs text-muted-foreground">
                Required checks for branch protection on <code className="font-mono">main</code>.
                These must pass before merge — equivalent to Odoo.sh commit status updates.
              </p>
              <div className="space-y-2">
                {[
                  { name: "ci / lint-typecheck",           required: true  },
                  { name: "ci / spec-validate",             required: true  },
                  { name: "ci / odoo-parity-gate",          required: true  },
                  { name: "ci / dns-ssot-check",            required: true  },
                  { name: "ci / github-apps-ssot-guard",    required: true  },
                  { name: "ci / agent-instructions-drift",  required: true  },
                  { name: "ci / settings-snapshot",         required: false },
                ].map((c) => (
                  <div key={c.name} className="flex items-center justify-between py-2 border-b border-border/40 last:border-0">
                    <code className="text-xs font-mono">{c.name}</code>
                    <Badge status={c.required ? "active" : "planned"} />
                  </div>
                ))}
              </div>
              <p className="text-[10px] text-muted-foreground">
                Source: <code className="font-mono">ssot/ci_cd_policy_matrix.yaml</code> · Branch protection enforced via GitHub REST API.
              </p>
            </div>
          )}

          {/* ── Integrations ──────────────────────────────────────────────── */}
          {tab === "integrations" && (
            <div className="space-y-4">
              {/* GitHub App card */}
              <div className="glass-card rounded-xl p-6 space-y-3">
                <div className="flex items-center justify-between">
                  <h2 className="text-sm font-semibold uppercase tracking-wider">GitHub App</h2>
                  <Badge status={s?.integrations?.github_apps?.status ?? "unknown"} />
                </div>
                {s?.integrations?.github_apps ? (
                  <dl>
                    <KV label="App ID" value={s.integrations.github_apps.id} mono />
                    <KV label="Webhook URL" value={s.integrations.github_apps.webhook?.url ?? "—"} mono />
                    <KV label="Webhook active" value={s.integrations.github_apps.webhook?.active ? "yes" : "no"} />
                    <KV label="Events" value={(s.integrations.github_apps.events ?? []).join(", ")} />
                    <KV label="Deliveries table" value={s.integrations.github_apps.ledger?.deliveries_table ?? "—"} mono />
                  </dl>
                ) : (
                  <p className="text-xs text-muted-foreground">
                    Not yet provisioned. Run <code className="font-mono">scripts/github/create-app-from-manifest.sh ipai-integrations</code>.
                  </p>
                )}
              </div>

              {/* Webhook delivery ledger */}
              <div className="glass-card rounded-xl p-6 space-y-3">
                <h2 className="text-sm font-semibold uppercase tracking-wider">
                  Recent Webhook Deliveries
                  <span className="ml-2 text-[10px] text-muted-foreground font-normal">ops.github_webhook_deliveries</span>
                </h2>
                {deliveries.length === 0 ? (
                  <p className="text-xs text-muted-foreground">No deliveries recorded yet. Webhook not yet receiving events.</p>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-xs">
                      <thead>
                        <tr className="border-b border-border text-muted-foreground">
                          <th className="text-left py-1.5 pr-3 font-medium">Delivery ID</th>
                          <th className="text-left py-1.5 pr-3 font-medium">Event</th>
                          <th className="text-left py-1.5 pr-3 font-medium">Received</th>
                          <th className="text-left py-1.5 font-medium">Status</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-border/40">
                        {deliveries.map((d) => (
                          <tr key={d.delivery_id}>
                            <td className="py-1.5 pr-3 font-mono truncate max-w-[120px]">{d.delivery_id.slice(0, 8)}…</td>
                            <td className="py-1.5 pr-3">{d.event_type}</td>
                            <td className="py-1.5 pr-3 text-muted-foreground">{new Date(d.received_at).toLocaleString()}</td>
                            <td className="py-1.5"><Badge status={d.status} /></td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>

              {/* All integrations index */}
              {(s?.integrations?.all ?? []).length > 0 && (
                <div className="glass-card rounded-xl p-6 space-y-3">
                  <h2 className="text-sm font-semibold uppercase tracking-wider">All Integrations</h2>
                  <div className="space-y-1.5">
                    {(s!.integrations!.all).map((i) => (
                      <div key={i.id} className="flex items-center justify-between py-1.5 border-b border-border/40 last:border-0">
                        <div>
                          <span className="text-xs font-medium">{i.display_name ?? i.id}</span>
                          {i.kind && <span className="text-[10px] text-muted-foreground ml-2">{i.kind}</span>}
                        </div>
                        <Badge status={i.status} />
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* ── Submodules ────────────────────────────────────────────────── */}
          {tab === "submodules" && (
            <div className="glass-card rounded-xl p-6 space-y-4">
              <h2 className="text-sm font-semibold uppercase tracking-wider">Submodules (OCA)</h2>
              <p className="text-xs text-muted-foreground">
                OCA modules are pinned as Git submodules under <code className="font-mono">addons/oca/</code>.
                Never modify OCA source directly — create an <code className="font-mono">ipai_*</code> override module instead.
              </p>
              <dl>
                <KV label="Canonical path" value="addons/oca/" mono />
                <KV label="Docker mount" value="/workspaces/odoo/addons/oca/*" mono />
                <KV label="Update command" value="git submodule update --remote" mono />
                <KV label="Pin policy" value="Each submodule commit must be explicit in .gitmodules" />
              </dl>
              <div className="rounded-lg bg-muted/30 p-3 text-xs font-mono text-muted-foreground">
                <p className="text-[10px] text-muted-foreground mb-1">Add a public OCA submodule:</p>
                <p>git submodule add -b 19.0 git@github.com:OCA/REPO.git addons/oca/REPO</p>
                <p>git commit -a &amp;&amp; git push -u origin feat/my-branch</p>
              </div>
              <p className="text-[10px] text-muted-foreground">
                Source: <code className="font-mono">.gitmodules</code> · Rules: <code className="font-mono">.claude/rules/ssot-platform.md §Rule 10</code>
              </p>
            </div>
          )}

          {/* ── Storage ───────────────────────────────────────────────────── */}
          {tab === "storage" && (
            <div className="glass-card rounded-xl p-6 space-y-4">
              <h2 className="text-sm font-semibold uppercase tracking-wider">Storage & Telemetry</h2>
              {!s?.capacity ? (
                <Empty message="No storage snapshot available yet." />
              ) : (
                <dl>
                  <KV label="Odoo workers" value={String(s.capacity.odoo_workers ?? "—")} />
                  <KV label="DB max connections" value={String(s.capacity.db_max_connections ?? "—")} />
                  {s.capacity.note && <KV label="Note" value={s.capacity.note} />}
                </dl>
              )}
              <div className="rounded-lg bg-muted/30 p-3 text-xs font-mono text-muted-foreground">
                <p className="text-[10px] text-muted-foreground mb-1">Analyze disk usage (run in Odoo shell):</p>
                <p>ncdu /</p>
              </div>
              {s?.webhook_stats && (
                <dl>
                  <KV label="Webhook deliveries (24h)" value={String(s.webhook_stats.total_24h)} />
                  <KV label="Failed (24h)" value={String(s.webhook_stats.failed_24h)} />
                  <KV label="Last received" value={s.webhook_stats.last_received_at ?? "never"} />
                </dl>
              )}
              <p className="text-[10px] text-muted-foreground">
                Source: <code className="font-mono">ssot/runtime/prod_settings.yaml</code> · Storage plan adjustment is automatic when thresholds are crossed.
              </p>
            </div>
          )}

          {/* ── Workers ───────────────────────────────────────────────────── */}
          {tab === "workers" && (
            <div className="glass-card rounded-xl p-6 space-y-4">
              <h2 className="text-sm font-semibold uppercase tracking-wider">Workers & Capacity</h2>
              <p className="text-xs text-muted-foreground">
                More workers = more concurrent connections, not faster per-request performance.
                If operations are slow, the issue is likely code-level (N+1 queries, missing indexes).
              </p>
              {!s?.capacity ? (
                <Empty message="No capacity data in snapshot." />
              ) : (
                <dl>
                  <KV label="Odoo worker processes" value={String(s.capacity.odoo_workers ?? "—")} />
                  <KV label="PG max_connections" value={String(s.capacity.db_max_connections ?? "—")} />
                </dl>
              )}
              <dl>
                <KV label="Config file" value="config/prod/odoo.conf" mono />
                <KV label="SSOT" value="ssot/runtime/prod_settings.yaml" mono />
                <KV label="Drift check" value="scripts/ci/check_prod_settings_ssot.py" mono />
              </dl>
              <p className="text-[10px] text-muted-foreground">
                Worker changes require a container restart. Use <code className="font-mono">deploy/odoo-prod.compose.yml</code>.
              </p>
            </div>
          )}

          {/* ── Staging ───────────────────────────────────────────────────── */}
          {tab === "staging" && (
            <div className="glass-card rounded-xl p-6 space-y-4">
              <h2 className="text-sm font-semibold uppercase tracking-wider">Staging & Preview Environments</h2>
              <p className="text-xs text-muted-foreground">
                Each branch pattern maps to a preview environment. Vercel handles web previews automatically per PR.
                Odoo staging runs against <code className="font-mono">odoo_stage</code> DB.
              </p>
              {!s?.dns ? (
                <Empty message="No DNS data in snapshot." />
              ) : (
                <div className="space-y-2">
                  {s.dns.subdomains
                    .filter((sub) => sub.lifecycle !== "deprecated")
                    .map((sub) => (
                      <div key={sub.name} className="flex items-center justify-between py-2 border-b border-border/40 last:border-0">
                        <div>
                          <code className="text-xs font-mono text-foreground">{sub.name}.insightpulseai.com</code>
                          {sub.port && <span className="text-[10px] text-muted-foreground ml-2">:{sub.port}</span>}
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-[10px] text-muted-foreground">{sub.type}</span>
                          <Badge status={sub.backing_status ?? sub.lifecycle} />
                        </div>
                      </div>
                    ))}
                </div>
              )}
              <p className="text-[10px] text-muted-foreground">
                Source: <code className="font-mono">infra/dns/subdomain-registry.yaml</code> (SSOT — edit this, not generated files).
              </p>
            </div>
          )}

          {/* ── Parity ────────────────────────────────────────────────────── */}
          {tab === "parity" && (
            <div className="space-y-4">
              {/* Summary card */}
              <div className="glass-card rounded-xl p-6">
                <h2 className="text-sm font-semibold uppercase tracking-wider mb-3">EE Parity Gate</h2>
                {!s?.parity ? (
                  <Empty message="No parity data in snapshot." />
                ) : (
                  <>
                    <p className="text-xs text-muted-foreground mb-3">{s.parity.scope}</p>
                    <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
                      {[
                        { label: "Total",   value: s.parity.total,            cls: "text-foreground" },
                        { label: "Met",     value: s.parity.met,              cls: "text-green-400" },
                        { label: "Partial", value: s.parity.partial,          cls: "text-yellow-400" },
                        { label: "Missing", value: s.parity.missing,          cls: "text-red-400" },
                        { label: "Waived",  value: s.parity.waived,           cls: "text-muted-foreground" },
                      ].map((stat) => (
                        <div key={stat.label} className="rounded-lg bg-muted/30 p-3 text-center">
                          <p className={`text-2xl font-bold ${stat.cls}`}>{stat.value}</p>
                          <p className="text-[10px] text-muted-foreground mt-0.5">{stat.label}</p>
                        </div>
                      ))}
                    </div>
                    {s.parity.required_missing > 0 && (
                      <div className="mt-3 rounded-lg border border-red-500/30 bg-red-500/10 p-3">
                        <p className="text-xs text-red-400 font-medium">
                          ⚠ {s.parity.required_missing} required feature(s) missing — blocks go-live gate
                        </p>
                      </div>
                    )}
                  </>
                )}
              </div>

              {/* Feature list */}
              {(s?.parity?.features ?? []).length > 0 && (
                <div className="glass-card rounded-xl p-6 space-y-3">
                  <h2 className="text-sm font-semibold uppercase tracking-wider">Feature Detail</h2>
                  <div className="overflow-x-auto">
                    <table className="w-full text-xs">
                      <thead>
                        <tr className="border-b border-border text-muted-foreground">
                          <th className="text-left py-1.5 pr-3 font-medium">ID</th>
                          <th className="text-left py-1.5 pr-3 font-medium">Category</th>
                          <th className="text-left py-1.5 pr-3 font-medium">Description</th>
                          <th className="text-left py-1.5 pr-3 font-medium">Impl.</th>
                          <th className="text-center py-1.5 font-medium">Status</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-border/40">
                        {(s!.parity!.features!).map((f) => (
                          <tr key={f.id}>
                            <td className="py-1.5 pr-3 font-mono text-[10px] text-muted-foreground">{f.id}</td>
                            <td className="py-1.5 pr-3">{f.category}</td>
                            <td className="py-1.5 pr-3 text-muted-foreground">{f.description}</td>
                            <td className="py-1.5 pr-3 font-mono text-[10px]">{f.implementation}</td>
                            <td className="py-1.5 text-center"><Badge status={f.status} /></td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              <p className="text-[10px] text-muted-foreground">
                Source: <code className="font-mono">ssot/parity/odoo_enterprise.yaml</code> ·
                Gate: <code className="font-mono">scripts/ci/check_odoo_enterprise_parity.py</code>
              </p>
            </div>
          )}
        </>
      )}
    </div>
  )
}
