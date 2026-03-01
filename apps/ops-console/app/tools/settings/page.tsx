// app/tools/settings/page.tsx
// Odoo.sh Settings parity — centralizes Deploy, Domains, Secrets, Supabase health.
// Server component: all data fetched server-side, secrets never reach client.
import { createClient } from "@supabase/supabase-js"

type TabId = "deploy" | "domains" | "secrets" | "supabase"

interface Deployment {
  id: string
  url: string
  state: string
  createdAt: number
  sha?: string
  message?: string
  errorMessage?: string | null
}

interface MissingSecret {
  name: string
  severity: string
  last_checked?: string
}

interface RunEntry {
  function_name: string
  status: string
  started_at: string
}

interface DomainEntry {
  subdomain: string
  type: string
  target: string
  purpose: string
  status?: string
}

// ── Data fetchers ─────────────────────────────────────────────────────────────

async function fetchDeployments(): Promise<{ deployments: Deployment[]; error?: string }> {
  const token = process.env.VERCEL_API_TOKEN ?? ""
  if (!token || token === "YOUR_VERCEL_TOKEN_HERE") {
    return { deployments: [], error: "VERCEL_API_TOKEN not configured — set in Vercel env vars" }
  }
  try {
    const res = await fetch(
      "https://api.vercel.com/v6/deployments?projectId=odooops-console&limit=8",
      {
        headers: { Authorization: `Bearer ${token}` },
        next: { revalidate: 60 },
      }
    )
    if (!res.ok) return { deployments: [], error: `Vercel API ${res.status}` }
    const data = await res.json()
    return {
      deployments: (data.deployments ?? []).map((d: Record<string, unknown>) => ({
        id:           d.uid as string,
        url:          d.url as string,
        state:        d.state as string,
        createdAt:    d.createdAt as number,
        sha:          (d.meta as Record<string, string>)?.githubCommitSha,
        message:      (d.meta as Record<string, string>)?.githubCommitMessage,
        errorMessage: (d.errorMessage as string | null) ?? null,
      })),
    }
  } catch (e) {
    return { deployments: [], error: String(e) }
  }
}

async function fetchSupabaseHealth(): Promise<{
  missingSecrets: MissingSecret[]
  recentRuns: RunEntry[]
  error?: string
}> {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL ?? ""
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY ?? ""
  if (!url || !key) return { missingSecrets: [], recentRuns: [], error: "Supabase not configured" }

  const client = createClient(url, key, { auth: { persistSession: false } })
  const [secretsResult, runsResult] = await Promise.all([
    client.schema("ops").from("secret_inventory").select("name,severity,last_checked")
      .eq("status", "missing").order("severity").limit(20),
    client.schema("ops").from("runs").select("function_name,status,started_at")
      .order("started_at", { ascending: false }).limit(20),
  ])

  return {
    missingSecrets: (secretsResult.data ?? []) as MissingSecret[],
    recentRuns:     (runsResult.data ?? []) as RunEntry[],
  }
}

// ── Static domain data (from SSOT — no DB call needed) ───────────────────────

const CANONICAL_DOMAINS: DomainEntry[] = [
  { subdomain: "ops",      type: "CNAME", target: "cname.vercel-dns.com", purpose: "Ops Console",           status: "planned" },
  { subdomain: "erp",      type: "A",     target: "178.128.112.214",       purpose: "Odoo ERP",              status: "active" },
  { subdomain: "n8n",      type: "A",     target: "178.128.112.214",       purpose: "n8n automation",        status: "active" },
  { subdomain: "ocr",      type: "A",     target: "178.128.112.214",       purpose: "OCR service",           status: "active" },
  { subdomain: "auth",     type: "A",     target: "178.128.112.214",       purpose: "Authentication",        status: "active" },
  { subdomain: "chat",     type: "A",     target: "178.128.112.214",       purpose: "Mattermost (legacy)",   status: "deprecated" },
  { subdomain: "mcp",      type: "CNAME", target: "pulse-hub-web-an645.ondigitalocean.app", purpose: "MCP server", status: "drift" },
  { subdomain: "superset", type: "CNAME", target: "superset-nlavf.ondigitalocean.app",      purpose: "Superset BI",status: "active" },
]

// ── Helpers ───────────────────────────────────────────────────────────────────

function stateColor(state: string) {
  const map: Record<string, string> = {
    READY:    "bg-green-100 text-green-800",
    ERROR:    "bg-red-100 text-red-800",
    BUILDING: "bg-yellow-100 text-yellow-800",
    CANCELED: "bg-gray-100 text-gray-600",
  }
  return map[state] ?? "bg-gray-100 text-gray-600"
}

