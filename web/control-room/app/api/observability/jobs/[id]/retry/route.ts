import { NextRequest, NextResponse } from 'next/server';
import { retryJob } from '@/lib/supabase/observability';

/**
 * POST /api/observability/jobs/[id]/retry
 * Retry a failed or dead letter job
 */
export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const success = await retryJob(params.id);

    if (!success) {
      return NextResponse.json(
        { error: 'Job not found or not retryable' },
        { status: 404 }
      );
    }

    return NextResponse.json({ ok: true, message: 'Job queued for retry' });
  } catch (error) {
    console.error('Failed to retry job:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to retry job' },
      { status: 500 }
    );
  }
}
