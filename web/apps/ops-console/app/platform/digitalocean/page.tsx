import { Badge } from "@/components/ui/badge"
import { Server, Database, Shield, ArrowUpRight, Clock } from "lucide-react"

export const revalidate = 60

// ── Types ─────────────────────────────────────────────────────────────────────

interface DoDroplet {
  id: number
  name: string
  region: string
  size_slug: string
  ipv4_public: string | null
  status: string
  tags: string[] | null
  synced_at: string | null
}

interface DoDatabase {
  id: string
  name: string
  engine: string
  version: string
  region: string
  status: string
  endpoint_host: string | null
  num_nodes: number | null
  synced_at: string | null
}

interface DoFirewall {
  id: string
  name: string
  status: string
  inbound_rules: unknown[] | null
  outbound_rules: unknown[] | null
  synced_at: string | null
}

// ── Data fetching ─────────────────────────────────────────────────────────────

async function fetchDroplets(): Promise<DoDroplet[]> {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY

  if (!url || !key) return []

  try {
    const res = await fetch(
      `${url}/rest/v1/do_droplets?select=*&status=eq.active&schema=ops`,
      {
        headers: {
          apikey: key,
          Authorization: `Bearer ${key}`,
          "Accept-Profile": "ops",
        },
        next: { revalidate: 60 },
      }
    )
    if (!res.ok) return []
    return res.json()
  } catch {
    return []
  }
}

async function fetchDatabases(): Promise<DoDatabase[]> {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY

  if (!url || !key) return []

  try {
    const res = await fetch(
      `${url}/rest/v1/do_databases?select=*&status=eq.online&schema=ops`,
      {
        headers: {
          apikey: key,
          Authorization: `Bearer ${key}`,
          "Accept-Profile": "ops",
        },
        next: { revalidate: 60 },
      }
    )
    if (!res.ok) return []
    return res.json()
  } catch {
    return []
  }
}

async function fetchFirewalls(): Promise<DoFirewall[]> {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY

  if (!url || !key) return []

  try {
    const res = await fetch(
      `${url}/rest/v1/do_firewalls?select=*&schema=ops`,
      {
        headers: {
          apikey: key,
          Authorization: `Bearer ${key}`,
          "Accept-Profile": "ops",
        },
        next: { revalidate: 60 },
      }
    )
    if (!res.ok) return []
    return res.json()
  } catch {
    return []
  }
}

// ── Badge helpers ─────────────────────────────────────────────────────────────

function statusBadge(status: string) {
  const s = (status ?? "unknown").toLowerCase()
  if (s === "active" || s === "online")
    return (
      <Badge
        variant="outline"
        className="text-[10px] font-bold border bg-green-500/10 text-green-400 border-green-500/20"
      >
        {status}
      </Badge>
    )
  if (s === "off" || s === "offline" || s === "error")
    return (
      <Badge
        variant="outline"
        className="text-[10px] font-bold border bg-red-500/10 text-red-400 border-red-500/20"
      >
        {status}
      </Badge>
    )
  return (
    <Badge
      variant="outline"
      className="text-[10px] font-bold border bg-zinc-500/10 text-zinc-400 border-zinc-500/20"
    >
      {status}
    </Badge>
  )
}

// ── Sub-components ────────────────────────────────────────────────────────────

function SummaryCard({
  icon: Icon,
  label,
  value,
  sub,
}: {
  icon: React.ElementType
  label: string
  value: number
  sub?: string
}) {
  return (
    <div className="glass-card rounded-xl p-5 space-y-3">
      <div className="flex items-center gap-3">
        <div className="h-10 w-10 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center">
          <Icon className="h-5 w-5 text-primary" />
        </div>
        <div>
          <p className="text-[10px] uppercase tracking-wider text-muted-foreground font-semibold">
            {label}
          </p>
          <p className="text-2xl font-bold">{value}</p>
          {sub && <p className="text-[10px] text-muted-foreground mt-0.5">{sub}</p>}
        </div>
      </div>
    </div>
  )
}

