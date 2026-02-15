/**
 * GET /api/jobs/list
 *
 * Purpose: List jobs with optional filters
 * Query Params:
 * - source: string (optional)
 * - jobType: string (optional)
 * - status: string (optional)
 * - limit: number (optional, default: 100)
 */

import { NextResponse } from 'next/server'
import { listJobs, JobStatus } from '@/lib/supabaseJobsClient'

export async function GET(req: Request) {
  try {
    const { searchParams } = new URL(req.url)

    const source = searchParams.get('source') || undefined
    const jobType = searchParams.get('jobType') || undefined
    const status = (searchParams.get('status') as JobStatus) || undefined
    const limit = parseInt(searchParams.get('limit') || '100', 10)

    const jobs = await listJobs(
      {
        source,
        jobType,
        status,
      },
      limit
    )

    return NextResponse.json({
      ok: true,
      jobs,
      count: jobs.length,
    })
  } catch (err: any) {
    console.error('Job list error:', err)
    return NextResponse.json(
      {
        ok: false,
        error: err.message || 'Internal server error',
      },
      { status: 500 }
    )
  }
}
