/**
 * POST /api/jobs/enqueue
 *
 * Purpose: Enqueue new job to mcp_jobs Supabase backend
 * Auth: Server-side only (uses service role key)
 *
 * Request Body:
 * {
 *   source: string           // Required: Source app (e.g., "v0-open-in-v0-sa")
 *   jobType: string          // Required: Job type (e.g., "discovery", "sync")
 *   payload: object          // Required: Job-specific data
 *   priority?: number        // Optional: 1-10 (default: 5)
 *   scheduledAt?: string     // Optional: ISO date string
 *   maxRetries?: number      // Optional: Max retry attempts (default: 3)
 * }
 *
 * Response:
 * {
 *   ok: boolean
 *   jobId?: string
 *   error?: string
 * }
 */

import { NextResponse } from 'next/server'
import { enqueueJob } from '@/lib/supabaseJobsClient'

export async function POST(req: Request) {
  try {
    const body = await req.json()

    // Validate required fields
    if (!body.source) {
      return NextResponse.json({ ok: false, error: 'Missing required field: source' }, { status: 400 })
    }

    if (!body.jobType) {
      return NextResponse.json({ ok: false, error: 'Missing required field: jobType' }, { status: 400 })
    }

    if (!body.payload) {
      return NextResponse.json({ ok: false, error: 'Missing required field: payload' }, { status: 400 })
    }

    // Enqueue job
    const jobId = await enqueueJob(body.source, body.jobType, body.payload, {
      priority: body.priority,
      scheduledAt: body.scheduledAt,
      maxRetries: body.maxRetries,
    })

    return NextResponse.json({
      ok: true,
      jobId,
    })
  } catch (err: any) {
    console.error('Job enqueue error:', err)
    return NextResponse.json(
      {
        ok: false,
        error: err.message || 'Internal server error',
      },
      { status: 500 }
    )
  }
}