function PendingSync({ label }: { label: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center gap-3">
      <Clock className="h-8 w-8 text-muted-foreground/40" />
      <p className="text-sm font-medium text-muted-foreground">Pending first sync</p>
      <p className="text-xs text-muted-foreground/60">
        {label} will appear here after the DigitalOcean ingestion job runs.
      </p>
    </div>
  )
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default async function DigitalOceanPlatformPage() {
  const [droplets, databases, firewalls] = await Promise.all([
    fetchDroplets(),
    fetchDatabases(),
    fetchFirewalls(),
  ])

  return (
    <div className="space-y-8 animate-in zoom-in-95 duration-700">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-gradient">
            DigitalOcean
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Compute, managed databases, and firewall inventory — synced from DO API.
          </p>
        </div>
        <a
          href="https://cloud.digitalocean.com"
          target="_blank"
          rel="noopener noreferrer"
          className="hidden md:flex items-center gap-1 text-xs border border-border rounded-lg px-3 py-1.5 hover:border-primary/30 transition-colors text-muted-foreground hover:text-foreground"
        >
          DO Dashboard <ArrowUpRight className="h-3 w-3 ml-1" />
        </a>
      </div>

      {/* Summary cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <SummaryCard
          icon={Server}
          label="Active Droplets"
          value={droplets.length}
          sub="status = active"
        />
        <SummaryCard
          icon={Database}
          label="Database Clusters"
          value={databases.length}
          sub="status = online"
        />
        <SummaryCard
          icon={Shield}
          label="Firewall Policies"
          value={firewalls.length}
        />
      </div>

      {/* Droplets table */}
      <section>
        <h2 className="text-xs font-bold uppercase tracking-[0.2em] text-muted-foreground mb-4 flex items-center gap-2">
          <Server className="h-4 w-4" />
          Droplets
          <span className="text-[10px] text-muted-foreground/50">({droplets.length})</span>
        </h2>

        {droplets.length === 0 ? (
          <div className="glass-card rounded-xl">
            <PendingSync label="Droplet data" />
          </div>
        ) : (
          <div className="glass-card rounded-xl overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead className="border-b border-black/5">
                  <tr>
                    {["Name", "Region", "Size", "Public IP", "Status", "Tags"].map(
                      (h) => (
                        <th
                          key={h}
                          className="px-4 py-3 text-[10px] font-bold uppercase tracking-wider text-muted-foreground whitespace-nowrap"
                        >
                          {h}
                        </th>
                      )
                    )}
                  </tr>
                </thead>
                <tbody className="divide-y divide-black/5">
                  {droplets.map((d) => (
                    <tr
                      key={d.id}
                      className="hover:bg-white/30 transition-colors"
                    >
                      <td className="px-4 py-3 text-sm font-medium">{d.name}</td>
                      <td className="px-4 py-3 text-xs font-mono text-muted-foreground uppercase">
                        {d.region}
                      </td>
                      <td className="px-4 py-3 text-xs font-mono text-muted-foreground">
                        {d.size_slug}
                      </td>
                      <td className="px-4 py-3 text-xs font-mono">
                        {d.ipv4_public ?? (
                          <span className="text-muted-foreground/50">—</span>
                        )}
                      </td>
                      <td className="px-4 py-3">{statusBadge(d.status)}</td>
                      <td className="px-4 py-3">
                        <div className="flex flex-wrap gap-1">
                          {(d.tags ?? []).length > 0 ? (
                            (d.tags ?? []).map((t) => (
                              <Badge
                                key={t}
                                variant="secondary"
                                className="text-[9px] font-mono px-1.5 py-0"
                              >
                                {t}
                              </Badge>
                            ))
                          ) : (
                            <span className="text-[10px] text-muted-foreground/40">
                              —
                            </span>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </section>

      {/* Databases table */}
      <section>
        <h2 className="text-xs font-bold uppercase tracking-[0.2em] text-muted-foreground mb-4 flex items-center gap-2">
          <Database className="h-4 w-4" />
          Managed Databases
          <span className="text-[10px] text-muted-foreground/50">({databases.length})</span>
        </h2>

        {databases.length === 0 ? (
          <div className="glass-card rounded-xl">
            <PendingSync label="Database cluster data" />
          </div>
        ) : (
          <div className="glass-card rounded-xl overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead className="border-b border-black/5">
                  <tr>
                    {[
                      "Name",
                      "Engine",
                      "Version",
                      "Region",
                      "Status",
                      "Endpoint",
                      "Nodes",
                    ].map((h) => (
                      <th
                        key={h}
                        className="px-4 py-3 text-[10px] font-bold uppercase tracking-wider text-muted-foreground whitespace-nowrap"
                      >
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-black/5">
                  {databases.map((db) => (
                    <tr
                      key={db.id}
                      className="hover:bg-white/30 transition-colors"
                    >
                      <td className="px-4 py-3 text-sm font-medium">{db.name}</td>
                      <td className="px-4 py-3 text-xs font-mono text-muted-foreground uppercase">
                        {db.engine}
                      </td>
                      <td className="px-4 py-3 text-xs font-mono text-muted-foreground">
                        {db.version}
                      </td>
                      <td className="px-4 py-3 text-xs font-mono text-muted-foreground uppercase">
                        {db.region}
                      </td>
                      <td className="px-4 py-3">{statusBadge(db.status)}</td>
                      <td className="px-4 py-3 text-xs font-mono">
                        {db.endpoint_host ?? (
                          <span className="text-muted-foreground/50">—</span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-xs text-muted-foreground">
                        {db.num_nodes ?? "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </section>

      <p className="text-xs text-muted-foreground/60">
        Data source:{" "}
        <code className="font-mono text-[10px]">ops.do_droplets</code>
        {" · "}
        <code className="font-mono text-[10px]">ops.do_databases</code>
        {" · "}
        <code className="font-mono text-[10px]">ops.do_firewalls</code>
        {" · Revalidates every 60s"}
      </p>
    </div>
  )
}
