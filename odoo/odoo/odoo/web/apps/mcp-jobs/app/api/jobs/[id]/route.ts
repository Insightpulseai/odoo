/**
 * GET /api/jobs/[id]
 *
 * Purpose: Get job details by ID including runs and events
 */

import { NextResponse } from 'next/server'
import { getJob, getJobRuns, getJobEvents } from '@/lib/supabaseJobsClient'

export async function GET(req: Request, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params

    if (!id) {
      return NextResponse.json({ ok: false, error: 'Missing job ID' }, { status: 400 })
    }

    const [job, runs, events] = await Promise.all([getJob(id), getJobRuns(id), getJobEvents(id)])

    if (!job) {
      return NextResponse.json({ ok: false, error: 'Job not found' }, { status: 404 })
    }

    return NextResponse.json({
      ok: true,
      job,
      runs,
      events,
    })
  } catch (err: any) {
    console.error('Job get error:', err)
    return NextResponse.json(
      {
        ok: false,
        error: err.message || 'Internal server error',
      },
      { status: 500 }
    )
  }
}

/**
 * DELETE /api/jobs/[id]
 *
 * Purpose: Cancel job (if queued)
 */
export async function DELETE(req: Request, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params

    if (!id) {
      return NextResponse.json({ ok: false, error: 'Missing job ID' }, { status: 400 })
    }

    const { cancelJob } = await import('@/lib/supabaseJobsClient')
    await cancelJob(id)

    return NextResponse.json({
      ok: true,
      message: 'Job cancelled successfully',
    })
  } catch (err: any) {
    console.error('Job cancel error:', err)
    return NextResponse.json(
      {
        ok: false,
        error: err.message || 'Internal server error',
      },
      { status: 500 }
    )
  }
}
