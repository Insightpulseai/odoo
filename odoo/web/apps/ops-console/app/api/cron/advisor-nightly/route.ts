import { NextRequest, NextResponse } from 'next/server'
import { getOrCreateRequestId, correlationHeaders } from '@/lib/http/correlation'

// Vercel Cron: runs daily at 01:00 UTC (vercel.json schedule: "0 1 * * *")
// Authorization: Vercel injects Authorization: Bearer ${CRON_SECRET} automatically.
// Ref: https://vercel.com/docs/cron-jobs/manage-cron-jobs

export const maxDuration = 300

export async function GET(req: NextRequest) {
  // Verify Vercel cron authorization
  const authHeader = req.headers.get('authorization')
  if (authHeader !== `Bearer ${process.env.CRON_SECRET}`) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const supabaseUrl = process.env.SUPABASE_URL
  const serviceKey = process.env.SUPABASE_SERVICE_ROLE_KEY
  if (!supabaseUrl || !serviceKey) {
    return NextResponse.json(
      { error: 'KEY_MISSING', ssot_ref: 'ssot/secrets/registry.yaml' },
      { status: 503 }
    )
  }

  const requestId = getOrCreateRequestId(req)
  const headers = { 'Content-Type': 'application/json', ...correlationHeaders(requestId), Authorization: `Bearer ${serviceKey}` }

  const providers = ['github', 'agentic_coding', 'devops_lifecycle'] as const
  const results: Record<string, unknown> = {}

  for (const provider of providers) {
    try {
      const scanRes = await fetch(
        `${req.nextUrl.origin}/api/advisor/scans/${provider}`,
        { method: 'POST', headers }
      )
      results[provider] = scanRes.ok
        ? await scanRes.json()
        : { error: `scan failed: ${scanRes.status}` }
    } catch (err) {
      results[provider] = { error: String(err) }
    }
  }

  // Log completion to ops.run_events
  await fetch(`${supabaseUrl}/rest/v1/ops.run_events`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', apikey: serviceKey, Authorization: `Bearer ${serviceKey}` },
    body: JSON.stringify({
      run_id: `cron-advisor-nightly-${requestId}`,
      level: 'info',
      message: 'advisor-nightly cron completed',
      payload: { providers, results },
    }),
  })

  return NextResponse.json({ ok: true, providers, results }, { headers: correlationHeaders(requestId) })
}
