/**
 * GET /api/observability/do/alerts
 *
 * Returns active DigitalOcean alert policies.
 * Server-only — DIGITALOCEAN_API_TOKEN never reaches the browser.
 *
 * Runbook: docs/ops/DIGITALOCEAN_OBSERVABILITY.md
 */
import { NextResponse } from 'next/server'
import { listAlertPolicies } from '@/lib/do-client'

export async function GET() {
  try {
    const policies = await listAlertPolicies()
    return NextResponse.json({ policies })
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error'
    return NextResponse.json({ error: message }, { status: 502 })
  }
}