function domainStatusColor(status: string) {
  const map: Record<string, string> = {
    active:     "bg-green-100 text-green-800",
    planned:    "bg-blue-100 text-blue-800",
    drift:      "bg-yellow-100 text-yellow-800",
    deprecated: "bg-gray-100 text-gray-600",
  }
  return map[status ?? ""] ?? "bg-gray-100 text-gray-600"
}

function sevColor(sev: string) {
  const map: Record<string, string> = {
    critical: "bg-red-100 text-red-800",
    high:     "bg-orange-100 text-orange-800",
    medium:   "bg-yellow-100 text-yellow-800",
    low:      "bg-gray-100 text-gray-600",
  }
  return map[sev] ?? "bg-gray-100 text-gray-600"
}

function fmtDate(ts: number | string) {
  const d = typeof ts === "number" ? new Date(ts) : new Date(ts)
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default async function SettingsPage({
  searchParams,
}: {
  searchParams: Promise<{ tab?: string }>
}) {
  const params = await searchParams
  const activeTab: TabId = (params.tab as TabId) ?? "deploy"

  const [deployData, supabaseData] = await Promise.all([
    fetchDeployments(),
    fetchSupabaseHealth(),
  ])

  const TABS: { id: TabId; label: string }[] = [
    { id: "deploy",   label: "Deploy" },
    { id: "domains",  label: "Domains" },
    { id: "secrets",  label: "Secrets" },
    { id: "supabase", label: "Supabase" },
  ]

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Settings</h1>
        <p className="text-sm text-gray-500 mt-1">
          Deploy, domains, secrets, and Supabase health — Odoo.sh parity surface.
        </p>
      </div>

      {/* Tab navigation (URL-based, no JS required) */}
      <div className="border-b border-gray-200">
        <nav className="flex -mb-px space-x-6">
          {TABS.map((tab) => (
            <a
              key={tab.id}
              href={`?tab=${tab.id}`}
              className={[
                "pb-3 text-sm font-medium border-b-2 transition-colors",
                activeTab === tab.id
                  ? "border-blue-600 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300",
              ].join(" ")}
            >
              {tab.label}
            </a>
          ))}
        </nav>
      </div>

      {/* Deploy tab */}
      {activeTab === "deploy" && (
        <section className="space-y-4">
          <h2 className="text-base font-medium text-gray-900">Recent Deployments</h2>
          {deployData.error && (
            <div className="rounded-md bg-yellow-50 border border-yellow-200 p-3 text-sm text-yellow-800">
              {deployData.error}
            </div>
          )}
          {deployData.deployments.length === 0 && !deployData.error && (
            <p className="text-sm text-gray-500">No deployments found.</p>
          )}
          <div className="space-y-2">
            {deployData.deployments.map((d) => (
              <div key={d.id} className="rounded-lg border border-gray-200 bg-white p-4">
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <span className={`inline-flex items-center rounded px-2 py-0.5 text-xs font-medium ${stateColor(d.state)}`}>
                        {d.state}
                      </span>
                      <span className="text-xs text-gray-400">{fmtDate(d.createdAt)}</span>
                    </div>
                    {d.message && (
                      <p className="mt-1 text-sm text-gray-700 truncate">{d.message}</p>
                    )}
                    {d.sha && (
                      <p className="mt-0.5 text-xs font-mono text-gray-400">{d.sha.slice(0, 8)}</p>
                    )}
                    {d.errorMessage && (
                      <p className="mt-1 text-xs text-red-600 truncate">{d.errorMessage}</p>
                    )}
                  </div>
                  {d.url && (
                    <a
                      href={`https://${d.url}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="shrink-0 text-xs text-blue-600 hover:underline"
                    >
                      View ↗
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Domains tab */}
      {activeTab === "domains" && (
        <section className="space-y-4">
          <h2 className="text-base font-medium text-gray-900">Domain Registry</h2>
          <p className="text-sm text-gray-500">
            Sourced from <code className="text-xs bg-gray-100 px-1 rounded">ssot/domains/subdomain-registry.yaml</code>.
            Edit the SSOT file to change records; Terraform applies on merge to main.
          </p>
          <div className="overflow-hidden rounded-lg border border-gray-200">
            <table className="min-w-full divide-y divide-gray-200 text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">Subdomain</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">Type</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">Target</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">Purpose</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 bg-white">
                {CANONICAL_DOMAINS.map((d) => (
                  <tr key={d.subdomain} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-mono text-xs text-gray-900">{d.subdomain}.insightpulseai.com</td>
                    <td className="px-4 py-3 text-xs text-gray-600">{d.type}</td>
                    <td className="px-4 py-3 font-mono text-xs text-gray-500 truncate max-w-[180px]">{d.target}</td>
                    <td className="px-4 py-3 text-xs text-gray-700">{d.purpose}</td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center rounded px-2 py-0.5 text-xs font-medium ${domainStatusColor(d.status ?? "")}`}>
                        {d.status ?? "unknown"}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* Secrets tab */}
      {activeTab === "secrets" && (
        <section className="space-y-4">
          <h2 className="text-base font-medium text-gray-900">Secret Inventory</h2>
          {supabaseData.error && (
            <div className="rounded-md bg-yellow-50 border border-yellow-200 p-3 text-sm text-yellow-800">
              {supabaseData.error}
            </div>
          )}
          {supabaseData.missingSecrets.length === 0 ? (
            <div className="rounded-md bg-green-50 border border-green-200 p-3 text-sm text-green-800">
              No missing secrets detected in ops.secret_inventory.
            </div>
          ) : (
            <>
              <p className="text-sm text-gray-500">
                {supabaseData.missingSecrets.length} missing secret(s) from{" "}
                <code className="text-xs bg-gray-100 px-1 rounded">ops.secret_inventory</code>.
              </p>
              <div className="overflow-hidden rounded-lg border border-gray-200">
                <table className="min-w-full divide-y divide-gray-200 text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">Secret Name</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">Severity</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">Last Checked</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100 bg-white">
                    {supabaseData.missingSecrets.map((s) => (
                      <tr key={s.name} className="hover:bg-gray-50">
                        <td className="px-4 py-3 font-mono text-xs text-gray-900">{s.name}</td>
                        <td className="px-4 py-3">
                          <span className={`inline-flex items-center rounded px-2 py-0.5 text-xs font-medium ${sevColor(s.severity)}`}>
                            {s.severity}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-xs text-gray-500">
                          {s.last_checked ? fmtDate(s.last_checked) : "—"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </section>
      )}

      {/* Supabase tab */}
      {activeTab === "supabase" && (
        <section className="space-y-6">
          <div>
            <h2 className="text-base font-medium text-gray-900">Supabase Health</h2>
            <p className="text-sm text-gray-500 mt-0.5">
              Project: <code className="text-xs bg-gray-100 px-1 rounded">spdtwktxdalcfigzeqrz</code> ·{" "}
              <a href="https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline text-xs">Dashboard ↗</a>
            </p>
          </div>

          {supabaseData.error && (
            <div className="rounded-md bg-yellow-50 border border-yellow-200 p-3 text-sm text-yellow-800">
              {supabaseData.error}
            </div>
          )}

          {/* Recent runs */}
          <div>
            <h3 className="text-sm font-medium text-gray-800 mb-2">Recent Function Runs</h3>
            {supabaseData.recentRuns.length === 0 ? (
              <p className="text-sm text-gray-500">No runs in ops.runs table (or table not yet created).</p>
            ) : (
              <div className="overflow-hidden rounded-lg border border-gray-200">
                <table className="min-w-full divide-y divide-gray-200 text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">Function</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">Status</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">Started</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100 bg-white">
                    {supabaseData.recentRuns.map((r, i) => (
                      <tr key={i} className="hover:bg-gray-50">
                        <td className="px-4 py-3 font-mono text-xs text-gray-900">{r.function_name}</td>
                        <td className="px-4 py-3">
                          <span className={`inline-flex items-center rounded px-2 py-0.5 text-xs font-medium ${
                            r.status === "success" ? "bg-green-100 text-green-800" :
                            r.status === "error" ? "bg-red-100 text-red-800" :
                            "bg-gray-100 text-gray-600"
                          }`}>
                            {r.status}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-xs text-gray-500">{fmtDate(r.started_at)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Quick links */}
          <div>
            <h3 className="text-sm font-medium text-gray-800 mb-2">Quick Links</h3>
            <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
              {[
                { label: "Edge Functions", href: "https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz/functions" },
                { label: "Migrations",     href: "https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz/database/migrations" },
                { label: "Table Editor",   href: "https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz/editor" },
                { label: "Vault",          href: "https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz/settings/vault-secrets" },
              ].map((link) => (
                <a
                  key={link.label}
                  href={link.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="rounded-md border border-gray-200 bg-white px-3 py-2 text-center text-xs text-gray-700 hover:bg-gray-50 hover:border-gray-300 transition-colors"
                >
                  {link.label} ↗
                </a>
              ))}
            </div>
          </div>
        </section>
      )}
    </div>
  )
}
