/**
 * GET /api/observability/do/metrics?dropletId=<id>&metric=<cpu|memory_utilization_percent|...>&hours=<1|6|24>
 *
 * Returns time-series metrics for a specific droplet.
 * Server-only — DIGITALOCEAN_API_TOKEN never reaches the browser.
 *
 * Runbook: docs/ops/DIGITALOCEAN_OBSERVABILITY.md
 */
import { NextRequest, NextResponse } from 'next/server'
import { getDropletMetrics } from '@/lib/do-client'
import { getOrCreateRequestId, correlationHeaders } from '@/lib/http/correlation'

const ALLOWED_METRICS = [
  'cpu',
  'memory_utilization_percent',
  'disk_utilization_percent',
  'public_outbound_bandwidth',
] as const

type MetricType = (typeof ALLOWED_METRICS)[number]

export async function GET(req: NextRequest) {
  const rid = getOrCreateRequestId(req.headers.get('x-request-id'))
  const hdrs = correlationHeaders(rid)

  const { searchParams } = req.nextUrl
  const dropletIdStr = searchParams.get('dropletId')
  const metric = searchParams.get('metric') as MetricType | null
  const hoursStr = searchParams.get('hours') ?? '1'

  if (!dropletIdStr || !metric) {
    return NextResponse.json({ error: 'dropletId and metric are required' }, { status: 400, headers: hdrs })
  }

  if (!ALLOWED_METRICS.includes(metric)) {
    return NextResponse.json({ error: `metric must be one of: ${ALLOWED_METRICS.join(', ')}` }, { status: 400, headers: hdrs })
  }

  const dropletId = parseInt(dropletIdStr, 10)
  if (isNaN(dropletId)) {
    return NextResponse.json({ error: 'dropletId must be a number' }, { status: 400, headers: hdrs })
  }

  const hours = Math.min(Math.max(parseInt(hoursStr, 10) || 1, 1), 24)
  const end = new Date()
  const start = new Date(end.getTime() - hours * 60 * 60 * 1000)

  try {
    const result = await getDropletMetrics(dropletId, metric, start, end)
    return NextResponse.json({ metric, dropletId, start: start.toISOString(), end: end.toISOString(), result }, { headers: hdrs })
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error'
    return NextResponse.json({ error: message }, { status: 502, headers: hdrs })
  }
}
