/**
 * do-client.ts
 * Server-only DigitalOcean API client.
 *
 * NEVER import this in client components or pages without "use server".
 * The DIGITALOCEAN_API_TOKEN must never reach the browser.
 *
 * Runbook: docs/ops/DIGITALOCEAN_OBSERVABILITY.md
 */

const DO_API_BASE = 'https://api.digitalocean.com/v2'

function getToken(): string {
  const token = process.env.DIGITALOCEAN_API_TOKEN
  if (!token) throw new Error('DIGITALOCEAN_API_TOKEN is not set')
  return token
}

async function doRequest<T>(path: string): Promise<T> {
  const res = await fetch(`${DO_API_BASE}${path}`, {
    headers: {
      Authorization: `Bearer ${getToken()}`,
      'Content-Type': 'application/json',
    },
    next: { revalidate: 60 }, // Cache 60s — DO metrics rate limit is 250 req/hr
  })

  if (!res.ok) {
    const body = await res.text()
    throw new Error(`DO API ${res.status}: ${body}`)
  }

  return res.json() as Promise<T>
}

// ─── Types ─────────────────────────────────────────────────────────────────

export interface DODroplet {
  id: number
  name: string
  status: 'new' | 'active' | 'off' | 'archive'
  region: { name: string; slug: string }
  size: { vcpus: number; memory: number; disk: number }
  networks: {
    v4: Array<{ ip_address: string; type: 'public' | 'private' }>
  }
  created_at: string
}

export interface DOAlertPolicy {
  uuid: string
  type: string
  description: string
  compare: string
  value: number
  window: string
  enabled: boolean
  tags: string[]
  alerts: {
    slack: { channels: string[]; urls: string[] }
    email: string[]
  }
}

export interface DOMetricResult {
  metric: Record<string, string>
  values: Array<[number, string]>
}

// ─── Droplets ──────────────────────────────────────────────────────────────

export async function listDroplets(): Promise<DODroplet[]> {
  const data = await doRequest<{ droplets: DODroplet[] }>('/droplets')
  return data.droplets
}

// ─── Alert Policies ────────────────────────────────────────────────────────

export async function listAlertPolicies(): Promise<DOAlertPolicy[]> {
  const data = await doRequest<{ policies: DOAlertPolicy[] }>('/monitoring/alerts')
  return data.policies
}

// ─── Metrics ────────────────────────────────────────────────────────────────
// Docs: https://docs.digitalocean.com/reference/api/api-reference/#operation/monitoring_get_dropletCpuMetrics

type MetricType =
  | 'cpu'
  | 'memory_utilization_percent'
  | 'disk_utilization_percent'
  | 'public_outbound_bandwidth'

export async function getDropletMetrics(
  dropletId: number,
  metric: MetricType,
  start: Date,
  end: Date,
): Promise<DOMetricResult[]> {
  const startStr = Math.floor(start.getTime() / 1000).toString()
  const endStr = Math.floor(end.getTime() / 1000).toString()

  const metricPath: Record<MetricType, string> = {
    cpu: 'cpu',
    memory_utilization_percent: 'memory_utilization_percent',
    disk_utilization_percent: 'disk_utilization_percent',
    public_outbound_bandwidth: 'public_outbound_bandwidth',
  }

  const path = `/monitoring/metrics/droplet/${metricPath[metric]}?host_id=${dropletId}&start=${startStr}&end=${endStr}`
  const data = await doRequest<{ data: { result: DOMetricResult[] } }>(path)
  return data.data.result
}
