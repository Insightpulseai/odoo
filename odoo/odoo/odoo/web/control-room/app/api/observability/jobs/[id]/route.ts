import { NextRequest, NextResponse } from 'next/server';
import { getJob } from '@/lib/supabase/observability';

/**
 * GET /api/observability/jobs/[id]
 * Get job details with runs and events
 */
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const job = await getJob(params.id);

    if (!job) {
      return NextResponse.json(
        { error: 'Job not found' },
        { status: 404 }
      );
    }

    return NextResponse.json(job);
  } catch (error) {
    console.error('Failed to get job:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to get job' },
      { status: 500 }
    );
  }
}
