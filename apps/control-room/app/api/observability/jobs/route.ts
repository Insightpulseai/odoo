import { NextRequest, NextResponse } from 'next/server';
import { listJobs, enqueueJob, getJobStats } from '@/lib/supabase/observability';

/**
 * GET /api/observability/jobs
 * List jobs with optional filtering
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);

    const filters = {
      source: searchParams.get('source') || undefined,
      job_type: searchParams.get('job_type') || undefined,
      status: searchParams.get('status') as any || undefined,
      limit: Number(searchParams.get('limit')) || 50,
      offset: Number(searchParams.get('offset')) || 0,
    };

    const result = await listJobs(filters);

    return NextResponse.json(result);
  } catch (error) {
    console.error('Failed to list jobs:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to list jobs' },
      { status: 500 }
    );
  }
}

/**
 * POST /api/observability/jobs
 * Enqueue a new job
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { source, job_type, payload, priority, scheduled_at, context } = body;

    if (!source || !job_type) {
      return NextResponse.json(
        { error: 'source and job_type are required' },
        { status: 400 }
      );
    }

    const jobId = await enqueueJob(source, job_type, payload || {}, {
      priority,
      scheduledAt: scheduled_at,
      context,
    });

    return NextResponse.json({ ok: true, job_id: jobId });
  } catch (error) {
    console.error('Failed to enqueue job:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to enqueue job' },
      { status: 500 }
    );
  }
}
