/**
 * GET /api/observability/do/droplets
 *
 * Returns the list of DigitalOcean droplets.
 * Server-only — DIGITALOCEAN_API_TOKEN never reaches the browser.
 *
 * Runbook: docs/ops/DIGITALOCEAN_OBSERVABILITY.md
 */
import { NextResponse } from 'next/server'
import { listDroplets } from '@/lib/do-client'

export async function GET() {
  try {
    const droplets = await listDroplets()
    return NextResponse.json({ droplets })
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error'
    return NextResponse.json({ error: message }, { status: 502 })
  }
}
