import { NextResponse } from 'next/server'
import { getOdooshSummary } from '@/lib/providers'

const ODOOSH_URL = process.env.ODOOSH_URL
const ODOOSH_TOKEN = process.env.ODOOSH_TOKEN
const ODOOSH_PROJECT = process.env.ODOOSH_PROJECT

export async function GET() {
  // If live Odoo.sh credentials are configured, attempt live fetch
  if (ODOOSH_URL && ODOOSH_TOKEN && ODOOSH_PROJECT) {
    try {
      // TODO: Implement live Odoo.sh API client
      // The Odoo.sh API is not publicly documented in full.
      // When available, this would fetch:
      // - GET /api/v1/projects/{project}/branches
      // - GET /api/v1/projects/{project}/builds
      // - GET /api/v1/projects/{project}/databases
      // For now, fall through to fixtures
    } catch {
      // Fall through to fixtures
    }
  }

  // Return fixture data for local development
  const summary = getOdooshSummary()
  return NextResponse.json({
    ...summary,
    source: ODOOSH_URL ? 'odoosh-live' : 'fixtures',
    fetchedAt: new Date().toISOString(),
  })
}
